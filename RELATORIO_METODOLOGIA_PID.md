# Relatório de Ajuste de Controladores PID: Método Ziegler-Nichols
**Data:** 20 de Janeiro de 2026
**Contexto:** Sintonia de controladores para juntas robóticas (`joint_azimuth`, `joint_elevation`) em ambiente de simulação Gazebo Garden.

## 1. Objetivo
Implementar e validar uma rotina experimental para a sintonia dos controladores PID das juntas do robô espacial simulado, utilizando o método clássico de Ziegler-Nichols (Método do Ganho Crítico em Malha Fechada). O objetivo específico foi isolar a dinâmica de cada junta para identificar seus parâmetros críticos ($K_u$ e $T_u$) e calcular os ganhos ótimos.

## 2. Metodologia Aplicada

### 2.1. Preparação do Ambiente de Simulação (SDF)
Para permitir a aplicação do método de Ziegler-Nichols, o arquivo SDF (`01_three_link_with_tracker_plate.sdf`) foi modificado para transformar os controladores PID em controladores puramente proporcionais (P):
- **Ação:** Os ganhos Integral ($K_i$) e Derivativo ($K_d$) foram zerados ($I=0, D=0$).
- **Isolamento de Juntas:** Para evitar acoplamento dinâmico (forças inerciais e de Coriolis) durante os testes, procedeu-se ao isolamento mecânico das juntas:
    - Durante a sintonia da **Elevação**, a junta de **Azimute** foi convertida temporariamente para o tipo `fixed` (fixa), garantindo uma base estável e eliminando perturbações cruzadas.

### 2.2. Ferramentas de Controle e Monitoramento Desenvolvidas
Foi identificada a necessidade de ferramentas precisas para excitação do sistema (degrau) e medição da resposta oscilatória. Duas ferramentas em Python foram desenvolvidas/adaptadas:

1.  **Interface de Controle Unificado (`02_unified_control_gui.py`):**
    - Consolidou as abas de controle de sensor, rastreamento e sol em uma única visão para facilitar a operação global.

2.  **Interface de Sintonia Fina (`08_manual_position_control.py`):**
    - Desenvolvida especificamente para este experimento.
    - **Funcionalidades:**
        - Envio de setpoints de posição precisos em graus.
        - **Monitoramento em Tempo Real:** Implementação de subscrição via `gz.transport` (alta frequência) para ler o tópico `/world/.../joint_state`.
        - **Análise de Oscilação:** Exibição dos valores **Mínimo** e **Máximo** atingidos pela junta em tempo real, permitindo identificar visualmente se a amplitude da oscilação estava crescendo (Instável, $P > K_u$), diminuindo (Estável, $P < K_u$) ou constante ($P = K_u$).

### 2.3. Procedimento Experimental (Junta de Elevação)
O processo iterativo de busca pelo Ganho Crítico ($K_u$) seguiu os seguintes passos:
1.  **Definição do $K_p$ Inicial:** Iniciou-se com valores altos ($P=4000$), observando-se instabilidade.
2.  **Busca Binária/Iterativa:** Os valores foram reduzidos progressivamente (3000, 2000, 50, 25, 35) para cercar o valor crítico.
    - Observou-se que valores altos (>100) causavam oscilações divergentes rápidas.
    - Valores baixos (<25) resultavam em resposta super-amortecida (sem oscilação).
    - O intervalo de interesse para o $K_u$ foi identificado entre 25 e 50.
3.  **Critério de Parada:** Busca-se o valor de $P$ que sustenta uma oscilação de amplitude constante (limitada marginalmente pelo amortecimento natural da simulação).

### 2.4. Resultados Preliminares e Discussão de Viabilidade (20/01)
Durante os testes na junta de **Elevação**, ganhos proporcionais elevados foram testados (até $K_p = 50.000$).
- **Observação:** Mesmo com $K_p = 50.000$, a resposta manteve-se subamortecida (oscilação decrescente), indicando que o amortecimento viscoso natural da simulação (damping das juntas + física) dissipa energia eficientemente.
- **Análise de Torque Realista:**
    - Um ganho $P = 50.000$ gera um torque de $5.000 \text{ Nm}$ para um erro de apenas $0.1 \text{ rad}$ ($5.7^\circ$).
    - Motores robóticos industriais típicos possuem torques de pico na faixa de $500 - 1000 \text{ Nm}$.
    - **Conclusão:** Embora a simulação suporte ganhos altíssimos, para fins de projeto de engenharia, o ganho final será limitado não pela instabilidade numérica, mas pela saturação de torque realista.

### 2.5. Testes em Cenário Idealizado (Sem Atrito)
Para investigar se a dissipação de energia observada era proveniente dos parâmetros físicos definidos ou de artefatos numéricos, realizou-se uma rodada de testes removendo temporariamente o amortecimento e atrito da junta de elevação (`damping=0.0`, `friction=0.0` no SDF).
- **Resultado:** O sistema comportou-se como um oscilador conservativo ideal. Ganhos baixos (ex: $P=10, 50, 100$) resultaram em oscilações de amplitude constante e sustentada, sem convergência ou divergência clara.
- **Análise:** Este cenário confirmou que o modelo "sem atrito" é excessivamente idealizado para a aplicação direta do critério de estabilidade marginal de Ziegler-Nichols (onde busca-se um limiar de instabilidade), pois o sistema torna-se marginalmente estável para qualquer $K_p > 0$.
- **Decisão:** Optou-se por restaurar os parâmetros realistas de amortecimento (`damping=0.1`) e atrito (`friction=0.2`) para prosseguir com a sintonia, buscando o $K_u$ no sistema físico real, onde a instabilidade deve superar a dissipação natural.

### 2.6. Teste de Estresse Extremo e Conclusão de Estabilidade Numérica (21/01)
Em uma última tentativa de encontrar o limite de divergência oscilatória, realizou-se um teste de estresse extremo:
- **Condições:** Amortecimento e atrito zerados (`0.0`), limite de torque aumentado para $2 \times 10^6 \text{ Nm}$ (2 milhões de Nm).
- **Parâmetros de Teste:** Testes com $K_p = 500.000$ e $K_p = 1.000.000$.
- **Observação:** Surpreendentemente, mesmo nestas condições extremas, a amplitude da oscilação estabilizou-se e manteve-se constante (comportamento de ciclo limite), sem apresentar divergência exponencial.
- **Conclusão Metodológica Final:** O motor de física (Bullet/Gazebo), através de seus métodos de integração numérica, introduz uma estabilidade intrínseca que impede a "explosão" do sistema simulado mesmo sob ganhos teoricamente infinitos.
- **Definição de Projeto:** Diante da impossibilidade de identificar $K_u$ via instabilidade na simulação, o critério limitante para o ganho proporcional será definido pela **capacidade física do atuador** (motor + redutor) do projeto real, e não pelo limite de estabilidade de malha fechada. O ganho será escolhido de forma a não saturar o torque máximo especificado para o hardware.

### 2.7. Plano de Continuação Atualizado
1. Definir o torque máximo do motor real (ex: 500 Nm).
2. Calcular o ganho $K_p$ máximo que respeita esse torque para um erro típico (ex: 5 graus).
3. Utilizar este $K_p$ "físico" como base para calcular $T_i$ e $T_d$ pelos métodos analíticos ou ajuste fino por desempenho.

## 3. Embasamento Teórico Verificado
Durante a análise dos valores originais do SDF, verificou-se a consistência com a fórmula de sintonia para PIDs completos:
$$ K_i \cdot K_d = \frac{K_p^2}{4} $$
- **Junta Azimute:** Verificou-se adesão a esta relação ($P=1000, I=100, D=2500 \rightarrow 250k \approx 250k$).
- **Junta Elevação:** Identificou-se um desvio intencional no termo Integral ($I$) nos valores originais.
    - **Justificativa:** Em braços manipuladores verticais, o termo Integral calculado puramente por Z-N frequentemente é insuficiente para compensar o torque gravitacional estático (peso do braço). O ajuste manual (aumento de $K_i$) é uma prática comum e necessária para eliminar o erro em regime permanente causado pela gravidade.

## 4. Próximos Passos (Sugeridos para Dissertação)
1.  **Determinação Final:** Fixar o valor de $K_u$ e medir o período $T_u$ com a ferramenta de monitoramento.
2.  **Cálculo:** Aplicar as fórmulas da tabela clássica de Ziegler-Nichols para obter $K_p, T_i, T_d$.
3.  **Ajuste Fino:** Reintroduzir a gravidade e ajustar o ganho $K_i$ conforme necessário para sustentar o braço, documentando esse desvio da teoria como "Compensação Gravitacional".
