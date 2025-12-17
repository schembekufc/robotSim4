#!/usr/bin/env python3
import numpy as np
import struct

def calculate_signed_volume_of_triangle(p1, p2, p3):
    v321 = p3[0]*p2[1]*p1[2]
    v231 = p2[0]*p3[1]*p1[2]
    v312 = p3[0]*p1[1]*p2[2]
    v132 = p1[0]*p3[1]*p2[2]
    v213 = p2[0]*p1[1]*p3[2]
    v123 = p1[0]*p2[1]*p3[2]
    return (1.0/6.0)*(-v321 + v231 + v312 - v132 - v213 + v123)

def analyze_stl(filepath):
    print(f"Lendo arquivo: {filepath}")
    
    vertices = []
    
    # Tentativa básica de leitura (STL pode ser ASCII ou Binário)
    # Vamos assumir binário padrão primeiro, se falhar tentamos ASCII ou usar trimesh se instalado
    # Como não tenho trimesh garantido, vou fazer um parser robusto simples
    try:
        # Tenta ler como binário
        with open(filepath, "rb") as f:
            header = f.read(80)
            count_bytes = f.read(4)
            num_triangles = struct.unpack("<I", count_bytes)[0]
            print(f"STL Binário detectado. Triângulos: {num_triangles}")
            
            total_volume = 0.0
            min_pt = np.array([float('inf'), float('inf'), float('inf')])
            max_pt = np.array([float('-inf'), float('-inf'), float('-inf')])
            
            # Ler triângulos em chunks para não estourar memória se for grande
            # Cada triângulo tem 50 bytes (12 float normais, 3x12 float verts, 2 bytes attr)
            
            for _ in range(num_triangles):
                data = f.read(50)
                if len(data) < 50: break
                
                # Normal (3f), V1 (3f), V2 (3f), V3 (3f), Attr (H)
                floats = struct.unpack("<12f", data[:48])
                
                p1 = np.array(floats[3:6])
                p2 = np.array(floats[6:9])
                p3 = np.array(floats[9:12])
                
                # Bounding Box Update
                for p in [p1, p2, p3]:
                    min_pt = np.minimum(min_pt, p)
                    max_pt = np.maximum(max_pt, p)
                
                # Volume calc
                total_volume += calculate_signed_volume_of_triangle(p1, p2, p3)
                
    except Exception as e:
        print(f"Erro ao ler binário ou arquivo é ASCII: {e}")
        # Implementação ASCII simplificada se necessário...
        return

    total_volume = abs(total_volume)
    dims = max_pt - min_pt
    
    print("\n=== Análise Geométrica do STL ===")
    print(f"Dimensões (Bounding Box):")
    print(f"  X: {min_pt[0]:.4f} a {max_pt[0]:.4f} (L = {dims[0]:.4f})")
    print(f"  Y: {min_pt[1]:.4f} a {max_pt[1]:.4f} (L = {dims[1]:.4f})")
    print(f"  Z: {min_pt[2]:.4f} a {max_pt[2]:.4f} (L = {dims[2]:.4f})")
    
    # Verificação de Escala
    max_dim = np.max(dims)
    scale_factor = 1.0
    unit_guess = "Metros"
    
    if max_dim > 100:
        print("\n[ALERTA] Dimensões > 100. Provavelmente em MILÍMETROS.")
        scale_factor = 0.001
        unit_guess = "Milímetros (convertendo para Metros)"
    elif max_dim > 10:
        print("\n[ALERTA] Dimensões entre 10 e 100. Verifique se são cm ou dm.")
    else:
        print("\nDimensões parecem estar em METROS.")

    # Aplicando escala
    vol_m3 = total_volume * (scale_factor**3)
    dims_m = dims * scale_factor
    
    print(f"\n=== Propriedades Físicas (Alumínio) ===")
    print(f"Unidade Original Estimada: {unit_guess}")
    print(f"Volume do Material: {vol_m3:.6f} m³")
    
    rho_al = 2700 # kg/m3
    mass = vol_m3 * rho_al
    
    print(f"Massa Calculada: {mass:.4f} kg")
    
    return {
        "mass": mass,
        "dims": dims_m
    }

if __name__ == "__main__":
    import sys
    file_to_analyze = "formas/costelas.stl"
    if len(sys.argv) > 1:
        file_to_analyze = sys.argv[1]
    analyze_stl(file_to_analyze)
