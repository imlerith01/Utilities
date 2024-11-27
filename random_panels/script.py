import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import random
import math
from io import BytesIO
import pandas as pd


# Helper function to initialize the grid for spatial partitioning
def initialize_grid(canvas_width, canvas_height, cell_size):
    grid = {}
    for x in range(0, math.ceil(canvas_width / cell_size)):
        for y in range(0, math.ceil(canvas_height / cell_size)):
            grid[(x, y)] = []
    return grid


# Optimized overlap check using spatial partitioning
def is_overlapping_optimized(x, y, radius, grid, cell_size, gap_between_circles):
    grid_x, grid_y = int(x // cell_size), int(y // cell_size)
    neighbors = [
        (grid_x + dx, grid_y + dy)
        for dx in range(-1, 2)
        for dy in range(-1, 2)
        if (grid_x + dx, grid_y + dy) in grid
    ]
    for neighbor in neighbors:
        for cx, cy, r in grid[neighbor]:
            distance = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if distance < r + radius + gap_between_circles:
                return True
    return False


# Optimized function to generate circles
def generate_circles_optimized(canvas_width, canvas_height, circle_specs, gap_between_circles):
    circles = []
    circle_data = {"red": [], "blue": [], "green": []}
    cell_size = max([spec[1] for spec in circle_specs]) * 2 + gap_between_circles
    grid = initialize_grid(canvas_width, canvas_height, cell_size)

    for spec in circle_specs:
        color, radius, count, label = spec
        added_circles = 0
        while added_circles < count:
            x = random.uniform(radius, canvas_width - radius)
            y = random.uniform(radius, canvas_height - radius)
            if not is_overlapping_optimized(x, y, radius, grid, cell_size, gap_between_circles):
                circles.append((x, y, radius, color))
                grid_x, grid_y = int(x // cell_size), int(y // cell_size)
                grid[(grid_x, grid_y)].append((x, y, radius))
                circle_data[label].append((x, y))
                added_circles += 1

    return circles, circle_data


# Function for batch rendering circles
def render_circles_batch(circles, canvas_width, canvas_height):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, canvas_width)
    ax.set_ylim(0, canvas_height)
    ax.set_facecolor("white")
    ax.axis("off")

    patches = []
    for x, y, radius, color in circles:
        patches.append(plt.Circle((x, y), radius, color=color))

    collection = PatchCollection(patches, match_original=True)
    ax.add_collection(collection)
    return fig


# Streamlit App
def main():
    st.title("Generátor kruhů - Optimalizovaná verze")

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
        circles, circle_data = generate_circles_optimized(canvas_width, canvas_height, circle_specs, gap_between_circles)
        fig = render_circles_batch(circles, canvas_width, canvas_height)
        st.session_state["generated_fig"] = fig
        st.session_state["circle_data"] = circle_data

    # Check if a figure is stored in session state
    if st.session_state["generated_fig"] is not None:
        st.write("### Vygenerované plátno")
        st.pyplot(st.session_state["generated_fig"])

        # Calculate and display ratio between surface of canvas and surface of all circles
        canvas_surface = canvas_width * canvas_height
        total_circle_surface = sum(math.pi * (r ** 2) for _, _, r, _ in circles)
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
