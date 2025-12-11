#!/usr/bin/env python3
"""
Script para otimizar malha 3D usando Blender
Reduz número de polígonos mantendo qualidade visual
"""

import bpy
import sys
import os

def optimize_mesh(input_file, output_file, ratio=0.15):
    """
    Otimiza malha 3D reduzindo polígonos
    
    Args:
        input_file: Caminho do arquivo de entrada (.dae)
        output_file: Caminho do arquivo de saída (.dae)
        ratio: Proporção de polígonos a manter (0.15 = 15% dos polígonos)
    """
    print(f"🔧 Otimizando malha: {input_file}")
    print(f"📊 Ratio de decimação: {ratio} ({ratio*100:.0f}% dos polígonos)")
    
    # Limpar cena
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Importar arquivo
    print("📥 Importando arquivo...")
    if input_file.endswith('.dae'):
        bpy.ops.wm.collada_import(filepath=input_file)
    elif input_file.endswith('.stl'):
        bpy.ops.import_mesh.stl(filepath=input_file)
    else:
        print(f"❌ Formato não suportado: {input_file}")
        return False
    
    # Selecionar todos os objetos importados
    bpy.ops.object.select_all(action='SELECT')
    
    # Juntar todos em um único objeto (se houver múltiplos)
    if len(bpy.context.selected_objects) > 1:
        print("🔗 Juntando múltiplos objetos...")
        bpy.ops.object.join()
    
    # Pegar objeto ativo
    obj = bpy.context.active_object
    
    if obj is None or obj.type != 'MESH':
        print("❌ Nenhum objeto mesh encontrado!")
        return False
    
    # Contar polígonos originais
    original_polys = len(obj.data.polygons)
    print(f"📐 Polígonos originais: {original_polys:,}")
    
    # Aplicar modificador Decimate
    print("⚙️  Aplicando Decimate modifier...")
    decimate = obj.modifiers.new(name="Decimate", type='DECIMATE')
    decimate.ratio = ratio
    decimate.use_collapse_triangulate = True
    
    # Aplicar modificador
    bpy.ops.object.modifier_apply(modifier="Decimate")
    
    # Contar polígonos após otimização
    optimized_polys = len(obj.data.polygons)
    reduction = (1 - optimized_polys / original_polys) * 100
    
    print(f"📐 Polígonos otimizados: {optimized_polys:,}")
    print(f"📉 Redução: {reduction:.1f}%")
    
    # Exportar
    print(f"💾 Exportando para: {output_file}")
    
    if output_file.endswith('.dae'):
        bpy.ops.wm.collada_export(
            filepath=output_file,
            apply_modifiers=True,
            triangulate=True
        )
    elif output_file.endswith('.stl'):
        bpy.ops.export_mesh.stl(
            filepath=output_file,
            use_selection=True
        )
    
    print("✅ Otimização concluída!")
    return True

if __name__ == "__main__":
    # Verificar argumentos
    if len(sys.argv) < 7:  # blender --background --python script.py -- input output ratio
        print("❌ Uso: blender --background --python optimize_mesh.py -- <input> <output> <ratio>")
        sys.exit(1)
    
    # Pegar argumentos após '--'
    argv = sys.argv[sys.argv.index("--") + 1:]
    
    input_file = argv[0]
    output_file = argv[1]
    ratio = float(argv[2]) if len(argv) > 2 else 0.15
    
    # Verificar se arquivo existe
    if not os.path.exists(input_file):
        print(f"❌ Arquivo não encontrado: {input_file}")
        sys.exit(1)
    
    # Otimizar
    success = optimize_mesh(input_file, output_file, ratio)
    
    sys.exit(0 if success else 1)
