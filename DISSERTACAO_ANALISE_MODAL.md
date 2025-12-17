# Análise Modal Estrutural do Manipulador Robótico

## 1. Introdução

Este capítulo apresenta a análise de vibração e rigidez estrutural do manipulador robótico desenvolvido para rastreamento solar. O objetivo é determinar as frequências naturais dos principais componentes mecânicos para garantir que o sistema não entre em ressonância durante a operação de rastreamento e suporte as cargas estáticas e dinâmicas, especialmente a ação do vento.

O sistema é analisado como uma estrutura de múltiplos corpos interconectados, onde cada subsistema (Torre, Braço, Refletor) possui propriedades elásticas específicas baseadas em seus materiais e geometria.

## 2. Definição do Modelo Analítico

Para a análise, o robô foi decomposto em três subsistemas principais, modelados analiticamente utilizando teorias de resistência dos materiais e dinâmica estrutural clássica (Método de Rayleigh e Aproximação de Viga de Euler-Bernoulli com Massa Concentrada).

### 2.1. Propriedades dos Materiais

Foram considerados três materiais distintos na construção do robô, conforme a função de cada componente:

**Tabela 1: Propriedades Físicas dos Materiais Adotados**

| Material | Aplicação | Módulo de Elasticidade ($E$) | Densidade ($\rho$) | Coef. de Poisson ($\nu$) |
| :--- | :--- | :--- | :--- | :--- |
| **Aço ASTM A36** | Estrutura da Torre e Braço | 200 GPa | 7850 kg/m³ | 0.26 |
| **Alumínio 6061-T6** | Costelas de Reforço do Prato | 68.9 GPa | 2700 kg/m³ | 0.33 |
| **Fibra de Vidro/Epóxi** | Superfície do Refletor | 30 GPa | 1900 kg/m³ | 0.28 |

### 2.2. Modelo do Refletor Parabólico (Subsistema 1)
O refletor é o componente de maior área e inércia. Foi modelado como uma estrutura híbrida composta por uma "pele" de fibra de vidro de 10 mm de espessura, reforçada por **6 costelas radiais** de alumínio (seção $50 \times 100$ mm).

*   **Método de Análise:** Método de Energia de Rayleigh assumindo modo de deformação radial quadrático ("Guarda-chuva").

### 2.3. Modelo do Braço de Elevação (Subsistema 2)
O braço que sustenta o refletor foi modelado como uma **viga engastada-livre (cantilever)** sujeita a flexão, com uma grande massa concentrada na ponta (representando o peso do refletor).

*   **Geometria:** Tubo retangular de Aço ($150 \times 200$ mm), espessura de parede 6 mm, comprimento 2.0 m.
*   **Carga na Ponta:** Massa do Refletor (~265 kg).

### 2.4. Modelo da Torre Base (Subsistema 3)
A torre foi modelada como uma viga curta e robusta engastada no solo, suportando a massa de todo o conjunto superior (Braço + Refletor).

*   **Geometria:** Tubo quadrado de Aço ($300 \times 300$ mm), espessura de parede 8 mm, altura 1.3 m.

## 3. Resultados da Simulação Numérica

Utilizando um script computacional desenvolvido em Python para automatizar os cálculos do modelo analítico descrito, obtiveram-se os seguintes resultados:

### 3.1. Análise Individual dos Componentes

**Tabela 2: Resultados da Análise Modal por Subsistema**

| Subsistema | Massa Própria | Carga Suportada | Rigidez Equivalente ($k_{eq}$) | Frequência Natural ($f_n$) |
| :--- | :--- | :--- | :--- | :--- |
| **Refletor** (Prato) | 169.2 kg (Real) | N/A | $2.31 \times 10^6$ N/m | **14.76 Hz** |
| **Braço de Elevação** | 63.7 kg | 174.2 kg | $1.77 \times 10^6$ N/m | **15.38 Hz** |
| **Torre da Base** | 95.4 kg | 257.9 kg | $17.5 \times 10^6$ N/m | **57.22 Hz** |

### 3.2. Discussão dos Modos de Vibração

A análise atualizada com a massa real da estrutura de reforço (obtida via CAD) revela um sistema mais equilibrado e leve:

1.  **Modo Estrutural Global (~15 Hz):** Observa-se um acoplamento interessante entre o modo de vibração do prato (14.76 Hz) e do braço (15.38 Hz). Como as frequências são muito próximas, é provável que ocorra uma interação dinâmica onde a vibração do braço excite a ressonância do prato e vice-versa. Para o controle, isso significa que existe uma "zona proibida" clara em torno de 15 Hz que deve ser evitada pelos filtros notch do controlador.

2.  **Benefício da Redução de Massa:** A utilização de costelas leves (28 kg no total, em vez de perfis maciços) permitiu reduzir a carga na ponta do braço em quase 100 kg. Isso elevou a frequência natural do braço de ~12 Hz (estimativa anterior) para 15.38 Hz, melhorando a largura de banda disponível para o controle.

3.  **Torre Robusta:** A torre mantém-se como um componente extremamente rígido (> 50 Hz), garantindo uma base estável para o apontamento preciso.

## 4. Conclusão da Análise

A estrutura projetada em aço com refletor híbrido apresenta frequências naturais acima de 12 Hz. Considerando que os distúrbios ambientais (vento) possuem espectro de energia concentrado abaixo de 1 Hz, e que o rastreamento solar é um processo lento (quase-estático), a estrutura é considerada **dinamicamente estável e apta para a aplicação**, desde que os controladores dos motores sejam sintonizados para não excitar a frequência de ressonância do braço (12.6 Hz).

---
## Apêndice: Código Computacional

Abaixo segue o código Python utilizado para gerar os resultados apresentados:

*(O código completo do arquivo `full_robot_vibration_analysis.py` pode ser inserido aqui)*
