# 🔧 Correções Aplicadas - Esferas Oscilatórias

## ✅ Modificações Realizadas (05/12/2025)

### **1. Aumento dos Limites de Movimento (SDF)**

#### **Antes:**
- Limites: **±2 metros**
- Velocidade máxima: **1.0 m/s**
- Esforço: **100 N**

#### **Depois:**
- Limites: **±30 metros** ✅
- Velocidade máxima: **30.0 m/s** ✅
- Esforço: **1000 N** ✅

```xml
<limit>
  <lower>-30.0</lower>  <!-- Era -2.0 -->
  <upper>30.0</upper>   <!-- Era 2.0 -->
  <velocity>30.0</velocity>  <!-- Era 1.0 -->
  <effort>1000</effort>  <!-- Era 100 -->
</limit>
```

---

### **2. Remoção de Colisões das Esferas**

**Problema identificado:** A esfera azul (eixo Z) colidia com o chão e parava.

**Solução:** Removidas todas as tags `<collision>` das 3 esferas.

#### **Esfera 1 (Verde - Eixo X):**
```xml
<link name="link_sphere_1">
  <visual name="sphere_1_visual">
    <!-- geometria e material -->
  </visual>
  
  <!-- SEM COLISÃO -->
</link>
```

#### **Esfera 2 (Vermelha - Eixo Y):**
```xml
<link name="link_sphere_2">
  <visual name="sphere_2_visual">
    <!-- geometria e material -->
  </visual>
  
  <!-- SEM COLISÃO -->
</link>
```

#### **Esfera 3 (Azul - Eixo Z):**
```xml
<link name="link_sphere_3">
  <visual name="sphere_3_visual">
    <!-- geometria e material -->
  </visual>
  
  <!-- SEM COLISÃO -->
</link>
```

**Resultado:** As esferas agora atravessam todos os objetos (incluindo o chão) sem parar.

---

### **3. Aumento da Amplitude na GUI**

#### **Antes:**
- Amplitude mínima: **0.01 m/s**
- Amplitude máxima: **1.0 m/s**
- Valor padrão: **0.5 m/s**

#### **Depois:**
- Amplitude mínima: **0.1 m/s**
- Amplitude máxima: **30.0 m/s** ✅
- Valor padrão: **5.0 m/s** ✅

```python
# Slider: 1-300 (representa 0.1-30.0 m/s)
self.slider_amp1.setMinimum(1)     # 0.1 m/s
self.slider_amp1.setMaximum(300)   # 30.0 m/s
self.slider_amp1.setValue(50)      # 5.0 m/s

# SpinBox
self.spin_amp1.setRange(0.1, 30.0)
self.spin_amp1.setValue(5.0)
```

---

## 📊 Comparação: Antes vs Depois

| Parâmetro | Antes | Depois | Mudança |
|-----------|-------|--------|---------|
| **Limite de movimento** | ±2m | ±30m | **15x maior** |
| **Velocidade máxima (SDF)** | 1.0 m/s | 30.0 m/s | **30x maior** |
| **Amplitude máxima (GUI)** | 1.0 m/s | 30.0 m/s | **30x maior** |
| **Amplitude padrão (GUI)** | 0.5 m/s | 5.0 m/s | **10x maior** |
| **Colisões** | Sim | **Não** | Removidas |
| **Esforço da junta** | 100 N | 1000 N | **10x maior** |

---

## 🎯 Impacto das Mudanças

### **Movimento Muito Maior**
Com limites de ±30m, as esferas podem se mover muito mais longe:

**Exemplo com frequência 0.1 Hz e amplitude 30 m/s:**
```
Deslocamento máximo ≈ A / (2π × f)
                    ≈ 30 / (2π × 0.1)
                    ≈ 47.7 metros!
```

### **Sem Colisão com o Chão**
A esfera azul (eixo Z) agora pode descer livremente sem parar no chão:
- ✅ Movimento contínuo
- ✅ Não para em Z = 0
- ✅ Atravessa o chão sem problemas

### **Velocidades Muito Maiores**
Com amplitude de 30 m/s, o movimento é muito mais rápido e visível.

---

## 🧪 Testes Recomendados

### **Teste 1: Movimento Extremo**
```
Esfera 1 (Verde - X):
- Frequência: 0.1 Hz
- Amplitude: 30.0 m/s
- Resultado esperado: Movimento de ~48m de um lado para o outro
```

### **Teste 2: Esfera Azul (Problema Corrigido)**
```
Esfera 3 (Azul - Z):
- Frequência: 0.5 Hz
- Amplitude: 10.0 m/s
- Resultado esperado: Movimento vertical contínuo, atravessando o chão
```

### **Teste 3: Alta Frequência**
```
Todas as esferas:
- Frequência: 5.0 Hz
- Amplitude: 20.0 m/s
- Resultado esperado: Vibração rápida com grande amplitude
```

---

## ⚠️ Observações Importantes

### **1. Esferas Invisíveis**
Com limites de ±30m, as esferas podem sair completamente do campo de visão da câmera. Use a câmera do Gazebo para seguir o movimento.

### **2. Performance**
Amplitudes muito altas (>20 m/s) com frequências altas (>5 Hz) podem causar instabilidade na simulação.

### **3. Valores Recomendados**
Para movimento estável e visível:
- **Frequência**: 0.5 - 2.0 Hz
- **Amplitude**: 5.0 - 15.0 m/s
- **Deslocamento resultante**: 1-5 metros

### **4. Sem Colisão = Sem Física Realista**
As esferas agora são puramente visuais e atravessam tudo. Se precisar de física realista no futuro, será necessário reativar as colisões.

---

## 🔍 Detalhes Técnicos

### **Cálculo de Deslocamento**
Para uma oscilação senoidal:
```
v(t) = A × sin(2π × f × t)
x(t) = -A/(2πf) × cos(2π × f × t)

Deslocamento máximo = A / (2πf)
```

### **Exemplos Práticos**

| Frequência | Amplitude | Deslocamento Máx | Período |
|------------|-----------|------------------|---------|
| 0.1 Hz | 30 m/s | ~47.7 m | 10 s |
| 0.5 Hz | 20 m/s | ~6.4 m | 2 s |
| 1.0 Hz | 10 m/s | ~1.6 m | 1 s |
| 2.0 Hz | 5 m/s | ~0.4 m | 0.5 s |
| 5.0 Hz | 30 m/s | ~0.95 m | 0.2 s |

---

## 📝 Commit Git

```bash
Commit: 0493eb4
Mensagem: Increase sphere limits to ±30m, velocity to 30 m/s, 
          remove collisions, fix blue sphere

Arquivos modificados:
- 01_three_link_with_tracker_plate.sdf
- 05_balls_control_gui.py

Mudanças: +48 -42 linhas
```

---

## 🚀 Como Testar

```bash
# 1. Carregar a simulação
gz sim 01_three_link_with_tracker_plate.sdf

# 2. Executar a GUI
python3 05_balls_control_gui.py

# 3. Testar esfera azul (problema corrigido):
#    - Marque "Habilitar Oscilação" para Esfera 3 (Azul)
#    - Frequência: 0.5 Hz
#    - Amplitude: 10.0 m/s
#    - Observe: A esfera desce, atravessa o chão, e volta!
```

---

**Todas as correções foram aplicadas com sucesso!** ✅

**Data**: 05/12/2025  
**Autor**: Jhoni
