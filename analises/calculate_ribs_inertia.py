#!/usr/bin/env python3
"""
Cálculo estimado de massa e momento de inércia das costelas de alumínio.
Baseado em estimativa de 6 costelas radiais em perfil tubular.
"""

import math

# Propriedades do alumínio
ALUMINUM_DENSITY = 2700  # kg/m³

# Geometria estimada das costelas (baseado no prato de 3m de diâmetro)
NUM_RIBS = 6  # 6 costelas radiais
RIB_LENGTH = 1.5  # metros (raio do prato)
RIB_PROFILE = "rectangular_tube"  # Perfil tubular retangular

# Dimensões do perfil (estimativa para tubular de alumínio estrutural)
PROFILE_WIDTH = 0.05  # 5 cm (largura externa)
PROFILE_HEIGHT = 0.08  # 8 cm (altura externa)
WALL_THICKNESS = 0.003  # 3 mm (espessura da parede)

def calculate_rectangular_tube_properties():
    """
    Calcula propriedades de um tubo retangular de alumínio.
    """
    # Área da seção transversal
    outer_area = PROFILE_WIDTH * PROFILE_HEIGHT
    inner_width = PROFILE_WIDTH - 2 * WALL_THICKNESS
    inner_height = PROFILE_HEIGHT - 2 * WALL_THICKNESS
    inner_area = inner_width * inner_height
    cross_section_area = outer_area - inner_area
    
    # Volume de uma costela
    volume_per_rib = cross_section_area * RIB_LENGTH
    
    # Volume total (6 costelas)
    total_volume = volume_per_rib * NUM_RIBS
    
    # Massa total
    total_mass = total_volume * ALUMINUM_DENSITY
    
    # Momentos de inércia para uma barra fina ao longo do eixo radial
    # Assumindo que as costelas estão distribuídas radialmente a partir do centro
    
    # Para uma barra de comprimento L e massa m:
    # I_perpendicular = (1/12) * m * L²
    # I_axial ≈ (1/12) * m * (w² + h²)
    
    mass_per_rib = total_mass / NUM_RIBS
    
    # Momentos de inércia de uma costela em relação ao seu centro
    I_length = (1/12) * mass_per_rib * RIB_LENGTH**2  # Perpendicular ao comprimento
    I_cross = (1/12) * mass_per_rib * (PROFILE_WIDTH**2 + PROFILE_HEIGHT**2)  # Ao longo do comprimento
    
    # Aplicando teorema dos eixos paralelos para centro de massa no centro do prato
    # d = distância do CM da costela ao centro do prato = L/2
    d = RIB_LENGTH / 2
    
    # Momentos de inércia total (somando as 6 costelas dispostas radialmente)
    # Ixx e Iyy (no plano): contribuição de todas as costelas
    # Izz (perpendicular ao plano): costelas giram ao redor do centro
    
    # Simplificação: costelas distribuídas uniformemente em 360° / 6 = 60°
    Ixx = 0
    Iyy = 0
    Izz = 0
    
    for i in range(NUM_RIBS):
        angle = i * (2 * math.pi / NUM_RIBS)
        # Contribuição de cada costela usando teorema dos eixos paralelos
        Ixx += I_length + mass_per_rib * (d * math.sin(angle))**2
        Iyy += I_length + mass_per_rib * (d * math.cos(angle))**2
        Izz += 2 * I_length + mass_per_rib * d**2  # No plano XY
    
    # Produtos de inércia (assumindo simetria, são pequenos)
    Ixy = 0.0
    Ixz = 0.0
    Iyz = 0.0
    
    return {
        'cross_section_area_m2': cross_section_area,
        'volume_per_rib_m3': volume_per_rib,
        'total_volume_m3': total_volume,
        'mass_kg': total_mass,
        'ixx': Ixx,
        'iyy': Iyy,
        'izz': Izz,
        'ixy': Ixy,
        'ixz': Ixz,
        'iyz': Iyz
    }

def main():
    print("=" * 70)
    print("CÁLCULO DE PROPRIEDADES FÍSICAS - COSTELAS DE ALUMÍNIO")
    print("=" * 70)
    print(f"\nMaterial: Alumínio")
    print(f"Densidade: {ALUMINUM_DENSITY} kg/m³")
    print(f"\nGeometria:")
    print(f"  Número de costelas: {NUM_RIBS}")
    print(f"  Comprimento (raio): {RIB_LENGTH} m")
    print(f"  Perfil: Tubo retangular {PROFILE_WIDTH*100}x{PROFILE_HEIGHT*100} cm")
    print(f"  Espessura parede: {WALL_THICKNESS*1000} mm")
    print("\nCalculando...\n")
    
    # Calcular propriedades
    props = calculate_rectangular_tube_properties()
    
    # Exibir resultados
    print("RESULTADOS:")
    print("-" * 70)
    print(f"Área seção transversal: {props['cross_section_area_m2']*1e6:.2f} mm²")
    print(f"Volume por costela:     {props['volume_per_rib_m3']*1e6:.2f} cm³")
    print(f"Volume total (6x):      {props['total_volume_m3']*1e6:.2f} cm³")
    print(f"\nMassa total:            {props['mass_kg']:.4f} kg")
    print(f"Massa total:            {props['mass_kg']*1000:.2f} g")
    print(f"Massa por costela:      {props['mass_kg']/NUM_RIBS:.4f} kg")
    print(f"\nMomentos de Inércia (kg·m²):")
    print(f"  Ixx: {props['ixx']:.6f}")
    print(f"  Iyy: {props['iyy']:.6f}")
    print(f"  Izz: {props['izz']:.6f}")
    print(f"  Ixy: {props['ixy']:.6f}")
    print(f"  Ixz: {props['ixz']:.6f}")
    print(f"  Iyz: {props['iyz']:.6f}")
    
    print("\n" + "=" * 70)
    print("VALORES PARA O SDF:")
    print("=" * 70)
    print(f"""
<inertial>
  <mass>{props['mass_kg']:.4f}</mass>  <!-- {NUM_RIBS} costelas de alumínio -->
  <inertia>
    <ixx>{props['ixx']:.6f}</ixx>
    <iyy>{props['iyy']:.6f}</iyy>
    <izz>{props['izz']:.6f}</izz>
    <ixy>{props['ixy']:.6f}</ixy>
    <ixz>{props['ixz']:.6f}</ixz>
    <iyz>{props['iyz']:.6f}</iyz>
  </inertia>
</inertial>
    """)
    
    print("\nOBSERVAÇÃO: Estes valores são estimativas baseadas em:")
    print("  - 6 costelas radiais")
    print(f"  - Perfil tubular retangular {PROFILE_WIDTH*100}x{PROFILE_HEIGHT*100} cm")
    print(f"  - Espessura de parede {WALL_THICKNESS*1000} mm")
    print("  - Comprimento de 1.5 m (raio do prato)")
    print("\nAjuste as dimensões do perfil conforme o design real das costelas.")

if __name__ == "__main__":
    main()
