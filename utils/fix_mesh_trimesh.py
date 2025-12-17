#!/usr/bin/env python3
"""
Alternative mesh repair script using trimesh library
"""
try:
    import trimesh
    import numpy as np
    
    print("Loading mesh...")
    mesh = trimesh.load("/home/lhmt-jhoni/Gazebo/robotSim2/formas/Espelho.dae")
    
    print(f"Original mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
    
    # Remove degenerate faces
    print("Removing degenerate faces...")
    mesh.remove_degenerate_faces()
    
    # Remove duplicate faces
    print("Removing duplicate faces...")
    mesh.remove_duplicate_faces()
    
    # Merge vertices that are very close
    print("Merging close vertices...")
    mesh.merge_vertices()
    
    # Fill holes if any
    print("Filling holes...")
    mesh.fill_holes()
    
    # Fix normals
    print("Fixing normals...")
    mesh.fix_normals()
    
    print(f"Cleaned mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
    
    # Export as STL
    output_file = "/home/lhmt-jhoni/Gazebo/robotSim2/formas/Espelho_fixed.stl"
    print(f"Exporting to {output_file}...")
    mesh.export(output_file)
    
    print("SUCCESS: Mesh cleaned and exported!")
    
except ImportError:
    print("ERROR: trimesh library not installed")
    print("Install with: pip install trimesh")
    exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
