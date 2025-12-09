#!/usr/bin/env python3
"""
Interface Gráfica Unificada - Controle Solar e Rastreamento
Combina as funcionalidades de:
- light_sensor_gui.py (Sensor de Foco)
- tracker_auto_control_gui.py (Rastreamento Automático)
- sun_control_gui.py (Controle do Sol)
"""
import sys
import math
import threading
import numpy as np
import time
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QGridLayout, QLabel, QProgressBar,
    QPushButton, QSlider, QDoubleSpinBox, QTextEdit,
    QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

# Gazebo Transport
try:
    from gz.transport13 import Node
    from gz.msgs10.image_pb2 import Image
    from gz.msgs10.double_pb2 import Double
    from gz.msgs10.pose_v_pb2 import Pose_V
    from gz.msgs10.light_pb2 import Light
except ImportError:
    print("ERRO: Instale: sudo apt install python3-gz-transport13 python3-gz-msgs10")
    sys.exit(1)

WORLD_NAME = "three_link_with_tracker_plate_world"
LIGHT_NAME = "sun"

def quaternion_to_rotation_matrix(q):
    """Converte quaternion (w, x, y, z) para matriz de rotação 3x3."""
    w, x, y, z = q.w, q.x, q.y, q.z
    return np.array([
        [1 - 2*y*y - 2*z*z,     2*x*y - 2*z*w,     2*x*z + 2*y*w],
        [    2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z,     2*y*z - 2*x*w],
        [    2*x*z - 2*y*w,     2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y]
    ])

class QuadCameraReader:
    def __init__(self, node: Node):
        self.node = node
        self.lum = {
            "cam_q1": None,
            "cam_q2": None,
            "cam_q3": None,
            "cam_q4": None,
        }
        self.lock = threading.Lock()

        self.node.subscribe(Image, "plate/cam_q1/image",
                            lambda msg: self.image_callback(msg, "cam_q1"))
        self.node.subscribe(Image, "plate/cam_q2/image",
                            lambda msg: self.image_callback(msg, "cam_q2"))
        self.node.subscribe(Image, "plate/cam_q3/image",
                            lambda msg: self.image_callback(msg, "cam_q3"))
        self.node.subscribe(Image, "plate/cam_q4/image",
                            lambda msg: self.image_callback(msg, "cam_q4"))

    def image_callback(self, msg, cam_name):
        width = msg.width
        height = msg.height
        data = np.frombuffer(msg.data, dtype=np.uint8)
        expected_size = width * height * 3
        if data.size < expected_size:
            return
        data = data[:expected_size]
        img = data.reshape((height, width, 3))

        r = img[:, :, 0].astype(float)
        g = img[:, :, 1].astype(float)
        b = img[:, :, 2].astype(float)

        lum = 0.299 * r + 0.587 * g + 0.114 * b
        avg_lum = float(lum.mean())

        with self.lock:
            self.lum[cam_name] = avg_lum

    def get_luminances(self):
        with self.lock:
            return dict(self.lum)


class JointStateReader:
    """Lê o estado das juntas usando comando gz topic via subprocess."""
    
    @staticmethod
    def read_joint_position(joint_name):
        try:
            cmd = (
                f'gz topic -e -t /world/three_link_with_tracker_plate_world/model/three_link_model/joint_state '
                f'| awk \'/name: "{joint_name}"/ {{flag=1}} flag && /position:/ {{print $2; flag=0}}\' '
                f'| head -n 1'
            )
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
            
            if result.stdout and result.stdout.strip():
                try:
                    value = float(result.stdout.strip())
                    return value
                except ValueError:
                    return None
            else:
                return None
        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            return None


class UnifiedControlGUI(QWidget):
    # Sinais
    update_sensor_signal = pyqtSignal(float)
    update_math_signal = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle Unificado - Sistema Solar Parabólico")
        
        # Nó Gazebo
        self.node = Node()
        
        # ===== SENSOR DE FOCO =====
        self.sensor_value = 0.0
        self.dot_product = 0.0
        self.sun_vector = np.array([0.0, 0.0, 1.0])
        self.dish_normal = np.array([0.0, 0.0, 1.0])
        
        # ===== RASTREAMENTO =====
        self.cam_reader = QuadCameraReader(self.node)
        self.pub_joint1 = None
        self.pub_joint2 = None
        self.joint1_offset = 0.0
        self.joint2_offset = 0.0
        self.joint1_initial = 0.0
        self.joint2_initial = 0.0
        self.tracking_active = False
        
        # Passos base (4 níveis)
        self.step_1 = 0.0001
        self.step_2 = 0.001
        self.step_3 = 0.01
        self.step_4 = 0.003
        
        self.thresh_1 = 1.0
        self.thresh_2 = 15.0
        self.thresh_3 = 25.0
        self.eps = 0.00001
        self.control_freq_hz = 40.0
        
        # ===== CONTROLE DO SOL =====
        self.azimute_deg = -45.0
        self.elevacao_deg = 45.0
        self.intensity = 1.0
        self.raio = 100.0
        
        self.topic_light = f"/world/{WORLD_NAME}/light_config"
        self.pub_light = self.node.advertise(self.topic_light, Light)
        
        self.init_ui()
        
        # Subscribers
        self.node.subscribe(Image, "parabolic_dish/focus_cam/image", self.on_focus_image)
        self.node.subscribe(Pose_V, f"/world/{WORLD_NAME}/pose/info", self.on_pose)
        self.node.subscribe(Light, self.topic_light, self.on_light)
        
        self.update_sensor_signal.connect(self.update_sensor_ui)
        self.update_math_signal.connect(self.update_math_ui)
        
        # Timer de controle
        self.timer = QTimer()
        self.timer.timeout.connect(self.control_step)
        interval_ms = max(1, int(1000.0 / self.control_freq_hz))
        self.timer.start(interval_ms)
        
        # Enviar configuração inicial do sol
        self.enviar_light_config()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tabs
        tabs = QTabWidget()
        
        # ===== TAB 1: SENSOR DE FOCO =====
        tab_sensor = QWidget()
        layout_sensor = QVBoxLayout()
        
        # Grupo Sensor (Câmera)
        group_cam = QGroupBox("Sensor de Luminosidade (Câmera)")
        layout_cam = QVBoxLayout()
        
        self.lbl_sensor = QLabel("Intensidade Média: 0.00")
        self.lbl_sensor.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout_cam.addWidget(self.lbl_sensor)
        
        self.bar_sensor = QProgressBar()
        self.bar_sensor.setRange(0, 255)
        self.bar_sensor.setValue(0)
        self.bar_sensor.setStyleSheet("QProgressBar::chunk { background-color: #FFA500; }")
        layout_cam.addWidget(self.bar_sensor)
        
        group_cam.setLayout(layout_cam)
        layout_sensor.addWidget(group_cam)
        
        # Grupo Matemático
        group_math = QGroupBox("Cálculo Matemático")
        layout_math = QVBoxLayout()
        
        self.lbl_math = QLabel("Alinhamento (Dot): 0.000")
        self.lbl_math.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout_math.addWidget(self.lbl_math)
        
        self.bar_math = QProgressBar()
        self.bar_math.setRange(0, 100)
        self.bar_math.setValue(0)
        self.bar_math.setStyleSheet("QProgressBar::chunk { background-color: #00BFFF; }")
        layout_math.addWidget(self.bar_math)
        
        self.lbl_deg = QLabel("Desvio: 0.0000°")
        self.lbl_deg.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout_math.addWidget(self.lbl_deg)
        
        self.bar_deg = QProgressBar()
        self.bar_deg.setRange(0, 100)
        self.bar_deg.setValue(0)
        self.bar_deg.setAlignment(Qt.AlignCenter)
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
        layout_sensor.addWidget(group_math)
        
        self.lbl_info = QLabel("Aguardando dados do Gazebo...")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        layout_sensor.addWidget(self.lbl_info)
        
        tab_sensor.setLayout(layout_sensor)
        tabs.addTab(tab_sensor, "Sensor de Foco")
        
        # ===== TAB 2: RASTREAMENTO =====
        tab_tracker = QWidget()
        layout_tracker = QVBoxLayout()
        
        # Luminâncias
        group_lum = QGroupBox("Luminância média (0–255)")
        grid_lum = QGridLayout()
        
        self.lbl_q1 = QLabel("Q1 (vermelho): ---")
        self.lbl_q2 = QLabel("Q2 (verde escuro): ---")
        self.lbl_q3 = QLabel("Q3 (azul): ---")
        self.lbl_q4 = QLabel("Q4 (amarelo escuro): ---")
        
        grid_lum.addWidget(self.lbl_q1, 0, 0)
        grid_lum.addWidget(self.lbl_q2, 0, 1)
        grid_lum.addWidget(self.lbl_q3, 1, 0)
        grid_lum.addWidget(self.lbl_q4, 1, 1)
        
        group_lum.setLayout(grid_lum)
        layout_tracker.addWidget(group_lum)
        
        # Diferenças
        group_diff = QGroupBox("Diferenças e passos")
        grid_diff = QGridLayout()
        
        self.lbl_d12 = QLabel("Δ12 = Q1 - Q2: ---")
        self.lbl_d14 = QLabel("Δ14 = Q1 - Q4: ---")
        self.lbl_d32 = QLabel("Δ32 = Q3 - Q2: ---")
        self.lbl_d34 = QLabel("Δ34 = Q3 - Q4: ---")
        self.lbl_step1 = QLabel("step joint1: ---")
        self.lbl_step2 = QLabel("step joint2: ---")
        self.lbl_comp = QLabel("Comparação (Q1+Q4) vs (Q2+Q3): ---")
        
        grid_diff.addWidget(self.lbl_d12, 0, 0)
        grid_diff.addWidget(self.lbl_d14, 0, 1)
        grid_diff.addWidget(self.lbl_d32, 1, 0)
        grid_diff.addWidget(self.lbl_d34, 1, 1)
        grid_diff.addWidget(self.lbl_comp, 2, 0, 1, 2)
        grid_diff.addWidget(self.lbl_step1, 3, 0)
        grid_diff.addWidget(self.lbl_step2, 3, 1)
        
        group_diff.setLayout(grid_diff)
        layout_tracker.addWidget(group_diff)
        
        # Status
        self.lbl_status = QLabel("Status: PARADO - Clique em 'Iniciar Rastreamento'")
        self.lbl_status.setStyleSheet("color: red; font-weight: bold;")
        layout_tracker.addWidget(self.lbl_status)
        
        # Debug log
        group_debug = QGroupBox("Debug Log")
        self.txt_debug = QTextEdit()
        self.txt_debug.setReadOnly(True)
        self.txt_debug.setMaximumHeight(100)
        group_debug.setLayout(QVBoxLayout())
        group_debug.layout().addWidget(self.txt_debug)
        layout_tracker.addWidget(group_debug)
        
        # Comandos de junta
        group_cmd = QGroupBox("Comandos de juntas")
        grid_cmd = QGridLayout()
        
        self.lbl_j1 = QLabel("joint1 offset (rad): ---")
        self.lbl_j2 = QLabel("joint2 offset (rad): ---")
        self.lbl_j1_real = QLabel("joint1 comando (rad): ---")
        self.lbl_j2_real = QLabel("joint2 comando (rad): ---")
        self.lbl_j1_init = QLabel("joint1 inicial (rad): ---")
        self.lbl_j2_init = QLabel("joint2 inicial (rad): ---")
        
        grid_cmd.addWidget(self.lbl_j1_init, 0, 0)
        grid_cmd.addWidget(self.lbl_j2_init, 0, 1)
        grid_cmd.addWidget(self.lbl_j1, 1, 0)
        grid_cmd.addWidget(self.lbl_j2, 1, 1)
        grid_cmd.addWidget(self.lbl_j1_real, 2, 0)
        grid_cmd.addWidget(self.lbl_j2_real, 2, 1)
        
        group_cmd.setLayout(grid_cmd)
        layout_tracker.addWidget(group_cmd)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        self.btn_iniciar = QPushButton("Iniciar Rastreamento")
        self.btn_iniciar.clicked.connect(self.iniciar_rastreamento)
        self.btn_iniciar.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        
        self.btn_parar = QPushButton("Parar Rastreamento")
        self.btn_parar.clicked.connect(self.parar_rastreamento)
        self.btn_parar.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
        self.btn_parar.setEnabled(False)
        
        btn_layout.addWidget(self.btn_iniciar)
        btn_layout.addWidget(self.btn_parar)
        layout_tracker.addLayout(btn_layout)
        
        tab_tracker.setLayout(layout_tracker)
        tabs.addTab(tab_tracker, "Rastreamento")
        
        # ===== TAB 3: CONTROLE DO SOL =====
        tab_sun = QWidget()
        layout_sun = QVBoxLayout()
        
        group_sun = QGroupBox("Parâmetros do Sol")
        grid_sun = QGridLayout()
        
        # Azimute
        self.lbl_az = QLabel("Azimute (°):")
        self.slider_az = QSlider(Qt.Horizontal)
        self.slider_az.setMinimum(-18000)
        self.slider_az.setMaximum(18000)
        self.slider_az.setValue(int(self.azimute_deg * 100))
        self.slider_az.valueChanged.connect(self.on_slider_az_changed)
        
        self.spin_az = QDoubleSpinBox()
        self.spin_az.setRange(-180.0, 180.0)
        self.spin_az.setDecimals(2)
        self.spin_az.setSingleStep(0.1)
        self.spin_az.setValue(self.azimute_deg)
        self.spin_az.valueChanged.connect(self.on_spin_az_changed)
        
        grid_sun.addWidget(self.lbl_az, 0, 0)
        grid_sun.addWidget(self.slider_az, 0, 1)
        grid_sun.addWidget(self.spin_az, 0, 2)
        
        # Elevação
        self.lbl_el = QLabel("Elevação (°):")
        self.slider_el = QSlider(Qt.Horizontal)
        self.slider_el.setMinimum(0)
        self.slider_el.setMaximum(9000)
        self.slider_el.setValue(int(self.elevacao_deg * 100))
        self.slider_el.valueChanged.connect(self.on_slider_el_changed)
        
        self.spin_el = QDoubleSpinBox()
        self.spin_el.setRange(0.0, 90.0)
        self.spin_el.setDecimals(2)
        self.spin_el.setSingleStep(0.1)
        self.spin_el.setValue(self.elevacao_deg)
        self.spin_el.valueChanged.connect(self.on_spin_el_changed)
        
        grid_sun.addWidget(self.lbl_el, 1, 0)
        grid_sun.addWidget(self.slider_el, 1, 1)
        grid_sun.addWidget(self.spin_el, 1, 2)
        
        # Intensidade
        self.lbl_int = QLabel("Intensidade:")
        self.slider_int = QSlider(Qt.Horizontal)
        self.slider_int.setMinimum(100)
        self.slider_int.setMaximum(1000)
        self.slider_int.setValue(int(self.intensity * 100))
        self.slider_int.valueChanged.connect(self.on_slider_int_changed)
        
        self.spin_int = QDoubleSpinBox()
        self.spin_int.setRange(1.0, 10.0)
        self.spin_int.setDecimals(2)
        self.spin_int.setSingleStep(0.1)
        self.spin_int.setValue(self.intensity)
        self.spin_int.valueChanged.connect(self.on_spin_int_changed)
        
        grid_sun.addWidget(self.lbl_int, 2, 0)
        grid_sun.addWidget(self.slider_int, 2, 1)
        grid_sun.addWidget(self.spin_int, 2, 2)
        
        group_sun.setLayout(grid_sun)
        layout_sun.addWidget(group_sun)
        
        self.lbl_topic = QLabel(f"Tópico luz: {self.topic_light}  |  nome: {LIGHT_NAME}")
        layout_sun.addWidget(self.lbl_topic)
        
        tab_sun.setLayout(layout_sun)
        tabs.addTab(tab_sun, "Controle do Sol")
        
        # ===== LAYOUT PRINCIPAL =====
        layout.addWidget(tabs)
        
        btn_quit = QPushButton("Sair")
        btn_quit.clicked.connect(self.close)
        layout.addWidget(btn_quit)
        
        self.setLayout(layout)
        self.resize(700, 800)

    # ===== CALLBACKS SENSOR DE FOCO =====
    def on_focus_image(self, msg: Image):
        data = msg.data
        if not data:
            return
        try:
            arr = np.frombuffer(data, dtype=np.uint8)
            avg_intensity = np.mean(arr)
            self.sensor_value = avg_intensity
            self.update_sensor_signal.emit(avg_intensity)
        except Exception as e:
            print(f"Erro ao processar imagem: {e}")

    def on_pose(self, msg: Pose_V):
        found = False
        dish_rotation_matrix = np.eye(3)

        for p in msg.pose:
            if "link_parabolic_dish" in p.name:
                dish_rotation_matrix = quaternion_to_rotation_matrix(p.orientation)
                found = True
                break
        
        if not found:
            for p in msg.pose:
                if "link3" in p.name:
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

    # ===== CALLBACKS RASTREAMENTO =====
    def log_debug(self, msg):
        self.txt_debug.append(msg)
        self.txt_debug.verticalScrollBar().setValue(
            self.txt_debug.verticalScrollBar().maximum()
        )

    def iniciar_rastreamento(self):
        if not self.tracking_active:
            self.lbl_status.setText("Status: Lendo posição atual das juntas...")
            self.lbl_status.setStyleSheet("color: blue; font-weight: bold;")
            self.log_debug("Iniciando leitura de posições...")
            
            j1_atual = JointStateReader.read_joint_position("joint1")
            j2_atual = JointStateReader.read_joint_position("joint2")
            
            self.log_debug(f"Leitura: j1={j1_atual}, j2={j2_atual}")
            
            if j1_atual is None or j2_atual is None:
                self.lbl_status.setText("✗ Erro: Não conseguiu ler posição das juntas!")
                self.lbl_status.setStyleSheet("color: darkred; font-weight: bold;")
                self.log_debug("FALHA: Valores None")
                return
            
            self.joint1_initial = j1_atual
            self.joint2_initial = j2_atual
            
            self.lbl_j1_init.setText(f"joint1 inicial (rad): {self.joint1_initial:.4f}")
            self.lbl_j2_init.setText(f"joint2 inicial (rad): {self.joint2_initial:.4f}")
            
            self.joint1_offset = 0.0
            self.joint2_offset = 0.0
            
            self.pub_joint1 = self.node.advertise(
                "/model/three_link_model/joint/joint1/cmd_pos", Double
            )
            self.pub_joint2 = self.node.advertise(
                "/model/three_link_model/joint/joint2/cmd_pos", Double
            )
            
            self.tracking_active = True
            
            self.lbl_status.setText(
                f"Status: RASTREANDO - j1={self.joint1_initial:.4f}, j2={self.joint2_initial:.4f}"
            )
            self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
            self.btn_iniciar.setEnabled(False)
            self.btn_parar.setEnabled(True)
            
            self.log_debug(f"✓ Rastreamento iniciado: j1={self.joint1_initial:.4f}, j2={self.joint2_initial:.4f}")

    def parar_rastreamento(self):
        if self.tracking_active:
            self.tracking_active = False
            self.pub_joint1 = None
            self.pub_joint2 = None
            
            self.lbl_status.setText("Status: PARADO - Clique em 'Iniciar Rastreamento'")
            self.lbl_status.setStyleSheet("color: red; font-weight: bold;")
            self.btn_iniciar.setEnabled(True)
            self.btn_parar.setEnabled(False)
            
            self.log_debug("Rastreamento parado")

    def send_joint(self, name, pos):
        if not self.tracking_active or self.pub_joint1 is None or self.pub_joint2 is None:
            return
        
        msg = Double()
        msg.data = pos
        if name == "joint1":
            self.pub_joint1.publish(msg)
        elif name == "joint2":
            self.pub_joint2.publish(msg)

    def control_step(self):
        if not self.tracking_active:
            return
        
        lum = self.cam_reader.get_luminances()
        q1 = lum.get("cam_q1")
        q2 = lum.get("cam_q2")
        q3 = lum.get("cam_q3")
        q4 = lum.get("cam_q4")

        def fmt(v):
            return "---" if v is None else f"{v:.4f}"

        self.lbl_q1.setText(f"Q1 (vermelho): {fmt(q1)}")
        self.lbl_q2.setText(f"Q2 (verde escuro): {fmt(q2)}")
        self.lbl_q3.setText(f"Q3 (azul): {fmt(q3)}")
        self.lbl_q4.setText(f"Q4 (amarelo escuro): {fmt(q4)}")

        if None in (q1, q2, q3, q4):
            return

        d12 = q1 - q2
        d14 = q1 - q4
        d32 = q3 - q2
        d34 = q3 - q4
        self.lbl_d12.setText(f"Δ12 = Q1 - Q2: {d12:.5f}")
        self.lbl_d14.setText(f"Δ14 = Q1 - Q4: {d14:.5f}")
        self.lbl_d32.setText(f"Δ32 = Q3 - Q2: {d32:.5f}")
        self.lbl_d34.setText(f"Δ34 = Q3 - Q4: {d34:.5f}")

        def get_step(diff):
            ad = abs(diff)
            if ad < self.thresh_1: return self.step_1
            if ad < self.thresh_2: return self.step_2
            if ad < self.thresh_3: return self.step_3
            return self.step_4

        step2 = get_step(d12)

        sum_q1_q4 = q1 + q4
        sum_q2_q3 = q2 + q3
        
        if sum_q1_q4 > sum_q2_q3:
            step1 = get_step(d14)
            self.lbl_comp.setText(f"(Q1+Q4)={(sum_q1_q4):.2f} > (Q2+Q3)={(sum_q2_q3):.2f} → Modo 1 (d14)")
            
            if d14 > self.eps:
                self.joint1_offset += step1
            elif d14 < -self.eps:
                self.joint1_offset -= step1
        else:
            step1 = get_step(d32)
            self.lbl_comp.setText(f"(Q1+Q4)={(sum_q1_q4):.2f} ≤ (Q2+Q3)={(sum_q2_q3):.2f} → Modo 2 (Q2 vs Q3)")
            
            if q2 > q3 + self.eps:
                self.joint1_offset += step1
            elif q2 < q3 - self.eps:
                self.joint1_offset -= step1

        self.lbl_step1.setText(f"step joint1: {step1:.4f}")
        self.lbl_step2.setText(f"step joint2: {step2:.4f}")

        if d12 > self.eps:
            self.joint2_offset += step2
        elif d12 < -self.eps:
            self.joint2_offset -= step2

        joint1_cmd = self.joint1_initial + self.joint1_offset
        joint2_cmd = self.joint2_initial + self.joint2_offset

        self.lbl_j1.setText(f"joint1 offset (rad): {self.joint1_offset:.4f}")
        self.lbl_j2.setText(f"joint2 offset (rad): {self.joint2_offset:.4f}")
        self.lbl_j1_real.setText(f"joint1 comando (rad): {joint1_cmd:.4f}")
        self.lbl_j2_real.setText(f"joint2 comando (rad): {joint2_cmd:.4f}")

        self.send_joint("joint1", joint1_cmd)
        self.send_joint("joint2", joint2_cmd)

    # ===== CALLBACKS CONTROLE DO SOL =====
    def on_slider_az_changed(self, value):
        val_float = value / 100.0
        self.azimute_deg = val_float
        self.spin_az.blockSignals(True)
        self.spin_az.setValue(val_float)
        self.spin_az.blockSignals(False)
        self.enviar_light_config()

    def on_spin_az_changed(self, value):
        self.azimute_deg = value
        self.slider_az.blockSignals(True)
        self.slider_az.setValue(int(value * 100))
        self.slider_az.blockSignals(False)
        self.enviar_light_config()

    def on_slider_el_changed(self, value):
        val_float = value / 100.0
        self.elevacao_deg = val_float
        self.spin_el.blockSignals(True)
        self.spin_el.setValue(val_float)
        self.spin_el.blockSignals(False)
        self.enviar_light_config()

    def on_spin_el_changed(self, value):
        self.elevacao_deg = value
        self.slider_el.blockSignals(True)
        self.slider_el.setValue(int(value * 100))
        self.slider_el.blockSignals(False)
        self.enviar_light_config()

    def on_slider_int_changed(self, value):
        val_float = value / 100.0
        self.intensity = val_float
        self.spin_int.blockSignals(True)
        self.spin_int.setValue(val_float)
        self.spin_int.blockSignals(False)
        self.enviar_light_config()

    def on_spin_int_changed(self, value):
        self.intensity = value
        self.slider_int.blockSignals(True)
        self.slider_int.setValue(int(value * 100))
        self.slider_int.blockSignals(False)
        self.enviar_light_config()

    def enviar_light_config(self):
        az = math.radians(self.azimute_deg)
        el = math.radians(self.elevacao_deg)

        x = self.raio * math.cos(el) * math.cos(az)
        y = self.raio * math.cos(el) * math.sin(az)
        z = self.raio * math.sin(el)

        dx = -x
        dy = -y
        dz = -z
        norm = math.sqrt(dx*dx + dy*dy + dz*dz) or 1.0
        dx /= norm
        dy /= norm
        dz /= norm

        msg = Light()
        msg.name = LIGHT_NAME
        msg.type = Light.DIRECTIONAL

        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.position.z = z
        msg.pose.orientation.w = 1.0
        msg.pose.orientation.x = 0.0
        msg.pose.orientation.y = 0.0
        msg.pose.orientation.z = 0.0

        msg.direction.x = dx
        msg.direction.y = dy
        msg.direction.z = dz

        msg.cast_shadows = True

        msg.intensity = self.intensity
        msg.diffuse.r = 1.0
        msg.diffuse.g = 1.0
        msg.diffuse.b = 1.0
        msg.diffuse.a = 1.0

        msg.specular.r = 0.8
        msg.specular.g = 0.8
        msg.specular.b = 0.8
        msg.specular.a = 1.0

        self.pub_light.publish(msg)


def main():
    app = QApplication(sys.argv)
    gui = UnifiedControlGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
