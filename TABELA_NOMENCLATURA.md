# 📊 Tabela Resumida - Nomenclatura do Robô

## 🎯 Comparação Rápida das 3 Opções

---

## 🔗 LINKS PRINCIPAIS

| Atual | Opção 1 (PT-BR) | Opção 2 (EN) | Opção 3 (Híbrida) ⭐ | Função |
|-------|-----------------|--------------|---------------------|---------|
| `link1` | `base_fixa` | `base_platform` | `link_base` | Base do sistema |
| `link2` | `torre_vertical` | `vertical_tower` | `link_tower` | Torre vertical |
| `link3` | `braco_horizontal` | `horizontal_arm` | `link_arm` | Braço horizontal |
| `link_tracker` | `placa_rastreadora` | `tracker_plate` | `link_tracker_plate` | Placa com sensores |
| `link_parabolic_dish` | `prato_parabolico` | `parabolic_dish` | `link_dish` | Prato parabólico |

---

## 🔧 JUNTAS (JOINTS)

| Atual | Opção 1 (PT-BR) | Opção 2 (EN) | Opção 3 (Híbrida) ⭐ | Função |
|-------|-----------------|--------------|---------------------|---------|
| `world_to_link1` | `fixacao_base_mundo` | `base_to_world` | `joint_base_fixed` | Fixa base ao mundo |
| `joint1` | `junta_azimutal` | `azimuth_joint` | `joint_azimuth` | Rotação Z (azimute) |
| `joint2` | `junta_elevacao` | `elevation_joint` | `joint_elevation` | Rotação Y (elevação) |
| `tracker_fixed_joint` | `fixacao_placa` | `tracker_attachment` | `joint_tracker_fixed` | Fixa placa ao braço |
| `parabolic_dish_fixed_joint` | `fixacao_prato` | `dish_attachment` | `joint_dish_fixed` | Fixa prato ao braço |

---

## 📷 SENSORES DA PLACA RASTREADORA

| Atual | Sugestão Alternativa 1 | Sugestão Alternativa 2 | Cor | Posição |
|-------|------------------------|------------------------|-----|---------|
| `cam_q1` | `sensor_quadrant_1` | `cam_q1_red` | 🔴 Vermelho | (+X, +Y) |
| `cam_q2` | `sensor_quadrant_2` | `cam_q2_green` | 🟢 Verde | (-X, +Y) |
| `cam_q3` | `sensor_quadrant_3` | `cam_q3_blue` | 🔵 Azul | (-X, -Y) |
| `cam_q4` | `sensor_quadrant_4` | `cam_q4_yellow` | 🟡 Amarelo | (+X, -Y) |
| `sun_sensor_tube` | `sensor_sun_tube` | `cam_sun_tube` | ⚫ Preto | Centro (0, 0) |

---

## 🎨 ELEMENTOS VISUAIS - PLACA RASTREADORA

| Atual | Sugerido | Descrição |
|-------|----------|-----------|
| `tracker_plate_visual` | `visual_plate_base` | Base da placa (20x20cm) |
| `tracker_opaque_disk_visual` | `visual_disk_opaque` | Disco opaco central (Ø9.5cm) |
| `tracker_wall_x_visual` | `visual_wall_x_axis` | Anteparo no eixo X |
| `tracker_wall_y_visual` | `visual_wall_y_axis` | Anteparo no eixo Y |
| `tracker_support_rod_visual` | `visual_support_rod` | Aste de fixação (Ø3cm, 30cm) |
| `tube_seg_1` ... `tube_seg_8` | `visual_tube_segment_1` ... `_8` | Segmentos do tubo solar |
| `cam_q1_marker` | `visual_marker_q1_red` | Marcador visual Q1 |
| `cam_q2_marker` | `visual_marker_q2_green` | Marcador visual Q2 |
| `cam_q3_marker` | `visual_marker_q3_blue` | Marcador visual Q3 |
| `cam_q4_marker` | `visual_marker_q4_yellow` | Marcador visual Q4 |

---

## 🛰️ ELEMENTOS DO PRATO PARABÓLICO

| Atual | Sugerido | Descrição |
|-------|----------|-----------|
| `parabolic_dish_visual` | `visual_dish_reflector` | Superfície refletora parabólica |
| `parabolic_dish_collision` | `collision_dish` | Colisão do prato |
| `feed_support_rod_visual` | `visual_feed_support` | Haste de suporte (1.8m) |
| `feed_sensor_housing_visual` | `visual_sensor_housing` | Caixa do sensor focal |
| `camera_filter_visual` | `visual_filter_dark` | Filtro escuro (óculos de sol) |
| `camera_lens_center_visual` | `visual_lens_center` | Lente central transparente |
| `focus_camera` | `sensor_focus_camera` | Câmera no foco (1.8m) |

---

## 🏗️ ELEMENTOS DO BRAÇO (link3)

| Atual | Sugerido | Descrição |
|-------|----------|-----------|
| `link3_visual` | `visual_arm_structure` | Estrutura do braço H |
| `link3_collision` | `collision_arm` | Colisão do braço |

---

## 📐 DIMENSÕES IMPORTANTES

| Componente | Dimensão | Observação |
|------------|----------|------------|
| Base (link1) | 20x20x20 cm | Cubo |
| Torre (link2) | 40x40x100 cm | Prisma vertical |
| Braço (link3) | 50x30x80 cm | Braço H |
| Placa rastreadora | 20x20x0.5 cm | Placa fina |
| Disco opaco | Ø9.5cm x 0.5cm | Centro da placa |
| Tubo solar | Ø1cm x 5cm | Cilindro oco (8 segmentos) |
| Prato parabólico | Ø3m, foco 1.8m | Malha STL |
| Aste suporte placa | Ø3cm x 30cm | Cilindro |
| Aste suporte sensor | Ø4cm x 180cm | Cilindro |

---

## 🎯 RECOMENDAÇÃO

### ⭐ **Opção 3 (Nomenclatura Híbrida)** é a mais recomendada:

**Vantagens:**
- ✅ Mantém prefixos padronizados (`link_`, `joint_`, `sensor_`, `visual_`)
- ✅ Nomes em inglês (padrão internacional)
- ✅ Descritiva e clara
- ✅ Compatível com ROS/Gazebo
- ✅ Fácil de manter e expandir

**Mudanças Necessárias nos Códigos Python:**

1. `02_unified_control_gui.py` - Atualizar referências a links e juntas
2. `03_light_sensor_gui.py` - Atualizar referências a links
3. `plate_light_gui_images.py` - Atualizar tópicos de câmeras (se necessário)
4. `tracker_auto_control_gui.py` - Atualizar comandos de juntas
5. `05_balls_control_gui.py` - Verificar referências

---

## 📋 CHECKLIST DE ALTERAÇÕES

Após escolher a nomenclatura:

- [ ] Atualizar arquivo SDF
- [ ] Atualizar scripts Python
- [ ] Atualizar README.md
- [ ] Testar simulação no Gazebo
- [ ] Testar todas as GUIs
- [ ] Atualizar documentação técnica
- [ ] Fazer commit das alterações

---

**Status:** 🟡 Aguardando aprovação para implementar as mudanças
