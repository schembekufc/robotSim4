# 📝 CHANGELOG - Padronização de Nomenclatura

**Data:** 11/12/2025  
**Versão:** 2.0.0  
**Tipo:** Refatoração de Nomenclatura (Breaking Changes)

---

## 🎯 Resumo das Mudanças

Implementada padronização completa de nomenclatura seguindo a **Opção 3 - Nomenclatura Híbrida**, conforme documentado em `NOMENCLATURA_SUGERIDA.md`.

### Princípios Aplicados:
- ✅ Prefixos funcionais padronizados (`link_`, `joint_`, `sensor_`, `visual_`, `collision_`)
- ✅ Nomes descritivos em inglês (padrão internacional)
- ✅ Snake_case consistente
- ✅ Hierarquia clara refletindo função e posição

---

## 📦 Mudanças no Arquivo SDF

### **Arquivo:** `01_three_link_with_tracker_plate.sdf`

#### **Links Principais:**

| Antes | Depois | Tipo |
|-------|--------|------|
| `link1` | `link_base` | Base do sistema |
| `link2` | `link_tower` | Torre vertical |
| `link3` | `link_arm` | Braço horizontal |
| `link_tracker` | `link_tracker_plate` | Placa rastreadora |
| `link_parabolic_dish` | `link_dish` | Prato parabólico |

#### **Joints:**

| Antes | Depois | Tipo |
|-------|--------|------|
| `world_to_link1` | `joint_base_fixed` | Fixação ao mundo |
| `joint1` | `joint_azimuth` | Rotação azimutal (Z) |
| `joint2` | `joint_elevation` | Rotação de elevação (Y) |
| `tracker_fixed_joint` | `joint_tracker_fixed` | Fixação da placa |
| `parabolic_dish_fixed_joint` | `joint_dish_fixed` | Fixação do prato |

#### **Sensores (Câmeras):**

| Antes | Depois | Descrição |
|-------|--------|-----------|
| `cam_q1` | `sensor_quadrant_1` | Sensor quadrante 1 (vermelho) |
| `cam_q2` | `sensor_quadrant_2` | Sensor quadrante 2 (verde) |
| `cam_q3` | `sensor_quadrant_3` | Sensor quadrante 3 (azul) |
| `cam_q4` | `sensor_quadrant_4` | Sensor quadrante 4 (amarelo) |
| `sun_sensor_tube` | `sensor_sun_tube` | Sensor solar tipo tubo |
| `focus_camera` | `sensor_focus_camera` | Câmera no foco do prato |

#### **Elementos Visuais - link_base:**

| Antes | Depois |
|-------|--------|
| `link1_visual` | `visual_base_structure` |
| `link1_collision` | `collision_base` |

#### **Elementos Visuais - link_tower:**

| Antes | Depois |
|-------|--------|
| `link2_visual` | `visual_tower_structure` |
| `link2_collision` | `collision_tower` |

#### **Elementos Visuais - link_arm:**

| Antes | Depois |
|-------|--------|
| `link3_visual` | `visual_arm_structure` |
| `link3_collision` | `collision_arm` |
| `tracker_support_rod_visual` | `visual_support_rod` |
| `tracker_support_rod_collision` | `collision_support_rod` |

#### **Elementos Visuais - link_tracker_plate:**

| Antes | Depois |
|-------|--------|
| `tracker_plate_visual` | `visual_plate_base` |
| `tracker_opaque_disk_visual` | `visual_disk_opaque` |
| `tracker_opaque_disk_collision` | `collision_disk_opaque` |
| `tracker_wall_x_visual` | `visual_wall_x_axis` |
| `tracker_wall_y_visual` | `visual_wall_y_axis` |
| `cam_q1_marker` | `visual_marker_q1_red` |
| `cam_q2_marker` | `visual_marker_q2_green` |
| `cam_q3_marker` | `visual_marker_q3_blue` |
| `cam_q4_marker` | `visual_marker_q4_yellow` |
| `tube_seg_1` ... `tube_seg_8` | `visual_tube_segment_1` ... `_8` |

#### **Elementos Visuais - link_dish:**

| Antes | Depois |
|-------|--------|
| `parabolic_dish_visual` | `visual_dish_reflector` |
| `parabolic_dish_collision` | `collision_dish` |
| `feed_support_rod_visual` | `visual_feed_support` |
| `feed_sensor_housing_visual` | `visual_sensor_housing` |
| `camera_filter_visual` | `visual_filter_dark` |
| `camera_lens_center_visual` | `visual_lens_center` |

#### **Tópicos de Controle Atualizados:**

| Antes | Depois |
|-------|--------|
| `/model/three_link_model/joint/joint1/cmd_pos` | `/model/three_link_model/joint/joint_azimuth/cmd_pos` |
| `/model/three_link_model/joint/joint2/cmd_pos` | `/model/three_link_model/joint/joint_elevation/cmd_pos` |

---

## 🐍 Mudanças nos Arquivos Python

### **1. `02_unified_control_gui.py`**

**Mudanças:**
- ✅ `link_parabolic_dish` → `link_dish` (linha 459)
- ✅ `link3` → `link_arm` (linha 466)
- ✅ `joint1` → `joint_azimuth` (múltiplas linhas)
- ✅ `joint2` → `joint_elevation` (múltiplas linhas)
- ✅ Tópicos de comando atualizados

**Linhas Afetadas:** ~10 alterações

---

### **2. `03_light_sensor_gui.py`**

**Mudanças:**
- ✅ `link_parabolic_dish` → `link_dish` (linha 251)
- ✅ `link3` → `link_arm` (linha 258)

**Linhas Afetadas:** 2 alterações

---

### **3. `tracker_auto_control_gui.py`**

**Mudanças:**
- ✅ `joint1` → `joint_azimuth` (múltiplas linhas)
- ✅ `joint2` → `joint_elevation` (múltiplas linhas)
- ✅ Tópicos de comando atualizados

**Linhas Afetadas:** ~8 alterações

---

### **4. `tracker_auto_control.py`**

**Mudanças:**
- ✅ `joint1` → `joint_azimuth` (múltiplas linhas)
- ✅ `joint2` → `joint_elevation` (múltiplas linhas)
- ✅ Tópicos de comando atualizados

**Linhas Afetadas:** ~6 alterações

---

### **5. Arquivos NÃO Modificados:**

Os seguintes arquivos **não** precisaram de alterações pois não referenciam os componentes renomeados:

- ✅ `04_sun_control_gui.py` - Controla apenas a luz solar
- ✅ `05_balls_control_gui.py` - Controla apenas as esferas rotativas
- ✅ `plate_light_gui_images.py` - Usa apenas tópicos de imagem (não afetados)
- ✅ Scripts utilitários (`generate_*.py`, `calculate_*.py`, `fix_*.py`)

---

## 🔄 Compatibilidade

### **Breaking Changes:**

⚠️ **ATENÇÃO:** Esta atualização contém mudanças incompatíveis com versões anteriores!

**Impactos:**
1. ❌ Arquivos SDF antigos não funcionarão com GUIs novas
2. ❌ GUIs antigas não funcionarão com arquivo SDF novo
3. ❌ Tópicos Gazebo Transport foram renomeados

**Solução:**
- Use todos os arquivos atualizados em conjunto
- Backups foram criados com extensão `.backup`

---

## 📋 Arquivos de Backup Criados

Todos os arquivos foram salvos antes das modificações:

```
01_three_link_with_tracker_plate.sdf.backup
02_unified_control_gui.py.backup
03_light_sensor_gui.py.backup
04_sun_control_gui.py.backup
05_balls_control_gui.py.backup
tracker_auto_control_gui.py.backup
tracker_auto_control.py.backup
plate_light_gui_images.py.backup
[... todos os outros .py.backup]
```

**Para restaurar versão anterior:**
```bash
cp 01_three_link_with_tracker_plate.sdf.backup 01_three_link_with_tracker_plate.sdf
cp 02_unified_control_gui.py.backup 02_unified_control_gui.py
# etc...
```

---

## ✅ Testes Recomendados

Após aplicar as mudanças, teste:

1. **Simulação Básica:**
   ```bash
   gz sim 01_three_link_with_tracker_plate.sdf
   ```

2. **GUI Unificada:**
   ```bash
   python3 02_unified_control_gui.py
   ```

3. **GUI de Sensores:**
   ```bash
   python3 03_light_sensor_gui.py
   ```

4. **Controle Automático:**
   ```bash
   python3 tracker_auto_control_gui.py
   ```

5. **Verificar Tópicos:**
   ```bash
   gz topic -l | grep joint
   ```
   
   Deve mostrar:
   - `/model/three_link_model/joint/joint_azimuth/cmd_pos`
   - `/model/three_link_model/joint/joint_elevation/cmd_pos`

---

## 📊 Estatísticas

- **Arquivos SDF modificados:** 1
- **Arquivos Python modificados:** 4
- **Total de linhas alteradas:** ~150
- **Links renomeados:** 5
- **Joints renomeadas:** 5
- **Sensores renomeados:** 6
- **Elementos visuais renomeados:** ~25
- **Tempo de implementação:** ~2 horas

---

## 📚 Documentação Relacionada

- `NOMENCLATURA_SUGERIDA.md` - Análise detalhada das opções
- `TABELA_NOMENCLATURA.md` - Comparação rápida
- `HIERARQUIA_ROBO.md` - Diagrama estrutural completo
- `RESUMO_EXECUTIVO.md` - Plano de implementação

---

## 👤 Autor

**Implementado por:** Antigravity AI Assistant  
**Aprovado por:** Jhoni (lhmt-jhoni)  
**Data:** 11/12/2025

---

## 🎯 Próximos Passos

- [ ] Testar simulação completa
- [ ] Testar todas as GUIs
- [ ] Atualizar README.md com novos nomes
- [ ] Fazer commit das alterações
- [ ] Atualizar documentação técnica

---

**Status:** ✅ Implementação Completa
