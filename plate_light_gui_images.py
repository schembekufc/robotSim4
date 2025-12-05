#!/usr/bin/env python3
import sys
import threading
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QGroupBox, QGridLayout, QPushButton
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont

# Gazebo Transport
try:
    from gz.transport13 import Node
    from gz.msgs10.image_pb2 import Image
except ImportError:
    print("ERRO: Instale: sudo apt install python3-gz-transport13 python3-gz-msgs10")
    sys.exit(1)


class QuadCameraReader:
    def __init__(self):
        self.node = Node()

        self.lum = {
            "cam_q1": None,
            "cam_q2": None,
            "cam_q3": None,
            "cam_q4": None,
        }
        self.img = {
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
            self.img[cam_name] = img.copy()

    def get_luminances(self):
        with self.lock:
            return dict(self.lum)

    def get_images(self):
        with self.lock:
            return dict(self.img)

    def compute_error(self):
        with self.lock:
            q1 = self.lum["cam_q1"]
            q2 = self.lum["cam_q2"]
            q3 = self.lum["cam_q3"]
            q4 = self.lum["cam_q4"]

        if None in (q1, q2, q3, q4):
            return None, None

        left = (q2 + q3) / 2.0
        right = (q1 + q4) / 2.0
        bottom = (q3 + q4) / 2.0
        top = (q1 + q2) / 2.0

        err_x = right - left
        err_y = top - bottom
        return err_x, err_y


class QuadCamGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Placa Rastreadora - 4 Câmeras (Imagens + Luminância)")
        self.reader = QuadCameraReader()
        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)

    def init_ui(self):
        main_layout = QVBoxLayout()

        img_layout = QGridLayout()

        font_title = QFont()
        font_title.setBold(True)

        self.lbl_img_q1 = QLabel("Q1 (+x,+y)")
        self.lbl_img_q1.setAlignment(Qt.AlignCenter)
        self.lbl_img_q1.setFont(font_title)
        self.lbl_img_q1.setStyleSheet("color: rgb(255,0,0);")      # Q1 vermelho

        self.lbl_img_q2 = QLabel("Q2 (-x,+y)")
        self.lbl_img_q2.setAlignment(Qt.AlignCenter)
        self.lbl_img_q2.setFont(font_title)
        self.lbl_img_q2.setStyleSheet("color: rgb(0,180,0);")      # Q2 verde escuro

        self.lbl_img_q3 = QLabel("Q3 (-x,-y)")
        self.lbl_img_q3.setAlignment(Qt.AlignCenter)
        self.lbl_img_q3.setFont(font_title)
        self.lbl_img_q3.setStyleSheet("color: rgb(0,0,255);")      # Q3 azul

        self.lbl_img_q4 = QLabel("Q4 (+x,-y)")
        self.lbl_img_q4.setAlignment(Qt.AlignCenter)
        self.lbl_img_q4.setFont(font_title)
        self.lbl_img_q4.setStyleSheet("color: rgb(200,200,0);")    # Q4 amarelo escuro

        self.view_q1 = QLabel()
        self.view_q1.setFixedSize(160, 160)
        self.view_q1.setStyleSheet("background-color: #202020;")

        self.view_q2 = QLabel()
        self.view_q2.setFixedSize(160, 160)
        self.view_q2.setStyleSheet("background-color: #202020;")

        self.view_q3 = QLabel()
        self.view_q3.setFixedSize(160, 160)
        self.view_q3.setStyleSheet("background-color: #202020;")

        self.view_q4 = QLabel()
        self.view_q4.setFixedSize(160, 160)
        self.view_q4.setStyleSheet("background-color: #202020;")

        img_layout.addWidget(self.lbl_img_q2, 0, 0)
        img_layout.addWidget(self.lbl_img_q1, 0, 1)
        img_layout.addWidget(self.lbl_img_q3, 2, 0)
        img_layout.addWidget(self.lbl_img_q4, 2, 1)

        img_layout.addWidget(self.view_q2, 1, 0)
        img_layout.addWidget(self.view_q1, 1, 1)
        img_layout.addWidget(self.view_q3, 3, 0)
        img_layout.addWidget(self.view_q4, 3, 1)

        group_imgs = QGroupBox("Imagens das 4 Câmeras (espelhadas horizontalmente)")
        group_imgs.setLayout(img_layout)
        main_layout.addWidget(group_imgs)

        grid_lum = QGridLayout()
        self.lbl_q1 = QLabel("Q1 (+x,+y): ---")
        self.lbl_q1.setStyleSheet("color: rgb(255,0,0);")

        self.lbl_q2 = QLabel("Q2 (-x,+y): ---")
        self.lbl_q2.setStyleSheet("color: rgb(0,180,0);")

        self.lbl_q3 = QLabel("Q3 (-x,-y): ---")
        self.lbl_q3.setStyleSheet("color: rgb(0,0,255);")

        self.lbl_q4 = QLabel("Q4 (+x,-y): ---")
        self.lbl_q4.setStyleSheet("color: rgb(200,200,0);")

        grid_lum.addWidget(self.lbl_q2, 0, 0)
        grid_lum.addWidget(self.lbl_q1, 0, 1)
        grid_lum.addWidget(self.lbl_q3, 1, 0)
        grid_lum.addWidget(self.lbl_q4, 1, 1)

        group_lum = QGroupBox("Luminância Média (0–255 aprox.)")
        group_lum.setLayout(grid_lum)
        main_layout.addWidget(group_lum)

        self.lbl_err_x = QLabel("err_x: ---")
        self.lbl_err_y = QLabel("err_y: ---")
        self.lbl_sug_x = QLabel("Sugestão X: ---")
        self.lbl_sug_y = QLabel("Sugestão Y: ---")

        err_layout = QVBoxLayout()
        err_layout.addWidget(self.lbl_err_x)
        err_layout.addWidget(self.lbl_err_y)
        err_layout.addWidget(self.lbl_sug_x)
        err_layout.addWidget(self.lbl_sug_y)

        group_err = QGroupBox("Erro de Rastreamento (exemplo)")
        group_err.setLayout(err_layout)
        main_layout.addWidget(group_err)

        btn_quit = QPushButton("Sair")
        btn_quit.clicked.connect(self.close)
        main_layout.addWidget(btn_quit)

        self.setLayout(main_layout)
        self.resize(800, 800)

    def ndarray_to_qpixmap(self, img):
        if img is None:
            return None

        img = np.fliplr(img)

        h, w, ch = img.shape
        bytes_per_line = ch * w
        buffer = img.tobytes()
        qimg = QImage(buffer, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qimg)

    def update_ui(self):
        lum = self.reader.get_luminances()
        imgs = self.reader.get_images()

        q1 = lum["cam_q1"]
        q2 = lum["cam_q2"]
        q3 = lum["cam_q3"]
        q4 = lum["cam_q4"]

        # 3 casas decimais (mude para .2f se quiser 2 casas)
        def fmt(v):
            return "---" if v is None else f"{v:.3f}"

        self.lbl_q1.setText(f"Q1 (+x,+y): {fmt(q1)}")
        self.lbl_q2.setText(f"Q2 (-x,+y): {fmt(q2)}")
        self.lbl_q3.setText(f"Q3 (-x,-y): {fmt(q3)}")
        self.lbl_q4.setText(f"Q4 (+x,-y): {fmt(q4)}")

        pix1 = self.ndarray_to_qpixmap(imgs["cam_q1"])
        pix2 = self.ndarray_to_qpixmap(imgs["cam_q2"])
        pix3 = self.ndarray_to_qpixmap(imgs["cam_q3"])
        pix4 = self.ndarray_to_qpixmap(imgs["cam_q4"])

        if pix2:
            self.view_q2.setPixmap(pix2.scaled(self.view_q2.size(),
                                               Qt.KeepAspectRatio,
                                               Qt.SmoothTransformation))
        if pix1:
            self.view_q1.setPixmap(pix1.scaled(self.view_q1.size(),
                                               Qt.KeepAspectRatio,
                                               Qt.SmoothTransformation))
        if pix3:
            self.view_q3.setPixmap(pix3.scaled(self.view_q3.size(),
                                               Qt.KeepAspectRatio,
                                               Qt.SmoothTransformation))
        if pix4:
            self.view_q4.setPixmap(pix4.scaled(self.view_q4.size(),
                                               Qt.KeepAspectRatio,
                                               Qt.SmoothTransformation))

        err_x, err_y = self.reader.compute_error()
        if err_x is None:
            self.lbl_err_x.setText("err_x: ---")
            self.lbl_err_y.setText("err_y: ---")
            self.lbl_sug_x.setText("Sugestão X: ---")
            self.lbl_sug_y.setText("Sugestão Y: ---")
        else:
            self.lbl_err_x.setText(f"err_x (dir - esq): {err_x:.3f}")
            self.lbl_err_y.setText(f"err_y (cima - baixo): {err_y:.3f}")

            sug_x = "centro"
            if err_x > 5:
                sug_x = "mover para +X (direita)"
            elif err_x < -5:
                sug_x = "mover para -X (esquerda)"

            sug_y = "centro"
            if err_y > 5:
                sug_y = "mover para +Y (cima)"
            elif err_y < -5:
                sug_y = "mover para -Y (baixo)"

            self.lbl_sug_x.setText(f"Sugestão X: {sug_x}")
            self.lbl_sug_y.setText(f"Sugestão Y: {sug_y}")


def main():
    app = QApplication(sys.argv)
    gui = QuadCamGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

