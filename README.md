# 🤖 Robot Simulation 4 - Gazebo Tracker Plate

Simulação de uma placa rastreadora solar com 3 links e sensores de luz no Gazebo.

## 📋 Descrição

Este projeto implementa uma simulação de um sistema de rastreamento solar usando Gazebo. O sistema inclui:

- **Placa rastreadora** com 3 links articulados
- **4 câmeras/sensores de luz** posicionados em quadrantes (Q1, Q2, Q3, Q4)
- **Prato parabólico** com espelho
- **Esferas rotativas** controladas por juntas
- **Interfaces gráficas (GUIs)** para controle e monitoramento

## 🚀 Funcionalidades

### Arquivos Principais

- `three_link_with_tracker_plate.sdf` - Modelo SDF da simulação
- `plate_light_gui_images.py` - GUI para monitorar 4 câmeras e calcular erro de rastreamento
- `tracker_auto_control_gui.py` - Controle automático do rastreador
- `unified_control_gui.py` - Interface unificada de controle
- `light_sensor_gui.py` - Monitoramento de sensores de luz
- `sun_control_gui.py` - Controle da posição do sol
- `balls_control_gui.py` - Controle das esferas rotativas

### Utilitários

- `generate_parabolic_dish.py` - Geração de malha do prato parabólico
- `calculate_dish_inertia.py` - Cálculo de inércia do prato
- `generate_lens_mask.py` - Geração de máscara para lente
- `fix_mesh.py` / `fix_mesh_trimesh.py` - Correção de malhas 3D

## 🛠️ Requisitos

```bash
# Gazebo Garden (ou superior)
sudo apt install gz-garden

# Python 3 e dependências
sudo apt install python3-pip
sudo apt install python3-gz-transport13 python3-gz-msgs10

# PyQt5 para interfaces gráficas
pip3 install PyQt5

# NumPy para processamento de dados
pip3 install numpy
```

## 📖 Como Usar

### 1. Iniciar a Simulação

```bash
gz sim three_link_with_tracker_plate.sdf
```

### 2. Executar a GUI de Monitoramento

```bash
python3 plate_light_gui_images.py
```

### 3. Controle Automático (opcional)

```bash
python3 tracker_auto_control_gui.py
```

## 📊 Sistema de Rastreamento

O sistema usa 4 câmeras posicionadas em quadrantes para detectar a direção da luz:

- **Q1** (+x, +y): Superior direito - Vermelho
- **Q2** (-x, +y): Superior esquerdo - Verde
- **Q3** (-x, -y): Inferior esquerdo - Azul
- **Q4** (+x, -y): Inferior direito - Amarelo

### Cálculo de Erro

- **err_x** = (Q1 + Q4)/2 - (Q2 + Q3)/2
- **err_y** = (Q1 + Q2)/2 - (Q3 + Q4)/2

Quando todos os quadrantes recebem luminância igual, a placa está perfeitamente alinhada com a fonte de luz.

## 📁 Estrutura do Projeto

```
robotSim4/
├── three_link_with_tracker_plate.sdf  # Modelo principal
├── plate_light_gui_images.py          # GUI de monitoramento
├── tracker_auto_control_gui.py        # Controle automático
├── unified_control_gui.py             # Interface unificada
├── formas/                            # Malhas 3D
│   └── Espelho.dae                    # Prato parabólico
├── lens_mask.obj                      # Máscara da lente
└── README.md                          # Este arquivo
```

## 🎯 Objetivos do Projeto

- Simular rastreamento solar passivo
- Testar algoritmos de controle
- Visualizar dados de sensores em tempo real
- Desenvolver interfaces de usuário intuitivas

## 📝 Licença

Este projeto é de uso educacional e acadêmico.

## 👤 Autor

Desenvolvido como parte de pesquisa em sistemas de rastreamento solar.
