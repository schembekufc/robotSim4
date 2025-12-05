# 🎮 Guia de Uso: Controle Oscilatório das Esferas

## 📋 Visão Geral

A GUI `05_balls_control_gui.py` controla as 3 esferas em **movimento oscilatório** (vai e vem) usando uma função senoidal:

```
v(t) = A × sin(2π × f × t)
```

Onde:
- **A** = Amplitude (velocidade máxima em m/s)
- **f** = Frequência (ciclos por segundo, em Hz)
- **t** = Tempo (segundos)

---

## 🚀 Como Executar

### 1. Iniciar a Simulação
```bash
gz sim 01_three_link_with_tracker_plate.sdf
```

### 2. Executar a GUI
```bash
python3 05_balls_control_gui.py
```

---

## 🎛️ Controles Disponíveis

### **Para Cada Esfera:**

#### ✅ **Habilitar Oscilação**
- Checkbox para ligar/desligar o movimento oscilatório
- Quando desabilitado, a esfera para imediatamente

#### 📊 **Frequência (0.1 Hz - 10 Hz)**
- **Slider**: Ajuste rápido
- **SpinBox**: Ajuste preciso (2 casas decimais)
- **0.1 Hz**: 1 ciclo a cada 10 segundos (muito lento)
- **1.0 Hz**: 1 ciclo por segundo (padrão)
- **10 Hz**: 10 ciclos por segundo (muito rápido)

#### 📈 **Amplitude (0.01 m/s - 1.0 m/s)**
- **Slider**: Ajuste rápido
- **SpinBox**: Ajuste preciso (2 casas decimais)
- Define a **velocidade máxima** da oscilação
- **0.5 m/s** (padrão): Movimento moderado

#### 📍 **Status**
- Mostra se a esfera está oscilando ou parada
- Exibe a frequência atual quando ativa

---

## 🎯 Configuração das Esferas

| Esfera | Cor | Eixo | Movimento |
|--------|-----|------|-----------|
| **1** | 🟢 Verde | **X** | Esquerda ↔ Direita |
| **2** | 🔴 Vermelha | **Y** | Trás ↔ Frente |
| **3** | 🔵 Azul | **Z** | Baixo ↔ Cima |

---

## 🔘 Botões Globais

### **Iniciar Todas (1 Hz)**
- Habilita oscilação de todas as 3 esferas
- Define frequência de 1 Hz para todas
- Mantém as amplitudes individuais

### **Parar Todas**
- Desabilita oscilação de todas as esferas
- Esferas param imediatamente

### **Sincronizar Fase**
- Reinicia o contador de tempo
- Faz todas as esferas começarem na mesma fase
- Útil para criar padrões sincronizados

---

## 📊 Exemplos de Uso

### **Exemplo 1: Oscilação Simples**
1. Habilite apenas a **Esfera 1 (Verde)**
2. Configure:
   - Frequência: **1.0 Hz**
   - Amplitude: **0.5 m/s**
3. Observe o movimento de vai e vem no eixo X

### **Exemplo 2: Movimento Lento**
1. Habilite a **Esfera 2 (Vermelha)**
2. Configure:
   - Frequência: **0.1 Hz** (1 ciclo a cada 10 segundos)
   - Amplitude: **0.3 m/s**
3. Observe o movimento suave e lento

### **Exemplo 3: Movimento Rápido**
1. Habilite a **Esfera 3 (Azul)**
2. Configure:
   - Frequência: **5.0 Hz** (5 ciclos por segundo)
   - Amplitude: **0.8 m/s**
3. Observe o movimento rápido de vibração

### **Exemplo 4: Padrão Sincronizado**
1. Clique em **"Iniciar Todas (1 Hz)"**
2. Todas as esferas começam a oscilar em sincronia
3. Clique em **"Sincronizar Fase"** para resetar a fase
4. Ajuste amplitudes diferentes para cada esfera:
   - Esfera 1: 0.3 m/s
   - Esfera 2: 0.5 m/s
   - Esfera 3: 0.7 m/s

### **Exemplo 5: Frequências Diferentes**
1. Habilite todas as 3 esferas
2. Configure frequências diferentes:
   - Esfera 1: **0.5 Hz**
   - Esfera 2: **1.0 Hz**
   - Esfera 3: **2.0 Hz**
3. Observe o padrão complexo de movimento

---

## 🔬 Detalhes Técnicos

### **Função de Oscilação**
```python
velocity = amplitude * sin(2π * frequency * time)
```

### **Taxa de Atualização**
- A GUI atualiza as velocidades a cada **50ms** (20 Hz)
- Isso garante movimento suave mesmo em altas frequências

### **Limites de Movimento**
- Cada esfera pode se mover **±2 metros** em seu eixo
- Se a esfera atingir o limite, o Gazebo impedirá movimento adicional
- Para evitar isso, ajuste a amplitude e frequência adequadamente

### **Cálculo de Deslocamento**
Para uma frequência **f** e amplitude **A**, o deslocamento máximo é aproximadamente:
```
Deslocamento_max ≈ A / (2π × f)
```

Exemplos:
- **f = 1 Hz, A = 0.5 m/s**: ~0.08 m (8 cm)
- **f = 0.1 Hz, A = 0.5 m/s**: ~0.8 m (80 cm)
- **f = 10 Hz, A = 0.5 m/s**: ~0.008 m (8 mm)

---

## ⚠️ Observações Importantes

1. **Sincronização de Fase**:
   - Use o botão "Sincronizar Fase" para alinhar todas as oscilações
   - Útil após ajustar frequências

2. **Limites Físicos**:
   - As esferas têm limites de ±2m no SDF
   - Frequências muito baixas com amplitudes altas podem atingir os limites

3. **Performance**:
   - Frequências acima de 5 Hz podem causar comportamento instável
   - Recomendado: 0.1 Hz a 5 Hz para movimento suave

4. **Movimento Senoidal**:
   - A velocidade varia suavemente de -A a +A
   - Velocidade zero nos extremos do movimento
   - Velocidade máxima no centro

---

## 🎨 Interface Visual

```
┌─────────────────────────────────────────────────────┐
│  Esfera 1 (Verde - Eixo X)                          │
│  ☑ Habilitar Oscilação                              │
│  Frequência (Hz):  [━━━━━━━━━━] [1.00]              │
│  Amplitude (m/s):  [━━━━━━━━━━] [0.50]              │
│  Status: Oscilando (1.00 Hz)                        │
├─────────────────────────────────────────────────────┤
│  Esfera 2 (Vermelha - Eixo Y)                       │
│  ☐ Habilitar Oscilação                              │
│  Frequência (Hz):  [━━━━━━━━━━] [1.00]              │
│  Amplitude (m/s):  [━━━━━━━━━━] [0.50]              │
│  Status: Parado                                     │
├─────────────────────────────────────────────────────┤
│  Esfera 3 (Azul - Eixo Z)                           │
│  ☐ Habilitar Oscilação                              │
│  Frequência (Hz):  [━━━━━━━━━━] [1.00]              │
│  Amplitude (m/s):  [━━━━━━━━━━] [0.50]              │
│  Status: Parado                                     │
├─────────────────────────────────────────────────────┤
│  Controles Globais                                  │
│  [Iniciar Todas] [Parar Todas] [Sincronizar Fase]  │
├─────────────────────────────────────────────────────┤
│  [Sair]                                             │
└─────────────────────────────────────────────────────┘
```

---

## 📝 Changelog

### Versão 2.0 (05/12/2025)
- ✅ Reescrita completa para movimento oscilatório
- ✅ Controle de frequência (0.1 - 10 Hz)
- ✅ Controle de amplitude (0.01 - 1.0 m/s)
- ✅ Movimento senoidal suave
- ✅ Sincronização de fase
- ✅ Atualização em tempo real (20 Hz)

### Versão 1.0 (Anterior)
- ❌ Controle de rotação (obsoleto)
- ❌ Velocidade angular em rad/s

---

## 🆘 Solução de Problemas

### **Esferas não se movem**
1. Verifique se a simulação está rodando
2. Confirme que o checkbox está marcado
3. Verifique se a amplitude não é zero

### **Movimento irregular**
1. Reduza a frequência (< 5 Hz)
2. Verifique se o Gazebo não está sobrecarregado
3. Reinicie a simulação

### **Esferas param nos limites**
1. Reduza a amplitude
2. Aumente a frequência
3. Use o botão "Sincronizar Fase" para resetar

---

**Desenvolvido por**: Jhoni  
**Data**: 05/12/2025  
**Versão**: 2.0
