#!/usr/bin/env python3
"""
Cálculo de Inércia do Prato (Parabolic Dish) a partir do arquivo STL.

Este script calcula o volume, centro de massa e tensor de inércia
de uma malha fechada (STL) usando o método de integração por tetraedros.
Como arquivos STP requerem bibliotecas complexas (pythonocc/gmsh), 
usamos a versão STL 'parabolic_dish.stl' que é mais acessível via numpy.

Autor: Antigravity Agent
"""

import os
import sys
import numpy as np

def parse_ascii_stl(filepath):
    """
    Lê um arquivo STL ASCII simples e retorna um array de triângulos.
    Retorna: numpy array de shape (N, 3, 3) onde N é o número de triângulos.
    """
    triangles = []
    current_triangle = []
    
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
                
            if parts[0] == 'vertex':
                # Parse vertex coordinates
                v = [float(parts[1]), float(parts[2]), float(parts[3])]
                current_triangle.append(v)
                
            if len(current_triangle) == 3:
                triangles.append(current_triangle)
                current_triangle = []
                
    return np.array(triangles)

def calculate_mesh_properties(triangles, density=1.0):
    """
    Calcula propriedades de massa da malha (assumindo objeto feeder).
    
    Parâmetros:
      triangles: array (N, 3, 3) com vértices
      density: densidade do material (kg/m^3)
      
    Retorna:
      bvolume: Volume total
      center_mass: Centro de Massa (x, y, z)
      inertia_tensor: Tensor de Inércia (3x3) no CM
    """
    # Referência: "Efficient geometric modeling for calculating mass properties of 3D objects"
    # Eberly, J.
    
    total_volume = 0.0
    total_center = np.zeros(3)
    total_inertia = np.zeros((3, 3))
    
    # Extrair vértices
    v0 = triangles[:, 0, :]
    v1 = triangles[:, 1, :]
    v2 = triangles[:, 2, :]
    
    # Calcular Jacobiano (produto cruzado e determinante)
    # Volume assinado de cada tetraedro (Origem -> v0 -> v1 -> v2)
    # V = (1/6) * dot(v0, cross(v1, v2))
    
    cross_v1_v2 = np.cross(v1, v2)
    # Determinante (6 * Volume)
    dets = np.sum(v0 * cross_v1_v2, axis=1)
    
    # Volumes dos tetraedros
    volumes = dets / 6.0
    total_volume = np.sum(volumes)
    
    # Centro de massa acumulado
    # COM de um tetraedro com origem é 0.25 * (v0 + v1 + v2)
    # Momento = Volume * COM
    coms_tetra = 0.25 * (v0 + v1 + v2)
    weighted_coms = coms_tetra * volumes[:, np.newaxis]
    total_center = np.sum(weighted_coms, axis=0)
    
    if total_volume == 0:
        return 0, np.zeros(3), np.zeros((3,3))
        
    center_mass = total_center / total_volume
    
    # Cálculo do Tensor de Inércia sobre a ORIGEM
    # Para um tetraedro canônico na origem... é complexo.
    # Usando a expansão direta dos termos canônicos para tetraedro (O, A, B, C):
    # Fonte simplificada para integração numérica exata sobre tetraedros.
    
    # Vamos usar uma aproximação ou a fórmula exata das diagonais e fora-diagonais.
    # Fórmula exata para matriz de covariância C de um tetraedro canonical (x,y,z):
    # \int x^2 dV etc.
    
    # Método mais direto: 
    # Computar termos quadráticos integrais (xx, yy, zz, xy, yz, zx)
    # Integral(x^2) = Scale * (x0^2 + ... + product terms)
    # Para ser robusto e vetorizado, é um pouco extenso.
    
    # Vamos usar loop simples para clareza se não for muito lento, 
    # ou vetorizar a fórmula de Tonon.
    
    # Fórmula vetorizada simplificada para segundos momentos:
    # A matriz de inércia requer integrais de x^2, y^2, z^2, xy, etc.
    # Para um tetraedro com vértices (x0, y0, z0)...
    # int(x^2) = (det/120) * (x0^2 + x1^2 + x2^2 + x0x1 + x0x2 + x1x2)
    # onde x0, x1, x2 são coords x dos vertices do triangulo (assumindo origem como 4o vertice)
    
    factor = dets / 120.0  # det = 6*Vol. Então Vol/20. 
    
    # Coords
    x0, y0, z0 = v0[:,0], v0[:,1], v0[:,2]
    x1, y1, z1 = v1[:,0], v1[:,1], v1[:,2]
    x2, y2, z2 = v2[:,0], v2[:,1], v2[:,2]
    
    # Integrais de momento de segunda ordem
    int_xx = np.sum(factor * (x0*x0 + x1*x1 + x2*x2 + x0*x1 + x0*x2 + x1*x2))
    int_yy = np.sum(factor * (y0*y0 + y1*y1 + y2*y2 + y0*y1 + y0*y2 + y1*y2))
    int_zz = np.sum(factor * (z0*z0 + z1*z1 + z2*z2 + z0*z1 + z0*z2 + z1*z2))
    
    int_xy = np.sum(factor * (x0*y0 + x1*y1 + x2*y2 + x0*y1 + x0*y2 + x1*y0 + x1*y2 + x2*y0 + x2*y1 + 1.5*(x0*y0+x1*y1+x2*y2) - 1.5*(x0*y0+x1*y1+x2*y2))) 
    # Wait, a formula mista é: (det/120) * (2*sum(xi*yi) + sum(xi*yj + xj*yi))
    # Simplificando: (x0+x1+x2)*(y0+y1+y2) + x0y0 + x1y1 + x2y2 is related?
    # Vamos usar a expressão explicita:
    # int_xy = (det/120) * ( 2*(x0y0 + x1y1 + x2y2) + (x0y1 + x0y2 + x1y0 + x1y2 + x2y0 + x2y1) )
    
    int_xy = np.sum(factor * (2*(x0*y0 + x1*y1 + x2*y2) + (x0*y1 + x0*y2 + x1*y0 + x1*y2 + x2*y0 + x2*y1)))
    int_yz = np.sum(factor * (2*(y0*z0 + y1*z1 + y2*z2) + (y0*z1 + y0*z2 + y1*z0 + y1*z2 + y2*z0 + y2*z1)))
    int_zx = np.sum(factor * (2*(z0*x0 + z1*x1 + z2*x2) + (z0*x1 + z0*x2 + z1*x0 + z1*x2 + z2*x0 + z2*x1)))
    
    # Construir tensor de inércia na Origem
    # Ixx = int(y^2 + z^2) dm = density * (int_yy + int_zz)
    Ixx = density * (int_yy + int_zz)
    Iyy = density * (int_xx + int_zz)
    Izz = density * (int_xx + int_yy)
    Ixy = -density * int_xy
    Iyz = -density * int_yz
    Izx = -density * int_zx
    
    J_origin = np.array([
        [Ixx, Ixy, Izx],
        [Ixy, Iyy, Iyz],
        [Izx, Iyz, Izz]
    ])
    
    mass = total_volume * density
    
    # Transladar para o CM (Teorema dos Eixos Paralelos)
    # J_cm = J_origin - mass * ( ||d||^2 I - d x d )
    # Onde d é o vetor do CM
    
    x, y, z = center_mass
    
    # Matriz de correção
    # I_correction_xx = mass * (y^2 + z^2)
    # I_correction_xy = - mass * (x * y)
    
    J_correction = np.zeros((3,3))
    J_correction[0,0] = mass * (y**2 + z**2)
    J_correction[1,1] = mass * (x**2 + z**2)
    J_correction[2,2] = mass * (x**2 + y**2)
    J_correction[0,1] = J_correction[1,0] = -mass * x * y
    J_correction[0,2] = J_correction[2,0] = -mass * x * z
    J_correction[1,2] = J_correction[2,1] = -mass * y * z
    
    J_cm = J_origin - J_correction
    
    return total_volume, mass, center_mass, J_cm

def main():
    # Caminho do arquivo
    # Assumindo que estamos em 'analises/', o arquivo está em '../formas/parabolic_dish.stl'
    base_dir = os.path.dirname(os.path.abspath(__file__))
    stl_path = os.path.join(base_dir, "..", "formas", "parabolic_dish.stl")
    
    # Verifica se existe, senão tenta o caminho absoluto provável
    if not os.path.exists(stl_path):
        stl_path = "/home/lhmt-jhoni/Gazebo/robotSim4/formas/parabolic_dish.stl"
        
    if not os.path.exists(stl_path):
        print(f"Erro: Arquivo não encontrado: {stl_path}")
        return

    print(f"Lendo arquivo: {stl_path}")
    try:
        triangles = parse_ascii_stl(stl_path)
        print(f"Triângulos lidos: {len(triangles)}")
    except Exception as e:
        print(f"Erro ao ler STL: {e}")
        return

    # Material
    density = 2700.0 # Alumínio (kg/m3) S.I.
    print(f"Material: Alumínio (estimado)")
    print(f"Densidade: {density} kg/m³")
    
    vol, mass, com, J = calculate_mesh_properties(triangles, density)
    
    print("-" * 50)
    print("RESULTADOS:")
    print("-" * 50)
    print(f"Volume: {vol:.6g} m³ ({vol*1e6:.2f} cm³)")
    print(f"Massa:  {mass:.4f} kg ({mass*1000:.2f} g)")
    print(f"Centro de Massa (x, y, z) [m]:")
    print(f"  [{com[0]:.6f}, {com[1]:.6f}, {com[2]:.6f}]")
    
    print("-" * 50)
    print("Tensor de Inércia no Centro de Massa (kg*m²):")
    print(f"Ixx: {J[0,0]:.8f}")
    print(f"Iyy: {J[1,1]:.8f}")
    print(f"Izz: {J[2,2]:.8f}")
    print(f"Ixy: {J[0,1]:.8f}")
    print(f"Ixz: {J[0,2]:.8f}")
    print(f"Iyz: {J[1,2]:.8f}")
    
    print("-" * 50)
    print("XML para SDF (copie e cole no <inertial>):")
    print(f"""
<inertial>
  <mass>{mass:.4f}</mass>
  <inertia>
    <ixx>{J[0,0]:.8g}</ixx>
    <iyy>{J[1,1]:.8g}</iyy>
    <izz>{J[2,2]:.8g}</izz>
    <ixy>{J[0,1]:.8g}</ixy>
    <ixz>{J[0,2]:.8g}</ixz>
    <iyz>{J[1,2]:.8g}</iyz>
  </inertia>
</inertial>
""")

if __name__ == "__main__":
    main()
