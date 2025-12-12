#!/usr/bin/env python3
"""
GUI de Controle de Torque (Constante + Senoidal) para Cilindros
Controla:
- /model/three_link_model/joint/joint_cylinder/cmd_force (Vermelho)
- /model/three_link_model/joint/joint_cylinder_green/cmd_force (Verde)
"""

import sys
import math
import time
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QGridLayout, QLabel, QPushButton, 
    QSlider, QDoubleSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer

# Gazebo Transport
try:
    from gz.transport13 import Node
    from gz.msgs10.double_pb2 import Double
except ImportError:
    print("ERRO: Instale: sudo apt install python3-gz-transport13 python3-gz-msgs10")
    sys.exit(1)

# Configurações de Tópicos
TOPIC_RED = "/model/three_link_model/joint/joint_cylinder/cmd_force"
TOPIC_GREEN = "/model/three_link_model/joint/joint_cylinder_green/cmd_force"

class TorqueControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle de Torque - Cilindros")
        
        self.node = Node()
        self.pub_red = self.node.advertise(TOPIC_RED, Double)
        self.pub_green = self.node.advertise(TOPIC_GREEN, Double)
        
        # Estado do Torque
        self.t = 0.0
        self.active = False
        
        # Parâmetros Vermelho
        self.red_const = 0.0
        self.red_sine_active = False
        self.red_amp = 0.0
        self.red_freq = 0.5
        
        # Parâmetros Verde
        self.green_const = 0.0
        self.green_sine_active = False
        self.green_amp = 0.0
        self.green_freq = 0.5
        
        self.init_ui()
        
        # Timer de Controle (50 Hz)
        self.output_freq = 50.0
        self.timer = QTimer()
        self.timer.timeout.connect(self.control_loop)
        self.timer.start(int(1000/self.output_freq))

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # ===== GRUPO VERMELHO =====
        group_red = QGroupBox("Cilindro Vermelho (Joint Cylinder)")
        group_red.setStyleSheet("QGroupBox { font-weight: bold; color: darkred; border: 1px solid darkred; }")
        layout_red = QGridLayout()
        
        # Constante
        layout_red.addWidget(QLabel("Torque Constante (Nm):"), 0, 0)
        self.spin_red_const = QDoubleSpinBox()
        self.config_spin(self.spin_red_const, -10000.0, 10000.0, 0.0)
        self.spin_red_const.valueChanged.connect(self.update_params)
        layout_red.addWidget(self.spin_red_const, 0, 1)
        
        # Senoidal
        self.chk_red_sine = QCheckBox("Ativar Senoidal")
        self.chk_red_sine.toggled.connect(self.update_params)
        layout_red.addWidget(self.chk_red_sine, 1, 0, 1, 2)
        
        layout_red.addWidget(QLabel("Amplitude (Nm):"), 2, 0)
        self.spin_red_amp = QDoubleSpinBox()
        self.config_spin(self.spin_red_amp, 0.0, 10000.0, 10.0)
        self.spin_red_amp.valueChanged.connect(self.update_params)
        layout_red.addWidget(self.spin_red_amp, 2, 1)
        
        layout_red.addWidget(QLabel("Frequência (Hz):"), 3, 0)
        self.spin_red_freq = QDoubleSpinBox()
        self.config_spin(self.spin_red_freq, 0.0, 20.0, 0.5, step=0.1)
        self.spin_red_freq.valueChanged.connect(self.update_params)
        layout_red.addWidget(self.spin_red_freq, 3, 1)
        
        self.lbl_red_out = QLabel("Saída Atual: 0.00 Nm")
        layout_red.addWidget(self.lbl_red_out, 4, 0, 1, 2)
        
        group_red.setLayout(layout_red)
        main_layout.addWidget(group_red)
        
        # ===== GRUPO VERDE =====
        group_green = QGroupBox("Cilindro Verde (Joint Cylinder Green)")
        group_green.setStyleSheet("QGroupBox { font-weight: bold; color: darkgreen; border: 1px solid darkgreen; }")
        layout_green = QGridLayout()
        
        # Constante
        layout_green.addWidget(QLabel("Torque Constante (Nm):"), 0, 0)
        self.spin_green_const = QDoubleSpinBox()
        self.config_spin(self.spin_green_const, -10000.0, 10000.0, 0.0)
        self.spin_green_const.valueChanged.connect(self.update_params)
        layout_green.addWidget(self.spin_green_const, 0, 1)
        
        # Senoidal
        self.chk_green_sine = QCheckBox("Ativar Senoidal")
        self.chk_green_sine.toggled.connect(self.update_params)
        layout_green.addWidget(self.chk_green_sine, 1, 0, 1, 2)
        
        layout_green.addWidget(QLabel("Amplitude (Nm):"), 2, 0)
        self.spin_green_amp = QDoubleSpinBox()
        self.config_spin(self.spin_green_amp, 0.0, 10000.0, 10.0)
        self.spin_green_amp.valueChanged.connect(self.update_params)
        layout_green.addWidget(self.spin_green_amp, 2, 1)
        
        layout_green.addWidget(QLabel("Frequência (Hz):"), 3, 0)
        self.spin_green_freq = QDoubleSpinBox()
        self.config_spin(self.spin_green_freq, 0.0, 20.0, 0.5, step=0.1)
        self.spin_green_freq.valueChanged.connect(self.update_params)
        layout_green.addWidget(self.spin_green_freq, 3, 1)
        
        self.lbl_green_out = QLabel("Saída Atual: 0.00 Nm")
        layout_green.addWidget(self.lbl_green_out, 4, 0, 1, 2)
        
        group_green.setLayout(layout_green)
        main_layout.addWidget(group_green)
        
        # ===== CONTROLES GERAIS =====
        self.btn_toggle = QPushButton("INICIAR APLICAÇÃO DE TORQUE")
        self.btn_toggle.setCheckable(True)
        self.btn_toggle.setStyleSheet("background-color: green; color: white; font-weight: bold; padding: 10px;")
        self.btn_toggle.toggled.connect(self.toggle_active)
        main_layout.addWidget(self.btn_toggle)
        
        self.setLayout(main_layout)
        self.resize(400, 500)

    def config_spin(self, spin, min_val, max_val, default, step=1.0):
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setSingleStep(step)
        spin.setDecimals(2)

    def update_params(self):
        # Vermelho
        self.red_const = self.spin_red_const.value()
        self.red_sine_active = self.chk_red_sine.isChecked()
        self.red_amp = self.spin_red_amp.value()
        self.red_freq = self.spin_red_freq.value()
        
        # Verde
        self.green_const = self.spin_green_const.value()
        self.green_sine_active = self.chk_green_sine.isChecked()
        self.green_amp = self.spin_green_amp.value()
        self.green_freq = self.spin_green_freq.value()

    def toggle_active(self, checked):
        self.active = checked
        if checked:
            self.btn_toggle.setText("PARAR APLICAÇÃO DE TORQUE")
            self.btn_toggle.setStyleSheet("background-color: red; color: white; font-weight: bold; padding: 10px;")
            self.t = 0.0 # Reinicia tempo ao ativar? Ou continua? Reiniciar garante fase 0.
        else:
            self.btn_toggle.setText("INICIAR APLICAÇÃO DE TORQUE")
            self.btn_toggle.setStyleSheet("background-color: green; color: white; font-weight: bold; padding: 10px;")
            # Zera saídas ao parar
            self.publish_torque(self.pub_red, 0.0)
            self.publish_torque(self.pub_green, 0.0)
            self.lbl_red_out.setText("Saída Atual: 0.00 Nm (PARADO)")
            self.lbl_green_out.setText("Saída Atual: 0.00 Nm (PARADO)")

    def control_loop(self):
        if not self.active:
            return
            
        dt = 1.0 / self.output_freq
        self.t += dt
        
        # Cálculo Vermelho
        torque_red = self.red_const
        if self.red_sine_active:
            torque_red += self.red_amp * math.sin(2 * math.pi * self.red_freq * self.t)
            
        # Cálculo Verde
        torque_green = self.green_const
        if self.green_sine_active:
            torque_green += self.green_amp * math.sin(2 * math.pi * self.green_freq * self.t)
            
        # Publicar
        self.publish_torque(self.pub_red, torque_red)
        self.publish_torque(self.pub_green, torque_green)
        
        # Atualizar Labels
        self.lbl_red_out.setText(f"Saída Atual: {torque_red:.2f} Nm")
        self.lbl_green_out.setText(f"Saída Atual: {torque_green:.2f} Nm")

    def publish_torque(self, publisher, value):
        msg = Double()
        msg.data = value
        publisher.publish(msg)

def main():
    app = QApplication(sys.argv)
    gui = TorqueControlGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
