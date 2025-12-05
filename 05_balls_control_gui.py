#!/usr/bin/env python3
"""
Interface Gráfica - Controle Oscilatório das Esferas
Controla o movimento de vai e vem das 3 esferas com frequências de 0.1 Hz a 10 Hz
"""
import sys
import math
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QGridLayout, QLabel, QSlider,
    QPushButton, QDoubleSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer

# Gazebo Transport
try:
    from gz.transport13 import Node
    from gz.msgs10.double_pb2 import Double
except ImportError:
    print("ERRO: Instale: sudo apt install python3-gz-transport13 python3-gz-msgs10")
    sys.exit(1)


class OscillatoryControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle Oscilatório das Esferas (Vai e Vem)")
        
        # Nó Gazebo
        self.node = Node()
        
        # Publishers para as 3 esferas (POSIÇÃO)
        self.pub_sphere1 = self.node.advertise(
            "/model/three_link_model/joint/joint_sphere_1/cmd_pos", Double
        )
        self.pub_sphere2 = self.node.advertise(
            "/model/three_link_model/joint/joint_sphere_2/cmd_pos", Double
        )
        self.pub_sphere3 = self.node.advertise(
            "/model/three_link_model/joint/joint_sphere_3/cmd_pos", Double
        )
        
        # Parâmetros de oscilação para cada esfera
        self.freq_sphere1 = 1.0  # Hz
        self.freq_sphere2 = 1.0  # Hz
        self.freq_sphere3 = 1.0  # Hz
        
        self.amplitude_sphere1 = 0.5  # metros (deslocamento máximo)
        self.amplitude_sphere2 = 0.5  # metros
        self.amplitude_sphere3 = 0.5  # metros
        
        self.enabled_sphere1 = False
        self.enabled_sphere2 = False
        self.enabled_sphere3 = False
        
        # Tempo inicial
        self.start_time = time.time()
        
        self.init_ui()
        
        # Timer para atualizar as velocidades
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_oscillations)
        self.timer.start(50)  # Atualiza a cada 50ms (20 Hz)

    def init_ui(self):
        layout = QVBoxLayout()
        
        # ===== ESFERA 1 (Verde - Eixo X) =====
        group_sphere1 = QGroupBox("Esfera 1 (Verde - Eixo X)")
        group_sphere1.setStyleSheet("QGroupBox::title { color: green; font: bold; }")
        grid_sphere1 = QGridLayout()
        
        # Checkbox para habilitar
        self.check_sphere1 = QCheckBox("Habilitar Oscilação")
        self.check_sphere1.stateChanged.connect(self.on_check_sphere1_changed)
        grid_sphere1.addWidget(self.check_sphere1, 0, 0, 1, 3)
        
        # Frequência
        lbl_freq1 = QLabel("Frequência (Hz):")
        self.slider_freq1 = QSlider(Qt.Horizontal)
        self.slider_freq1.setMinimum(1)    # 0.1 Hz
        self.slider_freq1.setMaximum(100)  # 10.0 Hz
        self.slider_freq1.setValue(10)     # 1.0 Hz
        self.slider_freq1.valueChanged.connect(self.on_freq1_changed)
        
        self.spin_freq1 = QDoubleSpinBox()
        self.spin_freq1.setRange(0.1, 10.0)
        self.spin_freq1.setDecimals(2)
        self.spin_freq1.setSingleStep(0.1)
        self.spin_freq1.setValue(1.0)
        self.spin_freq1.valueChanged.connect(self.on_spin_freq1_changed)
        
        grid_sphere1.addWidget(lbl_freq1, 1, 0)
        grid_sphere1.addWidget(self.slider_freq1, 1, 1)
        grid_sphere1.addWidget(self.spin_freq1, 1, 2)
        
        # Amplitude (deslocamento máximo)
        lbl_amp1 = QLabel("Amplitude (metros):")
        self.slider_amp1 = QSlider(Qt.Horizontal)
        self.slider_amp1.setMinimum(0)     # 0.0 m
        self.slider_amp1.setMaximum(100)   # 1.0 m
        self.slider_amp1.setValue(50)      # 0.5 m
        self.slider_amp1.valueChanged.connect(self.on_amp1_changed)
        
        self.spin_amp1 = QDoubleSpinBox()
        self.spin_amp1.setRange(0.0, 1.0)
        self.spin_amp1.setDecimals(2)
        self.spin_amp1.setSingleStep(0.01)
        self.spin_amp1.setValue(0.5)
        self.spin_amp1.valueChanged.connect(self.on_spin_amp1_changed)
        
        grid_sphere1.addWidget(lbl_amp1, 2, 0)
        grid_sphere1.addWidget(self.slider_amp1, 2, 1)
        grid_sphere1.addWidget(self.spin_amp1, 2, 2)
        
        # Label de status
        self.lbl_status1 = QLabel("Status: Parado")
        self.lbl_status1.setStyleSheet("color: red; font-weight: bold;")
        grid_sphere1.addWidget(self.lbl_status1, 3, 0, 1, 3)
        
        group_sphere1.setLayout(grid_sphere1)
        layout.addWidget(group_sphere1)
        
        # ===== ESFERA 2 (Vermelha - Eixo Y) =====
        group_sphere2 = QGroupBox("Esfera 2 (Vermelha - Eixo Y)")
        group_sphere2.setStyleSheet("QGroupBox::title { color: red; font: bold; }")
        grid_sphere2 = QGridLayout()
        
        self.check_sphere2 = QCheckBox("Habilitar Oscilação")
        self.check_sphere2.stateChanged.connect(self.on_check_sphere2_changed)
        grid_sphere2.addWidget(self.check_sphere2, 0, 0, 1, 3)
        
        lbl_freq2 = QLabel("Frequência (Hz):")
        self.slider_freq2 = QSlider(Qt.Horizontal)
        self.slider_freq2.setMinimum(1)
        self.slider_freq2.setMaximum(100)
        self.slider_freq2.setValue(10)
        self.slider_freq2.valueChanged.connect(self.on_freq2_changed)
        
        self.spin_freq2 = QDoubleSpinBox()
        self.spin_freq2.setRange(0.1, 10.0)
        self.spin_freq2.setDecimals(2)
        self.spin_freq2.setSingleStep(0.1)
        self.spin_freq2.setValue(1.0)
        self.spin_freq2.valueChanged.connect(self.on_spin_freq2_changed)
        
        grid_sphere2.addWidget(lbl_freq2, 1, 0)
        grid_sphere2.addWidget(self.slider_freq2, 1, 1)
        grid_sphere2.addWidget(self.spin_freq2, 1, 2)
        
        lbl_amp2 = QLabel("Amplitude (metros):")
        self.slider_amp2 = QSlider(Qt.Horizontal)
        self.slider_amp2.setMinimum(0)     # 0.0 m
        self.slider_amp2.setMaximum(100)   # 1.0 m
        self.slider_amp2.setValue(50)      # 0.5 m
        self.slider_amp2.valueChanged.connect(self.on_amp2_changed)
        
        self.spin_amp2 = QDoubleSpinBox()
        self.spin_amp2.setRange(0.0, 1.0)
        self.spin_amp2.setDecimals(2)
        self.spin_amp2.setSingleStep(0.01)
        self.spin_amp2.setValue(0.5)
        self.spin_amp2.valueChanged.connect(self.on_spin_amp2_changed)
        
        grid_sphere2.addWidget(lbl_amp2, 2, 0)
        grid_sphere2.addWidget(self.slider_amp2, 2, 1)
        grid_sphere2.addWidget(self.spin_amp2, 2, 2)
        
        self.lbl_status2 = QLabel("Status: Parado")
        self.lbl_status2.setStyleSheet("color: red; font-weight: bold;")
        grid_sphere2.addWidget(self.lbl_status2, 3, 0, 1, 3)
        
        group_sphere2.setLayout(grid_sphere2)
        layout.addWidget(group_sphere2)
        
        # ===== ESFERA 3 (Azul - Eixo Z) =====
        group_sphere3 = QGroupBox("Esfera 3 (Azul - Eixo Z)")
        group_sphere3.setStyleSheet("QGroupBox::title { color: blue; font: bold; }")
        grid_sphere3 = QGridLayout()
        
        self.check_sphere3 = QCheckBox("Habilitar Oscilação")
        self.check_sphere3.stateChanged.connect(self.on_check_sphere3_changed)
        grid_sphere3.addWidget(self.check_sphere3, 0, 0, 1, 3)
        
        lbl_freq3 = QLabel("Frequência (Hz):")
        self.slider_freq3 = QSlider(Qt.Horizontal)
        self.slider_freq3.setMinimum(1)
        self.slider_freq3.setMaximum(100)
        self.slider_freq3.setValue(10)
        self.slider_freq3.valueChanged.connect(self.on_freq3_changed)
        
        self.spin_freq3 = QDoubleSpinBox()
        self.spin_freq3.setRange(0.1, 10.0)
        self.spin_freq3.setDecimals(2)
        self.spin_freq3.setSingleStep(0.1)
        self.spin_freq3.setValue(1.0)
        self.spin_freq3.valueChanged.connect(self.on_spin_freq3_changed)
        
        grid_sphere3.addWidget(lbl_freq3, 1, 0)
        grid_sphere3.addWidget(self.slider_freq3, 1, 1)
        grid_sphere3.addWidget(self.spin_freq3, 1, 2)
        
        lbl_amp3 = QLabel("Amplitude (metros):")
        self.slider_amp3 = QSlider(Qt.Horizontal)
        self.slider_amp3.setMinimum(0)     # 0.0 m
        self.slider_amp3.setMaximum(100)   # 1.0 m
        self.slider_amp3.setValue(50)      # 0.5 m
        self.slider_amp3.valueChanged.connect(self.on_amp3_changed)
        
        self.spin_amp3 = QDoubleSpinBox()
        self.spin_amp3.setRange(0.0, 1.0)
        self.spin_amp3.setDecimals(2)
        self.spin_amp3.setSingleStep(0.01)
        self.spin_amp3.setValue(0.5)
        self.spin_amp3.valueChanged.connect(self.on_spin_amp3_changed)
        
        grid_sphere3.addWidget(lbl_amp3, 2, 0)
        grid_sphere3.addWidget(self.slider_amp3, 2, 1)
        grid_sphere3.addWidget(self.spin_amp3, 2, 2)
        
        self.lbl_status3 = QLabel("Status: Parado")
        self.lbl_status3.setStyleSheet("color: red; font-weight: bold;")
        grid_sphere3.addWidget(self.lbl_status3, 3, 0, 1, 3)
        
        group_sphere3.setLayout(grid_sphere3)
        layout.addWidget(group_sphere3)
        
        # ===== BOTÕES DE PRESET =====
        group_preset = QGroupBox("Controles Globais")
        btn_layout = QHBoxLayout()
        
        btn_start_all = QPushButton("Iniciar Todas (1 Hz)")
        btn_start_all.clicked.connect(self.start_all)
        btn_start_all.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        btn_stop_all = QPushButton("Parar Todas")
        btn_stop_all.clicked.connect(self.stop_all)
        btn_stop_all.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        
        btn_sync = QPushButton("Sincronizar Fase")
        btn_sync.clicked.connect(self.sync_phase)
        btn_sync.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        
        btn_layout.addWidget(btn_start_all)
        btn_layout.addWidget(btn_stop_all)
        btn_layout.addWidget(btn_sync)
        
        group_preset.setLayout(btn_layout)
        layout.addWidget(group_preset)
        
        # ===== BOTÃO SAIR =====
        btn_quit = QPushButton("Sair")
        btn_quit.clicked.connect(self.close)
        layout.addWidget(btn_quit)
        
        self.setLayout(layout)
        self.resize(700, 600)

    # ===== CALLBACKS ESFERA 1 =====
    def on_check_sphere1_changed(self, state):
        self.enabled_sphere1 = (state == Qt.Checked)
        if self.enabled_sphere1:
            self.lbl_status1.setText(f"Status: Oscilando ({self.freq_sphere1:.2f} Hz)")
            self.lbl_status1.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.lbl_status1.setText("Status: Parado")
            self.lbl_status1.setStyleSheet("color: red; font-weight: bold;")
            self.send_position(1, 0.0)  # Volta para o centro
    
    def on_freq1_changed(self, value):
        freq = value / 10.0
        self.freq_sphere1 = freq
        self.spin_freq1.blockSignals(True)
        self.spin_freq1.setValue(freq)
        self.spin_freq1.blockSignals(False)
        if self.enabled_sphere1:
            self.lbl_status1.setText(f"Status: Oscilando ({freq:.2f} Hz)")
    
    def on_spin_freq1_changed(self, value):
        self.freq_sphere1 = value
        self.slider_freq1.blockSignals(True)
        self.slider_freq1.setValue(int(value * 10))
        self.slider_freq1.blockSignals(False)
        if self.enabled_sphere1:
            self.lbl_status1.setText(f"Status: Oscilando ({value:.2f} Hz)")
    
    def on_amp1_changed(self, value):
        amp = value / 100.0  # Slider 0-100 -> 0.0-1.0
        self.amplitude_sphere1 = amp
        self.spin_amp1.blockSignals(True)
        self.spin_amp1.setValue(amp)
        self.spin_amp1.blockSignals(False)
    
    def on_spin_amp1_changed(self, value):
        self.amplitude_sphere1 = value
        self.slider_amp1.blockSignals(True)
        self.slider_amp1.setValue(int(value * 100))  # 0.0-1.0 -> 0-100
        self.slider_amp1.blockSignals(False)

    # ===== CALLBACKS ESFERA 2 =====
    def on_check_sphere2_changed(self, state):
        self.enabled_sphere2 = (state == Qt.Checked)
        if self.enabled_sphere2:
            self.lbl_status2.setText(f"Status: Oscilando ({self.freq_sphere2:.2f} Hz)")
            self.lbl_status2.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.lbl_status2.setText("Status: Parado")
            self.lbl_status2.setStyleSheet("color: red; font-weight: bold;")
            self.send_position(2, 0.0)  # Volta para o centro
    
    def on_freq2_changed(self, value):
        freq = value / 10.0
        self.freq_sphere2 = freq
        self.spin_freq2.blockSignals(True)
        self.spin_freq2.setValue(freq)
        self.spin_freq2.blockSignals(False)
        if self.enabled_sphere2:
            self.lbl_status2.setText(f"Status: Oscilando ({freq:.2f} Hz)")
    
    def on_spin_freq2_changed(self, value):
        self.freq_sphere2 = value
        self.slider_freq2.blockSignals(True)
        self.slider_freq2.setValue(int(value * 10))
        self.slider_freq2.blockSignals(False)
        if self.enabled_sphere2:
            self.lbl_status2.setText(f"Status: Oscilando ({value:.2f} Hz)")
    
    def on_amp2_changed(self, value):
        amp = value / 100.0  # Slider 0-100 -> 0.0-1.0
        self.amplitude_sphere2 = amp
        self.spin_amp2.blockSignals(True)
        self.spin_amp2.setValue(amp)
        self.spin_amp2.blockSignals(False)
    
    def on_spin_amp2_changed(self, value):
        self.amplitude_sphere2 = value
        self.slider_amp2.blockSignals(True)
        self.slider_amp2.setValue(int(value * 100))  # 0.0-1.0 -> 0-100
        self.slider_amp2.blockSignals(False)

    # ===== CALLBACKS ESFERA 3 =====
    def on_check_sphere3_changed(self, state):
        self.enabled_sphere3 = (state == Qt.Checked)
        if self.enabled_sphere3:
            self.lbl_status3.setText(f"Status: Oscilando ({self.freq_sphere3:.2f} Hz)")
            self.lbl_status3.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.lbl_status3.setText("Status: Parado")
            self.lbl_status3.setStyleSheet("color: red; font-weight: bold;")
            self.send_position(3, 0.0)  # Volta para o centro
    
    def on_freq3_changed(self, value):
        freq = value / 10.0
        self.freq_sphere3 = freq
        self.spin_freq3.blockSignals(True)
        self.spin_freq3.setValue(freq)
        self.spin_freq3.blockSignals(False)
        if self.enabled_sphere3:
            self.lbl_status3.setText(f"Status: Oscilando ({freq:.2f} Hz)")
    
    def on_spin_freq3_changed(self, value):
        self.freq_sphere3 = value
        self.slider_freq3.blockSignals(True)
        self.slider_freq3.setValue(int(value * 10))
        self.slider_freq3.blockSignals(False)
        if self.enabled_sphere3:
            self.lbl_status3.setText(f"Status: Oscilando ({value:.2f} Hz)")
    
    def on_amp3_changed(self, value):
        amp = value / 100.0  # Slider 0-100 -> 0.0-1.0
        self.amplitude_sphere3 = amp
        self.spin_amp3.blockSignals(True)
        self.spin_amp3.setValue(amp)
        self.spin_amp3.blockSignals(False)
    
    def on_spin_amp3_changed(self, value):
        self.amplitude_sphere3 = value
        self.slider_amp3.blockSignals(True)
        self.slider_amp3.setValue(int(value * 100))  # 0.0-1.0 -> 0-100
        self.slider_amp3.blockSignals(False)

    # ===== FUNÇÕES AUXILIARES =====
    def update_oscillations(self):
        """Atualiza as posições oscilatórias de todas as esferas."""
        current_time = time.time() - self.start_time
        
        # Esfera 1
        if self.enabled_sphere1:
            # Posição senoidal: x(t) = A × sin(2π × f × t)
            position1 = self.amplitude_sphere1 * math.sin(2 * math.pi * self.freq_sphere1 * current_time)
            self.send_position(1, position1)
        
        # Esfera 2
        if self.enabled_sphere2:
            position2 = self.amplitude_sphere2 * math.sin(2 * math.pi * self.freq_sphere2 * current_time)
            self.send_position(2, position2)
        
        # Esfera 3
        if self.enabled_sphere3:
            position3 = self.amplitude_sphere3 * math.sin(2 * math.pi * self.freq_sphere3 * current_time)
            self.send_position(3, position3)

    def send_position(self, sphere_num, position):
        """Envia comando de posição para a esfera especificada."""
        msg = Double()
        msg.data = position
        
        if sphere_num == 1:
            self.pub_sphere1.publish(msg)
        elif sphere_num == 2:
            self.pub_sphere2.publish(msg)
        elif sphere_num == 3:
            self.pub_sphere3.publish(msg)

    def start_all(self):
        """Inicia oscilação de todas as esferas com 1 Hz."""
        self.check_sphere1.setChecked(True)
        self.check_sphere2.setChecked(True)
        self.check_sphere3.setChecked(True)
        
        self.spin_freq1.setValue(1.0)
        self.spin_freq2.setValue(1.0)
        self.spin_freq3.setValue(1.0)

    def stop_all(self):
        """Para todas as esferas."""
        self.check_sphere1.setChecked(False)
        self.check_sphere2.setChecked(False)
        self.check_sphere3.setChecked(False)

    def sync_phase(self):
        """Sincroniza a fase de todas as oscilações (reinicia o tempo)."""
        self.start_time = time.time()


def main():
    app = QApplication(sys.argv)
    gui = OscillatoryControlGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
