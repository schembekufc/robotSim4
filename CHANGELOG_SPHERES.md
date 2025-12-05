# 📝 Resumo das Modificações - Esferas Prismáticas

## 🔄 Mudanças Realizadas

### ✅ Conversão de Juntas: Revolute → Prismatic

As 3 esferas foram convertidas de **juntas de rotação** para **juntas prismáticas** (movimento linear):

| Esfera | Cor Anterior | Cor Nova | Eixo Anterior | Eixo Novo | Tipo Anterior | Tipo Novo |
|--------|--------------|----------|---------------|-----------|---------------|-----------|
| **Esfera 1** | Cinza | **Verde** | Rotação Y | **Translação X** | Revolute | **Prismatic** |
| **Esfera 2** | Vermelha | Vermelha | Rotação +60° | **Translação Y** | Revolute | **Prismatic** |
| **Esfera 3** | Azul | Azul | Rotação -60° | **Translação Z** | Revolute | **Prismatic** |

---

## 🎯 Detalhes Técnicos

### Esfera 1 (Verde - Eixo X)
```xml
<joint name="joint_sphere_1" type="prismatic">
  <axis>
    <xyz>1 0 0</xyz> <!-- Movimento em X -->
    <limit>
      <lower>-2.0</lower>
      <upper>2.0</upper>
      <velocity>1.0</velocity>
    </limit>
  </axis>
</joint>
```
- **Movimento**: -2m a +2m no eixo X
- **Velocidade máxima**: 1.0 m/s
- **Cor**: RGB(0.2, 0.8, 0.2) - Verde

### Esfera 2 (Vermelha - Eixo Y)
```xml
<joint name="joint_sphere_2" type="prismatic">
  <axis>
    <xyz>0 1 0</xyz> <!-- Movimento em Y -->
    <limit>
      <lower>-2.0</lower>
      <upper>2.0</upper>
      <velocity>1.0</velocity>
    </limit>
  </axis>
</joint>
```
- **Movimento**: -2m a +2m no eixo Y
- **Velocidade máxima**: 1.0 m/s
- **Cor**: RGB(0.8, 0.2, 0.2) - Vermelha (mantida)

### Esfera 3 (Azul - Eixo Z)
```xml
<joint name="joint_sphere_3" type="prismatic">
  <axis>
    <xyz>0 0 1</xyz> <!-- Movimento em Z -->
    <limit>
      <lower>-2.0</lower>
      <upper>2.0</upper>
      <velocity>1.0</velocity>
    </limit>
  </axis>
</joint>
```
- **Movimento**: -2m a +2m no eixo Z
- **Velocidade máxima**: 1.0 m/s
- **Cor**: RGB(0.2, 0.2, 0.8) - Azul (mantida)

---

## 🎮 Controladores

Os controladores de velocidade foram mantidos e atualizados:

```bash
# Esfera 1 (Verde - X)
/model/three_link_model/joint/joint_sphere_1/cmd_vel

# Esfera 2 (Vermelha - Y)
/model/three_link_model/joint/joint_sphere_2/cmd_vel

# Esfera 3 (Azul - Z)
/model/three_link_model/joint/joint_sphere_3/cmd_vel
```

**Nota**: Agora os comandos de velocidade controlam **movimento linear** (m/s) em vez de **rotação** (rad/s).

---

## 📊 Comparação Visual

### Antes (Revolute):
```
Esfera 1 (Cinza):  ↻ Rotação no eixo Y
Esfera 2 (Vermelha): ↻ Rotação inclinada +60°
Esfera 3 (Azul):   ↻ Rotação inclinada -60°
```

### Depois (Prismatic):
```
Esfera 1 (Verde):  ← → Movimento linear no eixo X
Esfera 2 (Vermelha): ↑ ↓ Movimento linear no eixo Y
Esfera 3 (Azul):   ⬆ ⬇ Movimento linear no eixo Z
```

---

## 🔧 Como Testar

### 1. Carregar a Simulação
```bash
gz sim 01_three_link_with_tracker_plate.sdf
```

### 2. Mover as Esferas via Terminal

```bash
# Mover Esfera 1 (Verde) no eixo X
gz topic -t "/model/three_link_model/joint/joint_sphere_1/cmd_vel" \
         -m gz.msgs.Double -p "data: 0.5"

# Mover Esfera 2 (Vermelha) no eixo Y
gz topic -t "/model/three_link_model/joint/joint_sphere_2/cmd_vel" \
         -m gz.msgs.Double -p "data: 0.5"

# Mover Esfera 3 (Azul) no eixo Z
gz topic -t "/model/three_link_model/joint/joint_sphere_3/cmd_vel" \
         -m gz.msgs.Double -p "data: 0.5"

# Parar todas
gz topic -t "/model/three_link_model/joint/joint_sphere_1/cmd_vel" \
         -m gz.msgs.Double -p "data: 0.0"
gz topic -t "/model/three_link_model/joint/joint_sphere_2/cmd_vel" \
         -m gz.msgs.Double -p "data: 0.0"
gz topic -t "/model/three_link_model/joint/joint_sphere_3/cmd_vel" \
         -m gz.msgs.Double -p "data: 0.0"
```

---

## 📝 Commit Git

```
Commit: 4f7000b
Mensagem: Convert sphere joints from revolute to prismatic (X,Y,Z axes) 
          and change sphere 1 color to green
Arquivos modificados: 01_three_link_with_tracker_plate.sdf
Linhas: +27 -32
```

---

## ⚠️ Observações Importantes

1. **Limites de Movimento**: Cada esfera pode se mover ±2 metros em seu eixo
2. **Velocidade**: Limitada a 1.0 m/s (antes era 10 rad/s)
3. **Controladores**: Os mesmos tópicos funcionam, mas agora controlam velocidade linear
4. **GUI Existente**: Se você tiver uma GUI de controle (como `balls_control_gui.py`), ela precisará ser atualizada para refletir movimento linear em vez de rotação

---

**Data**: 05/12/2025  
**Autor**: Jhoni
