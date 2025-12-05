#!/usr/bin/env python3
"""
Gerador de Prato Parabólico para Gazebo
Especificações:
- Diâmetro: 3 m
- Distância focal: 1.8 m
- Área de cada segmento: < 4 cm²
- Orientação: côncava para cima (+Z)
- Espessura: 1 cm
"""

import numpy as np
import math

# ============================================================================
# PARÂMETROS DO PRATO PARABÓLICO
# ============================================================================
DIAMETER = 3.0          # metros
FOCAL_LENGTH = 1.8      # metros
MAX_SEGMENT_AREA = 4e-4 # 4 cm² em m²
THICKNESS = 0.01        # 1 cm em metros
OUTPUT_FILE = "formas/parabolic_dish.stl"

# ============================================================================
# CÁLCULO DO NÚMERO DE SEGMENTOS
# ============================================================================
radius = DIAMETER / 2.0

# Para um paraboloide, a = 1/(4*f) onde f é a distância focal
a = 1.0 / (4.0 * FOCAL_LENGTH)

# Profundidade do prato no raio máximo: z = a * r²
depth = a * radius**2

print(f"=== Especificações do Prato Parabólico ===")
print(f"Diâmetro: {DIAMETER} m")
print(f"Raio: {radius} m")
print(f"Distância focal: {FOCAL_LENGTH} m")
print(f"Profundidade: {depth:.4f} m")
print(f"Espessura: {THICKNESS} m")
print(f"Coeficiente parabólico (a): {a:.6f}")

# Estimar número de segmentos necessários
# Área aproximada de cada segmento triangular em uma malha circular
# Área total da superfície ≈ π * r²
surface_area = math.pi * radius**2
min_segments = int(surface_area / MAX_SEGMENT_AREA)

# Para uma malha circular, usamos segmentos radiais e angulares
# Número de divisões angulares (theta)
n_theta = int(math.sqrt(min_segments * 2))
# Número de divisões radiais
n_radial = int(min_segments / n_theta)

# Ajustar para garantir que a área seja menor que o máximo
n_theta = max(n_theta, 50)
n_radial = max(n_radial, 30)

print(f"\n=== Malha ===")
print(f"Segmentos angulares: {n_theta}")
print(f"Segmentos radiais: {n_radial}")
print(f"Total de faces (aproximado): {n_theta * n_radial * 2}")

# ============================================================================
# GERAÇÃO DA GEOMETRIA
# ============================================================================

def parabola_z(r):
    """Calcula a altura Z para um dado raio r"""
    return a * r**2

# Listas para armazenar vértices e faces
vertices = []
faces = []

# Gerar superfície superior (côncava para cima)
print("\nGerando superfície superior...")
for i in range(n_radial + 1):
    r = (i / n_radial) * radius
    z = parabola_z(r)
    
    for j in range(n_theta):
        theta = (j / n_theta) * 2 * math.pi
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        vertices.append([x, y, z])

# Gerar superfície inferior (offset pela espessura)
print("Gerando superfície inferior...")
for i in range(n_radial + 1):
    r = (i / n_radial) * radius
    z = parabola_z(r) - THICKNESS
    
    for j in range(n_theta):
        theta = (j / n_theta) * 2 * math.pi
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        vertices.append([x, y, z])

n_vertices_per_surface = (n_radial + 1) * n_theta

# Gerar faces da superfície superior
print("Gerando faces da superfície superior...")
for i in range(n_radial):
    for j in range(n_theta):
        # Índices dos vértices
        v1 = i * n_theta + j
        v2 = i * n_theta + (j + 1) % n_theta
        v3 = (i + 1) * n_theta + j
        v4 = (i + 1) * n_theta + (j + 1) % n_theta
        
        # Dois triângulos por quad (normal apontando para cima/fora)
        faces.append([v1, v3, v2])
        faces.append([v2, v3, v4])

# Gerar faces da superfície inferior
print("Gerando faces da superfície inferior...")
for i in range(n_radial):
    for j in range(n_theta):
        # Índices dos vértices (offset para a superfície inferior)
        offset = n_vertices_per_surface
        v1 = offset + i * n_theta + j
        v2 = offset + i * n_theta + (j + 1) % n_theta
        v3 = offset + (i + 1) * n_theta + j
        v4 = offset + (i + 1) * n_theta + (j + 1) % n_theta
        
        # Dois triângulos por quad (normal apontando para baixo/dentro)
        faces.append([v1, v2, v3])
        faces.append([v2, v4, v3])

# Gerar faces da borda (conectando superior e inferior)
print("Gerando faces da borda...")
i = n_radial  # Última linha radial (borda externa)
for j in range(n_theta):
    # Vértices da borda superior
    v1_top = i * n_theta + j
    v2_top = i * n_theta + (j + 1) % n_theta
    
    # Vértices da borda inferior
    v1_bot = n_vertices_per_surface + i * n_theta + j
    v2_bot = n_vertices_per_surface + i * n_theta + (j + 1) % n_theta
    
    # Dois triângulos para fechar a borda
    faces.append([v1_top, v1_bot, v2_top])
    faces.append([v2_top, v1_bot, v2_bot])

# ============================================================================
# EXPORTAR PARA STL (ASCII)
# ============================================================================
print(f"\nExportando para {OUTPUT_FILE}...")

vertices = np.array(vertices)
faces = np.array(faces)

with open(OUTPUT_FILE, 'w') as f:
    f.write(f"solid parabolic_dish\n")
    
    for face in faces:
        # Calcular normal da face
        v0 = vertices[face[0]]
        v1 = vertices[face[1]]
        v2 = vertices[face[2]]
        
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = np.cross(edge1, edge2)
        
        # Normalizar
        norm_length = np.linalg.norm(normal)
        if norm_length > 0:
            normal = normal / norm_length
        
        # Escrever faceta
        f.write(f"  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}\n")
        f.write(f"    outer loop\n")
        f.write(f"      vertex {v0[0]:.6e} {v0[1]:.6e} {v0[2]:.6e}\n")
        f.write(f"      vertex {v1[0]:.6e} {v1[1]:.6e} {v1[2]:.6e}\n")
        f.write(f"      vertex {v2[0]:.6e} {v2[1]:.6e} {v2[2]:.6e}\n")
        f.write(f"    endloop\n")
        f.write(f"  endfacet\n")
    
    f.write(f"endsolid parabolic_dish\n")

print(f"\n✅ Prato parabólico gerado com sucesso!")
print(f"   Arquivo: {OUTPUT_FILE}")
print(f"   Vértices: {len(vertices)}")
print(f"   Faces: {len(faces)}")
print(f"\nPróximos passos:")
print(f"1. Execute este script: python3 generate_parabolic_dish.py")
print(f"2. O arquivo STL será criado em: {OUTPUT_FILE}")
print(f"3. Atualize o SDF para usar este arquivo")
