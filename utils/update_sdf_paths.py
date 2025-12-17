#!/usr/bin/env python3
"""
Script para atualizar caminhos absolutos para relativos no SDF
"""

import re

# Arquivo SDF
sdf_file = "01_three_link_with_tracker_plate.sdf"

# Mapeamento de caminhos
path_mappings = {
    r'file:///home/lhmt-jhoni/testes/formas/catia/1_Base\.dae': 'file://models/catia/1_Base.dae',
    r'file:///home/lhmt-jhoni/testes/formas/catia/2_Torre\.dae': 'file://models/catia/2_Torre.dae',
    r'file:///home/lhmt-jhoni/testes/formas/catia/3_BracoH\.dae': 'file://models/catia/3_BracoH.dae',
    r'file:///home/lhmt-jhoni/Gazebo/robotSim2/formas/parabolic_dish\.stl': 'file://formas/parabolic_dish.stl',
    r'file:///home/lhmt-jhoni/Gazebo/robotSim3/lens_mask\.obj': 'file://lens_mask.obj',
}

print("🔧 Atualizando caminhos no SDF...")
print(f"📄 Arquivo: {sdf_file}")

# Ler arquivo
with open(sdf_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Contar substituições
total_replacements = 0

# Aplicar substituições
for old_path, new_path in path_mappings.items():
    count = len(re.findall(old_path, content))
    if count > 0:
        content = re.sub(old_path, new_path, content)
        print(f"  ✅ {old_path.split('/')[-1]} → {new_path.split('/')[-1]} ({count}x)")
        total_replacements += count

# Salvar arquivo
with open(sdf_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Total de substituições: {total_replacements}")
print(f"💾 Arquivo atualizado: {sdf_file}")
