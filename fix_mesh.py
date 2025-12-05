#!/usr/bin/env python3
"""
Blender script to clean and repair the Espelho.dae mesh
This script removes degenerate faces and exports to STL format
"""
import bpy
import sys

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import the DAE file
input_file = "/home/lhmt-jhoni/Gazebo/robotSim2/formas/Espelho.dae"
output_file = "/home/lhmt-jhoni/Gazebo/robotSim2/formas/Espelho_fixed.stl"

print(f"Importing {input_file}...")
bpy.ops.wm.collada_import(filepath=input_file)

# Select all imported objects
bpy.ops.object.select_all(action='SELECT')

# Join all objects into one
if len(bpy.context.selected_objects) > 1:
    bpy.ops.object.join()

# Get the active object
obj = bpy.context.active_object

if obj and obj.type == 'MESH':
    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select all
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Remove doubles (merge vertices that are very close)
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    
    # Delete degenerate faces
    bpy.ops.mesh.delete_loose()
    
    # Recalculate normals
    bpy.ops.mesh.normals_make_consistent(inside=False)
    
    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Export as STL
    print(f"Exporting to {output_file}...")
    bpy.ops.export_mesh.stl(
        filepath=output_file,
        use_selection=False,
        global_scale=1.0,
        use_mesh_modifiers=True
    )
    
    print("Mesh cleaned and exported successfully!")
else:
    print("ERROR: No mesh object found!")
    sys.exit(1)
