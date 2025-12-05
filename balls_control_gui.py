#!/usr/bin/env python3
"""
Interface Gráfica - Controle das Esferas Giratórias
Controla a velocidade de rotação das 3 esferas
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QGridLayout, QLabel, QSlider,
    QPushButton, QDoubleSpinBox
)
from PyQt5.QtCore import Qt

# Gazebo Transport
try:
    from gz.transport13 import Node
    from gz.msgs10.double_pb2 import Double
except ImportError:
    print("ERRO: Instale: sudo apt install python3-gz-transport13 python3-gz-msgs10")
    sys.exit(1)


class VerticalBarsControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle das Esferas Giratórias")
        
        # Nó Gazebo
        self.node = Node()
        
        # Publishers para as 3 esferas
        self.pub_sphere1 = self.node.advertise(
            "/model/three_link_model/joint/joint_sphere_1/cmd_vel", Double
        )
        self.pub_sphere2 = self.node.advertise(
            "/model/three_link_model/joint/joint_sphere_2/cmd_vel", Double
        )
        self.pub_sphere3 = self.node.advertise(
            "/model/three_link_model/joint/joint_sphere_3/cmd_vel", Double
        )
        
        # Velocidades atuais (rad/s)
        self.vel_sphere1 = 0.0
        self.vel_sphere2 = 0.0
        self.vel_sphere3 = 0.0
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # ===== ESFERA 1 (Cinza - Eixo Y) =====
        group_sphere1 = QGroupBox("Esfera 1 (Cinza - Eixo Y)")
        grid_sphere1 = QGridLayout()
        
        lbl_vel1 = QLabel("Velocidade (rad/s):")
        
        # Slider (-10 a +10 rad/s)
        self.slider_sphere1 = QSlider(Qt.Horizontal)
        self.slider_sphere1.setMinimum(-1000)  # -10.0 rad/s
        self.slider_sphere1.setMaximum(1000)   # +10.0 rad/s
        self.slider_sphere1.setValue(0)
        self.slider_sphere1.valueChanged.connect(self.on_slider_sphere1_changed)
        
        # SpinBox
        self.spin_sphere1 = QDoubleSpinBox()
        self.spin_sphere1.setRange(-10.0, 10.0)
        self.spin_sphere1.setDecimals(3)
        self.spin_sphere1.setSingleStep(0.1)
        self.spin_sphere1.setValue(0.0)
        self.spin_sphere1.valueChanged.connect(self.on_spin_sphere1_changed)
        
        # Label RPM
        self.lbl_rpm1 = QLabel("0.00 RPM")
        
        grid_sphere1.addWidget(lbl_vel1, 0, 0)
        grid_sphere1.addWidget(self.slider_sphere1, 0, 1)
        grid_sphere1.addWidget(self.spin_sphere1, 0, 2)
        grid_sphere1.addWidget(self.lbl_rpm1, 1, 1)
        
        group_sphere1.setLayout(grid_sphere1)
        layout.addWidget(group_sphere1)
        
        # ===== ESFERA 2 (Vermelha - +60°) =====
        group_sphere2 = QGroupBox("Esfera 2 (Vermelha - +60°)")
        grid_sphere2 = QGridLayout()
        
        lbl_vel2 = QLabel("Velocidade (rad/s):")
        
        self.slider_sphere2 = QSlider(Qt.Horizontal)
        self.slider_sphere2.setMinimum(-1000)
        self.slider_sphere2.setMaximum(1000)
        self.slider_sphere2.setValue(0)
        self.slider_sphere2.valueChanged.connect(self.on_slider_sphere2_changed)
        
        self.spin_sphere2 = QDoubleSpinBox()
        self.spin_sphere2.setRange(-10.0, 10.0)
        self.spin_sphere2.setDecimals(3)
        self.spin_sphere2.setSingleStep(0.1)
        self.spin_sphere2.setValue(0.0)
        self.spin_sphere2.valueChanged.connect(self.on_spin_sphere2_changed)
        
        self.lbl_rpm2 = QLabel("0.00 RPM")
        
        grid_sphere2.addWidget(lbl_vel2, 0, 0)
        grid_sphere2.addWidget(self.slider_sphere2, 0, 1)
        grid_sphere2.addWidget(self.spin_sphere2, 0, 2)
        grid_sphere2.addWidget(self.lbl_rpm2, 1, 1)
        
        group_sphere2.setLayout(grid_sphere2)
        layout.addWidget(group_sphere2)
        
        # ===== ESFERA 3 (Azul - -60°) =====
        group_sphere3 = QGroupBox("Esfera 3 (Azul - -60°)")
        grid_sphere3 = QGridLayout()
        
        lbl_vel3 = QLabel("Velocidade (rad/s):")
        
        self.slider_sphere3 = QSlider(Qt.Horizontal)
        self.slider_sphere3.setMinimum(-1000)
        self.slider_sphere3.setMaximum(1000)
        self.slider_sphere3.setValue(0)
        self.slider_sphere3.valueChanged.connect(self.on_slider_sphere3_changed)
        
        self.spin_sphere3 = QDoubleSpinBox()
        self.spin_sphere3.setRange(-10.0, 10.0)
        self.spin_sphere3.setDecimals(3)
        self.spin_sphere3.setSingleStep(0.1)
        self.spin_sphere3.setValue(0.0)
        self.spin_sphere3.valueChanged.connect(self.on_spin_sphere3_changed)
        
        self.lbl_rpm3 = QLabel("0.00 RPM")
        
        grid_sphere3.addWidget(lbl_vel3, 0, 0)
        grid_sphere3.addWidget(self.slider_sphere3, 0, 1)
        grid_sphere3.addWidget(self.spin_sphere3, 0, 2)
        grid_sphere3.addWidget(self.lbl_rpm3, 1, 1)
        
        group_sphere3.setLayout(grid_sphere3)
        layout.addWidget(group_sphere3)
        
        # ===== BOTÕES DE PRESET =====
        group_preset = QGroupBox("Presets")
        btn_layout = QHBoxLayout()
        
        btn_20rpm = QPushButton("Todas 20 RPM")
        btn_20rpm.clicked.connect(lambda: self.set_all_rpm(20))
        btn_20rpm.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        btn_stop = QPushButton("Parar Todas")
        btn_stop.clicked.connect(lambda: self.set_all_rpm(0))
        btn_stop.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        
        btn_reverse = QPushButton("Inverter Todas")
        btn_reverse.clicked.connect(self.reverse_all)
        btn_reverse.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        
        btn_layout.addWidget(btn_20rpm)
        btn_layout.addWidget(btn_stop)
        btn_layout.addWidget(btn_reverse)
        
        group_preset.setLayout(btn_layout)
        layout.addWidget(group_preset)
        
        # ===== BOTÃO SAIR =====
        btn_quit = QPushButton("Sair")
        btn_quit.clicked.connect(self.close)
        layout.addWidget(btn_quit)
        
        self.setLayout(layout)
        self.resize(600, 400)

    # ===== CALLBACKS ESFERA 1 =====
    def on_slider_sphere1_changed(self, value):
        val_float = value / 100.0
        self.vel_sphere1 = val_float
        self.spin_sphere1.blockSignals(True)
        self.spin_sphere1.setValue(val_float)
        self.spin_sphere1.blockSignals(False)
        self.update_rpm_label(1, val_float)
        self.send_velocity(1, val_float)

    def on_spin_sphere1_changed(self, value):
        self.vel_sphere1 = value
        self.slider_sphere1.blockSignals(True)
        self.slider_sphere1.setValue(int(value * 100))
        self.slider_sphere1.blockSignals(False)
        self.update_rpm_label(1, value)
        self.send_velocity(1, value)

    # ===== CALLBACKS ESFERA 2 =====
    def on_slider_sphere2_changed(self, value):
        val_float = value / 100.0
        self.vel_sphere2 = val_float
        self.spin_sphere2.blockSignals(True)
        self.spin_sphere2.setValue(val_float)
        self.spin_sphere2.blockSignals(False)
        self.update_rpm_label(2, val_float)
        self.send_velocity(2, val_float)

    def on_spin_sphere2_changed(self, value):
        self.vel_sphere2 = value
        self.slider_sphere2.blockSignals(True)
        self.slider_sphere2.setValue(int(value * 100))
        self.slider_sphere2.blockSignals(False)
        self.update_rpm_label(2, value)
        self.send_velocity(2, value)

    # ===== CALLBACKS ESFERA 3 =====
    def on_slider_sphere3_changed(self, value):
        val_float = value / 100.0
        self.vel_sphere3 = val_float
        self.spin_sphere3.blockSignals(True)
        self.spin_sphere3.setValue(val_float)
        self.spin_sphere3.blockSignals(False)
        self.update_rpm_label(3, val_float)
        self.send_velocity(3, val_float)

    def on_spin_sphere3_changed(self, value):
        self.vel_sphere3 = value
        self.slider_sphere3.blockSignals(True)
        self.slider_sphere3.setValue(int(value * 100))
        self.slider_sphere3.blockSignals(False)
        self.update_rpm_label(3, value)
        self.send_velocity(3, value)

    # ===== FUNÇÕES AUXILIARES =====
    def update_rpm_label(self, bar_num, rad_per_sec):
        """Converte rad/s para RPM e atualiza o label."""
        rpm = rad_per_sec * 60 / (2 * 3.14159265359)
        if bar_num == 1:
            self.lbl_rpm1.setText(f"{rpm:.2f} RPM")
        elif bar_num == 2:
            self.lbl_rpm2.setText(f"{rpm:.2f} RPM")
        elif bar_num == 3:
            self.lbl_rpm3.setText(f"{rpm:.2f} RPM")

    def send_velocity(self, sphere_num, velocity):
        """Envia comando de velocidade para a esfera especificada."""
        msg = Double()
        msg.data = velocity
        
        if sphere_num == 1:
            self.pub_sphere1.publish(msg)
        elif sphere_num == 2:
            self.pub_sphere2.publish(msg)
        elif sphere_num == 3:
            self.pub_sphere3.publish(msg)

    def set_all_rpm(self, rpm):
        """Define a mesma velocidade (em RPM) para todas as esferas."""
        rad_per_sec = rpm * 2 * 3.14159265359 / 60
        
        self.spin_sphere1.setValue(rad_per_sec)
        self.spin_sphere2.setValue(rad_per_sec)
        self.spin_sphere3.setValue(rad_per_sec)

    def reverse_all(self):
        """Inverte a direção de rotação de todas as esferas."""
        self.spin_sphere1.setValue(-self.vel_sphere1)
        self.spin_sphere2.setValue(-self.vel_sphere2)
        self.spin_sphere3.setValue(-self.vel_sphere3)


def main():
    app = QApplication(sys.argv)
    gui = VerticalBarsControlGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
