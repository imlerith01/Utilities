import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import math
from io import BytesIO
import pandas as pd

# ---------- RYCHLÁ VEKTOROVÁ KOLIZE ----------
def overlaps_np(x, y, r, centers, radii, gap):
    """Vrátí True, pokud nový kruh (x,y,r) koliduje s existujícími.
    centers: np.ndarray shape (N,2), radii: np.ndarray shape (N,)"""
    if centers.size == 0:
        return False
    dx = centers[:, 0] - x
    dy = centers[:, 1] - y
    # Porovnáváme vzdálenost^2 a (součet poloměrů + mezera)^2
    dist2 = dx*dx + dy*dy
    limit = radii + r + gap
    return np.any(dist2 < (limit * limit))

def generate_circles(canvas_w, canvas_h, circle_specs, gap, max_attempts_per_circle, rng):
    """
    circle_specs: list of tuples (color, radius, count, label)
    Vrací: ax_figure (matplotlib Figure), circle_rows (list of dicts s daty všech kruhů)
    """
    centers = np.empty((0, 2), dtype=float)
    radii = np.empty((0,), dtype=float)

    rows = []  # pro CSV a další výpočty
    # Vykreslení až po generování — menší nároky na paměť při opakovaném běhu
    for color, radius, count, label in circle_specs:
        placed = 0
        attempts = 0
        while placed < count and attempts < max_attempts_per_circle:
            # Náhodné CELÉ souřadnice středů v rámci plátna
            x = int(rng.integers(radius, canvas_w - radius + 1))
            y = int(rng.integers(radius, canvas_h - radius + 1))

            if not overlaps_np(x, y, radius, centers, radii, gap):
                # Přidat
                centers = np.vstack((centers, [x, y]))
                radii = np.append(radii, radius)
                rows.append({
                    "ID": len(rows) + 1,
                    "Type": label.capitalize(),
                    "Color": color,
                    "X": int(x),
                    "Y": int(y),
                    "Radius": int(radius),
                    "Canvas Width": int(canvas_w),
                    "Canvas Height": int(canvas_h),
                    "Gap Between Circles": int(gap),
                })
                placed += 1
                attempts = 0  # resetovat pokusy pro další kruh této barvy
            else:
                attempts += 1

        if placed < count:
            st.warning(f"⚠️ Nepodařilo se umístit {count - placed} z požadovaných {count} „{label}“ kruhů "
                       f"(pravděpodobně vysoká hustota). Zvažte větší plátno, menší poloměry nebo větší mezeru.")

    # Vykreslení
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, canvas_w)
    ax.set_ylim(0, canvas_h)
    ax.set_aspect("equal", adjustable="box")
    ax.set_facecolor("white")
    ax.axis("off")
    # Kreslit až teď, aby bylo rychlé
    for row in rows:
        c = plt.Circle((row["X"], row["Y"]), row["Radius"], color=row["Color"])
        ax.add_artist(c)
    return fig, rows

# ---------- STREAMLIT APLIKACE ----------
def main():
    st.title("Generátor kruhů — stabilní a rychlý")

    # Sidebar – plátno
    st.sidebar.header("Nastavení plátna")
    canvas_width = st.sidebar.slider("Šířka plátna", 200, 4000, 1000, step=50)
    canvas_height = st.sidebar.slider("Výška plátna", 200, 4000, 1000, step=50)

    # Sidebar – parametry
    st.sidebar.header("Nastavení kruhů")
    gap_between_circles = st.sidebar.slider("Minimální mezera mezi kruhy", 0, 100, 5)
    max_attempts_per_circle = st.sidebar.slider("Max. počet pokusů na jeden kruh", 50, 20000, 5000, step=50)

    st.sidebar.header("Reprodukovatelnost")
    use_seed = st.sidebar.checkbox("Použít seed (opakovatelná generace)?", value=False)
    seed_value = st.sidebar.number_input("Seed", min_value=0, max_value=2**32-1, value=42, step=1)

    st.sidebar.header("Export")
    png_dpi = st.sidebar.slider("DPI pro PNG export", 72, 600, 200, step=4)

    # Barvy
    st.sidebar.subheader("Červené kruhy")
    num_red_circles = st.sidebar.slider("Počet červených kruhů", 0, 2000, 30)
    red_circle_radius = st.sidebar.slider("Poloměr červených kruhů", 1, 200, 20)

    st.sidebar.subheader("Modré kruhy")
    num_blue_circles = st.sidebar.slider("Počet modrých kruhů", 0, 2000, 20)
    blue_circle_radius = st.sidebar.slider("Poloměr modrých kruhů", 1, 200, 10)

    st.sidebar.subheader("Zelené kruhy")
    num_green_circles = st.sidebar.slider("Počet zelených kruhů", 0, 2000, 10)
    green_circle_radius = st.sidebar.slider("Poloměr zelených kruhů", 1, 200, 5)

    # Stav
    if "rows" not in st.session_state:
        st.session_state["rows"] = None
    if "image_bytes" not in st.session_state:
        st.session_state["image_bytes"] = None

    # Generování
    if st.sidebar.button("Generovat"):
        rng = np.random.default_rng(seed_value) if use_seed else np.random.default_rng()
        circle_specs = [
            ("red",   red_circle_radius,   num_red_circles,   "red"),
            ("blue",  blue_circle_radius,  num_blue_circles,  "blue"),
            ("green", green_circle_radius, num_green_circles, "green"),
        ]

        fig, rows = generate_circles(
            canvas_width, canvas_height,
            circle_specs, gap_between_circles,
            max_attempts_per_circle, rng
        )

        # Uložit PNG do paměti
        png_buffer = BytesIO()
        fig.savefig(png_buffer, format="png", dpi=png_dpi, bbox_inches="tight")
        png_buffer.seek(0)
        st.session_state["image_bytes"] = png_buffer.read()
        plt.close(fig)  # uvolnit paměť

        st.session_state["rows"] = rows

    # Zobrazení výsledku
    if st.session_state["rows"]:
        # Náhled obrázku
        st.write("### Vygenerované plátno")
        st.image(st.session_state["image_bytes"], caption="Náhled PNG", use_container_width=True)

        # Přesné pokrytí plochy (jen z reálně umístěných kruhů)
        df = pd.DataFrame(st.session_state["rows"])
        total_circle_surface = float(np.pi * np.sum(np.square(df["Radius"])))
        canvas_surface = float(canvas_width * canvas_height)
        ratio_percentage = (total_circle_surface / canvas_surface) * 100.0
        st.write(f"### Poměr děrování (pokrytí): {ratio_percentage:.2f}%")
        st.caption("Počítáno ze skutečně umístěných kruhů.")

        # Přehled počtů
        counts = df["Type"].value_counts().to_dict()
        st.write("**Počty umístěných kruhů:** "
                 + ", ".join([f'{k}: {v}' for k, v in counts.items()])
                 + f" (celkem {len(df)})")

        # Exporty
        # PNG
        st.download_button(
            label="Stáhnout PNG",
            data=st.session_state["image_bytes"],
            file_name="kruhove_platno.png",
            mime="image/png",
        )
        # CSV
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
        st.info("Klikněte na **Generovat** v levém panelu.")

if __name__ == "__main__":
    main()
