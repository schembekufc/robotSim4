# 🏗️ Hierarquia Estrutural do Robô - Robot Sim 4

## 📊 Árvore de Componentes

```
🌍 WORLD (Mundo Gazebo)
│
├─🔗 MODELO: three_link_model
│  │
│  ├─📦 LINK: link1 (Base)
│  │  ├─ 🎨 Visual: link1_visual (Mesh: 1_Base.dae)
│  │  └─ 💥 Collision: link1_collision (Box 20x20x20cm)
│  │
│  ├─🔩 JOINT: world_to_link1 (FIXED)
│  │  └─ Conecta: world → link1
│  │
│  ├─📦 LINK: link2 (Torre)
│  │  ├─ 🎨 Visual: link2_visual (Mesh: 2_Torre.dae)
│  │  └─ 💥 Collision: link2_collision (Box 40x40x100cm)
│  │
│  ├─🔩 JOINT: joint1 (REVOLUTE - Azimute)
│  │  ├─ Conecta: link1 → link2
│  │  ├─ Eixo: Z (rotação horizontal)
│  │  ├─ 📡 Sensor: joint1_force_torque
│  │  └─ 🎮 Controller: JointPositionController
│  │
│  ├─📦 LINK: link3 (Braço H)
│  │  ├─ 🎨 Visual: link3_visual (Mesh: 3_BracoH.dae)
│  │  ├─ 💥 Collision: link3_collision (Box 50x30x80cm)
│  │  ├─ 🎨 Visual: tracker_support_rod_visual (Cilindro Ø3cm x 30cm)
│  │  └─ 💥 Collision: tracker_support_rod_collision
│  │
│  ├─🔩 JOINT: joint2 (REVOLUTE - Elevação)
│  │  ├─ Conecta: link2 → link3
│  │  ├─ Eixo: Y (rotação vertical)
│  │  ├─ 📡 Sensor: joint2_force_torque
│  │  └─ 🎮 Controller: JointPositionController
│  │
│  ├─📦 LINK: link_tracker (Placa Rastreadora)
│  │  │
│  │  ├─ 🎨 VISUAIS:
│  │  │  ├─ tracker_plate_visual (Placa 20x20x0.5cm)
│  │  │  ├─ tracker_opaque_disk_visual (Disco Ø9.5cm)
│  │  │  ├─ tracker_wall_x_visual (Anteparo X)
│  │  │  ├─ tracker_wall_y_visual (Anteparo Y)
│  │  │  ├─ tube_seg_1 ... tube_seg_8 (Tubo solar)
│  │  │  ├─ cam_q1_marker (Marcador vermelho)
│  │  │  ├─ cam_q2_marker (Marcador verde)
│  │  │  ├─ cam_q3_marker (Marcador azul)
│  │  │  └─ cam_q4_marker (Marcador amarelo)
│  │  │
│  │  ├─ 💥 COLISÕES:
│  │  │  └─ tracker_opaque_disk_collision
│  │  │
│  │  └─ 📷 SENSORES (Câmeras):
│  │     ├─ cam_q1 → Tópico: plate/cam_q1/image (Q1: +X,+Y) 🔴
│  │     ├─ cam_q2 → Tópico: plate/cam_q2/image (Q2: -X,+Y) 🟢
│  │     ├─ cam_q3 → Tópico: plate/cam_q3/image (Q3: -X,-Y) 🔵
│  │     ├─ cam_q4 → Tópico: plate/cam_q4/image (Q4: +X,-Y) 🟡
│  │     └─ sun_sensor_tube → Tópico: plate/sun_sensor/image ⚫
│  │
│  ├─🔩 JOINT: tracker_fixed_joint (FIXED)
│  │  └─ Conecta: link3 → link_tracker
│  │
│  ├─📦 LINK: link_parabolic_dish (Prato Parabólico)
│  │  │
│  │  ├─ 🎨 VISUAIS:
│  │  │  ├─ parabolic_dish_visual (Mesh: parabolic_dish.stl)
│  │  │  ├─ feed_support_rod_visual (Haste Ø4cm x 180cm)
│  │  │  ├─ feed_sensor_housing_visual (Caixa sensor Ø10cm)
│  │  │  ├─ camera_filter_visual (Filtro escuro)
│  │  │  └─ camera_lens_center_visual (Lente central)
│  │  │
│  │  ├─ 💥 COLISÕES:
│  │  │  └─ parabolic_dish_collision (Mesh: parabolic_dish.stl)
│  │  │
│  │  └─ 📷 SENSOR:
│  │     └─ focus_camera → Tópico: parabolic_dish/focus_cam/image
│  │        └─ Posição: Foco do prato (1.8m acima da base)
│  │
│  └─🔩 JOINT: parabolic_dish_fixed_joint (FIXED)
│     └─ Conecta: link3 → link_parabolic_dish
│
├─🔗 MODELO: chao (Chão)
│  └─📦 LINK: chao_link
│     ├─ 🎨 Visual: chao_visual (Plano 100x100m)
│     └─ 💥 Collision: chao_collision
│
├─🔗 MODELO: compass (Rosa dos Ventos)
│  └─ [Componentes de orientação]
│
└─☀️ LUZ: sun (Sol Direcional)
   ├─ Tipo: Directional
   ├─ Intensidade: 1.0
   └─ Direção: Controlável via GUI
```

---

## 🔄 Fluxo de Controle

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTROLE DO ROBÔ                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   GUI Python (02_unified_control_gui.py) │
        └─────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
    ┌───────────────────┐       ┌───────────────────┐
    │  Comando Manual   │       │ Rastreamento Auto │
    └───────────────────┘       └───────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              ▼
                    ┌─────────────────────┐
                    │  Gazebo Transport   │
                    └─────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
    ┌───────────────────────┐   ┌───────────────────────┐
    │ /model/.../joint/     │   │ /model/.../joint/     │
    │ joint1/cmd_pos        │   │ joint2/cmd_pos        │
    └───────────────────────┘   └───────────────────────┘
                │                           │
                ▼                           ▼
    ┌───────────────────────┐   ┌───────────────────────┐
    │  JointPosition        │   │  JointPosition        │
    │  Controller (joint1)  │   │  Controller (joint2)  │
    └───────────────────────┘   └───────────────────────┘
                │                           │
                ▼                           ▼
    ┌───────────────────────┐   ┌───────────────────────┐
    │  Rotação Azimute (Z)  │   │ Rotação Elevação (Y)  │
    │  link1 → link2        │   │  link2 → link3        │
    └───────────────────────┘   └───────────────────────┘
```

---

## 📡 Fluxo de Dados dos Sensores

```
┌─────────────────────────────────────────────────────────────┐
│                   SENSORES → GUI                            │
└─────────────────────────────────────────────────────────────┘

☀️ SOL (Luz Direcional)
  │
  ├─→ 📷 cam_q1 (Quadrante 1) ──→ plate/cam_q1/image ──┐
  ├─→ 📷 cam_q2 (Quadrante 2) ──→ plate/cam_q2/image ──┤
  ├─→ 📷 cam_q3 (Quadrante 3) ──→ plate/cam_q3/image ──┼──→ GUI
  ├─→ 📷 cam_q4 (Quadrante 4) ──→ plate/cam_q4/image ──┤
  ├─→ 📷 sun_sensor_tube ────────→ plate/sun_sensor/image ─┤
  └─→ 📷 focus_camera ───────────→ parabolic_dish/focus_cam/image ─┘

┌─────────────────────────────────────────────────────────────┐
│                    CÁLCULO DE ERRO                          │
└─────────────────────────────────────────────────────────────┘

Luminância: L1 (Q1), L2 (Q2), L3 (Q3), L4 (Q4)

err_x = (L1 + L4)/2 - (L2 + L3)/2
err_y = (L1 + L2)/2 - (L3 + L4)/2

Objetivo: err_x ≈ 0 e err_y ≈ 0
```

---

## 🎯 Sistema de Coordenadas

```
                    +Z (Cima)
                     ↑
                     │
                     │
                     │
                     └────────→ +X (Frente)
                    ╱
                   ╱
                  ↙
                +Y (Esquerda)

┌─────────────────────────────────────────────────────────────┐
│                 QUADRANTES DA PLACA                         │
└─────────────────────────────────────────────────────────────┘

                +Y (Esquerda)
                     ↑
                     │
         Q2 🟢       │       🔴 Q1
        (-X,+Y)      │      (+X,+Y)
                     │
    ─────────────────┼─────────────────→ +X (Frente)
                     │
        (-X,-Y)      │      (+X,-Y)
         Q3 🔵       │       🟡 Q4
                     │
                     ↓
                -Y (Direita)
```

---

## 📏 Dimensões e Massas

| Componente | Massa (kg) | Dimensões | Material |
|------------|------------|-----------|----------|
| link1 (Base) | 2.0 | 20x20x20 cm | Metal |
| link2 (Torre) | 20.0 | 40x40x100 cm | Metal |
| link3 (Braço) | 25.0 | 50x30x80 cm | Metal |
| link_tracker (Placa) | 0.5 | 20x20x0.5 cm | Alumínio |
| link_parabolic_dish (Prato) | 145.5 | Ø300cm, foco 180cm | Resina + Fibra de Vidro |

---

## 🔌 Tópicos Gazebo Transport

### Comandos (Publicação):
- `/model/three_link_model/joint/joint1/cmd_pos` - Comando de posição joint1
- `/model/three_link_model/joint/joint2/cmd_pos` - Comando de posição joint2
- `/world/three_link_with_tracker_plate_world/light_config` - Configuração do sol

### Sensores (Subscrição):
- `plate/cam_q1/image` - Imagem câmera Q1
- `plate/cam_q2/image` - Imagem câmera Q2
- `plate/cam_q3/image` - Imagem câmera Q3
- `plate/cam_q4/image` - Imagem câmera Q4
- `plate/sun_sensor/image` - Imagem sensor solar
- `parabolic_dish/focus_cam/image` - Imagem câmera focal
- `/world/three_link_with_tracker_plate_world/pose/info` - Poses dos links

---

## 🎨 Código de Cores dos Sensores

| Sensor | Cor | RGB | Posição | Função |
|--------|-----|-----|---------|--------|
| cam_q1 | 🔴 Vermelho | (255, 0, 0) | (+X, +Y) | Detecta luz frontal-esquerda |
| cam_q2 | 🟢 Verde | (0, 255, 0) | (-X, +Y) | Detecta luz traseira-esquerda |
| cam_q3 | 🔵 Azul | (0, 0, 255) | (-X, -Y) | Detecta luz traseira-direita |
| cam_q4 | 🟡 Amarelo | (255, 255, 0) | (+X, -Y) | Detecta luz frontal-direita |
| sun_sensor_tube | ⚫ Preto | (0, 0, 0) | (0, 0) | Sensor solar preciso |

---

## 🔧 Controladores Ativos

1. **JointPositionController (joint1)**
   - P_gain: 1000
   - I_gain: 100
   - D_gain: 3000
   - Controla rotação azimutal

2. **JointPositionController (joint2)**
   - P_gain: 4000
   - I_gain: 5000
   - D_gain: 4000
   - Controla rotação de elevação

3. **JointStatePublisher**
   - Publica estado de joint1 e joint2

---

**Documento gerado para auxiliar na padronização da nomenclatura do Robot Sim 4** 🤖
