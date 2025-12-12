# ⚙️ CHANGELOG - Física e Interface (Torque e Juntas)

**Data:** 12/12/2025 - 18:35  
**Autor:** Antigravity  
**Status:** ✅ **Aplicado**

---

## 🏗️ Alterações na Física (SDF)

### 1. Reposicionamento do Cilindro Vermelho (`link_cylinder`)
*   **Posição Z:** Reduzida em **25 cm** (de `1.503` para `1.253`).
*   **Hierarquia:** A junta `joint_cylinder` agora conecta o `link_cylinder` diretamente ao `link_base` (antes era `link_tower`). Isso desacopla a rotação da torre da rotação do cilindro vermelho.
*   **Geometria:** O raio do cilindro foi aumentado em **5 cm** (de `0.125m` para `0.175m`).

### 2. Ajustes na Junta Azimutal (`joint_azimuth`)
*   **Velocidade Máxima:** Aumentada drasticamente para **100 rad/s** (permitindo giros rápidos).
*   **Dinâmica:**
    *   Amortecimento (`damping`) ajustado para **10**.
    *   Atrito (`friction`) ajustado para **1**.
*   **Torque Máximo:** Restaurado para **2000 Nm** (após teste temporário com 0 Nm).

---

## 🖥️ Alterações na Interface Gráfica (`06_torque_control_gui.py`)

### 1. Redesign Visual
*   **Tema:** Alterado para **Light Theme (Claro)** moderno e limpo.
*   **Cores:**
    *   Vermelho Suave (`#FFEBEE`/`#D32F2F`) para controles do Cilindro Vermelho.
    *   Verde Suave (`#E8F5E9`/`#2E7D32`) para controles do Cilindro Verde.
*   **Layout:** Mais espaçado e organizado em duas colunas de controles.

### 2. Funcionalidades
*   **Botões de Reset:** Adicionados botões "0" ao lado de cada campo numérico para zerar rapidamente os valores.
*   **Sincronização Temporal:** 
    *   A geração de ondas senoidais agora usa o **Tempo de Simulação do Gazebo** (`/world/.../stats`) em vez do tempo real do computador.
    *   Isso garante que a frequência da força aplicada seja física e matematicamente correta, mesmo se a simulação estiver rodando em câmera lenta (Real Time Factor < 1.0) ou acelerada.
    *   Adicionado display "Sim Time" no topo da janela.

---

## 📜 Arquivos Modificados
*   `01_three_link_with_tracker_plate.sdf`
*   `06_torque_control_gui.py`

---
