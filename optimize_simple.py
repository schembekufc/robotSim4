import bpy
import sys

# Limpar cena
bpy.ops.wm.read_factory_settings(use_empty=True)

# Importar PLY
print("Importando PLY...")
bpy.ops.import_mesh.ply(filepath="models/catia/2_Torre_temp.ply")

# Selecionar objeto
obj = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj

print(f"Polígonos originais: {len(obj.data.polygons):,}")

# Aplicar Decimate
print("Aplicando Decimate...")
mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
mod.ratio = 0.12  # 12% dos polígonos
bpy.ops.object.modifier_apply(modifier="Decimate")

print(f"Polígonos finais: {len(obj.data.polygons):,}")

# Exportar como DAE
print("Exportando DAE...")
bpy.ops.wm.collada_export(filepath="models/catia/2_Torre.dae", apply_modifiers=True)

print("✅ Concluído!")
