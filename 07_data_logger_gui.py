#!/usr/bin/env python3
"""
GUI de Data Logger para RobotSim4
Versão Avançada:
- Grava dados de juntas (Posição, Velocidade) do JointState.
- Recupera Esforço dos Cilindros via comando (cmd_force).
- Estima Esforço das Juntas PID (Azimuth/Elevation) via cálculo matemático (Engenharia Reversa do PID).
"""

import sys
import os
import csv
import datetime
import math
from collections import defaultdict

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QGridLayout, QLabel, QPushButton, 
    QLineEdit, QCheckBox, QFileDialog, QScrollArea,
    QProgressBar, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QPalette, QColor

# Imports Gazebo
try:
    from gz.transport13 import Node
    from gz.msgs10.model_pb2 import Model
    from gz.msgs10.world_stats_pb2 import WorldStatistics
    from gz.msgs10.double_pb2 import Double
except ImportError:
    print("ERRO: Instale as dependências: sudo apt install python3-gz-transport13 python3-gz-msgs10")
    sys.exit(1)

# === CONFIGURAÇÕES ===
TOPIC_JOINT_STATE = "/world/three_link_with_tracker_plate_world/model/three_link_model/joint_state"
TOPIC_STATS = "/world/three_link_with_tracker_plate_world/stats"

# Tópicos de Comando (Para Cilindros)
TOPIC_CMD_FORCE_RED = "/model/three_link_model/joint/joint_cylinder/cmd_force"
TOPIC_CMD_FORCE_GREEN = "/model/three_link_model/joint/joint_cylinder_green/cmd_force"

# Tópicos de Alvo (Para PIDs)
TOPIC_CMD_POS_AZIMUTH = "/model/three_link_model/joint/joint_azimuth/cmd_pos"
TOPIC_CMD_POS_ELEVATION = "/model/three_link_model/joint/joint_elevation/cmd_pos"

# Parâmetros PID (Copiados do SDF)
PID_GAINS = {
    "joint_azimuth": {
        "p": 1000.0, "i": 100.0, "d": 3000.0, 
        "i_max": 1000.0, "i_min": -1000.0,
        "cmd_max": 2000.0, "cmd_min": -2000.0
    },
    "joint_elevation": {
        "p": 4000.0, "i": 5000.0, "d": 4000.0, 
        "i_max": 500.0, "i_min": -500.0,
        "cmd_max": 1000.0, "cmd_min": -1000.0
    }
}

KNOWN_JOINTS = [
    "joint_azimuth",
    "joint_elevation",
    "joint_cylinder",
    "joint_cylinder_green"
]

class Signals(QObject):
    update_stats = pyqtSignal(float, float) # current_time, dt
    update_data = pyqtSignal(object)
    update_cmd_force = pyqtSignal(str, float)
    update_cmd_pos = pyqtSignal(str, float)

class DataLoggerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Logger Avançado - RobotSim4")
        self.resize(700, 800)
        
        # Gazebo setup
        self.node = Node()
        self.signals = Signals()
        self.signals.update_stats.connect(self.update_sim_time)
        self.signals.update_data.connect(self.process_joint_state)
        self.signals.update_cmd_force.connect(self.update_force_command)
        self.signals.update_cmd_pos.connect(self.update_pos_command)
        
        # Subscribers
        self.node.subscribe(WorldStatistics, TOPIC_STATS, self.on_stats)
        self.node.subscribe(Model, TOPIC_JOINT_STATE, self.on_joint_state)
        
        # Cmd Force Subs
        self.node.subscribe(Double, TOPIC_CMD_FORCE_RED, lambda msg: self.on_double(msg, "joint_cylinder"))
        self.node.subscribe(Double, TOPIC_CMD_FORCE_GREEN, lambda msg: self.on_double(msg, "joint_cylinder_green"))
        
        # Cmd Pos Subs
        self.node.subscribe(Double, TOPIC_CMD_POS_AZIMUTH, lambda msg: self.on_double_pos(msg, "joint_azimuth"))
        self.node.subscribe(Double, TOPIC_CMD_POS_ELEVATION, lambda msg: self.on_double_pos(msg, "joint_elevation"))
        
        # Estado
        self.recording = False
        self.current_sim_time = 0.0
        self.last_sim_time = 0.0
        self.dt = 0.0
        
        # Data Stores
        self.latest_state = {}     # {joint: {pos, vel}}
        self.latest_force_cmd = {} # {joint: eff} (Cylinders)
        self.latest_pos_target = {} # {joint: target_pos} (PIDs)
        
        # PID Integrators
        self.pid_integrals = defaultdict(float)
        self.calculated_pid_efforts = defaultdict(float)
        
        self.csv_file = None
        self.csv_writer = None
        self.data_count = 0
        
        # UI
        self.apply_light_theme()
        self.init_ui()
        self.update_default_filename()

    def apply_light_theme(self):
        self.setStyle(QApplication.style())
        p = QPalette()
        p.setColor(QPalette.Window, QColor(245, 245, 245))
        p.setColor(QPalette.WindowText, QColor(0, 0, 0))
        p.setColor(QPalette.Base, QColor(255, 255, 255))
        p.setColor(QPalette.Button, QColor(240, 240, 240))
        p.setColor(QPalette.Highlight, QColor(0, 120, 215))
        self.setPalette(p)
        font = QFont("Segoe UI", 10)
        if not font.exactMatch(): font = QFont("Roboto", 10)
        self.setFont(font)

    def init_ui(self):
        main = QVBoxLayout()
        main.setSpacing(15)
        main.setContentsMargins(20, 20, 20, 20)
        
        # Header
        lbl = QLabel("ROBOT DATA LOGGER (PID + FORCE)")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; letter-spacing: 1px;")
        main.addWidget(lbl)
        
        # Info Box
        info = QLabel("Modo Avançado: Estima torques PID matematicamente e lê comandos de força dos cilindros.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; font-style: italic; font-size: 12px; margin-bottom: 10px;")
        info.setAlignment(Qt.AlignCenter)
        main.addWidget(info)
        
        # Sim Time
        self.lbl_time = QLabel("Aguardando Simulação...")
        self.lbl_time.setAlignment(Qt.AlignCenter)
        self.lbl_time.setStyleSheet("font-family: Monospace; font-size: 14px; color: #333; background: #e0e0e0; border-radius: 4px; padding: 8px;")
        main.addWidget(self.lbl_time)

        # File Config
        grp_file = QGroupBox("Configuração do Arquivo")
        grp_file.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #ccc; border-radius: 6px; margin-top: 10px; }")
        lay_file = QGridLayout()
        lay_file.addWidget(QLabel("Salvar em:"), 0, 0)
        self.txt_dir = QLineEdit(os.getcwd())
        lay_file.addWidget(self.txt_dir, 0, 1)
        btn_dir = QPushButton("...")
        btn_dir.setFixedWidth(40)
        btn_dir.clicked.connect(self.choose_directory)
        lay_file.addWidget(btn_dir, 0, 2)
        
        lay_file.addWidget(QLabel("Nome:"), 1, 0)
        self.txt_name = QLineEdit()
        lay_file.addWidget(self.txt_name, 1, 1)
        btn_refresh = QPushButton("↻")
        btn_refresh.setFixedWidth(40)
        btn_refresh.clicked.connect(self.update_default_filename)
        lay_file.addWidget(btn_refresh, 1, 2)
        grp_file.setLayout(lay_file)
        main.addWidget(grp_file)

        # Variables
        lbl_vars = QLabel("Variáveis para Gravação:")
        lbl_vars.setStyleSheet("font-weight: bold; margin-top: 10px;")
        main.addWidget(lbl_vars)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        lay_vars = QVBoxLayout(container)
        
        self.checkboxes = {} 
        
        for j_name in KNOWN_JOINTS:
            row = QHBoxLayout()
            lbl_j = QLabel(j_name)
            lbl_j.setFixedWidth(180)
            
            # Color code labels
            if j_name in PID_GAINS:
                lbl_j.setStyleSheet("font-weight: bold; color: #d84315;") # PID (Orangeish)
                suffix_eff = " (Estimado PID)"
            else:
                lbl_j.setStyleSheet("font-weight: bold; color: #2e7d32;") # Direct (Greenish)
                suffix_eff = " (Comando)"
                
            row.addWidget(lbl_j)
            
            cb_pos = QCheckBox("Pos")
            cb_pos.setChecked(True)
            cb_vel = QCheckBox("Vel")
            cb_vel.setChecked(True)
            cb_eff = QCheckBox("Eff" + suffix_eff)
            cb_eff.setChecked(True)
            
            row.addWidget(cb_pos)
            row.addWidget(cb_vel)
            row.addWidget(cb_eff)
            lay_vars.addLayout(row)
            
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet("background-color: #eee;")
            lay_vars.addWidget(line)
            
            self.checkboxes[j_name] = {"pos": cb_pos, "vel": cb_vel, "eff": cb_eff}
            
        scroll.setWidget(container)
        main.addWidget(scroll)

        # Controls
        lay_ctrl = QHBoxLayout()
        self.btn_rec = QPushButton("INICIAR GRAVAÇÃO")
        self.btn_rec.setCheckable(True)
        self.btn_rec.setFixedHeight(50)
        self.btn_rec.setCursor(Qt.PointingHandCursor)
        self.btn_rec.setStyleSheet("""
            QPushButton { background-color: #1976D2; color: white; font-weight: bold; font-size: 14px; border-radius: 6px; }
            QPushButton:hover { background-color: #2196F3; }
            QPushButton:checked { background-color: #D32F2F; }
        """)
        self.btn_rec.clicked.connect(self.toggle_recording)
        lay_ctrl.addWidget(self.btn_rec)
        main.addLayout(lay_ctrl)
        
        # Status
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("QProgressBar { height: 8px; border-radius: 4px; } QProgressBar::chunk { background-color: #D32F2F; }")
        main.addWidget(self.progress)
        
        self.lbl_status = QLabel("Pronto para gravar.")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        main.addWidget(self.lbl_status)
        
        self.setLayout(main)

    # ==== LOGIC ====
    def update_default_filename(self):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        self.txt_name.setText(f"robot_pid_data_{timestamp}.csv")

    def choose_directory(self):
        d = QFileDialog.getExistingDirectory(self, "Escolher Diretório", self.txt_dir.text())
        if d: self.txt_dir.setText(d)

    # -- Gazebo Callbacks --
    def on_stats(self, msg):
        t = msg.sim_time.sec + (msg.sim_time.nsec * 1e-9)
        dt = t - self.current_sim_time
        if dt < 0: dt = 0 # Reset or lag
        self.signals.update_stats.emit(t, dt)

    def on_joint_state(self, msg):
        self.signals.update_data.emit(msg)

    def on_double(self, msg, joint_name):
        self.signals.update_cmd_force.emit(joint_name, msg.data)

    def on_double_pos(self, msg, joint_name):
        self.signals.update_cmd_pos.emit(joint_name, msg.data)

    # -- Signal Handlers --
    def update_sim_time(self, t, dt):
        self.current_sim_time = t
        self.dt = dt
        status = "GRAVANDO" if self.recording else "Inativo"
        self.lbl_time.setText(f"Sim Time: {t:.3f} s  (dt={dt*1000:.1f}ms) [{status}]")
        
        # Run PID Calculation continuously regardless of recording 
        # to convert state to effort
        self.calculate_pids()

    def update_force_command(self, joint, val):
        self.latest_force_cmd[joint] = val

    def update_pos_command(self, joint, val):
        self.latest_pos_target[joint] = val

    def process_joint_state(self, msg):
        # Extract kinematics from JointState
        for j in msg.joint:
            if j.HasField("axis1"):
                self.latest_state[j.name] = {
                    "pos": j.axis1.position,
                    "vel": j.axis1.velocity
                }
        
        # If recording, write ROW
        if self.recording:
            self.write_log_row()

    def calculate_pids(self):
        # Execute PID Math
        for j_name, params in PID_GAINS.items():
            if j_name not in self.latest_state: continue
            
            current_pos = self.latest_state[j_name]["pos"]
            current_vel = self.latest_state[j_name]["vel"] # dE/dt term implicitly
            target_pos = self.latest_pos_target.get(j_name, 0.0) # Default target 0
            
            # Error
            error = target_pos - current_pos
            
            # Integral
            if self.dt > 0:
                self.pid_integrals[j_name] += error * self.dt
                # Clamp Integral
                self.pid_integrals[j_name] = max(min(self.pid_integrals[j_name], params["i_max"]), params["i_min"])
            
            # Derivative (Velocity error, assuming target vel is 0 for fixed point control)
            # D term usually works on -velocity to avoid derivative kick on setpoint change
            d_error = -current_pos # ??? No, simple PID is Kd * (de/dt)
            # Standard implementation: P*error + I*integral + D*(error - last_error)/dt
            # Or simpler: P*error - D*current_vel (if setpoint is constant)
            # Let's use P*e - D*vel
            
            # Calculate Terms
            p_term = params["p"] * error
            i_term = params["i"] * self.pid_integrals[j_name]
            d_term = params["d"] * (0.0 - current_vel) # Target Velocity assumed 0
            
            output = p_term + i_term + d_term
            
            # Clamp Output
            output = max(min(output, params["cmd_max"]), params["cmd_min"])
            
            self.calculated_pid_efforts[j_name] = output

    # -- Recording --
    def toggle_recording(self):
        if self.btn_rec.isChecked():
            path = os.path.join(self.txt_dir.text(), self.txt_name.text())
            header = ["Time_s"]
            self.active_cols = []
            
            for j in KNOWN_JOINTS:
                chk = self.checkboxes[j]
                if chk["pos"].isChecked(): 
                    self.active_cols.append((j, "pos"))
                    header.append(f"{j}_pos")
                if chk["vel"].isChecked():
                    self.active_cols.append((j, "vel"))
                    header.append(f"{j}_vel")
                if chk["eff"].isChecked():
                    self.active_cols.append((j, "eff"))
                    header.append(f"{j}_eff")
            
            try:
                self.csv_file = open(path, 'w', newline='')
                self.csv_writer = csv.writer(self.csv_file)
                self.csv_writer.writerow(header)
                self.recording = True
                self.data_count = 0
                self.btn_rec.setText("PARAR GRAVAÇÃO")
                self.progress.setRange(0, 0)
                self.txt_name.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))
                self.btn_rec.setChecked(False)
        else:
            self.stop_recording()

    def stop_recording(self):
        self.recording = False
        if self.csv_file: self.csv_file.close()
        self.btn_rec.setText("INICIAR GRAVAÇÃO")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.txt_name.setEnabled(True)
        self.update_default_filename()
        QMessageBox.information(self, "Salvo", f"Gravado {self.data_count} linhas.")

    def write_log_row(self):
        row = [f"{self.current_sim_time:.4f}"]
        
        for j_name, v_type in self.active_cols:
            val = 0.0
            
            # POS / VEL -> From JointState
            if v_type in ["pos", "vel"]:
                if j_name in self.latest_state:
                    val = self.latest_state[j_name][v_type]
                    
            # EFF -> Hibrido
            elif v_type == "eff":
                if j_name in self.latest_force_cmd:
                    # Cilindros (Command)
                    val = self.latest_force_cmd[j_name]
                elif j_name in self.calculated_pid_efforts:
                    # PID (Calculated)
                    val = self.calculated_pid_efforts[j_name]
                    
            row.append(f"{val:.6f}")
            
        self.csv_writer.writerow(row)
        self.data_count += 1
        if self.data_count % 50 == 0:
            self.lbl_status.setText(f"Linhas: {self.data_count}")

def main():
    app = QApplication(sys.argv)
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    gui = DataLoggerGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
