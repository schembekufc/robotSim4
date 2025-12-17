# Metodologia de Análise Modal da Estrutura do Refletor

Esta seção detalha a metodologia analítica empregada para estimar as frequências naturais de vibração da estrutura do prato parabólico do robô. Dado que o refletor é o componente de maior inércia e área aerodinâmica, sua rigidez estrutural é crítica para a precisão do apontamento.

## 1. Definição do Modelo Físico

A análise considera o refletor como uma estrutura híbrida composta por dois elementos principais:
1.  **Pele (Skin):** Superfície parabólica feita de compósito de fibra de vidro com resina epóxi.
2.  **Esqueleto de Reforço (Ribs):** Estrutura traseira composta por varetas radiais de alumínio, destinadas a aumentar a rigidez à flexão sem adicionar massa excessiva.

### 1.1. Parâmetros dos Materiais e Geometria

Para a simulação numérica, foram adotados os seguintes parâmetros conservadores:

**Tabela 1: Propriedades dos Materiais**

| Componente | Material | Módulo de Young ($E$) | Densidade ($\rho$) | Poisson ($\nu$) |
| :--- | :--- | :--- | :--- | :--- |
| Pele do Prato | Fibra de Vidro | 30 GPa | 1900 kg/m³ | 0.28 |
| Estrutura de Reforço | Alumínio 6061-T6 | 68.9 GPa | 2700 kg/m³ | 0.33 |

**Tabela 2: Geometria da Estrutura**

| Parâmetro | Valor | Descrição |
| :--- | :--- | :--- |
| Raio ($R$) | 1.5 m | Diâmetro total de 3.0 m |
| Espessura da Pele ($h_{skin}$) | 10 mm | Espessura média da fibra de vidro |
| Quantidade de Reforços | 8 | Varetas radiais uniformemente espaçadas |
| Seção Transversal Reforço | $50 \times 100$ mm | Perfil retangular sólido (Base x Altura) |

## 2. Modelo Matemático (Método de Rayleigh)

Para determinar a frequência fundamental de vibração ($\omega_n$), utilizou-se o **Método de Rayleigh (Quociente de Rayleigh)**. Este método energético iguala a energia potencial máxima ($U_{max}$) à energia cinética máxima ($T_{ref}^*$) de um sistema conservativo oscilando em um modo natural assumido.

$$ \omega_n^2 = \frac{U_{max}}{T_{ref}^*} $$

### 2.1. Função de Forma Assumida
Assumiu-se que o modo de vibração fundamental se comporta como uma deformação simétrica radial ("Modo Guarda-Chuva"), engastada no centro e livre nas bordas. A função de deflexão vertical $w(r)$ foi aproximada por uma função quadrática:

$$ w(r) = \delta_{tip} \left( \frac{r}{R} \right)^2 $$

Onde $\delta_{tip}$ é a deflexão máxima na borda do prato.

### 2.2. Energia Potencial Elástica ($U$)
A energia potencial total é a soma da energia de deformação da placa e das vigas de reforço.

$$ U_{total} = U_{placa} + \sum U_{viga} $$

Para a placa com rigidez à flexão $D = \frac{Eh^3}{12(1-\nu^2)}$, e para as vigas com rigidez $EI$, a rigidez equivalente ($K_{eq}$) aproximada foi calculada integrando a curvatura $\kappa \approx w''(r)$ ao longo do raio.

### 2.3. Energia Cinética Equivalente ($T$)
A energia cinética considera a massa efetiva que participa do movimento. Devido à forma do modo (maior amplitude na ponta), a massa perto do centro contribui menos para a inércia dinâmica.

$$ M_{eq} = \int \rho(r) [ \phi(r) ]^2 dV $$

Para o perfil parabólico de deformação assumido, determinou-se analiticamente que:
*   Massa Efetiva da Placa $\approx \frac{1}{3} M_{placa}$
*   Massa Efetiva das Vigas $\approx \frac{1}{5} M_{viga}$

## 3. Implementação Computacional

O cálculo foi automatizado utilizando um script em Python para permitir rápida iteração de parâmetros de projeto. O código abaixo apresenta a implementação da metodologia descrita.

```python
import numpy as np
import math

class StructuralAnalysis:
    def __init__(self):
        # Materiais e Geometria definidos conforme Tabela 1 e 2
        self.E_glass = 30e9       
        self.rho_glass = 1900     
        self.nu_glass = 0.28      
        self.E_al = 68.9e9        
        self.rho_al = 2700        
        self.R = 1.5              
        self.h_skin = 0.01        
        self.num_ribs = 8         
        self.rib_width = 0.05     
        self.rib_height = 0.10    
        self.L_rib = self.R       

    def calculate_properties(self):
        # ... cálculo de massas e inércias de área (I = bh^3/12) ...
        # (Ver código completo nos apêndices)
        pass

    def run_rayleigh_analysis(self):
        # Rigidez Equivalente das Varetas (Beams)
        # K_rib = (4 * E * I) / L^3 (Derivado da integral de energia para w=r^2)
        self.K_rib_eq = (4 * self.E_al * self.I_rib) / (self.L_rib**3)
        
        # Rigidez Equivalente da Placa
        self.K_plate_eq = 16 * np.pi * self.D_plate / (self.R**2)
        
        self.K_total = self.K_plate_eq + (self.num_ribs * self.K_rib_eq)
        
        # Massas Equivalentes Dinâmicas
        self.M_eq_plate = self.mass_skin / 3.0
        self.M_eq_ribs = (self.mass_one_rib * self.num_ribs) / 5.0
        self.M_total_eq = self.M_eq_plate + self.M_eq_ribs
        
        # Frequência Natural
        self.omega_n = math.sqrt(self.K_total / self.M_total_eq)
        return self.omega_n / (2 * math.pi)
```

## 4. Resultados e Discussão

A aplicação do modelo analítico gerou os seguintes resultados para a estrutura proposta:

*   **Massa Total do Conjunto:** 303.02 kg
*   **Rigidez Dinâmica Equivalente:** $2.78 \times 10^6$ N/m
*   **Massa Dinâmica Equivalente:** 79.41 kg

O resultado final para a frequência natural fundamental foi:

$$ f_n \approx 29.79 \text{ Hz} $$

### Interpretação
O valor de aprox. **30 Hz** indica uma estrutura robusta para aplicações de rastreamento solar, estando bem acima das frequências típicas de controle de malha fechada (geralmente < 5 Hz) e das excitações eólicas comuns (< 1 Hz).

A análise demonstra que a inclusão das nervuras de alumínio é fundamental. Sem elas, a frequência natural da pele de fibra de vidro seria inferior a 5 Hz, o que resultaria em ressonância e instabilidade sob carga de vento.
