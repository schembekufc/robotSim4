# Prato Parabólico - Guia de Uso

## ✅ Prato Parabólico Criado com Sucesso!

### Especificações do Prato
- **Diâmetro**: 3.0 m
- **Distância focal**: 1.8 m  
- **Profundidade**: 0.3125 m (31.25 cm)
- **Espessura**: 1 cm
- **Orientação**: Côncava para cima (+Z)
- **Arquivo**: `formas/parabolic_dish.stl` (18 MB)
- **Malha**: 35,530 vértices, 70,686 faces

---

## 📍 Como Ajustar a Posição do Prato

Abra o arquivo [`three_link_with_tracker_plate.sdf`](file:///home/lhmt-jhoni/Gazebo/robotSim2/three_link_with_tracker_plate.sdf) e localize a linha com a tag `<pose>` dentro do elemento `parabolic_dish_visual` (aproximadamente linha 178).

### Formato da Pose
```xml
<pose>X Y Z Roll Pitch Yaw</pose>
```

Onde:
- **X, Y, Z**: Posição em metros (relativa ao `link3`)
- **Roll, Pitch, Yaw**: Rotação em radianos

### Posição Atual
```xml
<pose>-0.07 -0.1725 2.5 0 0 0</pose>
```

### Exemplos de Ajustes

#### Mover o prato 0.5m para frente (eixo X)
```xml
<pose>0.43 -0.1725 2.5 0 0 0</pose>
```

#### Mover o prato 1m para cima (eixo Z)
```xml
<pose>-0.07 -0.1725 3.5 0 0 0</pose>
```

#### Inclinar o prato 45° (π/4 rad) no eixo Y (Pitch)
```xml
<pose>-0.07 -0.1725 2.5 0 0.785398 0</pose>
```

#### Rotacionar o prato 90° (π/2 rad) no eixo Z (Yaw)
```xml
<pose>-0.07 -0.1725 2.5 0 0 1.5708</pose>
```

### ⚠️ Importante
**Você precisa ajustar a pose em DOIS lugares:**

1. **Visual** (linha ~178):
   ```xml
   <visual name="parabolic_dish_visual">
     <pose>X Y Z Roll Pitch Yaw</pose>
   ```

2. **Colisão** (linha ~194):
   ```xml
   <collision name="parabolic_dish_collision">
     <pose>X Y Z Roll Pitch Yaw</pose>
   ```

Mantenha os valores idênticos nos dois lugares para que a geometria visual e de colisão fiquem alinhadas.

---

## 🔄 Regenerar o Prato com Parâmetros Diferentes

Se você quiser alterar o diâmetro, distância focal ou outros parâmetros, edite o arquivo [`generate_parabolic_dish.py`](file:///home/lhmt-jhoni/Gazebo/robotSim2/generate_parabolic_dish.py):

```python
# Linha 11-15
DIAMETER = 3.0          # metros - ALTERE AQUI
FOCAL_LENGTH = 1.8      # metros - ALTERE AQUI
MAX_SEGMENT_AREA = 4e-4 # 4 cm² - ALTERE AQUI
THICKNESS = 0.01        # 1 cm - ALTERE AQUI
```

Depois execute:
```bash
python3 generate_parabolic_dish.py
```

O arquivo `formas/parabolic_dish.stl` será sobrescrito com a nova geometria.

---

## 📐 Conversão de Ângulos

| Graus | Radianos |
|-------|----------|
| 0°    | 0        |
| 30°   | 0.5236   |
| 45°   | 0.7854   |
| 60°   | 1.0472   |
| 90°   | 1.5708   |
| 180°  | 3.1416   |
| 270°  | 4.7124   |
| 360°  | 6.2832   |

**Fórmula**: `radianos = graus × π / 180`

---

## 🎯 Sistema de Coordenadas

O prato está fixo ao `link3`. As coordenadas são relativas ao frame do `link3`:

- **+X**: Para frente
- **+Y**: Para a esquerda  
- **+Z**: Para cima
- **Roll**: Rotação em torno do eixo X
- **Pitch**: Rotação em torno do eixo Y
- **Yaw**: Rotação em torno do eixo Z
