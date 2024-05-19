import ifcopenshell
model = ifcopenshell.open(r"C:\Users\dvjak\Documents\GitHub\Utilities\AC20-FZK-Haus.ifc")

# print(model.schema) # May return IFC2X3, IFC4, or IFC4X3

# print(model.by_id(1)) # Get data by GlobalId

# print(model.by_guid("0EI0MSHbX9gg8Fxwar7lL8"))
walls = model.by_type('IfcWall')
# print(len(walls)) #Get number of IfcWall elemetns


wall = model.by_type('IfcWall')[0] # Get the first item in IfcWall list
# print(wall.is_a()) # Returns class of provided element

# print(wall.is_a('IfcWall')) # Returns True
# print(wall.is_a('IfcElement')) # Returns True
# print(wall.is_a('IfcWindow')) # Returns False

# print(wall.id())

# Access parameters by atribute
# print(wall[0]) # The first attribute is the GlobalId
# print(wall[2]) # The third attribute is the Name

# Access parameters by name
# print(wall.GlobalId)
# print(wall.Name)

# Gives us a dictionary of attributes, such as:
# {'id': 8, 'type': 'IfcWall', 'GlobalId': '2_qMTAIHrEYu0vYcqK8cBX', ... }


# Get all parameters
# print(wall.get_info())

# Get element psets and parameters
# import ifcopenshell.util
# import ifcopenshell.util.element
# print(ifcopenshell.util.element.get_psets(wall))


# print(wall.IsDefinedBy)

# Get related elements
# print(model.get_inverse(wall))

# print(model.traverse(wall))
# # Or, let's just go down one level deep
# print(model.traverse(wall, max_levels=1))

# Function to change the PSet name for a specific IfcWall
# def change_pset_name(old_pset_name, new_pset_name):
#     # Find the specific IfcWall
#     wall = model.by_type('IfcWall')[0]
#     if not wall:
#         print("Wall not found!")
#         return
#
#     # Iterate through property sets of the wall
#     for definition in wall.IsDefinedBy:
#         if definition.is_a('IfcRelDefinesByProperties'):
#             property_set = definition.RelatingPropertyDefinition
#             if property_set.is_a('IfcPropertySet') and property_set.Name == old_pset_name:
#                 # Change the PSet name
#                 property_set.Name = new_pset_name
#                 print(f"Property Set name changed to {new_pset_name}")
#                 return
#
#     print("Property Set not found!")
#
#
# # Call the function with specific parameters
# change_pset_name(  'Pset_WallCommon', 'Testing')
#
# # Write the changes to a new IFC file
# model.write(r"C:\Users\dvjak\Documents\GitHub\Utilities\AC20-FZK-Haus.ifc")