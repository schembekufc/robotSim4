#!/usr/bin/env python3
import sys
import math
import numpy as np
import struct

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QGroupBox, QGridLayout, QLabel, QProgressBar,
    QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

# Gazebo Transport
try:
    from gz.transport13 import Node
    from gz.msgs10.image_pb2 import Image
    from gz.msgs10.pose_v_pb2 import Pose_V
    from gz.msgs10.light_pb2 import Light
except ImportError:
    print("ERRO: Instale as dependencias do Gazebo Transport (python3-gz-transport13, etc)")
    sys.exit(1)

WORLD_NAME = "three_link_with_tracker_plate_world"
# Tópico da câmera definido no SDF
CAMERA_TOPIC = "parabolic_dish/focus_cam/image"
# Tópico de poses (padrão do Gazebo Sim)
POSE_TOPIC = f"/world/{WORLD_NAME}/pose/info"
# Tópico de configuração de luz (para saber a direção do sol)
LIGHT_TOPIC = f"/world/{WORLD_NAME}/light_config"

def quaternion_to_rotation_matrix(q):
    """Converte quaternion (w, x, y, z) para matriz de rotação 3x3."""
    w, x, y, z = q.w, q.x, q.y, q.z
    return np.array([
        [1 - 2*y*y - 2*z*z,     2*x*y - 2*z*w,     2*x*z + 2*y*w],
        [    2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z,     2*y*z - 2*x*w],
        [    2*x*z - 2*y*w,     2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y]
    ])

class LightSensorGUI(QWidget):
    # Sinais para atualizar a GUI a partir de threads de callback
    update_sensor_signal = pyqtSignal(float)
    update_math_signal = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensor de Foco - Prato Parabólico")
        
        self.node = Node()
        
        # Estado
        self.sensor_value = 0.0
        self.dot_product = 0.0
        
        # Direção do sol padrão (0, 0, -1) -> Vetor apontando para baixo
        # Vetor DO sol (para cálculo de incidência) seria (0, 0, -1)
        # Mas para produto escalar com a normal, queremos o vetor QUE APONTA PARA O SOL.
        # Se a luz vem de (0,0,100) e aponta (0,0,-1), o vetor PARA o sol é (0,0,1).
        self.sun_vector = np.array([0.0, 0.0, 1.0]) 
        
        self.dish_normal = np.array([0.0, 0.0, 1.0]) # Normal local do prato (+Z)

        self.init_ui()
        
        # Subscribers
        self.node.subscribe(Image, CAMERA_TOPIC, self.on_image)
        self.node.subscribe(Pose_V, POSE_TOPIC, self.on_pose)
        # Monitorar mudanças na luz (se o usuário usar o outro script)
        self.node.subscribe(Light, LIGHT_TOPIC, self.on_light)

        self.update_sensor_signal.connect(self.update_sensor_ui)
        self.update_math_signal.connect(self.update_math_ui)

    def init_ui(self):
        layout = QVBoxLayout()

        # Grupo Sensor (Câmera)
        group_cam = QGroupBox("Sensor de Luminosidade (Câmera)")
        layout_cam = QVBoxLayout()
        
        self.lbl_sensor = QLabel("Intensidade Média: 0.00")
        self.lbl_sensor.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout_cam.addWidget(self.lbl_sensor)
        
        self.bar_sensor = QProgressBar()
        self.bar_sensor.setRange(0, 255)
        self.bar_sensor.setValue(0)
        self.bar_sensor.setStyleSheet("QProgressBar::chunk { background-color: #FFA500; }") # Laranja
        layout_cam.addWidget(self.bar_sensor)
        
        group_cam.setLayout(layout_cam)
        layout.addWidget(group_cam)

        # Grupo Matemático
        group_math = QGroupBox("Cálculo Matemático")
        layout_math = QVBoxLayout()
        
        # Alinhamento (Dot Product)
        self.lbl_math = QLabel("Alinhamento (Dot): 0.000")
        self.lbl_math.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout_math.addWidget(self.lbl_math)
        
        self.bar_math = QProgressBar()
        self.bar_math.setRange(0, 100)
        self.bar_math.setValue(0)
        self.bar_math.setStyleSheet("QProgressBar::chunk { background-color: #00BFFF; }") # Azul
        layout_math.addWidget(self.bar_math)

        # Desvio (Graus)
        self.lbl_deg = QLabel("Desvio: 0.00°")
        self.lbl_deg.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout_math.addWidget(self.lbl_deg)

        self.bar_deg = QProgressBar()
        self.bar_deg.setRange(0, 100) # 0 a 100%
        self.bar_deg.setValue(0)
        self.bar_deg.setAlignment(Qt.AlignCenter)
        # Fundo branco, barra verde (invertido: 100% = 0°, 0% = ≥5°)
        self.bar_deg.setStyleSheet("""
            QProgressBar {
                background-color: white; 
                border: 1px solid grey;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #32CD32; 
            }
        """) 
        layout_math.addWidget(self.bar_deg)
        
        group_math.setLayout(layout_math)
        layout.addWidget(group_math)
        
        # Info
        self.lbl_info = QLabel("Aguardando dados do Gazebo...")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_info)

        self.setLayout(layout)
        self.resize(400, 400)

    def on_image(self, msg: Image):
        """Callback da câmera."""
        width = msg.width
        height = msg.height
        # Assumindo R8G8B8 (3 bytes por pixel)
        # Dados brutos
        data = msg.data
        
        if not data:
            return

        # Converter para numpy array
        # A imagem pode vir como bytes.
        try:
            # R8G8B8
            arr = np.frombuffer(data, dtype=np.uint8)
            
            # Calcular média simples de todos os canais (intensidade global)
            avg_intensity = np.mean(arr)
            
            self.sensor_value = avg_intensity
            self.update_sensor_signal.emit(avg_intensity)
            
        except Exception as e:
            print(f"Erro ao processar imagem: {e}")

    def on_pose(self, msg: Pose_V):
        """Callback de poses para encontrar a orientação do prato."""
        # Procurar pelo link do prato
        # A estrutura do Pose_V lista poses de modelos.
        # Se os links forem publicados, eles aparecem com nomes tipo "three_link_model::link_parabolic_dish" ou similar,
        # dependendo da versão do Gazebo.
        # Vamos tentar encontrar algo que contenha "parabolic_dish" ou "link3" se o prato for fixo nele.
        
        found = False
        dish_rotation_matrix = np.eye(3)

        for p in msg.pose:
            # O nome pode ser "three_link_model" (se quisermos a base) ou o link específico.
            # Em gz-sim, geralmente links individuais têm nomes completos.
            if "link_parabolic_dish" in p.name:
                dish_rotation_matrix = quaternion_to_rotation_matrix(p.orientation)
                found = True
                break
        
        # Fallback: Se não achar o link específico, tenta o link3
        if not found:
            for p in msg.pose:
                if "link3" in p.name:
                    dish_rotation_matrix = quaternion_to_rotation_matrix(p.orientation)
                    found = True
                    break
        
        if found:
            # Normal do prato no frame local é +Z (0, 0, 1)
            local_normal = np.array([0, 0, 1])
            # Normal no frame global
            global_normal = dish_rotation_matrix.dot(local_normal)
            
            # Produto escalar com o vetor do sol
            # Sun vector aponta PARA o sol. Normal aponta PARA FORA do prato.
            # Se estiverem alinhados, dot = 1.
            dot_raw = np.dot(global_normal, self.sun_vector)
            
            # Clamp entre 0 e 1 (não consideramos luz vindo de trás do prato para o sensor de alinhamento)
            dot_clamped = max(0.0, dot_raw)
            
            self.dot_product = dot_clamped
            self.update_math_signal.emit(dot_clamped)
            
            self.lbl_info.setText(f"Prato detectado!")

    def on_light(self, msg: Light):
        """Callback para mudanças na luz (sol)."""
        # A mensagem Light tem 'direction'.
        # Se direction for (0, 0, -1), a luz aponta para baixo.
        # O vetor PARA o sol é o oposto da direção da luz.
        d = msg.direction
        # Normalizar e inverter
        vec = np.array([-d.x, -d.y, -d.z])
        norm = np.linalg.norm(vec)
        if norm > 0:
            self.sun_vector = vec / norm

    def update_sensor_ui(self, value):
        self.lbl_sensor.setText(f"Intensidade Média: {value:.2f}")
        self.bar_sensor.setValue(int(value))

    def update_math_ui(self, value):
        # Value é o dot product (0 a 1)
        self.lbl_math.setText(f"Alinhamento (Dot): {value:.3f}")
        
        # Calcular graus primeiro para usar na lógica da barra
        angle_rad = np.arccos(np.clip(value, 0.0, 1.0))
        angle_deg = np.degrees(angle_rad)

        # Mostrar valor real sem arredondamento
        self.bar_math.setValue(int(value * 100))
            
        self.lbl_deg.setText(f"Desvio: {angle_deg:.4f}°")
        
        # Inverter a barra: 0° = 100%, 5° ou mais = 0%
        if angle_deg >= 5.0:
            bar_value = 0
        else:
            # Interpolar linearmente: 0° → 100%, 5° → 0%
            bar_value = int(100 * (1 - angle_deg / 5.0))
        
        self.bar_deg.setValue(bar_value)
        self.bar_deg.setFormat(f"{angle_deg:.4f}°")

def main():
    app = QApplication(sys.argv)
    gui = LightSensorGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
