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
from PyQt5.QtGui import QImage, QPixmap
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
# Novo tópico da câmera do tubo
TUBE_CAMERA_TOPIC = "plate/sun_sensor/image"

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
    
    # Novo sinal para imagem (bytes, width, height, avg_intensity)
    update_image_signal = pyqtSignal(bytes, int, int, float)
    # Sinal para valores RGB do pixel central da câmera do tubo
    update_rgb_signal = pyqtSignal(int, int, int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensor de Foco - Prato Parabólico + Tubo")
        
        self.node = Node()
        
        # Estado
        self.sensor_value = 0.0
        self.dot_product = 0.0
        
        self.sun_vector = np.array([0.0, 0.0, 1.0]) 
        self.dish_normal = np.array([0.0, 0.0, 1.0]) # Normal local do prato (+Z)
        
        # Debug counter
        self.update_count = 0

        self.init_ui()
        
        # Subscribers
        self.node.subscribe(Image, CAMERA_TOPIC, self.on_image)
        self.node.subscribe(Image, TUBE_CAMERA_TOPIC, self.on_tube_image)
        self.node.subscribe(Pose_V, POSE_TOPIC, self.on_pose)
        self.node.subscribe(Light, LIGHT_TOPIC, self.on_light)

        self.update_sensor_signal.connect(self.update_sensor_ui)
        self.update_math_signal.connect(self.update_math_ui)
        self.update_image_signal.connect(self.update_image_ui)
        self.update_rgb_signal.connect(self.update_rgb_ui)

    def init_ui(self):
        layout = QVBoxLayout()

        group_tube = QGroupBox("Câmera do Tubo")
        layout_tube = QVBoxLayout()
        self.lbl_camera_image = QLabel("Aguardando imagem...")
        self.lbl_camera_image.setAlignment(Qt.AlignCenter)
        self.lbl_camera_image.setMinimumSize(128, 128) # Tamanho mínimo para ver algo (2x scale)
        self.lbl_camera_image.setStyleSheet("border: 1px solid black; background-color: #333;")
        layout_tube.addWidget(self.lbl_camera_image)
        
        # Indicador numérico de luminosidade do tubo
        self.lbl_tube_intensity = QLabel("Intensidade: 0.00000")
        self.lbl_tube_intensity.setAlignment(Qt.AlignCenter)
        self.lbl_tube_intensity.setStyleSheet("font-size: 16px; font-weight: bold; color: yellow; background-color: #222; border-radius: 5px; padding: 5px;")
        layout_tube.addWidget(self.lbl_tube_intensity)

        # Valores RGB do pixel central da câmera do tubo
        self.lbl_tube_rgb = QLabel("RGB centro: (0, 0, 0)")
        self.lbl_tube_rgb.setAlignment(Qt.AlignCenter)
        self.lbl_tube_rgb.setStyleSheet("font-size: 12px; color: white; background-color: #222; border-radius: 5px; padding: 3px;")
        layout_tube.addWidget(self.lbl_tube_rgb)
        
        group_tube.setLayout(layout_tube)
        layout.addWidget(group_tube)

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
        self.resize(400, 550)

    def on_image(self, msg: Image):
        """Callback da câmera (sensor de intensidade)."""
        # ... (Mantendo código original para luminosidade) ...
        data = msg.data
        if not data: return
        try:
            arr = np.frombuffer(data, dtype=np.uint8)
            avg_intensity = np.mean(arr)
            self.sensor_value = avg_intensity
            self.update_sensor_signal.emit(avg_intensity)
        except Exception as e:
            print(f"Erro ao processar imagem: {e}")

    def on_tube_image(self, msg: Image):
        """Callback da nova câmera do tubo (visualização)."""
        data = msg.data
        if not data:
            print("DEBUG: Tube callback called but NO DATA.")
            return

        # Calcular luminância média (0.299*R + 0.587*G + 0.114*B)
        # usando apenas a região central da imagem, para ficar mais
        # sensível ao feixe no meio do tubo.
        try:
            width = msg.width
            height = msg.height
            arr = np.frombuffer(data, dtype=np.uint8)
            expected_size = width * height * 3
            if arr.size < expected_size:
                print("DEBUG: Tube image smaller than expected, skipping frame.")
                return

            arr = arr[:expected_size]
            img = arr.reshape((height, width, 3))

            # Recorte central (50% central da imagem)
            h0 = int(height * 0.25)
            h1 = int(height * 0.75)
            w0 = int(width * 0.25)
            w1 = int(width * 0.75)

            region = img[h0:h1, w0:w1, :]

            r = region[:, :, 0].astype(float)
            g = region[:, :, 1].astype(float)
            b = region[:, :, 2].astype(float)
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            avg = float(lum.mean())

            # Pixel central (o mais central possível) da imagem completa
            cx = width // 2
            cy = height // 2
            pr, pg, pb = img[cy, cx]
            self.update_rgb_signal.emit(int(pr), int(pg), int(pb))
            # Também atualizar o valor de sensor global com a mesma
            # intensidade da câmera do tubo, para refletir na barra
            # "Intensidade Média" do GUI.
            self.sensor_value = avg
            self.update_sensor_signal.emit(avg)
        except Exception as e:
            print(f"DEBUG: Error calculating tube luminance: {e}")
            avg = 0.0

        # Emitir sinal com dados brutos para atualizar na thread principal
        self.update_image_signal.emit(data, msg.width, msg.height, avg)

    def update_rgb_ui(self, r, g, b):
        self.lbl_tube_rgb.setText(f"RGB centro: ({r}, {g}, {b})")

    def on_pose(self, msg: Pose_V):
        # ... (Mantendo lógica original de Pose) ...
        found = False
        dish_rotation_matrix = np.eye(3)

        for p in msg.pose:
            if "link_dish" in p.name:
                dish_rotation_matrix = quaternion_to_rotation_matrix(p.orientation)
                found = True
                break
        
        if not found:
            for p in msg.pose:
                if "link_arm" in p.name:
                    dish_rotation_matrix = quaternion_to_rotation_matrix(p.orientation)
                    found = True
                    break
        
        if found:
            local_normal = np.array([0, 0, 1])
            global_normal = dish_rotation_matrix.dot(local_normal)
            dot_raw = np.dot(global_normal, self.sun_vector)
            dot_clamped = max(0.0, dot_raw)
            self.dot_product = dot_clamped
            self.update_math_signal.emit(dot_clamped)
            self.lbl_info.setText(f"Prato detectado!")

    def on_light(self, msg: Light):
        d = msg.direction
        vec = np.array([-d.x, -d.y, -d.z])
        norm = np.linalg.norm(vec)
        if norm > 0:
            self.sun_vector = vec / norm

    def update_sensor_ui(self, value):
        self.lbl_sensor.setText(f"Intensidade Média: {value:.2f}")
        self.bar_sensor.setValue(int(value))

    def update_image_ui(self, data, width, height, intensity):
        """Atualiza o QLabel com a imagem da câmera e a barra de intensidade."""
        # Criar QImage a partir dos bytes (R8G8B8 = formato RGB888)
        qimg = QImage(data, width, height, width*3, QImage.Format_RGB888)
        
        # Converter para pixmap e escalar para visualização melhor
        pixmap = QPixmap.fromImage(qimg)
        scaled_pixmap = pixmap.scaled(128, 128, Qt.KeepAspectRatio) # 2x zoom (original 64x64)
        
        self.lbl_camera_image.setPixmap(scaled_pixmap)
        
        # Atualizar indicador numérico com contador de debug
        self.update_count += 1
        self.lbl_tube_intensity.setText(f"Intensidade: {intensity:.5f} ({self.update_count})")

    def update_math_ui(self, value):
        self.lbl_math.setText(f"Alinhamento (Dot): {value:.3f}")
        angle_rad = np.arccos(np.clip(value, 0.0, 1.0))
        angle_deg = np.degrees(angle_rad)
        self.bar_math.setValue(int(value * 100))
        self.lbl_deg.setText(f"Desvio: {angle_deg:.4f}°")
        if angle_deg >= 5.0:
            bar_value = 0
        else:
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
