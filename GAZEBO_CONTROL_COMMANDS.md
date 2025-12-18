# Comandos de Controle do Robô via Terminal (Gazebo)

Este documento lista comandos úteis para controlar as juntas do robô diretamente pelo terminal, utilizando a ferramenta `gz topic`.

Certifique-se de que a simulação esteja rodando antes de executar os comandos.

## 1. Listar tópicos disponíveis
Para confirmar os nomes exatos dos tópicos:
```bash
gz topic -l | grep cmd_pos
```

## 2. Controle de Posição (Joint Position Controller)
A sintaxe correta exige especificar o tipo de mensagem (`-m`) e o conteúdo (`-p`).
As unidades são em **radianos** para juntas rotativas.

### Junta Azimute (`joint_azimuth`)
*Rotação da base (Horizontal)*

**Ir para 0 graus (Reset):**
```bash
gz topic -t "/model/three_link_model/joint/joint_azimuth/cmd_pos" -m gz.msgs.Double -p "data: 0.0"
```

**Ir para 45 graus (aprox 0.785 rad):**
```bash
gz topic -t "/model/three_link_model/joint/joint_azimuth/cmd_pos" -m gz.msgs.Double -p "data: 0.785"
```

**Ir para 90 graus (aprox 1.57 rad):**
```bash
gz topic -t "/model/three_link_model/joint/joint_azimuth/cmd_pos" -m gz.msgs.Double -p "data: 1.5708"
```

**Girar sentido horário (-45 graus):**
```bash
gz topic -t "/model/three_link_model/joint/joint_azimuth/cmd_pos" -m gz.msgs.Double -p "data: -0.785"
```

### Junta Elevação (`joint_elevation`)
*Inclinação do braço (Vertical)*

**Ir para 0 graus (Horizontal):**
```bash
gz topic -t "/model/three_link_model/joint/joint_elevation/cmd_pos" -m gz.msgs.Double -p "data: 0.0"
```

**Ir para 30 graus (aprox 0.52 rad):**
```bash
gz topic -t "/model/three_link_model/joint/joint_elevation/cmd_pos" -m gz.msgs.Double -p "data: 0.523"
```

**Ir para 60 graus (aprox 1.047 rad):**
```bash
gz topic -t "/model/three_link_model/joint/joint_elevation/cmd_pos" -m gz.msgs.Double -p "data: 1.047"
```

## 3. Monitoramento
Para ver a posição atual das juntas em tempo real:
```bash
gz topic -e -t "/world/three_link_with_tracker_plate_world/model/three_link_model/joint_state"
```
