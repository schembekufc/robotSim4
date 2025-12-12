# 📊 CHANGELOG - Data Logger Avançado

**Data:** 12/12/2025 - 20:31
**Autor:** Antigravity  
**Status:** ✅ **Implementado**

---

## 🚀 Nova Ferramenta: Data Logger Híbrido (`07_data_logger_gui.py`)

Desenvolvemos uma ferramenta de coleta de dados capaz de contornar as limitações de leitura de esforço padrão do Gazebo, fornecendo dados completos para análise.

### 🌟 Principais Funcionalidades

1.  **Leitura Híbrida de Torque (Esforço)**
    *   **Para Juntas de Força (Cilindros):** O logger assina os tópicos de comando (`/cmd_force`) para registrar o valor exato que está sendo enviado pelo controlador de torque. Isso resolve o problema de leitura "0" causada pela ausência de sensores físicos.
    *   **Para Juntas PID (Azimute/Elevação):** Implementamos um **Cálculo de PID em Tempo Real** (Engenharia Reversa). O script lê a posição atual e o alvo, e usa os mesmos ganhos $K_p, K_i, K_d$ definidos no SDF para estimar matematicamente o torque aplicado pelo controlador.

2.  **Sincronização Perfeita**
    *   Os dados são gravados com base no *Timestamp* da simulação, não do relógio do sistema.

3.  **Interface Otimizada**
    *   Tema claro (Light Theme).
    *   Diferenciação visual: Juntas PID (Laranja) vs. Juntas de Comando (Verde).
    *   Seleção granular de colunas (Posição, Velocidade, Esforço).

### 📋 Como Usar

```bash
python3 07_data_logger_gui.py
```
*O arquivo CSV será salvo automaticamente com a data e hora atual no nome.*

---

## 🛠️ Alterações Recentes

*   **SDF (`01_three_link_with_tracker_plate.sdf`):**
    *   Correção de erro de sintaxe XML (tag `dynamics` estava corrompida).
    *   Reversão da adição de sensores `<force_torque>` (mantendo a simulação leve e usando a abordagem híbrida no Python).
    *   Ajuste na posição visual da faixa branca do cilindro para acompanhar o novo raio (0.175m).

---
