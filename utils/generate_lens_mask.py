import numpy as np

def generate_ring_obj(filename, inner_radius, outer_radius, segments=32):
    vertices = []
    faces = []
    
    # Generate vertices
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        # Inner vertex
        xi = inner_radius * np.cos(angle)
        yi = inner_radius * np.sin(angle)
        vertices.append((xi, yi, 0))
        
        # Outer vertex
        xo = outer_radius * np.cos(angle)
        yo = outer_radius * np.sin(angle)
        vertices.append((xo, yo, 0))
        
    # Generate faces
    # OBJ indices are 1-based
    for i in range(segments):
        # Indices for current segment
        i_inner = i * 2 + 1
        i_outer = i * 2 + 2
        
        # Indices for next segment (wrapping around)
        next_i = (i + 1) % segments
        next_i_inner = next_i * 2 + 1
        next_i_outer = next_i * 2 + 2
        
        # Face (quad defined as two triangles or one quad)
        # OBJ format: f v1 v2 v3 v4
        # Counter-clockwise order for normal pointing up (+Z)
        faces.append((i_inner, next_i_inner, next_i_outer, i_outer))

    with open(filename, 'w') as f:
        f.write("# Ring Mask OBJ\n")
        for v in vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        
        for face in faces:
            f.write(f"f {face[0]} {face[1]} {face[2]} {face[3]}\n")

if __name__ == "__main__":
    generate_ring_obj('/home/lhmt-jhoni/Gazebo/robotSim3/lens_mask.obj', 0.02, 0.03, 64)
    print("Generated lens_mask.obj")
