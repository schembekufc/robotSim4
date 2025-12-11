#!/usr/bin/env python3
import sys
import time
import threading
import numpy as np

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

        # Subscrever às 4 câmeras
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


class TrackerController:
    def __init__(self):
        self.node = Node()

        # Leitura das câmeras
        self.cam_reader = QuadCameraReader(self.node)

        # Publishers para comandos de junta
        self.pub_joint1 = self.node.advertise("/model/three_link_model/joint/joint_azimuth/cmd_pos", Double)
        self.pub_joint2 = self.node.advertise("/model/three_link_model/joint/joint_elevation/cmd_pos", Double)

        # Estimativa de posição atual das juntas (somente no script)
        self.joint1_pos = 0.0  # rad
        self.joint2_pos = 0.0  # rad

        # Passos mínimo e máximo
        self.step_big = 0.01   # passo grande
        self.step_small = 0.002  # passo pequeno

        # Limiar de diferença de luminância para trocar o passo
        self.diff_threshold = 1.0  # ajuste aqui conforme achar melhor

        # Banda morta para considerar Q1~Q2 ou Q1~Q4
        self.eps = 0.001

    def send_joint_command(self, joint_name, pos):
        msg = Double()
        msg.data = pos
        if joint_name == "joint_azimuth":
            self.pub_joint1.publish(msg)
        elif joint_name == "joint_elevation":
            self.pub_joint2.publish(msg)

    def control_loop(self):
        print("Iniciando controle automático de rastreamento...")
        print("Regras básicas:")
        print("  - Q1 > Q2 -> joint2 anti-horário (aumenta ângulo)")
        print("  - Q1 < Q2 -> joint2 horário (diminui ângulo)")
        print("  - Q1 > Q4 -> joint1 anti-horário (aumenta ângulo)")
        print("  - Q1 < Q4 -> joint1 horário (diminui ângulo)")
        print("Passo variável:")
        print(f"  - |Q1-Q2| ou |Q1-Q4| > {self.diff_threshold} -> passo = {self.step_big}")
        print(f"  - |Q1-Q2| ou |Q1-Q4| <= {self.diff_threshold} -> passo = {self.step_small}\n")

        try:
            while True:
                time.sleep(0.1)  # 10 Hz

                lum = self.cam_reader.get_luminances()
                q1 = lum["cam_q1"]
                q2 = lum["cam_q2"]
                q3 = lum["cam_q3"]
                q4 = lum["cam_q4"]

                if None in (q1, q2, q3, q4):
                    print("Aguardando dados das 4 câmeras...")
                    continue

                # Diferenças para decidir passo
                diff_12 = abs(q1 - q2)
                diff_14 = abs(q1 - q4)

                # Escolher passo para cada junta
                step2 = self.step_big if diff_12 > self.diff_threshold else self.step_small
                step1 = self.step_big if diff_14 > self.diff_threshold else self.step_small

                print(f"Q1={q1:.3f}  Q2={q2:.3f}  Q3={q3:.3f}  Q4={q4:.3f}  "
                      f"|Q1-Q2|={diff_12:.3f}  |Q1-Q4|={diff_14:.3f}")

                # Controle joint2 (baseado em Q1 vs Q2)
                if q1 > q2 + self.eps:
                    # Q1 > Q2 -> joint2 anti-horário (aumenta ângulo)
                    self.joint2_pos += step2
                elif q1 < q2 - self.eps:
                    # Q1 < Q2 -> joint2 horário (diminui ângulo)
                    self.joint2_pos -= step2

                # Controle joint1 (baseado em Q1 vs Q4)
                if q1 > q4 + self.eps:
                    # Q1 > Q4 -> joint1 anti-horário (aumenta ângulo)
                    self.joint1_pos += step1
                elif q1 < q4 - self.eps:
                    # Q1 < Q4 -> joint1 horário (diminui ângulo)
                    self.joint1_pos -= step1

                # Envia comandos
                self.send_joint_command("joint_azimuth", self.joint1_pos)
                self.send_joint_command("joint_elevation", self.joint2_pos)

                print(f"cmd joint1={self.joint1_pos:.3f} rad (step={step1:.3f})  "
                      f"joint2={self.joint2_pos:.3f} rad (step={step2:.3f})\n")

        except KeyboardInterrupt:
            print("\nEncerrando controle automático.")


def main():
    controller = TrackerController()
    controller.control_loop()


if __name__ == "__main__":
    main()

