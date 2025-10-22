import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import math
from io import BytesIO
import pandas as pd

# =========================
#  Prostorový index (hash mřížka) – rychlá kolizní detekce
# =========================
class SpatialIndex:
    def __init__(self, cell_size: int, neighbor_span: int = 2):
        """
        cell_size: velikost buňky mřížky (px)
        neighbor_span: jak daleko (v buňkách) se má při kolizi dívat do okolí (±neighbor_span).
                       2 => 5×5 okolí, bezpečné pro směs poloměrů.
        """
        self.cell = float(max(1, cell_size))
        self.span = int(max(1, neighbor_span))
        self.grid = {}  # (ix, iy) -> list[int] (indexy do polí níže)
        self.cx = []    # x středy
        self.cy = []    # y středy
        self.cr = []    # poloměry

    def _key(self, x: float, y: float):
        return (int(x // self.cell), int(y // self.cell))

    def _neighbors(self, x: float, y: float):
        ix, iy = self._key(x, y)
        s = self.span
        for dx in range(-s, s + 1):
            for dy in range(-s, s + 1):
                yield (ix + dx, iy + dy)

    def add(self, x: int, y: int, r: int):
        idx = len(self.cx)
        self.cx.append(x)
        self.cy.append(y)
        self.cr.append(r)
        k = self._key(x, y)
        self.grid.setdefault(k, []).append(idx)

    def overlaps(self, x: int, y: int, r: int, gap: int) -> bool:
        """True, pokud (x,y,r) koliduje s existujícím kruhem (s mezerou 'gap')."""
        for k in self._neighbors(x, y):
            for idx in self.grid.get(k, []):
                dx = x - self.cx[idx]
                dy = y - self.cy[idx]
                lim = r + self.cr[idx] + gap  # minimální povolená vzdálenost středů
                if dx * dx + dy * dy < lim * lim:
                    return True
        return False


# =========================
#  Rychlý odhad kapacity (varování před přehnanými počty)
# =========================
def capacity_check(canvas_w, canvas_h, specs, gap):
    """
    specs: [(color, radius, count, label), ...]
    Vrací tuple (requested_area, practical_capacity_area)
    """
    canvas_area = float(canvas_w * canvas_h)
    requested_area = float(sum(c * math.pi * r * r for _, r, c, _ in specs))
    # cca hex packing 90.69 %, ale s rezervou a penalizací za mezery:
    practical_fill = 0.9069 * 0.80
    max_r = max((r for _, r, _, _ in specs), default=1)
    gap_penalty = 1.0 + (gap / max(1, max_r)) * 0.5
    practical_cap = practical_fill * canvas_area / gap_penalty
    return requested_area, practical_cap


# =========================
#  Generování kruhů s prostorovým indexem
# =========================
def generate_circles_fast(canvas_w, canvas_h, circle_specs, gap, max_attempts_per_circle, rng):
    """
    circle_specs: list[(color:str, radius:int, count:int, label:str)]
    Vrací: (matplotlib.Figure, list[dict]) – fig, rows
    """
    # Varování kapacity (nezastavuje generování)
    req_area, cap_area = capacity_check(canvas_w, canvas_h, circle_specs, gap)
    if cap_area > 0 and req_area > cap_area:
        ratio = 100.0 * req_area / cap_area
        st.warning(
            f"Požadovaná plocha kruhů je ~{ratio:.0f}% praktického maxima. "
            "Může to zpomalit generování a snížit počet úspěšně umístěných kruhů. "
            "Zvažte větší plátno, menší poloměry nebo menší počty."
        )

    # Umisťuj od největších poloměrů k nejmenším
    circle_specs = sorted(circle_specs, key=lambda t: t[1], reverse=True)
    max_r = max((r for _, r, _, _ in circle_specs), default=1)

    # Buňka mřížky = (max_r + gap); sousedství 5×5 (span=2) pokrývá i dvě největší sousední buňky
    cell_size = int(max(1, max_r + gap))
    si = SpatialIndex(cell_size=cell_size, neighbor_span=2)

    rows = []
    for color, radius, count, label in circle_specs:
        placed = 0
        attempts = 0
        # upper bound pokusů roste s plochou plátna / plochou kruhu
        local_max_attempts = max_attempts_per_circle + int((canvas_w * canvas_h) / (math.pi * radius * radius) * 0.5)

        while placed < count and attempts < local_max_attempts:
            x = int(rng.integers(radius, canvas_w - radius + 1))
            y = int(rng.integers(radius, canvas_h - radius + 1))

            if not si.overlaps(x, y, radius, gap):
                si.add(x, y, radius)
                rows.append({
                    "ID": len(rows) + 1,
                    "Type": label.capitalize(),  # "Red"/"Blue"/"Green"
                    "Color": color,              # "red"/"blue"/"green"
                    "X": x,
                    "Y": y,
                    "Radius": int(radius),
                    "Canvas Width": int(canvas_w),
                    "Canvas Height": int(canvas_h),
                    "Gap Between Circles": int(gap),
                })
                placed += 1
                attempts = 0
            else:
                attempts += 1

        if placed < count:
            st.warning(f"Nepodařilo se umístit {count - placed} z {count} „{label}“ (hustota/hledání).")

    # Vykreslení až po generování – bez obrysu (linewidth=0)
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, canvas_w)
    ax.set_ylim(0, canvas_h)
    ax.set_aspect("equal", adjustable="box")
    ax.set_facecolor("white")
    ax.axis("off")

    for row in rows:
        c = plt.Circle((row["X"], row["Y"]), row["Radius"], color=row["Color"], linewidth=0)
        ax.add_artist(c)

    return fig, rows


# =========================
#  Streamlit aplikace
# =========================
def main():
    st.set_page_config(page_title="Generátor kruhů — rychlý", layout="wide")
    st.title("Generátor kruhů — rychlý a stabilní")

    # Formulář v sidebaru – žádné průběžné přepočty při posouvání sliderů
    with st.sidebar.form("cfg"):
        st.header("Nastavení plátna")
        canvas_width = st.slider("Šířka plátna", 200, 3000, 1000, step=50)
        canvas_height = st.slider("Výška plátna", 200, 3000, 1000, step=50)

        st.header("Nastavení kruhů")
        gap_between_circles = st.slider("Minimální mezera mezi kruhy", 0, 50, 5, step=1)
        max_attempts_per_circle = st.slider("Max. počet pokusů na 1 kruh", 50, 10000, 2000, step=100)

        st.header("Reprodukovatelnost")
        use_seed = st.checkbox("Použít seed (opakovatelná generace)?", value=False)
        seed_value = st.number_input("Seed", min_value=0, max_value=2**32 - 1, value=42, step=1)

        st.header("Export")
        png_dpi = st.slider("DPI pro PNG export", 72, 400, 200, step=4)

        st.header("Náhled")
        preview_width_px = st.slider("Šířka náhledu (px)", 300, 1200, 800, step=10)

        st.subheader("Červené kruhy")
        num_red_circles = st.slider("Počet červených kruhů", 0, 300, 50)
        red_circle_radius = st.slider("Poloměr červených kruhů", 1, 100, 20)

        st.subheader("Modré kruhy")
        num_blue_circles = st.slider("Počet modrých kruhů", 0, 300, 50)
        blue_circle_radius = st.slider("Poloměr modrých kruhů", 1, 100, 10)

        st.subheader("Zelené kruhy")
        num_green_circles = st.slider("Počet zelených kruhů", 0, 300, 50)
        green_circle_radius = st.slider("Poloměr zelených kruhů", 1, 100, 5)

        submitted = st.form_submit_button("Generovat")

    # Session state
    if "rows" not in st.session_state:
        st.session_state["rows"] = None
    if "image_bytes" not in st.session_state:
        st.session_state["image_bytes"] = None

    # Generování po odeslání formuláře
    if submitted:
        rng = np.random.default_rng(seed_value) if use_seed else np.random.default_rng()
        circle_specs = [
            ("red",   int(red_circle_radius),   int(num_red_circles),   "red"),
            ("blue",  int(blue_circle_radius),  int(num_blue_circles),  "blue"),
            ("green", int(green_circle_radius), int(num_green_circles), "green"),
        ]

        fig, rows = generate_circles_fast(
            int(canvas_width), int(canvas_height),
            circle_specs, int(gap_between_circles),
            int(max_attempts_per_circle), rng
        )

        # Uložit PNG do paměti a zavřít fig kvůli paměti
        png_buffer = BytesIO()
        fig.savefig(png_buffer, format="png", dpi=int(png_dpi), bbox_inches="tight")
        png_buffer.seek(0)
        st.session_state["image_bytes"] = png_buffer.read()
        plt.close(fig)

        st.session_state["rows"] = rows

    # Výstup
    if st.session_state["rows"]:
        st.write("### Vygenerované plátno")
        st.image(st.session_state["image_bytes"], caption="Náhled PNG", width=int(preview_width_px))

        df = pd.DataFrame(st.session_state["rows"])
        # Skutečné pokrytí podle opravdu umístěných kruhů
        total_circle_surface = float(np.pi * np.sum(np.square(df["Radius"])))
        canvas_surface = float(canvas_width * canvas_height)
        ratio_percentage = (total_circle_surface / max(1.0, canvas_surface)) * 100.0
        st.write(f"### Poměr děrování (pokrytí): {ratio_percentage:.2f}%")
        st.caption("Počítáno ze skutečně umístěných kruhů.")

        # Přehled počtů podle typu
        counts = df["Type"].value_counts().to_dict()
        st.write("**Počty umístěných kruhů:** " +
                 ", ".join([f"{k}: {v}" for k, v in counts.items()]) +
                 f" (celkem {len(df)})")

        # Download – PNG
        st.download_button(
            label="Stáhnout PNG",
            data=st.session_state["image_bytes"],
            file_name="kruhove_platno.png",
            mime="image/png",
        )

        # Download – CSV
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        st.download_button(
            label="Stáhnout CSV",
            data=csv_buffer,
            file_name="souradnice_kruhu.csv",
            mime="text/csv",
        )
    else:
        st.info("Nastav parametry v levém panelu a klikni na **Generovat**.")


if __name__ == "__main__":
    main()
