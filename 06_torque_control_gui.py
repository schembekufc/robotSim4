#!/usr/bin/env python3
"""
GUI de Controle de Torque (Constante + Senoidal) para Cilindros
Controla:
- /model/three_link_model/joint/joint_cylinder/cmd_force (Vermelho)
- /model/three_link_model/joint/joint_cylinder_green/cmd_force (Verde)

SINCRONIZAÇÃO:
Usa o tempo de simulação do Gazebo (/world/.../stats) para gerar as senoides,
garantindo frequência correta independente do Real Time Factor.
"""

import sys
import math
import time
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QGridLayout, QLabel, QPushButton, 
    QSlider, QDoubleSpinBox, QCheckBox, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor

# Gazebo Transport
try:
    from gz.transport13 import Node
    from gz.msgs10.double_pb2 import Double
    from gz.msgs10.world_stats_pb2 import WorldStatistics
except ImportError:
    print("ERRO: Instale: sudo apt install python3-gz-transport13 python3-gz-msgs10")
    sys.exit(1)

# Configurações de Tópicos
TOPIC_RED = "/model/three_link_model/joint/joint_cylinder/cmd_force"
TOPIC_GREEN = "/model/three_link_model/joint/joint_cylinder_green/cmd_force"
# Nome do mundo no SDF é "three_link_with_tracker_plate_world"
TOPIC_STATS = "/world/three_link_with_tracker_plate_world/stats"

class TorqueControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle de Torque Sincronizado - FRONTIER")
        
        self.node = Node()
        self.pub_red = self.node.advertise(TOPIC_RED, Double)
        self.pub_green = self.node.advertise(TOPIC_GREEN, Double)
        
        # Subscribe to World Stats
        self.node.subscribe(WorldStatistics, TOPIC_STATS, self.on_world_stats)
        
        # Estado do Tempo Simulado
        self.sim_time = 0.0
        self.last_sim_time = 0.0
        self.active = False
        
        # Parâmetros Vermelho
        self.red_const = 0.0
        self.red_sine_active = False
        self.red_amp = 200.0
        self.red_freq = 2.0
        
        # Parâmetros Verde
        self.green_const = 0.0
        self.green_sine_active = False
        self.green_amp = 200.0
        self.green_freq = 0.5
        
        self.apply_light_theme()
        self.init_ui()
        
        # Timer de Controle (50 Hz)
        # O timer serve para atualizar a UI e enviar comandos periodicamente
        self.output_freq = 50.0
        self.timer = QTimer()
        self.timer.timeout.connect(self.control_loop)
        self.timer.start(int(1000/self.output_freq))

    def on_world_stats(self, msg):
        # Callback executado em outra thread pelo gz-transport
        # Converte sim_time (sec + nsec) para float
        self.sim_time = msg.sim_time.sec + (msg.sim_time.nsec * 1e-9)

    def apply_light_theme(self):
        # Configurar Palette Light Moderno
        self.setStyle(QApplication.style())
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(0, 100, 200))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
        
        # Fonte Global
        font = QFont("Segoe UI", 10) 
        if not font.exactMatch():
            font = QFont("Roboto", 10)
        self.setFont(font)

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        lbl_title = QLabel("CONTROLE SINCRONIZADO (SIM TIME)")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; letter-spacing: 1px;")
        main_layout.addWidget(lbl_title)
        
        # Display do Tempo
        self.lbl_time = QLabel("Sim Time: 0.00 s")
        self.lbl_time.setAlignment(Qt.AlignCenter)
        self.lbl_time.setStyleSheet("font-size: 12px; color: #555;")
        main_layout.addWidget(self.lbl_time)
        
        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #ccc;")
        main_layout.addWidget(line)

        # ===== GRUPO VERMELHO =====
        self.group_red = self.create_control_group(
            "Cilindro Vermelho (Joint Cylinder)", 
            "#D32F2F", 
            "#FFEBEE", 
            self.red_const, self.red_amp, self.red_freq
        )
        main_layout.addWidget(self.group_red['groupbox'])
        
        # Conectar Sinais
        self.group_red['spin_const'].valueChanged.connect(self.update_params)
        self.group_red['chk_sine'].toggled.connect(self.update_params)
        self.group_red['spin_amp'].valueChanged.connect(self.update_params)
        self.group_red['spin_freq'].valueChanged.connect(self.update_params)

        # ===== GRUPO VERDE =====
        self.group_green = self.create_control_group(
            "Cilindro Verde (Joint Cylinder Green)", 
            "#2E7D32", 
            "#E8F5E9", 
            self.green_const, self.green_amp, self.green_freq
        )
        main_layout.addWidget(self.group_green['groupbox'])

        # Conectar Sinais
        self.group_green['spin_const'].valueChanged.connect(self.update_params)
        self.group_green['chk_sine'].toggled.connect(self.update_params)
        self.group_green['spin_amp'].valueChanged.connect(self.update_params)
        self.group_green['spin_freq'].valueChanged.connect(self.update_params)
        
        # Espaçador
        main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # ===== BOTÃO AÇÃO =====
        self.btn_toggle = QPushButton("INICIAR CONTROLE")
        self.btn_toggle.setCheckable(True)
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setFixedHeight(50)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 8px;
                border: 1px solid #1B5E20;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:checked {
                background-color: #C62828;
                border: 1px solid #B71C1C;
            }
            QPushButton:checked:hover {
                background-color: #D32F2F;
            }
        """)
        self.btn_toggle.toggled.connect(self.toggle_active)
        main_layout.addWidget(self.btn_toggle)
        
        self.setLayout(main_layout)
        self.resize(450, 600)

    def create_control_group(self, title, color_hex, bg_hex, default_const, default_amp, default_freq):
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                color: {color_hex};
                border: 1px solid #ccc;
                border-radius: 8px;
                margin-top: 12px;
                background-color: {bg_hex};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        
        layout = QGridLayout()
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(10)
        
        spin_style = """
            QDoubleSpinBox {
                background-color: #ffffff;
                color: #000;
                border: 1px solid #aaa;
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
            }
            QDoubleSpinBox:hover {
                border: 1px solid #0078d7;
            }
        """

        def create_reset_btn(target_spin):
            btn = QPushButton("0")
            btn.setFixedSize(24, 24)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip("Zerar valor")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #eee;
                    color: #555;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: #ddd;
                    color: #000;
                    border: 1px solid #999;
                }}
            """)
            btn.clicked.connect(lambda: target_spin.setValue(0.0))
            return btn

        # Linha 1: Constante
        layout.addWidget(QLabel("Torque Constante (Nm):"), 0, 0)
        spin_const = QDoubleSpinBox()
        self.config_spin(spin_const, -10000.0, 10000.0, default_const)
        spin_const.setStyleSheet(spin_style)
        layout.addWidget(spin_const, 0, 1)
        # Reset
        layout.addWidget(create_reset_btn(spin_const), 0, 2)
        
        # Linha 2: Checkbox
        chk_sine = QCheckBox("Ativar Onda Senoidal")
        chk_sine.setStyleSheet(f"QCheckBox {{ color: #000; }}")
        layout.addWidget(chk_sine, 1, 0, 1, 3)
        
        # Linha 3: Amplitude
        layout.addWidget(QLabel("Amplitude (Nm):"), 2, 0)
        spin_amp = QDoubleSpinBox()
        self.config_spin(spin_amp, 0.0, 10000.0, default_amp)
        spin_amp.setStyleSheet(spin_style)
        layout.addWidget(spin_amp, 2, 1)
        # Reset
        layout.addWidget(create_reset_btn(spin_amp), 2, 2)
        
        # Linha 4: Frequência
        layout.addWidget(QLabel("Frequência (Hz):"), 3, 0)
        spin_freq = QDoubleSpinBox()
        self.config_spin(spin_freq, 0.0, 50.0, default_freq, step=0.1)
        spin_freq.setStyleSheet(spin_style)
        layout.addWidget(spin_freq, 3, 1)
        # Reset
        layout.addWidget(create_reset_btn(spin_freq), 3, 2)
        
        # Linha 5: Saída
        lbl_out = QLabel("0.00 Nm")
        lbl_out.setAlignment(Qt.AlignCenter)
        lbl_out.setStyleSheet(f"""
            background-color: #ffffff; 
            color: {color_hex}; 
            font-family: 'Courier New'; 
            font-size: 18px; 
            font-weight: bold; 
            border: 1px solid #bbb; 
            border-radius: 6px; 
            padding: 8px;
        """)
        layout.addWidget(lbl_out, 4, 0, 1, 3)
        
        group.setLayout(layout)
        
        return {
            'groupbox': group,
            'spin_const': spin_const,
            'chk_sine': chk_sine,
            'spin_amp': spin_amp,
            'spin_freq': spin_freq,
            'lbl_out': lbl_out
        }

    def config_spin(self, spin, min_val, max_val, default, step=1.0):
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setSingleStep(step)
        spin.setDecimals(2)

    def update_params(self):
        # Vermelho
        self.red_const = self.group_red['spin_const'].value()
        self.red_sine_active = self.group_red['chk_sine'].isChecked()
        self.red_amp = self.group_red['spin_amp'].value()
        self.red_freq = self.group_red['spin_freq'].value()
        
        # Verde
        self.green_const = self.group_green['spin_const'].value()
        self.green_sine_active = self.group_green['chk_sine'].isChecked()
        self.green_amp = self.group_green['spin_amp'].value()
        self.green_freq = self.group_green['spin_freq'].value()

    def toggle_active(self, checked):
        self.active = checked
        if checked:
            self.btn_toggle.setText("PARAR APLICAÇÃO DE TORQUE")
        else:
            self.btn_toggle.setText("INICIAR CONTROLE")
            self.publish_torque(self.pub_red, 0.0)
            self.publish_torque(self.pub_green, 0.0)
            self.group_red['lbl_out'].setText("PARADO")
            self.group_green['lbl_out'].setText("PARADO")

    def control_loop(self):
        # Atualiza display de tempo
        self.lbl_time.setText(f"Sim Time: {self.sim_time:.3f} s")
        
        if not self.active:
            return
            
        # Usa o tempo de simulação para o cálculo
        t = self.sim_time
        
        # Cálculo Vermelho
        torque_red = self.red_const
        if self.red_sine_active:
            torque_red += self.red_amp * math.sin(2 * math.pi * self.red_freq * t)
            
        # Cálculo Verde
        torque_green = self.green_const
        if self.green_sine_active:
            torque_green += self.green_amp * math.sin(2 * math.pi * self.green_freq * t)
            
        # Publicar
        self.publish_torque(self.pub_red, torque_red)
        self.publish_torque(self.pub_green, torque_green)
        
        # Atualizar Labels
        self.group_red['lbl_out'].setText(f"{torque_red:.2f} Nm")
        self.group_green['lbl_out'].setText(f"{torque_green:.2f} Nm")

    def publish_torque(self, publisher, value):
        msg = Double()
        msg.data = value
        publisher.publish(msg)

def main():
    app = QApplication(sys.argv)
    
    # Enable High DPI display
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
    gui = TorqueControlGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
