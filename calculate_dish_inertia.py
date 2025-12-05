#!/usr/bin/env python3
"""
Cálculo de massa e inércia do prato parabólico
Material: Resina e fibra de vidro
"""
import math

# Propriedades do material
# Densidade típica de compósito de fibra de vidro com resina: 1800-2000 kg/m³
DENSITY = 1900  # kg/m³

# Dimensões do prato
DIAMETER = 3.0  # metros
RADIUS = DIAMETER / 2.0
FOCAL_LENGTH = 1.8  # metros
THICKNESS = 0.01  # metros (1 cm)

# Coeficiente parabólico
a = 1.0 / (4.0 * FOCAL_LENGTH)
depth = a * RADIUS**2

print("=" * 60)
print("CÁLCULO DE MASSA E INÉRCIA - PRATO PARABÓLICO")
print("=" * 60)
print(f"\nMaterial: Resina e Fibra de Vidro")
print(f"Densidade: {DENSITY} kg/m³")
print(f"\nDimensões:")
print(f"  Diâmetro: {DIAMETER} m")
print(f"  Raio: {RADIUS} m")
print(f"  Profundidade: {depth:.4f} m")
print(f"  Espessura: {THICKNESS} m")

# Cálculo do volume
# Para um paraboloide de revolução com espessura constante
# Volume ≈ Área da superfície × espessura

# Área da superfície de um paraboloide: A = (π/6a²) * [(1+4a²r²)^(3/2) - 1]
# Simplificação para espessura fina: A ≈ π * r² * sqrt(1 + (2ar)²)
surface_area = math.pi * RADIUS**2 * math.sqrt(1 + (2 * a * RADIUS)**2)

# Volume aproximado
volume = surface_area * THICKNESS

# Massa
mass = DENSITY * volume

print(f"\nCálculos:")
print(f"  Área da superfície: {surface_area:.4f} m²")
print(f"  Volume: {volume:.6f} m³")
print(f"  MASSA: {mass:.2f} kg")

# Momentos de inércia para um disco parabólico fino
# Aproximação: disco circular com distribuição de massa não uniforme
# Para um paraboloide fino, usamos aproximações baseadas em disco

# Ixx e Iyy (rotação em torno de eixos horizontais)
# Para um disco: I = (1/4) * m * r² + (1/12) * m * h²
# Onde h é a altura efetiva (profundidade do prato)
Ixx = (1/4) * mass * RADIUS**2 + (1/12) * mass * depth**2
Iyy = Ixx  # Simetria

# Izz (rotação em torno do eixo vertical - eixo de simetria)
# Para um disco: I = (1/2) * m * r²
Izz = (1/2) * mass * RADIUS**2

print(f"\nMomentos de Inércia:")
print(f"  Ixx: {Ixx:.4f} kg·m²")
print(f"  Iyy: {Iyy:.4f} kg·m²")
print(f"  Izz: {Izz:.4f} kg·m²")
print(f"  Ixy, Ixz, Iyz: 0 (simetria)")

print("\n" + "=" * 60)
print("VALORES PARA O SDF:")
print("=" * 60)
print(f"""
<inertial>
  <mass>{mass:.2f}</mass>
  <inertia>
    <ixx>{Ixx:.4f}</ixx>
    <iyy>{Iyy:.4f}</iyy>
    <izz>{Izz:.4f}</izz>
    <ixy>0</ixy>
    <ixz>0</ixz>
    <iyz>0</iyz>
  </inertia>
</inertial>
""")

print("=" * 60)
