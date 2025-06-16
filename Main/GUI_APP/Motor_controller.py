import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QMessageBox, QGridLayout, QFrame, QSlider
)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt


class MotorController(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dieu khien Robot - DHCN")
        self.setWindowIcon(QIcon("logo.png"))  # Use your own logo file
        self.setFixedSize(460, 620)
        self.serial_port = None
        self.last_command = None  # 🆕 Store last direction (F, B, L, R, T)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton#stopButton {
                background-color: #D70000;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton#stopButton:hover {
                background-color: #990000;
            }
            QLabel#devLabel {
                color: #555555;
                font-size: 13pt;
                font-style: italic;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignTop)

        # Logo
        logo = QLabel()
        pixmap = QPixmap("logo.png")
        if pixmap.isNull():
            print("❌ Error: logo not loaded")
        logo.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)

        # Developer name
        dev_label = QLabel("Doan Do")
        dev_label.setObjectName("devLabel")
        dev_label.setAlignment(Qt.AlignCenter)

        # COM port selection
        self.port_selector = QComboBox()
        self.refresh_ports()
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_serial)
        disconnect_btn = QPushButton("Disconnect")
        disconnect_btn.clicked.connect(self.disconnect_serial)

        port_row = QHBoxLayout()
        port_row.addWidget(QLabel("COM Port:"))
        port_row.addWidget(self.port_selector)
        port_row.addWidget(connect_btn)
        port_row.addWidget(disconnect_btn)

        # Speed slider
        speed_label_title = QLabel("Speed:")
        speed_label_title.setFont(QFont("Arial", 10))
        self.speed_value_label = QLabel("150")  # Default
        self.speed_value_label.setFont(QFont("Arial", 12, QFont.Bold))

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(255)
        self.speed_slider.setValue(150)
        self.speed_slider.valueChanged.connect(self.update_speed_label)

        speed_row = QHBoxLayout()
        speed_row.addWidget(speed_label_title)
        speed_row.addWidget(self.speed_slider)
        speed_row.addWidget(self.speed_value_label)

        # Control Buttons
        btn_forward = QPushButton("↑ Forward")
        btn_forward.clicked.connect(lambda: self.send_command('F'))

        btn_backward = QPushButton("↓ Backward")
        btn_backward.clicked.connect(lambda: self.send_command('B'))

        btn_left = QPushButton("← Left")
        btn_left.clicked.connect(lambda: self.send_command('L'))

        btn_right = QPushButton("→ Right")
        btn_right.clicked.connect(lambda: self.send_command('R'))

        btn_rotate = QPushButton("⟳ Rotate")
        btn_rotate.clicked.connect(lambda: self.send_command('T'))

        btn_stop = QPushButton("⛔ STOP")
        btn_stop.setObjectName("stopButton")
        btn_stop.clicked.connect(lambda: self.send_command('S'))

        # Control Grid
        grid = QGridLayout()
        grid.addWidget(btn_forward, 0, 1)
        grid.addWidget(btn_left, 1, 0)
        grid.addWidget(btn_rotate, 1, 1)
        grid.addWidget(btn_right, 1, 2)
        grid.addWidget(btn_backward, 2, 1)

        # Layout building
        main_layout.addWidget(logo)
        main_layout.addWidget(dev_label)
        main_layout.addLayout(port_row)
        main_layout.addSpacing(10)

        main_layout.addLayout(speed_row)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        main_layout.addLayout(grid)
        main_layout.addSpacing(20)
        main_layout.addWidget(btn_stop)

        self.setLayout(main_layout)

    def refresh_ports(self):
        self.port_selector.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_selector.addItem(port.device)

    def connect_serial(self):
        try:
            port = self.port_selector.currentText()
            self.serial_port = serial.Serial(port, 9600)
            QMessageBox.information(self, "Connected", f"Connected to {port}")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))

    def disconnect_serial(self):
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
            QMessageBox.information(self, "Disconnected", "Serial port disconnected")

    def send_command(self, direction_char):
        if not self.serial_port or not self.serial_port.is_open:
            QMessageBox.warning(self, "Not Connected", "Please connect to a COM port first.")
            return

        if direction_char == 'S':
            command = "S\n"
            self.last_command = None  # Stop cancels direction tracking
        else:
            speed = self.speed_slider.value()
            command = f"{direction_char}{speed}\n"
            self.last_command = direction_char  # 🆕 Track last direction

        print(f"Sending: {command.strip()}")
        self.serial_port.write(command.encode())

    def update_speed_label(self):
        speed = self.speed_slider.value()
        self.speed_value_label.setText(str(speed))

        # 🆕 If a direction was sent earlier, resend it with the new speed
        if self.last_command:
            self.send_command(self.last_command)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MotorController()
    window.show()
    sys.exit(app.exec_())
