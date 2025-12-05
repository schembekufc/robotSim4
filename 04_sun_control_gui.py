#!/usr/bin/env python3
import sys
import math

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QGroupBox, QGridLayout, QLabel, QSlider,
    QPushButton, QHBoxLayout, QDoubleSpinBox
)
from PyQt5.QtCore import Qt

# Gazebo Transport
try:
    from gz.transport13 import Node
    from gz.msgs10.light_pb2 import Light
except ImportError:
    print("ERRO: Instale: sudo apt install python3-gz-transport13 python3-gz-msgs10")
    sys.exit(1)


WORLD_NAME = "three_link_with_tracker_plate_world"
LIGHT_NAME = "sun"


class SunControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle do Sol - Gazebo (light_config)")

        self.node = Node()
        self.topic = f"/world/{WORLD_NAME}/light_config"
        self.pub_light = self.node.advertise(self.topic, Light)

        # Estado em graus
        self.azimute_deg = -45.0   # 0 = +X, 90 = +Y
        self.elevacao_deg = 45.0   # 0 = horizontal, 90 = z+
        self.intensity = 10.0      # Intensidade inicial

        # Raio da "órbita" do sol
        self.raio = 100.0

        self.init_ui()
        self.enviar_light_config()

    def init_ui(self):
        layout = QVBoxLayout()

        group = QGroupBox("Parâmetros do Sol")
        grid = QGridLayout()

        # --- Azimute ---
        self.lbl_az = QLabel("Azimute (°):")
        
        # Slider Azimute (-180 a 180)
        self.slider_az = QSlider(Qt.Horizontal)
        self.slider_az.setMinimum(-18000) # x100 para 2 casas decimais
        self.slider_az.setMaximum(18000)
        self.slider_az.setValue(int(self.azimute_deg * 100))
        self.slider_az.valueChanged.connect(self.on_slider_az_changed)

        # SpinBox Azimute
        self.spin_az = QDoubleSpinBox()
        self.spin_az.setRange(-180.0, 180.0)
        self.spin_az.setDecimals(2)
        self.spin_az.setSingleStep(0.1)
        self.spin_az.setValue(self.azimute_deg)
        self.spin_az.valueChanged.connect(self.on_spin_az_changed)

        # --- Elevação ---
        self.lbl_el = QLabel("Elevação (°):")

        # Slider Elevação (0 a 90)
        self.slider_el = QSlider(Qt.Horizontal)
        self.slider_el.setMinimum(0)
        self.slider_el.setMaximum(9000) # x100 para 2 casas decimais
        self.slider_el.setValue(int(self.elevacao_deg * 100))
        self.slider_el.valueChanged.connect(self.on_slider_el_changed)

        # SpinBox Elevação
        self.spin_el = QDoubleSpinBox()
        self.spin_el.setRange(0.0, 90.0)
        self.spin_el.setDecimals(2)
        self.spin_el.setSingleStep(0.1)
        self.spin_el.setValue(self.elevacao_deg)
        self.spin_el.valueChanged.connect(self.on_spin_el_changed)

        # --- Intensidade ---
        self.lbl_int = QLabel("Intensidade:")

        # Slider Intensidade (1 a 10)
        self.slider_int = QSlider(Qt.Horizontal)
        self.slider_int.setMinimum(100)  # 1.00
        self.slider_int.setMaximum(1000) # 10.00
        self.slider_int.setValue(int(self.intensity * 100))
        self.slider_int.valueChanged.connect(self.on_slider_int_changed)

        # SpinBox Intensidade
        self.spin_int = QDoubleSpinBox()
        self.spin_int.setRange(1.0, 10.0)
        self.spin_int.setDecimals(2)
        self.spin_int.setSingleStep(0.1)
        self.spin_int.setValue(self.intensity)
        self.spin_int.valueChanged.connect(self.on_spin_int_changed)

        # Adicionando ao Grid
        # Row 0: Azimute
        grid.addWidget(self.lbl_az, 0, 0)
        grid.addWidget(self.slider_az, 0, 1)
        grid.addWidget(self.spin_az, 0, 2)

        # Row 1: Elevação
        grid.addWidget(self.lbl_el, 1, 0)
        grid.addWidget(self.slider_el, 1, 1)
        grid.addWidget(self.spin_el, 1, 2)

        # Row 2: Intensidade
        grid.addWidget(self.lbl_int, 2, 0)
        grid.addWidget(self.slider_int, 2, 1)
        grid.addWidget(self.spin_int, 2, 2)

        group.setLayout(grid)
        layout.addWidget(group)

        self.lbl_topic = QLabel(f"Tópico luz: {self.topic}  |  nome: {LIGHT_NAME}")
        layout.addWidget(self.lbl_topic)

        btn_quit = QPushButton("Sair")
        btn_quit.clicked.connect(self.close)
        layout.addWidget(btn_quit)

        self.setLayout(layout)
        self.resize(600, 250)

    # --- Callbacks Azimute ---
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

    # --- Callbacks Elevação ---
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

    # --- Callbacks Intensidade ---
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
        """
        Publica Light no /world/.../light_config.
        Ajusta posição (pose.position) e direção (direction) do sol,
        mantendo cast_shadows = true e parâmetros básicos.
        """
        az = math.radians(self.azimute_deg)
        el = math.radians(self.elevacao_deg)

        # posição na esfera
        x = self.raio * math.cos(el) * math.cos(az)
        y = self.raio * math.cos(el) * math.sin(az)
        z = self.raio * math.sin(el)

        # direção: da luz para a origem (0,0,0)
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

        # posição
        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.position.z = z
        msg.pose.orientation.w = 1.0
        msg.pose.orientation.x = 0.0
        msg.pose.orientation.y = 0.0
        msg.pose.orientation.z = 0.0

        # direção
        msg.direction.x = dx
        msg.direction.y = dy
        msg.direction.z = dz

        # sombras
        msg.cast_shadows = True

        # intensidade e cores (como no SDF)
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
    gui = SunControlGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

