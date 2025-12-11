#!/usr/bin/env python3
import sys
import threading
import numpy as np
import time
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QGroupBox, QGridLayout, QPushButton, QTextEdit
)
from PyQt5.QtCore import QTimer, Qt

# Gazebo Transport
try:
    from gz.transport13 import Node
    from gz.msgs10.image_pb2 import Image
    from gz.msgs10.double_pb2 import Double
except ImportError:
    print("ERRO: Instale: sudo apt install python3-gz-transport13 python3-gz-msgs10")
    sys.exit(1)


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
        """
        Lê a posição de uma junta usando gz topic e awk.
        Retorna o valor numérico ou None se falhar.
        """
        try:
            # Comando direto, mais simples
            cmd = (
                f'gz topic -e -t /world/three_link_with_tracker_plate_world/model/three_link_model/joint_state '
                f'| awk \'/name: "{joint_name}"/ {{flag=1}} flag && /position:/ {{print $2; flag=0}}\' '
                f'| head -n 1'
            )
            
            print(f"[DEBUG] Executando comando para {joint_name}:")
            print(f"[DEBUG] {cmd}")
            
            # Executa o comando e captura a saída
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
            
            print(f"[DEBUG] Retorno ({joint_name}): stdout='{result.stdout.strip()}' stderr='{result.stderr.strip()}'")
            
            if result.stdout and result.stdout.strip():
                try:
                    value = float(result.stdout.strip())
                    print(f"[DEBUG] Sucesso! {joint_name} = {value}")
                    return value
                except ValueError:
                    print(f"[DEBUG] Não conseguiu converter para float: {result.stdout.strip()}")
                    return None
            else:
                print(f"[DEBUG] Nenhuma saída capturada")
                return None
        except subprocess.TimeoutExpired:
            print(f"[DEBUG] Timeout ao ler {joint_name}")
            return None
        except Exception as e:
            print(f"[DEBUG] Erro ao ler {joint_name}: {e}")
            return None


class TrackerAutoGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rastreamento Automático - Placa Rastreadora")

        # Nó Gazebo
        self.node = Node()
        self.cam_reader = QuadCameraReader(self.node)

        # Publishers para juntas
        self.pub_joint1 = None
        self.pub_joint2 = None

        # Estado das juntas (offset em relação à posição inicial)
        self.joint1_offset = 0.0
        self.joint2_offset = 0.0
        
        # Posições iniciais lidas do robô
        self.joint1_initial = 0.0
        self.joint2_initial = 0.0
        
        # Flag de controle ativo
        self.tracking_active = False

        # Passos base (4 níveis)
        self.step_1 = 0.00005  # Muito fino
        self.step_2 = 0.0005   # Fino
        self.step_3 = 0.002   # Médio
        self.step_4 = 0.003    # Grosso

        # Thresholds (limites de diferença para trocar de passo)
        self.thresh_1 = 1.0    # < 2.0 usa step_1
        self.thresh_2 = 5.0   # < 10.0 usa step_2
        self.thresh_3 = 15.0   # < 30.0 usa step_3, senão step_4

        # Banda morta
        self.eps = 0.00001          # ← Aumentar = menos sensível a pequenas diferenças

        # Frequência de correção (Hz). Ajuste aqui para mudar a taxa de controle.
        self.control_freq_hz = 40.0  # padrão: 10 Hz

        self.init_ui()

        # Timer de controle (usando control_freq_hz para calcular intervalo)
        self.timer = QTimer()
        self.timer.timeout.connect(self.control_step)
        interval_ms = max(1, int(1000.0 / self.control_freq_hz))  # evita 0 ms
        self.timer.start(interval_ms)

    def init_ui(self):
        layout = QVBoxLayout()

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
        layout.addWidget(group_lum)

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
        layout.addWidget(group_diff)

        # Status
        self.lbl_status = QLabel("Status: PARADO - Clique em 'Iniciar Rastreamento'")
        self.lbl_status.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.lbl_status)

        # Debug log
        group_debug = QGroupBox("Debug Log")
        self.txt_debug = QTextEdit()
        self.txt_debug.setReadOnly(True)
        self.txt_debug.setMaximumHeight(100)
        group_debug.setLayout(QVBoxLayout())
        group_debug.layout().addWidget(self.txt_debug)
        layout.addWidget(group_debug)

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
        layout.addWidget(group_cmd)

        # Botões
        btn_layout = QHBoxLayout()
        
        self.btn_iniciar = QPushButton("Iniciar Rastreamento")
        self.btn_iniciar.clicked.connect(self.iniciar_rastreamento)
        self.btn_iniciar.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        
        self.btn_parar = QPushButton("Parar Rastreamento")
        self.btn_parar.clicked.connect(self.parar_rastreamento)
        self.btn_parar.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
        self.btn_parar.setEnabled(False)
        
        self.btn_sair = QPushButton("Sair")
        self.btn_sair.clicked.connect(self.close)
        
        btn_layout.addWidget(self.btn_iniciar)
        btn_layout.addWidget(self.btn_parar)
        btn_layout.addWidget(self.btn_sair)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.resize(600, 700)

    def log_debug(self, msg):
        """Adiciona mensagem ao log de debug."""
        self.txt_debug.append(msg)
        # Auto-scroll para o final
        self.txt_debug.verticalScrollBar().setValue(
            self.txt_debug.verticalScrollBar().maximum()
        )

    def iniciar_rastreamento(self):
        """Lê a posição atual do robô e começa o rastreamento."""
        if not self.tracking_active:
            self.lbl_status.setText("Status: Lendo posição atual das juntas...")
            self.lbl_status.setStyleSheet("color: blue; font-weight: bold;")
            self.log_debug("Iniciando leitura de posições...")
            
            # Lê as posições atuais via subprocess
            j1_atual = JointStateReader.read_joint_position("joint_azimuth")
            j2_atual = JointStateReader.read_joint_position("joint_elevation")
            
            self.log_debug(f"Leitura: j1={j1_atual}, j2={j2_atual}")
            
            if j1_atual is None or j2_atual is None:
                self.lbl_status.setText("✗ Erro: Não conseguiu ler posição das juntas!")
                self.lbl_status.setStyleSheet("color: darkred; font-weight: bold;")
                self.log_debug("FALHA: Valores None")
                print(f"✗ Falha ao ler: j1={j1_atual}, j2={j2_atual}")
                return
            
            # Armazena como posição inicial
            self.joint1_initial = j1_atual
            self.joint2_initial = j2_atual
            
            self.lbl_j1_init.setText(f"joint1 inicial (rad): {self.joint1_initial:.4f}")
            self.lbl_j2_init.setText(f"joint2 inicial (rad): {self.joint2_initial:.4f}")
            
            # Reseta os offsets para zero
            self.joint1_offset = 0.0
            self.joint2_offset = 0.0
            
            # Cria os publishers
            self.pub_joint1 = self.node.advertise(
                "/model/three_link_model/joint/joint_azimuth/cmd_pos", Double
            )
            self.pub_joint2 = self.node.advertise(
                "/model/three_link_model/joint/joint_elevation/cmd_pos", Double
            )
            
            # Ativa o tracking
            self.tracking_active = True
            
            # Atualiza UI
            self.lbl_status.setText(
                f"Status: RASTREANDO - j1={self.joint1_initial:.4f}, j2={self.joint2_initial:.4f}"
            )
            self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
            self.btn_iniciar.setEnabled(False)
            self.btn_parar.setEnabled(True)
            
            self.log_debug(f"✓ Rastreamento iniciado: j1={self.joint1_initial:.4f}, j2={self.joint2_initial:.4f}")
            print(f"✓ Rastreamento iniciado")

    def parar_rastreamento(self):
        """Para o rastreamento."""
        if self.tracking_active:
            self.tracking_active = False
            self.pub_joint1 = None
            self.pub_joint2 = None
            
            # Atualiza UI
            self.lbl_status.setText("Status: PARADO - Clique em 'Iniciar Rastreamento'")
            self.lbl_status.setStyleSheet("color: red; font-weight: bold;")
            self.btn_iniciar.setEnabled(True)
            self.btn_parar.setEnabled(False)
            
            self.log_debug("Rastreamento parado")
            print("✓ Rastreamento parado")

    def send_joint(self, name, pos):
        """Envia comando de junta."""
        if not self.tracking_active or self.pub_joint1 is None or self.pub_joint2 is None:
            return
        
        msg = Double()
        msg.data = pos
        if name == "joint_azimuth":
            self.pub_joint1.publish(msg)
        elif name == "joint_elevation":
            self.pub_joint2.publish(msg)

    def set_control_frequency(self, hz: float):
        """Altera a frequência de correção (Hz) em tempo de execução."""
        if hz <= 0:
            return
        self.control_freq_hz = float(hz)
        if hasattr(self, "timer") and self.timer is not None:
            interval_ms = max(1, int(1000.0 / self.control_freq_hz))
            self.timer.start(interval_ms)
            self.log_debug(f"Frequência de correção ajustada para {self.control_freq_hz:.2f} Hz (intervalo {interval_ms} ms)")

    def control_step(self):
        """Executa o controle."""
        if not self.tracking_active:
            return
        
        # Leitura das luminâncias
        lum = self.cam_reader.get_luminances()
        q1 = lum.get("cam_q1")
        q2 = lum.get("cam_q2")
        q3 = lum.get("cam_q3")
        q4 = lum.get("cam_q4")

        # Atualiza labels
        def fmt(v):
            return "---" if v is None else f"{v:.4f}"

        self.lbl_q1.setText(f"Q1 (vermelho): {fmt(q1)}")
        self.lbl_q2.setText(f"Q2 (verde escuro): {fmt(q2)}")
        self.lbl_q3.setText(f"Q3 (azul): {fmt(q3)}")
        self.lbl_q4.setText(f"Q4 (amarelo escuro): {fmt(q4)}")

        if None in (q1, q2, q3, q4):
            return

        # Diferenças
        d12 = q1 - q2
        d14 = q1 - q4
        d32 = q3 - q2
        d34 = q3 - q4
        self.lbl_d12.setText(f"Δ12 = Q1 - Q2: {d12:.5f}")
        self.lbl_d14.setText(f"Δ14 = Q1 - Q4: {d14:.5f}")
        self.lbl_d32.setText(f"Δ32 = Q3 - Q2: {d32:.5f}")
        self.lbl_d34.setText(f"Δ34 = Q3 - Q4: {d34:.5f}")

        # Função local para escolher passo
        def get_step(diff):
            ad = abs(diff)
            if ad < self.thresh_1: return self.step_1
            if ad < self.thresh_2: return self.step_2
            if ad < self.thresh_3: return self.step_3
            return self.step_4

        # Passos adaptativos
        step2 = get_step(d12)

        # Comparação para decidir regra de joint1
        sum_q1_q4 = q1 + q4
        sum_q2_q3 = q2 + q3
        
        if sum_q1_q4 > sum_q2_q3:
            # Regra atual (usa d14)
            step1 = get_step(d14)
            self.lbl_comp.setText(f"(Q1+Q4)={(sum_q1_q4):.2f} > (Q2+Q3)={(sum_q2_q3):.2f} → Modo 1 (d14)")
            
            if d14 > self.eps:
                self.joint1_offset += step1
            elif d14 < -self.eps:
                self.joint1_offset -= step1
        else:
            # Nova regra (usa Q2 vs Q3)
            step1 = get_step(d32)
            self.lbl_comp.setText(f"(Q1+Q4)={(sum_q1_q4):.2f} ≤ (Q2+Q3)={(sum_q2_q3):.2f} → Modo 2 (Q2 vs Q3)")
            
            if q2 > q3 + self.eps:
                self.joint1_offset += step1
            elif q2 < q3 - self.eps:
                self.joint1_offset -= step1

        self.lbl_step1.setText(f"step joint1: {step1:.4f}")
        self.lbl_step2.setText(f"step joint2: {step2:.4f}")

        # Controle joint2 (mantém regra atual)
        if d12 > self.eps:
            self.joint2_offset += step2
        elif d12 < -self.eps:
            self.joint2_offset -= step2

        # Posições reais
        joint1_cmd = self.joint1_initial + self.joint1_offset
        joint2_cmd = self.joint2_initial + self.joint2_offset

        # Atualiza visual
        self.lbl_j1.setText(f"joint1 offset (rad): {self.joint1_offset:.4f}")
        self.lbl_j2.setText(f"joint2 offset (rad): {self.joint2_offset:.4f}")
        self.lbl_j1_real.setText(f"joint1 comando (rad): {joint1_cmd:.4f}")
        self.lbl_j2_real.setText(f"joint2 comando (rad): {joint2_cmd:.4f}")

        # Envia comando
        self.send_joint("joint_azimuth", joint1_cmd)
        self.send_joint("joint_elevation", joint2_cmd)


def main():
    app = QApplication(sys.argv)
    gui = TrackerAutoGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

