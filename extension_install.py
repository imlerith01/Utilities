import json

# Define the data to be added
extension_data = {
    "builtin": "False",
    "default_enabled": "True",
    "type": "extension",
    "rocket_mode_compatible": "False",
    "name": "#A99 tools",
    "description": "Atelier 99 extensions for PyRevit",
    "author": "Jakub Dvoracek",
    "author_profile": "https://github.com/imlerith01",
    "url": "https://github.com/imlerith01/A99-tools.git",
    "website": "https://github.com/imlerith01",
    "image": "",
    "dependencies": []
}

# Path to the JSON file
json_file_path = r"C:\Users\dvoracek\AppData\Roaming\pyRevit-Master\extensions\extensions.json"

# Read the existing JSON data
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Check if the "extensions" key exists
if "extensions" not in data:
    # If not, create the "extensions" key and assign an empty list to it
    data["extensions"] = []

# Append the new data to the "extensions" list
data["extensions"].append(extension_data)

# Write the updated JSON back to the file
with open(json_file_path, 'w') as file:
    json.dump(data, file, indent=4)

print("Data added successfully.")
