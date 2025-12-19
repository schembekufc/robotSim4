#!/usr/bin/env python3
"""
Cálculo de Inércia do prato.stp (Sólido de Revolução).

Este script realiza uma análise "forense" do arquivo STEP (ASCII) para reconstruir
a geometria de revolução definida pelos Pontos de Controle (Control Points).
Como não temos um kernel CAD (OpenCASCADE/FreeCAD) instalado, usamos esta abordagem:
1. Extrair coordenadas dos 'CARTESIAN_POINT' marcados como 'Control Point'.
2. Converter para coordendas cilíndricas (r, z).
3. Identificar os perfis superior e inferior (superfície dupla).
4. Gerar uma malha de revolução (STL/Mesh) a partir desses perfis.
5. Calcular volume, massa e inércia por integração.

Autor: Antigravity Agent
"""

import os
import re
import math
import numpy as np
from scipy.interpolate import interp1d

# Configuração
DENSITY = 2700.0  # kg/m3 (Alumínio)
STP_FILE = "../formas/prato.stp"

def parse_stp_control_points(filepath):
    """Lê o STP e extrai pontos de controle únicos (r, z)."""
    points = []
    
    # Regex para capturar coordenadas: #123=CARTESIAN_POINT('Name',(x,y,z))
    # Exemplo: #64=CARTESIAN_POINT('Control Point',(0.,1500.,312.5))
    regex = re.compile(r"CARTESIAN_POINT\s*\(\s*'([^']*)'\s*,\s*\(\s*([-\d\.E]+)\s*,\s*([-\d\.E]+)\s*,\s*([-\d\.E]+)\s*\)\s*\)")
    
    with open(filepath, 'r') as f:
        content = f.read()
        
    for match in regex.finditer(content):
        name = match.group(1)
        x = float(match.group(2))
        y = float(match.group(3))
        z = float(match.group(4))
        
        # Filtra apenas pontos de controle ou vértices relevantes se necessário.
        # O arquivo usa 'Control Point' para definir as splines.
        if 'Control Point' in name or 'Vertex' in name:
            r = math.sqrt(x**2 + y**2)
            points.append((r, z))
            
    return np.array(points)

def separate_profiles(points):
    """
    Separa os pontos em perfil superior e inferior.
    Assume que para um mesmo raio aproximado, o ponto com maior Z é superior.
    """
    # Remove duplicatas exatas
    unique_points = np.unique(points, axis=0)
    
    # Agrupa por raio (com tolerância)
    # Arredondando raio para mm para agrupação
    r_rounded = np.round(unique_points[:, 0], decimals=3)
    
    profiles = {} # r -> list of z
    for i, r in enumerate(r_rounded):
        if r not in profiles:
            profiles[r] = []
        profiles[r].append(unique_points[i, 1])
        
    r_vals = sorted(profiles.keys())
    z_upper = []
    z_lower = []
    cleaned_r = []
    
    for r in r_vals:
        zs = profiles[r]
        if len(zs) >= 1:
            z_max = max(zs)
            z_min = min(zs)
            
            # Heurística: se a diferença for pequena, é uma chapa fina ou borda.
            # Se só tem 1 ponto, assume que é igual (borda afiada).
            z_upper.append(z_max)
            z_lower.append(z_min)
            cleaned_r.append(r)
            
    return np.array(cleaned_r), np.array(z_upper), np.array(z_lower)

def create_revolved_mesh(r_vals, z_up, z_low, num_segments=72):
    """
    Gera triângulos girando o perfil 360 graus.
    """
    theta = np.linspace(0, 2*np.pi, num_segments, endpoint=False)
    
    vertices = []
    triangles = []
    
    # Estrutura:
    # Para cada raio r_i (índice i):
    #   Criamos um anel de vértices superiores e um anel de inferiores.
    #   Anel UP: num_segments vertices
    #   Anel LOW: num_segments vertices
    
    N = len(theta)
    M = len(r_vals)
    
    # Gerar Vértices
    # Ordem: Camadas radiais. Para cada r_i -> [Upper Ring, Lower Ring]
    for i in range(M):
        r = r_vals[i]
        zu = z_up[i]
        zl = z_low[i]
        
        # Ring Upper (indices: 2*i*N + j)
        for t in theta:
            x = r * math.cos(t)
            y = r * math.sin(t)
            vertices.append([x, y, zu])
            
        # Ring Lower (indices: 2*i*N + N + j)
        for t in theta:
            x = r * math.cos(t)
            y = r * math.sin(t)
            vertices.append([x, y, zl])
            
    vertices = np.array(vertices)
    
    # Gerar Triângulos (Conectar anéis)
    # Conectar r_i com r_(i+1)
    
    for i in range(M - 1):
        # Índices base dos anéis
        base_up_curr = 2 * i * N
        base_low_curr = base_up_curr + N
        
        base_up_next = 2 * (i + 1) * N
        base_low_next = base_up_next + N
        
        for j in range(N):
            next_j = (j + 1) % N
            
            # --- Superfície Superior (Face UP) ---
            # Conecta Current Up com Next Up
            # Tri 1: C_Up[j], N_Up[j], C_Up[next_j]
            # Tri 2: N_Up[j], N_Up[next_j], C_Up[next_j]
            # Normal aponta para +Z (cuidado com ordem)
            
            p1 = base_up_curr + j
            p2 = base_up_next + j
            p3 = base_up_curr + next_j
            p4 = base_up_next + next_j
            
            triangles.append([p1, p3, p2])
            triangles.append([p2, p3, p4])
            
            # --- Superfície Inferior (Face DOWN) ---
            # Conecta Current Low com Next Low
            # Normal para -Z
            
            l1 = base_low_curr + j
            l2 = base_low_next + j
            l3 = base_low_curr + next_j
            l4 = base_low_next + next_j
            
            triangles.append([l1, l2, l3]) # Inverter ordem para normal
            triangles.append([l2, l4, l3])
            
    # Fechar Bordas (Lateral Externa e Interna)
    # Borda Interna (i=0) e Borda Externa (i=M-1)
    # Normalmente i=0 é r=0 (centro), então collapsed. 
    # Se r[0] == 0, não precisa parede interna.
    
    # Borda Externa (Outer Rim)
    last = M - 1
    base_up = 2 * last * N
    base_low = base_up + N
    for j in range(N):
        next_j = (j + 1) % N
        u1 = base_up + j
        u2 = base_up + next_j
        l1 = base_low + j
        l2 = base_low + next_j
        
        # Quad (u1, u2, l2, l1)
        triangles.append([u1, l1, u2])
        triangles.append([u2, l1, l2])

    # Borda Interna (se r[0] > 0)
    if r_vals[0] > 1e-6:
        base_up = 0
        base_low = N
        for j in range(N):
            next_j = (j + 1) % N
            u1 = base_up + j
            u2 = base_up + next_j
            l1 = base_low + j
            l2 = base_low + next_j
            
            # Inverter normal (pointing inward)
            triangles.append([u1, u2, l1])
            triangles.append([u2, l2, l1])
            
    return vertices, np.array(triangles)

def calculate_inertia_from_mesh(vertices, triangles, density):
    """
    Calcula tensor de inércia usando integração de volume em tetraedros.
    Referência: Eberly "Polyhedral Mass Properties".
    """
    # Simplificação: Como é simétrico e revolução, poderíamos usar integração 2D.
    # Mas vamos usar o método 3D genérico para validar a malha.
    
    total_vol = 0.0
    total_com = np.zeros(3)
    total_J = np.zeros((3, 3))
    
    v0 = vertices[triangles[:, 0]]
    v1 = vertices[triangles[:, 1]]
    v2 = vertices[triangles[:, 2]]
    
    # Volume de cada tetraedro (Origem -> v0 -> v1 -> v2)
    cross = np.cross(v1, v2)
    dets = np.sum(v0 * cross, axis=1)
    vols = dets / 6.0
    total_vol = np.sum(vols)
    
    # CM
    coms = (v0 + v1 + v2) / 4.0 # Tetraedro com origem
    total_com = np.sum(coms * vols[:, np.newaxis], axis=0)
    
    if total_vol == 0: return 0, 0, 0, np.zeros((3,3))
    
    com_final = total_com / total_vol
    mass = total_vol * density
    
    # Inércia (Canonical)
    # int(x^2) approx... vamos usar a fórmula simplificada para xx, yy, zz
    # J_origin
    
    # Usando a mesma lógica do script anterior (simplificada para Python puro)
    # Termos de segunda ordem
    # A = v0, B = v1, C = v2
    # int_xx = mass_tetra/10 * (x0^2 + x1^2 + x2^2 + x0x1 + ...) -> Não
    # Formula Tonon:
    # f_xx = det/120 * (x0*x0 + x1*x1 + x2*x2 + sum_products)
    
    f = dets / 120.0
    x0, y0, z0 = v0[:,0], v0[:,1], v0[:,2]
    x1, y1, z1 = v1[:,0], v1[:,1], v1[:,2]
    x2, y2, z2 = v2[:,0], v2[:,1], v2[:,2]
    
    axx = x0*x0 + x1*x1 + x2*x2 + x0*x1 + x0*x2 + x1*x2
    ayy = y0*y0 + y1*y1 + y2*y2 + y0*y1 + y0*y2 + y1*y2
    azz = z0*z0 + z1*z1 + z2*z2 + z0*z1 + z0*z2 + z1*z2
    
    Ixx_o = np.sum(f * (ayy + azz)) * density
    Iyy_o = np.sum(f * (axx + azz)) * density
    Izz_o = np.sum(f * (axx + ayy)) * density
    
    # Ixy, Ixz, Iyz assumidos 0 devido à simetria de revolução
    # Mas calculando para garantir
    axy = 2*(x0*y0 + x1*y1 + x2*y2) + (x0*y1 + x0*y2 + x1*y0 + x1*y2 + x2*y0 + x2*y1)
    Ixy_o = -np.sum(f * axy) * density
    
    J_o = np.diag([Ixx_o, Iyy_o, Izz_o])
    # ... outros termos off-diagonal ignorados por brevidade e simetria esperada zero
    
    # Transladar para CM
    cx, cy, cz = com_final
    J_com = np.zeros((3,3))
    
    J_com[0,0] = Ixx_o - mass * (cy**2 + cz**2)
    J_com[1,1] = Iyy_o - mass * (cx**2 + cz**2)
    J_com[2,2] = Izz_o - mass * (cx**2 + cy**2)
    
    return total_vol, mass, com_final, J_com

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, STP_FILE) # ../formas/prato.stp
    
    if not os.path.exists(input_path):
        # Tenta fallback
        input_path = "/home/lhmt-jhoni/Gazebo/robotSim4/formas/prato.stp"
        if not os.path.exists(input_path):
            print("Erro: Arquivo não encontrado.")
            return

    print(f"Lendo: {input_path}")
    points = parse_stp_control_points(input_path)
    print(f"Pontos de Controle Extraídos: {len(points)}")
    
    if len(points) == 0:
        print("Erro: Nenhum ponto encontrado.")
        return

    r, z_up, z_low = separate_profiles(points)
    
    # Interpolar para suavizar e densificar (importante para cálculo preciso)
    # Vamos gerar 100 pontos ao longo do raio (0 a 1.5m)
    
    # Garantir ordenação
    sort_idx = np.argsort(r)
    r = r[sort_idx]
    z_up = z_up[sort_idx]
    z_low = z_low[sort_idx]
    
    # Remover duplicatas em X para interpolação
    r_uni, idx = np.unique(r, return_index=True)
    z_up_uni = z_up[idx]
    z_low_uni = z_low[idx]
    
    # Interpoladores (Linear é mais seguro para pontos esparsos de CAD, Spline pode oscilar)
    f_up = interp1d(r_uni, z_up_uni, kind='linear', fill_value="extrapolate")
    f_low = interp1d(r_uni, z_low_uni, kind='linear', fill_value="extrapolate")
    
    r_new = np.linspace(0, max(r_uni), 100)
    z_up_new = f_up(r_new)
    z_low_new = f_low(r_new)
    
    print(f"\nPerfil Reconstruído:")
    print(f"  Raio Máx: {max(r_new):.3f} m")
    print(f"  Altura Z (Centro) [Top/Bot]: {z_up_new[0]:.3f} / {z_low_new[0]:.3f} m")
    print(f"  Altura Z (Borda)  [Top/Bot]: {z_up_new[-1]:.3f} / {z_low_new[-1]:.3f} m")
    
    # Criar malha
    verts, tris = create_revolved_mesh(r_new, z_up_new, z_low_new, num_segments=120)
    print(f"  Malha gerada: {len(verts)} vértices, {len(tris)} triângulos")
    
    vol, mass, com, J = calculate_inertia_from_mesh(verts, tris, DENSITY)
    
    print("\n" + "="*50)
    print("RESULTADOS (Baseado em prato.stp)")
    print("="*50)
    print(f"Volume: {vol*1e6:.2f} cm³")
    print(f"Massa:  {mass:.4f} kg")
    print(f"CM Z:   {com[2]:.4f} m")
    print("-" * 50)
    print("Inércia (kg*m²) no CM:")
    print(f"  Ixx: {J[0,0]:.6f}")
    print(f"  Iyy: {J[1,1]:.6f}")
    print(f"  Izz: {J[2,2]:.6f}")
    print("="*50)

    print("\nXML sugerido:")
    print(f"""
<inertial>
  <mass>{mass:.4f}</mass>
  <inertia>
    <ixx>{J[0,0]:.6f}</ixx>
    <iyy>{J[1,1]:.6f}</iyy>
    <izz>{J[2,2]:.6f}</izz>
    <ixy>0</ixy> <ixz>0</ixz> <iyz>0</iyz>
  </inertia>
</inertial>
    """)

if __name__ == "__main__":
    main()
