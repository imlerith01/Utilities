import os
import pandas as pd
import ifcopenshell
from tkinter import Tk
from tkinter.filedialog import askopenfilename


def extract_ifc_data(ifc_file_path):
    # Load the IFC file
    ifc_file = ifcopenshell.open(ifc_file_path)

    # Dictionary to hold all entities and their attributes
    data = {
        'id': [],
        'type': [],
        'attributes': []
    }

    # Iterate through all entities in the IFC file
    for entity in ifc_file.by_type('IfcRoot'):  # This gets all entities; adjust the type as needed
        data['id'].append(entity.id())
        data['type'].append(entity.is_a())
        attrs = []
        for attr in entity.get_info().values():
            # Compile attributes into a single string for simplicity; customize as needed
            attrs.append(str(attr))
        data['attributes'].append('; '.join(attrs))

    # Convert dictionary to pandas DataFrame
    df = pd.DataFrame(data)
    return df


def select_ifc_file():
    # Hide the root window
    Tk().withdraw()
    # Show an "Open" dialog box and return the path to the selected file
    filename = askopenfilename(filetypes=[("IFC files", "*.ifc")])
    return filename


def main():
    # Let user select an IFC file
    ifc_file_path = select_ifc_file()

    if ifc_file_path:
        print(f"Selected file: {ifc_file_path}")
        # Extract data from the selected IFC file
        df = extract_ifc_data(ifc_file_path)

        # Define the Excel file path
        excel_file_path = os.path.splitext(ifc_file_path)[0] + '.xlsx'

        # Write DataFrame to an Excel file in the same directory as the IFC file
        df.to_excel(excel_file_path, index=False)
        print(f"Data exported to Excel file: {excel_file_path}")
    else:
        print("No file selected. Exiting...")


if __name__ == "__main__":
    main()
