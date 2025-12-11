# 📋 Sugestão de Padronização de Nomenclatura - Robot Sim 4

## 🎯 Objetivo
Este documento apresenta uma proposta de padronização dos nomes dos links, joints e componentes do arquivo SDF `01_three_link_with_tracker_plate.sdf`, visando maior clareza e consistência.

---

## 📊 Análise da Estrutura Atual

### Modelo Principal: `three_link_model`

#### **Links Atuais:**
1. `link1` - Base fixa do robô
2. `link2` - Torre vertical
3. `link3` - Braço horizontal (H-arm)
4. `link_tracker` - Placa rastreadora com sensores
5. `link_parabolic_dish` - Prato parabólico com espelho

#### **Joints Atuais:**
1. `world_to_link1` - Fixa o link1 ao mundo
2. `joint1` - Rotação azimutal (Z-axis) entre link1 e link2
3. `joint2` - Rotação de elevação (Y-axis) entre link2 e link3
4. `tracker_fixed_joint` - Fixa a placa ao link3
5. `parabolic_dish_fixed_joint` - Fixa o prato ao link3

---

## ✨ Nomenclatura Sugerida

### 🔧 **Opção 1: Nomenclatura Descritiva em Português**

#### **Links:**
| Nome Atual | Nome Sugerido | Descrição |
|------------|---------------|-----------|
| `link1` | `base_fixa` | Base fixa do sistema (fundação) |
| `link2` | `torre_vertical` | Torre que se eleva verticalmente |
| `link3` | `braco_horizontal` | Braço horizontal que suporta os sensores |
| `link_tracker` | `placa_rastreadora` | Placa com sensores de quadrante |
| `link_parabolic_dish` | `prato_parabolico` | Prato parabólico refletor |

#### **Joints:**
| Nome Atual | Nome Sugerido | Descrição |
|------------|---------------|-----------|
| `world_to_link1` | `fixacao_base_mundo` | Fixação da base ao mundo |
| `joint1` | `junta_azimutal` | Rotação azimutal (eixo Z) |
| `joint2` | `junta_elevacao` | Rotação de elevação (eixo Y) |
| `tracker_fixed_joint` | `fixacao_placa` | Fixação da placa ao braço |
| `parabolic_dish_fixed_joint` | `fixacao_prato` | Fixação do prato ao braço |

---

### 🔧 **Opção 2: Nomenclatura Técnica em Inglês**

#### **Links:**
| Nome Atual | Nome Sugerido | Descrição |
|------------|---------------|-----------|
| `link1` | `base_platform` | Base platform (foundation) |
| `link2` | `vertical_tower` | Vertical tower structure |
| `link3` | `horizontal_arm` | Horizontal arm (H-beam) |
| `link_tracker` | `tracker_plate` | Tracker plate with sensors |
| `link_parabolic_dish` | `parabolic_dish` | Parabolic reflector dish |

#### **Joints:**
| Nome Atual | Nome Sugerido | Descrição |
|------------|---------------|-----------|
| `world_to_link1` | `base_to_world` | Base to world attachment |
| `joint1` | `azimuth_joint` | Azimuth rotation (Z-axis) |
| `joint2` | `elevation_joint` | Elevation rotation (Y-axis) |
| `tracker_fixed_joint` | `tracker_attachment` | Tracker plate attachment |
| `parabolic_dish_fixed_joint` | `dish_attachment` | Dish attachment |

---

### 🔧 **Opção 3: Nomenclatura Híbrida (Recomendada)**

Esta opção combina clareza funcional com padronização técnica.

#### **Links:**
| Nome Atual | Nome Sugerido | Descrição |
|------------|---------------|-----------|
| `link1` | `link_base` | Base do sistema |
| `link2` | `link_tower` | Torre vertical |
| `link3` | `link_arm` | Braço horizontal |
| `link_tracker` | `link_tracker_plate` | Placa rastreadora |
| `link_parabolic_dish` | `link_dish` | Prato parabólico |

#### **Joints:**
| Nome Atual | Nome Sugerido | Descrição |
|------------|---------------|-----------|
| `world_to_link1` | `joint_base_fixed` | Fixação da base |
| `joint1` | `joint_azimuth` | Junta azimutal (rotação Z) |
| `joint2` | `joint_elevation` | Junta de elevação (rotação Y) |
| `tracker_fixed_joint` | `joint_tracker_fixed` | Fixação da placa |
| `parabolic_dish_fixed_joint` | `joint_dish_fixed` | Fixação do prato |

---

## 🔍 Componentes Internos dos Links

### **link_tracker (Placa Rastreadora)**

#### Sensores de Quadrante:
| Nome Atual | Nome Sugerido | Descrição |
|------------|---------------|-----------|
| `cam_q1` | `sensor_quadrant_1` ou `cam_q1_red` | Quadrante 1 (+X,+Y) - Vermelho |
| `cam_q2` | `sensor_quadrant_2` ou `cam_q2_green` | Quadrante 2 (-X,+Y) - Verde |
| `cam_q3` | `sensor_quadrant_3` ou `cam_q3_blue` | Quadrante 3 (-X,-Y) - Azul |
| `cam_q4` | `sensor_quadrant_4` ou `cam_q4_yellow` | Quadrante 4 (+X,-Y) - Amarelo |
| `sun_sensor_tube` | `sensor_sun_tube` | Sensor solar tipo tubo |

#### Elementos Visuais:
| Nome Atual | Nome Sugerido | Descrição |
|------------|---------------|-----------|
| `tracker_plate_visual` | `visual_plate_base` | Base da placa |
| `tracker_opaque_disk_visual` | `visual_disk_opaque` | Disco opaco central |
| `tracker_wall_x_visual` | `visual_wall_x_axis` | Anteparo eixo X |
| `tracker_wall_y_visual` | `visual_wall_y_axis` | Anteparo eixo Y |
| `tracker_support_rod_visual` | `visual_support_rod` | Aste de suporte |
| `tube_seg_1` até `tube_seg_8` | `visual_tube_segment_1` até `visual_tube_segment_8` | Segmentos do tubo |

---

### **link_parabolic_dish (Prato Parabólico)**

#### Componentes:
| Nome Atual | Nome Sugerido | Descrição |
|------------|---------------|-----------|
| `parabolic_dish_visual` | `visual_dish_reflector` | Superfície refletora |
| `parabolic_dish_collision` | `collision_dish` | Colisão do prato |
| `feed_support_rod_visual` | `visual_feed_support` | Haste de suporte do sensor |
| `feed_sensor_housing_visual` | `visual_sensor_housing` | Caixa do sensor focal |
| `camera_filter_visual` | `visual_filter_dark` | Filtro escuro (óculos de sol) |
| `camera_lens_center_visual` | `visual_lens_center` | Lente central |
| `focus_camera` | `sensor_focus_camera` | Câmera no ponto focal |

---

### **link_arm (Braço Horizontal - link3)**

#### Componentes:
| Nome Atual | Nome Sugerido | Descrição |
|------------|---------------|-----------|
| `link3_visual` | `visual_arm_structure` | Estrutura do braço H |
| `link3_collision` | `collision_arm` | Colisão do braço |

---

## 📝 Observações Importantes

### **Convenções de Nomenclatura:**

1. **Prefixos Funcionais:**
   - `link_` - Para links principais
   - `joint_` - Para juntas
   - `sensor_` - Para sensores (câmeras, etc.)
   - `visual_` - Para elementos visuais
   - `collision_` - Para elementos de colisão

2. **Padrão de Nomes:**
   - Use snake_case (palavras_separadas_por_underline)
   - Seja descritivo mas conciso
   - Evite abreviações obscuras
   - Mantenha consistência entre componentes similares

3. **Hierarquia:**
   - Nome do componente deve refletir sua função
   - Componentes relacionados devem ter prefixos similares
   - Números sequenciais para elementos repetidos (seg_1, seg_2, etc.)

---

## 🎨 Impacto nas GUIs Python

### **Arquivos que Precisarão de Atualização:**

Se você optar por mudar os nomes, os seguintes arquivos Python precisarão ser atualizados:

1. **`02_unified_control_gui.py`**
   - Referências a `link_parabolic_dish`
   - Referências a `link3`
   - Tópicos de comando das juntas (`joint1`, `joint2`)

2. **`03_light_sensor_gui.py`**
   - Referências a `link_parabolic_dish`
   - Referências a `link3`

3. **`plate_light_gui_images.py`**
   - Tópicos das câmeras (`plate/cam_q1/image`, etc.)

4. **`tracker_auto_control_gui.py`**
   - Comandos de juntas

5. **`05_balls_control_gui.py`**
   - Se houver referências aos links principais

---

## 💡 Recomendação Final

**Sugiro a Opção 3 (Nomenclatura Híbrida)** pelos seguintes motivos:

✅ **Vantagens:**
- Mantém o prefixo `link_` e `joint_` para facilitar identificação
- Nomes descritivos em inglês (padrão internacional)
- Fácil de entender para desenvolvedores
- Compatível com convenções do Gazebo/ROS
- Mudanças mínimas necessárias no código Python

✅ **Consistência:**
- Todos os links começam com `link_`
- Todas as juntas começam com `joint_`
- Sensores começam com `sensor_`
- Visuais começam com `visual_`

✅ **Clareza:**
- `link_base` é mais claro que `link1`
- `joint_azimuth` é mais descritivo que `joint1`
- `sensor_quadrant_1` é mais informativo que `cam_q1`

---

## 📋 Próximos Passos

Após sua aprovação da nomenclatura escolhida:

1. ✏️ Atualizar o arquivo SDF
2. 🔄 Atualizar os scripts Python
3. 📝 Atualizar a documentação (README.md)
4. ✅ Testar a simulação
5. 🎯 Verificar todas as GUIs

---

**Aguardando sua decisão sobre qual nomenclatura utilizar antes de fazer as alterações!** 🚀
