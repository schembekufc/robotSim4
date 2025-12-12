# � Tabela de Nomenclatura Padronizada (v2.1.0)

Esta tabela documenta **todos** os nomes de elementos utilizados no projeto `robotSim4`, incluindo as adições recentes.

---

## 🏗️ Estrutura Mecânica (Links e Joints)

| Tipo | Nome Atual | Descrição | Pai | Filho | Eixo |
|------|------------|-----------|-----|-------|------|
| **Link** | `link_base` | Base fixa do robô | - | - | - |
| **Link** | `link_tower` | Torre vertical principal | - | - | - |
| **Link** | `link_arm` | Braço horizontal | - | - | - |
| **Link** | `link_tracker_plate` | Placa rastreadora quadrangular | - | - | - |
| **Link** | `link_dish` | Prato parabólico refletor | - | - | - |
| **Link** | `link_cylinder` | **(NOVO)** Cilindro rotativo vermelho | - | - | - |
| **Joint** | `joint_base_fixed` | Fixa a base ao mundo | World | link_base | - |
| **Joint** | `joint_azimuth` | Rotação azimutal da torre | link_base | link_tower | Z |
| **Joint** | `joint_elevation` | Rotação de elevação do braço | link_tower | link_arm | Y |
| **Joint** | `joint_tracker_fixed` | Fixa a placa ao braço | link_arm | link_tracker_plate | - |
| **Joint** | `joint_dish_fixed` | Fixa o prato ao braço | link_arm | link_dish | - |
| **Joint** | `joint_cylinder` | **(NOVO)** Rotação do cilindro | link_tower | link_cylinder | Z |

---

## 👁️ Sensores e Câmeras

| Nome Atual | Tipo | Localização | Tópico Gazebo Transport |
|------------|------|-------------|-------------------------|
| `sensor_quadrant_1` | Camera | Placa (Q1 Vermelho) | `/plate/sensor_quadrant_1/image` |
| `sensor_quadrant_2` | Camera | Placa (Q2 Verde) | `/plate/sensor_quadrant_2/image` |
| `sensor_quadrant_3` | Camera | Placa (Q3 Azul) | `/plate/sensor_quadrant_3/image` |
| `sensor_quadrant_4` | Camera | Placa (Q4 Amarelo) | `/plate/sensor_quadrant_4/image` |
| `sensor_sun_tube` | Camera | Placa (Centro - Tubo) | `/plate/sensor_sun_tube/image` |
| `sensor_focus_camera` | Camera | Foco do Prato | `/parabolic_dish/sensor_focus_camera/image` |
| `joint1_force_torque` | Force/Torque | joint_azimuth | `/model/three_link_model/joint/joint_azimuth/force_torque` |
| `joint2_force_torque` | Force/Torque | joint_elevation | `/model/three_link_model/joint/joint_elevation/force_torque` |

---

## 🎨 Elementos Visuais e de Colisão

### Link Base
- `visual_base_structure`
- `collision_base`

### Link Tower
- `visual_tower_structure`
- `collision_tower`

### Link Arm
- `visual_arm_structure`
- `collision_arm`
- `visual_support_rod` (Haste de suporte da placa)
- `collision_support_rod`

### Link Tracker Plate
- `visual_plate_base`
- `collision_plate_base`
- `visual_disk_opaque` (Disco opaco central)
- `collision_disk_opaque`
- `visual_wall_x_axis` (Parede separadora X)
- `visual_wall_y_axis` (Parede separadora Y)
- `visual_marker_q1_red` ... `_q4_yellow` (Marcadores coloridos)
- `visual_tube_segment_1` ... `_8` (Segmentos do tubo solar)

### Link Dish
- `visual_dish_reflector`
- `collision_dish`
- `visual_feed_support` (Haste do foco)
- `visual_sensor_housing` (Caixa do sensor)
- `visual_filter_dark` (Filtro escuro)
- `visual_lens_center` (Lente)

### Link Cylinder (Novo)
- `visual_cylinder` (Cilindro vermelho)
- `collision_cylinder`

---

## 🎮 Tópicos de Controle

| Junta | Tópico de Comando | Tipo de Mensagem |
|-------|-------------------|------------------|
| **Azimute** | `/model/three_link_model/joint/joint_azimuth/cmd_pos` | `gz.msgs.Double` (Posição rad) |
| **Elevação** | `/model/three_link_model/joint/joint_elevation/cmd_pos` | `gz.msgs.Double` (Posição rad) |
| **Cilindro** | `/model/three_link_model/joint/joint_cylinder/cmd_force` | `gz.msgs.Double` (Torque N⋅m) |

---

## 📁 Arquivos de Malhas 3D (Models)

| Caminho Relativo | Descrição | Tamanho aprox. |
|------------------|-----------|----------------|
| `models/catia/1_Base.dae` | Base do robô | 800 KB |
| `models/catia/2_Torre.dae` | Torre vertical (LFS) | 123 MB |
| `models/catia/3_BracoH.dae` | Braço horizontal | 2.6 MB |
| `formas/parabolic_dish.stl` | Prato parabólico (LFS) | 18 MB |
| `formas/Espelho.dae` | Alternativa para prato | 2.4 MB |
| `lens_mask.obj` | Máscara da lente | 4.7 KB |

---

**Última atualização:** 11/12/2025 - Adicionado Link Cylinder
