#!/usr/bin/env python3
import sys
import math
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QDoubleSpinBox, QPushButton, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal

# Gazebo imports
try:
    from gz.transport13 import Node
    from gz.msgs10.double_pb2 import Double
    from gz.msgs10.model_pb2 import Model
except ImportError:
    print("ERRO: Instale as bibliotecas do Gazebo Transport (gz-transport13, gz-msgs10)")
    sys.exit(1)

class ManualPositionGUI(QWidget):
    # Sinais para atualizar a GUI a partir da thread do Gazebo
    update_az_signal = pyqtSignal(float)
    update_el_signal = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle Manual e Monitor (Graus) - RÁPIDO")
        self.setGeometry(100, 100, 500, 500)

        # Configuração Gazebo
        self.node = Node()
        self.topic_az = "/model/three_link_model/joint/joint_azimuth/cmd_pos"
        self.topic_el = "/model/three_link_model/joint/joint_elevation/cmd_pos"
        
        self.pub_az = self.node.advertise(self.topic_az, Double)
        self.pub_el = self.node.advertise(self.topic_el, Double)

        # Assinar tópico de estados (Nome Completo)
        self.node.subscribe(Model, "/world/three_link_with_tracker_plate_world/model/three_link_model/joint_state", self.on_joint_state)

        # Variáveis de monitoramento
        self.az_min = float('inf')
        self.az_max = float('-inf')
        self.el_min = float('inf')
        self.el_max = float('-inf')
        
        self.init_ui()
        
        # Conectar sinais
        self.update_az_signal.connect(self.process_az_update)
        self.update_el_signal.connect(self.process_el_update)

    def init_ui(self):
        layout = QVBoxLayout()

        # === AZIMUTE ===
        group_az = QGroupBox("Junta Azimute")
        layout_az = QVBoxLayout()
        
        # Monitoramento Azimute
        self.lbl_az_monitor = QLabel("Atual: --- | Min: --- | Max: ---")
        self.lbl_az_monitor.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        self.lbl_az_monitor.setAlignment(Qt.AlignCenter)
        layout_az.addWidget(self.lbl_az_monitor)
        
        btn_reset_az = QPushButton("Resetar Min/Max Azimute")
        btn_reset_az.clicked.connect(self.reset_az_stats)
        layout_az.addWidget(btn_reset_az)
        
        # Controle Azimute
        hbox_az = QHBoxLayout()
        self.spin_az = QDoubleSpinBox()
        self.spin_az.setRange(-360.0, 360.0)
        self.spin_az.setSingleStep(5.0)
        self.spin_az.setDecimals(1)
        self.spin_az.setSuffix("°")
        self.spin_az.setValue(0.0)
        
        btn_send_az = QPushButton("Enviar Cmd")
        btn_send_az.clicked.connect(self.send_azimuth)
        btn_send_az.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        hbox_az.addWidget(QLabel("Cmd:"))
        hbox_az.addWidget(self.spin_az)
        hbox_az.addWidget(btn_send_az)
        
        layout_az.addLayout(hbox_az)
        
        hbox_quick_az = QHBoxLayout()
        btns_az = [("0°", 0), ("45°", 45), ("90°", 90), ("-45°", -45), ("-90°", -90)]
        for text, val in btns_az:
            b = QPushButton(text)
            b.clicked.connect(lambda checked, v=val: self.set_and_send_az(v))
            hbox_quick_az.addWidget(b)
        layout_az.addLayout(hbox_quick_az)

        group_az.setLayout(layout_az)
        layout.addWidget(group_az)

        # === ELEVAÇÃO ===
        group_el = QGroupBox("Junta Elevação")
        layout_el = QVBoxLayout()
        
        # Monitoramento Elevação
        self.lbl_el_monitor = QLabel("Atual: --- | Min: --- | Max: ---")
        self.lbl_el_monitor.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        self.lbl_el_monitor.setAlignment(Qt.AlignCenter)
        layout_el.addWidget(self.lbl_el_monitor)
        
        btn_reset_el = QPushButton("Resetar Min/Max Elevação")
        btn_reset_el.clicked.connect(self.reset_el_stats)
        layout_el.addWidget(btn_reset_el)
        
        # Controle Elevação
        hbox_el = QHBoxLayout()
        self.spin_el = QDoubleSpinBox()
        self.spin_el.setRange(-180.0, 180.0)
        self.spin_el.setSingleStep(5.0)
        self.spin_el.setDecimals(1)
        self.spin_el.setSuffix("°")
        self.spin_el.setValue(0.0)
        
        btn_send_el = QPushButton("Enviar Cmd")
        btn_send_el.clicked.connect(self.send_elevation)
        btn_send_el.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        
        hbox_el.addWidget(QLabel("Cmd:"))
        hbox_el.addWidget(self.spin_el)
        hbox_el.addWidget(btn_send_el)
        
        layout_el.addLayout(hbox_el)
        
        hbox_quick_el = QHBoxLayout()
        btns_el = [("0°", 0), ("30°", 30), ("60°", 60), ("90°", 90), ("-30°", -30)]
        for text, val in btns_el:
            b = QPushButton(text)
            b.clicked.connect(lambda checked, v=val: self.set_and_send_el(v))
            hbox_quick_el.addWidget(b)
        layout_el.addLayout(hbox_quick_el)

        group_el.setLayout(layout_el)
        layout.addWidget(group_el)

        # Info
        self.lbl_status = QLabel("Monitorando via Gz Transport (Alta Velocidade)...")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("color: gray;")
        layout.addWidget(self.lbl_status)

        self.setLayout(layout)

    # Callback do Gazebo (Roda em outra thread)
    def on_joint_state(self, msg: Model):
        # Percorre as juntas na mensagem
        for joint in msg.joint:
            # Verifica se tem axis1 e posição
            if joint.HasField("axis1") and joint.name == "joint_azimuth":
                pos = joint.axis1.position
                self.update_az_signal.emit(pos)
            
            elif joint.HasField("axis1") and joint.name == "joint_elevation":
                pos = joint.axis1.position
                self.update_el_signal.emit(pos)

    # Processamento na Thread da GUI
    def process_az_update(self, rad_val):
        deg = math.degrees(rad_val)
        if deg < self.az_min: self.az_min = deg
        if deg > self.az_max: self.az_max = deg
        
        self.lbl_az_monitor.setText(f"Atual: {deg:.2f}° | Min: {self.az_min:.2f}° | Max: {self.az_max:.2f}°")

    def process_el_update(self, rad_val):
        deg = math.degrees(rad_val)
        if deg < self.el_min: self.el_min = deg
        if deg > self.el_max: self.el_max = deg
        
        # Ajuste visual para evitar flickering se o valor mudar muito rápido
        # (Opcional, mas aqui estamos mostrando tudo raw)
        self.lbl_el_monitor.setText(f"Atual: {deg:.2f}° | Min: {self.el_min:.2f}° | Max: {self.el_max:.2f}°")

    def reset_az_stats(self):
        self.az_min = float('inf')
        self.az_max = float('-inf')
        self.lbl_status.setText("Estatísticas de Azimute resetadas.")

    def reset_el_stats(self):
        self.el_min = float('inf')
        self.el_max = float('-inf')
        self.lbl_status.setText("Estatísticas de Elevação resetadas.")

    def send_azimuth(self):
        deg = self.spin_az.value()
        rad = math.radians(deg)
        msg = Double()
        msg.data = rad
        self.pub_az.publish(msg)
        self.lbl_status.setText(f"Azimute enviado: {deg}°")

    def send_elevation(self):
        deg = self.spin_el.value()
        rad = math.radians(deg)
        msg = Double()
        msg.data = rad
        self.pub_el.publish(msg)
        self.lbl_status.setText(f"Elevação enviada: {deg}°")

    def set_and_send_az(self, val):
        self.spin_az.setValue(float(val))
        self.send_azimuth()

    def set_and_send_el(self, val):
        self.spin_el.setValue(float(val))
        self.send_elevation()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ManualPositionGUI()
    gui.show()
    sys.exit(app.exec_())
