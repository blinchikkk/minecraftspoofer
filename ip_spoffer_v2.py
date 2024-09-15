import sys
import random
import psutil
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit, QDialog, QCheckBox, QDialogButtonBox, QFormLayout, QGroupBox, QMainWindow, QAction, QMenu)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class IPMacSpoofer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.dark_mode = True  # По умолчанию включена тёмная тема
        self.initUI()
        self.selected_processes = []
        self.spoofed_processes = {}  # Хранит информацию о процессе, его IP и MAC

    def initUI(self):
        # Установка заголовка окна и его размеров
        self.setWindowTitle("Minecraft Spoofer | By @blinxhiktg | Version: 2.0")
        self.setGeometry(100, 100, 800, 500)

        # Инициализация основной темы
        self.apply_theme(self.dark_mode)

        # Основной виджет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Создаем основные элементы интерфейса
        ip_label = QLabel('New IP:')
        self.ip_entry = QLineEdit()

        mac_label = QLabel('New MAC:')
        self.mac_entry = QLineEdit()

        # Кнопка для генерации случайного IP
        random_ip_button = QPushButton('Random IP', self)
        random_ip_button.clicked.connect(self.generate_random_ip)

        # Кнопка для генерации случайного MAC
        random_mac_button = QPushButton('Random MAC', self)
        random_mac_button.clicked.connect(self.generate_random_mac)

        # Кнопки для спуфинга и сброса
        change_button = QPushButton('Change IP & MAC', self)
        change_button.clicked.connect(self.change_ip_mac)

        reset_button = QPushButton('Reset MAC', self)
        reset_button.clicked.connect(self.reset_ip_mac)

        # Кнопка для проверки процессов Minecraft (javaw.exe)
        check_minecraft_button = QPushButton('Check Minecraft Status', self)
        check_minecraft_button.clicked.connect(self.check_minecraft_status)

        # Кнопка для выбора процессов Minecraft
        select_process_button = QPushButton('Select Minecraft Process', self)
        select_process_button.clicked.connect(self.open_process_selection_window)

        # Кнопка для открытия окна с ссылками разработчика
        developer_button = QPushButton('Developer Info', self)
        developer_button.clicked.connect(self.show_developer_info)

        # Кнопка для смены темы
        theme_button = QPushButton('Switch Theme', self)
        theme_button.clicked.connect(self.switch_theme)

        # Текстовое поле для вывода сообщений (мини-консоль)
        self.console = QTextEdit()
        self.console.setReadOnly(True)  # Делает консоль только для чтения

        # Кнопка для очистки консоли
        clear_console_button = QPushButton('Clear Console', self)
        clear_console_button.clicked.connect(self.clear_console)

        # Организация элементов в сетку
        grid = QGridLayout()
        grid.addWidget(ip_label, 0, 0)
        grid.addWidget(self.ip_entry, 0, 1)
        grid.addWidget(random_ip_button, 0, 2)  # Кнопка случайного IP

        grid.addWidget(mac_label, 1, 0)
        grid.addWidget(self.mac_entry, 1, 1)
        grid.addWidget(random_mac_button, 1, 2)  # Кнопка случайного MAC

        grid.addWidget(change_button, 2, 0, 1, 3)
        grid.addWidget(reset_button, 3, 0, 1, 3)

        grid.addWidget(check_minecraft_button, 4, 0, 1, 3)  # Кнопка проверки Minecraft
        grid.addWidget(select_process_button, 5, 0, 1, 3)   # Кнопка выбора процесса Minecraft
        grid.addWidget(developer_button, 6, 0, 1, 3)        # Кнопка для информации о разработчике
        grid.addWidget(theme_button, 7, 0, 1, 3)            # Кнопка для смены темы

        # Основная компоновка
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        left_layout.addLayout(grid)

        main_layout.addLayout(left_layout)

        # Добавляем консоль в правую часть
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.console)
        right_layout.addWidget(clear_console_button)  # Кнопка для очистки консоли

        main_layout.addLayout(right_layout)

        central_widget.setLayout(main_layout)

    # Функция для генерации случайного IP-адреса
    def generate_random_ip(self):
        random_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
        self.ip_entry.setText(random_ip)
        self.log_to_console(f"Generated random IP: {random_ip}")

    # Функция для генерации случайного MAC-адреса
    def generate_random_mac(self):
        random_mac = ":".join(f"{random.randint(0x00, 0xFF):02x}" for _ in range(6))
        self.mac_entry.setText(random_mac)
        self.log_to_console(f"Generated random MAC: {random_mac}")

    # Функция для спуфинга MAC-адреса
    def spoof_mac(self, ip, new_mac, proc_name, proc_pid):
        try:
            self.spoofed_processes[proc_pid] = (ip, new_mac)
            self.log_to_console(f"MAC Spoofing active for process {proc_name} (PID: {proc_pid}) with IP: {ip} and MAC: {new_mac}")
        except Exception as e:
            self.log_to_console(f"Error: {str(e)}")

    # Функция для сброса MAC-адреса на исходный
    def reset_mac(self, interface):
        try:
            original_mac = "00:00:00:00:00:00"  # Устанавливаем MAC по умолчанию
            self.log_to_console(f"MAC Reset to original: {original_mac}")
        except Exception as e:
            self.log_to_console(f"Error: {str(e)}")

    # Функция для подмены IP и MAC
    def change_ip_mac(self):
        ip = self.ip_entry.text()
        mac = self.mac_entry.text()
        if ip and mac:
            if self.selected_processes:
                for proc in self.selected_processes:
                    self.spoof_mac(ip, mac, proc.name(), proc.pid)
            else:
                self.log_to_console("No processes selected for spoofing.")
        else:
            self.log_to_console("Please provide both IP and MAC")

    # Функция для сброса MAC
    def reset_ip_mac(self):
        interface = "eth0"  # Замените на ваш сетевой интерфейс
        self.reset_mac(interface)

    # Проверка запущенных процессов Minecraft (javaw.exe)
    def check_minecraft_status(self):
        minecraft_processes = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'].lower() == 'javaw.exe':
                    minecraft_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if minecraft_processes:
            self.log_to_console(f"Found {len(minecraft_processes)} running Minecraft process(es) (javaw.exe).")
            for proc in minecraft_processes:
                status = self.spoofed_processes.get(proc.pid, ("Not spoofed", ""))
                self.log_to_console(f"Process ID: {proc.pid}, Name: {proc.name()}, Status: IP: {status[0]}, MAC: {status[1]}")
        else:
            self.log_to_console("No running Minecraft processes (javaw.exe) found.")

    # Открытие окна для выбора процесса Minecraft
    def open_process_selection_window(self):
        self.process_selection_window = ProcessSelectionWindow(self)
        self.process_selection_window.show()

    # Функция для логирования в консоль
    def log_to_console(self, message):
        self.console.append(message)

    # Функция для очистки консоли
    def clear_console(self):
        self.console.clear()

    # Показать окно с информацией о разработчике
    def show_developer_info(self):
        dev_info = DeveloperInfoWindow(self)
        dev_info.exec_()

    # Переключение между светлой и тёмной темой
    def switch_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme(self.dark_mode)

    # Применение темы
    def apply_theme(self, dark_mode):
        if dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                }
                QPushButton {
                    background-color: #3A3A3A;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    padding: 5px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
                QLineEdit {
                    background-color: #3A3A3A;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    border-radius: 5px;
                }
                QTextEdit {
                    background-color: #2B2B2B;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    border-radius: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #F0F0F0;
                    color: #000000;
                }
                QPushButton {
                    background-color: #008CBA;
                    color: #FFFFFF;
                    border: 1px solid #007399;
                    padding: 5px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #005f7f;
                }
                QLineEdit {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                }
                QTextEdit {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                }
            """)


class ProcessSelectionWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Minecraft Process")
        self.setGeometry(400, 400, 300, 200)

        layout = QVBoxLayout()
        self.checkboxes = []

        minecraft_processes = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'].lower() == 'javaw.exe':
                    minecraft_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if minecraft_processes:
            for proc in minecraft_processes:
                checkbox = QCheckBox(f"PID: {proc.pid}, Name: {proc.name()}")
                self.checkboxes.append((checkbox, proc))
                layout.addWidget(checkbox)
        else:
            layout.addWidget(QLabel("No running Minecraft processes (javaw.exe) found."))

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def accept(self):
        self.selected_processes = [proc for checkbox, proc in self.checkboxes if checkbox.isChecked()]
        self.parent().selected_processes = self.selected_processes
        self.close()


class DeveloperInfoWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Developer Info")
        self.setGeometry(300, 300, 250, 150)

        layout = QVBoxLayout()

        telegram_button = QPushButton("Telegram: @blinxhiktg", self)
        vk_button = QPushButton("VK: vk.com/psychoarc", self)

        layout.addWidget(telegram_button)
        layout.addWidget(vk_button)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    spoofer = IPMacSpoofer()
    spoofer.show()
    sys.exit(app.exec_())
