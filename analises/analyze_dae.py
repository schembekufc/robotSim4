import xml.etree.ElementTree as ET
import numpy as np
import sys

def analyze_dae(filepath, target_y_local, search_radius=0.1):
    print(f"Analisando {filepath}...")
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # Namespaces do Collada podem ser chatos, vamos tentar achar float_array ignorando namespace ou usando wildcard
        # Mas o jeito mais facil em python xml é iterar.
        
        # Checar transformações na cena visual
        print("Buscando transformações de cena...")
        for scene in root.iter():
            if 'visual_scene' in scene.tag:
                for node in scene.iter():
                    if 'node' in node.tag:
                        print(f"Node: {node.get('name') or node.get('id')}")
                        for child in node:
                            tag_name = child.tag.split('}')[-1] # remove namespace
                            if tag_name in ['matrix', 'rotate', 'translate', 'scale']:
                                print(f"  Transform {tag_name}: {child.text}")
        
        positions = []
        
        # Busca recursiva por float_array
        for elem in root.iter():
            if 'float_array' in elem.tag and 'positions' in elem.get('id', ''):
                text = elem.text
                if text:
                    floats = [float(x) for x in text.split()]
                    positions = floats
                    print(f"Encontrado array de posições com {len(floats)} elementos.")
                    break
        
        if not positions:
            print("Não foi possível encontrar float_array com 'positions' no ID. Tentando buscar o maior float_array.")
            max_len = 0
            for elem in root.iter():
                if 'float_array' in elem.tag:
                    text = elem.text
                    if text:
                        floats = [float(x) for x in text.split()]
                        if len(floats) > max_len:
                            max_len = len(floats)
                            positions = floats
            print(f"Maior array encontrado tem {len(positions)} elementos.")

        if not positions:
            print("Nenhum dado encontrado.")
            return

        # Checar up_axis
        up_axis = "Z_UP" # Default
        for elem in root.iter():
            if 'up_axis' in elem.tag:
                up_axis = elem.text
                break
        print(f"Up Axis detectado no DAE: {up_axis}")

        # Converter para numpy reshape (-1, 3)
        pts = np.array(positions).reshape(-1, 3)
        
        print(f"Total de vértices: {len(pts)}")
        print(f"Bounds Originais (DAE):")
        print(f"  X: {pts[:,0].min():.4f} a {pts[:,0].max():.4f}")
        print(f"  Y: {pts[:,1].min():.4f} a {pts[:,1].max():.4f}")
        print(f"  Z: {pts[:,2].min():.4f} a {pts[:,2].max():.4f}")
        
        # Simular conversão de coordenadas se for Y_UP para Z_UP (Gazebo standard)
        # Se for Y_UP: Gazebo costuma converter: x_gaz = x_dae, y_gaz = z_dae, z_gaz = y_dae ??? 
        # Na verdade, depende do loader. O loader do Gazebo geralmente respeita e rotaciona:
        # Mesh Y-up -> Rotated -90 X -> Z-up. 
        # Transformação típica: (x, y, z) -> (x, -z, y) ou (x, z, -y)? 
        # Blender Y-up export to Z-up usually does: X=X, Y=-Z, Z=Y
        
        pts_gaz = pts.copy()
        if up_axis == 'Y_UP':
             # Conversão Simples para raciocínio (pode variar, mas vamos testar)
             # Assumption: Y_UP -> Z_UP swap
             print("Aplicando conversão Y_UP -> Z_UP estimada (X, Z, -Y)...")
             pts_gaz[:, 0] = pts[:, 0]
             pts_gaz[:, 1] = pts[:, 2]  # Y do Gazebo vira o Z do DAE ? Não, Z_dae é profundidade?
             # Y_UP: Y é altura. Z é profundidade.
             # Z_UP: Z é altura. Y é profundidade.
             # Então Altura (Y_dae) vira Altura (Z_gaz). Profundidade (Z_dae) vira Y_gaz.
             # Normalmente Z_dae (-Z_dae) mapeia para Y_gaz.
             
             pts_gaz[:, 1] = -pts[:, 2] # Y_gaz = -Z_dae
             pts_gaz[:, 2] = pts[:, 1]  # Z_gaz = Y_dae
        
        # Matriz identificada:
        # 1 0 0 0.07
        # 0 0 1 0.17
        # 0 -1 0 -2.04
        # 0 0 0 1
        
        print("\nAplicando Matriz de Transformação da Cena...")
        # pts é N x 3. Precisamos N x 4 (homogêneo)
        ones = np.ones((len(pts), 1))
        pts_h = np.hstack([pts, ones])
        
        # Matriz (Transposta para multiplicar v * M se v for linha, mas aqui é M * v^T.
        # Vamos fazer dot product normal: v_new = M . v_old (coluna)
        # Ou v_new = v_old . M.T (linha)
        
        M = np.array([
            [1, 0, 0, 0.07],
            [0, 0, 1, 0.17],
            [0, -1, 0, -2.04],
            [0, 0, 0, 1]
        ])
        
        # pts_h é (N, 4). M é (4, 4).
        # Queremos (N, 4).
        # v' = M * v.T -> Resultado (4, N). Transpor de volta -> (N, 4)
        pts_trans = M @ pts_h.T
        pts_trans = pts_trans.T
        
        pts_final = pts_trans[:, :3] # descarta w
        
        print(f"Bounds Finais (Sistema Local do Visual):")
        print(f"  X: {pts_final[:,0].min():.4f} a {pts_final[:,0].max():.4f}")
        print(f"  Y: {pts_final[:,1].min():.4f} a {pts_final[:,1].max():.4f}")
        print(f"  Z: {pts_final[:,2].min():.4f} a {pts_final[:,2].max():.4f}")

        # Busca target_y_local (Já calculado como 2.3155)
        # Atenção: target_y_local passado na função assumia sistema sem transform.
        # Agora estamos no sistema transformado.
        
        print(f"\nBuscando Z máximo em Y = {target_y_local} +/- {search_radius}")
        
        mask = (np.abs(pts_final[:,1] - target_y_local) < search_radius) & (np.abs(pts_final[:,0]) < 0.2)
        candidates = pts_final[mask]
        
        if len(candidates) > 0:
            z_max = candidates[:,2].max()
            print(f"Encontrado! Z local máximo na região: {z_max:.6f}")
            print(f"Isso corresponde a uma geometria que vai até esse Z.")
            
            # Printar mais stats
            avg_z = np.mean(candidates[:,2])
            print(f"Z médio na região: {avg_z:.6f}")
        else:
            print("Nenhum ponto encontrado nessa região após transformação.")

    except Exception as e:
        print(f"Erro ao processar DAE: {e}")

if __name__ == "__main__":
    # Y_mundo desejado = 2.143
    # Y_local = Y_mundo - (-0.1725) = 2.143 + 0.1725 = 2.3155
    analyze_dae("models/catia/3_BracoH.dae", 2.3155)
