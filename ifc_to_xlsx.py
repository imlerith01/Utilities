import ifcopenshell
import pandas as pd


def extract_ifc_data(ifc_path):
    # Load the IFC file
    ifc_file = ifcopenshell.open(ifc_path)

    # Prepare a dictionary to hold data, keys are element IDs and values are dicts of parameters
    data_dict = {}

    # Iterate over all elements in the IFC file
    for element in ifc_file.by_type('IfcProduct'):
        element_data = {}

        # Get all attributes and dynamic properties
        for attr in element.__dict__.keys():
            try:
                value = getattr(element, attr)
                if value is not None:
                    element_data[attr] = value
            except AttributeError:
                continue

        # Additional properties from IsDefinedBy relationships
        for definition in element.IsDefinedBy:
            if definition.is_a('IfcRelDefinesByProperties'):
                property_set = definition.RelatingPropertyDefinition
                if property_set.is_a('IfcPropertySet'):
                    for property in property_set.HasProperties:
                        if property.is_a('IfcPropertySingleValue'):
                            element_data[
                                property.Name] = property.NominalValue.wrappedValue if property.NominalValue else None

        # Store data in the dictionary
        data_dict[element.GlobalId] = element_data

    return data_dict


def create_excel(data_dict, output_path):
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame.from_dict(data_dict, orient='index')

    # Ensure the GlobalId is the first column
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Element ID'}, inplace=True)

    # Save the DataFrame to an Excel file
    df.to_excel(output_path, index=False)


# Specify the path to your IFC file and the desired output Excel file path
ifc_path = r'C:\Users\dvjak\Documents\GitHub\Utilities\AC20-FZK-Haus.ifc'
output_excel_path = r'C:\Users\dvjak\Documents\GitHub\Utilities\AC20-FZK-Haus.xlsx'

# Extract data and create the Excel file
data = extract_ifc_data(ifc_path)
create_excel(data, output_excel_path)
