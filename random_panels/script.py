import streamlit as st
import matplotlib.pyplot as plt
import random
import math
from io import BytesIO
import pandas as pd  # For CSV generation

# Helper function to check overlap with a gap
def is_overlapping(x, y, existing_circles, radius, gap_between_circles):
    for cx, cy, r in existing_circles:
        distance = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        if distance < r + radius + gap_between_circles:
            return True
    return False

# Function to generate circles with integer coordinates
def generate_circles(canvas_width, canvas_height, circle_specs, gap_between_circles):
    circles = []
    circle_data = {"red": [], "blue": [], "green": []}
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, canvas_width)
    ax.set_ylim(0, canvas_height)
    ax.set_facecolor("white")
    ax.axis("off")  # Remove axes for a clean look

    for spec in circle_specs:
        color, radius, count, label = spec
        added_circles = 0
        while added_circles < count:
            x = round(random.uniform(radius, canvas_width - radius))  # Ensure integer x
            y = round(random.uniform(radius, canvas_height - radius))  # Ensure integer y
            if not is_overlapping(x, y, circles, radius, gap_between_circles):
                circles.append((x, y, radius))
                circle = plt.Circle((x, y), radius, color=color)
                ax.add_artist(circle)
                circle_data[label].append((x, y))  # Store center points
                added_circles += 1

    ax.set_aspect("equal", adjustable="box")
    return fig, circle_data

# Streamlit App
def main():
    st.title("Generátor kruhů")

    # Sidebar for inputs
    st.sidebar.header("Nastavení plátna")
    canvas_width = st.sidebar.slider("Šířka plátna", 200, 4000, 1000, step=50)
    canvas_height = st.sidebar.slider("Výška plátna", 200, 4000, 1000, step=50)

    st.sidebar.header("Nastavení kruhů")
    gap_between_circles = st.sidebar.slider("Minimální mezera mezi kruhy", 0, 50, 5)

    st.sidebar.subheader("Červené kruhy")
    num_red_circles = st.sidebar.slider("Počet červených kruhů", 1, 1000, 30)
    red_circle_radius = st.sidebar.slider("Poloměr červených kruhů", 1, 100, 20)

    st.sidebar.subheader("Modré kruhy")
    num_blue_circles = st.sidebar.slider("Počet modrých kruhů", 1, 1000, 20)
    blue_circle_radius = st.sidebar.slider("Poloměr modrých kruhů", 1, 100, 10)

    st.sidebar.subheader("Zelené kruhy")
    num_green_circles = st.sidebar.slider("Počet zelených kruhů", 1, 1000, 10)
    green_circle_radius = st.sidebar.slider("Poloměr zelených kruhů", 1, 100, 5)

    # Initialize session state
    if "generated_fig" not in st.session_state:
        st.session_state["generated_fig"] = None
    if "circle_data" not in st.session_state:
        st.session_state["circle_data"] = None

    if st.sidebar.button("Generovat"):
        # Generate circles and store in session state
        circle_specs = [
            ("red", red_circle_radius, num_red_circles, "red"),
            ("blue", blue_circle_radius, num_blue_circles, "blue"),
            ("green", green_circle_radius, num_green_circles, "green"),
        ]
        fig, circle_data = generate_circles(canvas_width, canvas_height, circle_specs, gap_between_circles)
        st.session_state["generated_fig"] = fig
        st.session_state["circle_data"] = circle_data

    # Check if a figure is stored in session state
    if st.session_state["generated_fig"] is not None:
        st.write("### Vygenerované plátno")
        st.pyplot(st.session_state["generated_fig"])

        # Calculate and display ratio between surface of canvas and surface of all circles
        canvas_surface = canvas_width * canvas_height
        total_circle_surface = (
            num_red_circles * math.pi * (red_circle_radius ** 2)
            + num_blue_circles * math.pi * (blue_circle_radius ** 2)
            + num_green_circles * math.pi * (green_circle_radius ** 2)
        )
        ratio_percentage = (total_circle_surface / canvas_surface) * 100
        st.write(f"### Poměr děrování: {ratio_percentage:.2f}%")

        # Create PNG and CSV data
        buffer = BytesIO()
        st.session_state["generated_fig"].savefig(buffer, format="png")
        buffer.seek(0)

        csv_data = pd.DataFrame(
            {
                "Type": ["Red"] * len(st.session_state["circle_data"]["red"])
                + ["Blue"] * len(st.session_state["circle_data"]["blue"])
                + ["Green"] * len(st.session_state["circle_data"]["green"]),
                "X": [x for x, y in st.session_state["circle_data"]["red"]]
                + [x for x, y in st.session_state["circle_data"]["blue"]]
                + [x for x, y in st.session_state["circle_data"]["green"]],
                "Y": [y for x, y in st.session_state["circle_data"]["red"]]
                + [y for x, y in st.session_state["circle_data"]["blue"]]
                + [y for x, y in st.session_state["circle_data"]["green"]],
                "Canvas Width": [canvas_width] * (len(st.session_state["circle_data"]["red"]) + len(st.session_state["circle_data"]["blue"]) + len(st.session_state["circle_data"]["green"])),
                "Canvas Height": [canvas_height] * (len(st.session_state["circle_data"]["red"]) + len(st.session_state["circle_data"]["blue"]) + len(st.session_state["circle_data"]["green"])),
                "Gap Between Circles": [gap_between_circles] * (len(st.session_state["circle_data"]["red"]) + len(st.session_state["circle_data"]["blue"]) + len(st.session_state["circle_data"]["green"])),
                "Red Circle Radius": [red_circle_radius] * len(st.session_state["circle_data"]["red"])
                + [None] * (len(st.session_state["circle_data"]["blue"]) + len(st.session_state["circle_data"]["green"])),
                "Blue Circle Radius": [None] * len(st.session_state["circle_data"]["red"])
                + [blue_circle_radius] * len(st.session_state["circle_data"]["blue"])
                + [None] * len(st.session_state["circle_data"]["green"]),
                "Green Circle Radius": [None] * (len(st.session_state["circle_data"]["red"]) + len(st.session_state["circle_data"]["blue"]))
                + [green_circle_radius] * len(st.session_state["circle_data"]["green"]),
            }
        )
        csv_buffer = BytesIO()
        csv_data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # Provide download buttons
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Stáhnout PNG",
                data=buffer,
                file_name="kruhove_platno.png",
                mime="image/png",
            )
        with col2:
            st.download_button(
                label="Stáhnout CSV",
                data=csv_buffer,
                file_name="souradnice_kruhu.csv",
                mime="text/csv",
            )

if __name__ == "__main__":
    main()