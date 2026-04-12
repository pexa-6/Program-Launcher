import os
import sys
import threading
import subprocess
from pathlib import Path
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QEvent, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QComboBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox, QGridLayout
)


# ==== Resource Path for EXE ====
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class _CallEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, func):
        super().__init__(self.EVENT_TYPE)
        self.func = func


class ProgramLauncher(QMainWindow):

    # ==== Window ====
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Program Launcher")
        self.setWindowIcon(QIcon(resource_path("Launcher_ico.ico")))
        self.setMinimumSize(1300, 1000)
        self.setMaximumSize(1300, 1000)

        # Убираем стандартную рамку окна
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.running_processes = []
        self.program_buttons = {}

        self.init_ui()

    # ==== GUI ====
    def init_ui(self):
        w = QWidget()
        self.setCentralWidget(w)

        # Кастомная панель управления
        custom_title_bar = QWidget()
        custom_title_bar.setObjectName("CustomTitleBar")
        custom_title_bar.setFixedHeight(40)

        title_bar_layout = QHBoxLayout(custom_title_bar)
        title_bar_layout.setContentsMargins(10, 0, 10, 0)

        # Заголовок окна
        title_label = QLabel("Program Launcher")
        title_label.setObjectName("TitleBarLabel")

        # Кнопки управления окном
        minimize_btn = QPushButton("−")
        minimize_btn.setObjectName("MinimizeBtn")
        minimize_btn.setFixedSize(40, 40)
        minimize_btn.clicked.connect(self.showMinimized)

        close_btn = QPushButton("×")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(40, 40)
        close_btn.clicked.connect(self.close)

        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(minimize_btn)
        title_bar_layout.addWidget(close_btn)

        # Основной контент
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Заголовок с иконкой
        title_container = QWidget()
        title_container.setObjectName("TitleContainer")
        title_container_layout = QHBoxLayout(title_container)
        title_container_layout.setContentsMargins(0, 0, 0, 0)

        # Иконка приложения
        icon_label = QLabel()
        icon_pixmap = QIcon(resource_path("Launcher_ico.ico")).pixmap(64, 64)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setObjectName("IconLabel")

        # Текст заголовка
        main_title_label = QLabel("Program Launcher")
        main_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_title_label.setObjectName("TitleLabel")

        title_container_layout.addStretch()
        title_container_layout.addWidget(icon_label)
        title_container_layout.addWidget(main_title_label)
        title_container_layout.addStretch()

        content_layout.addWidget(title_container)

        programs_container = QWidget()
        self.programs_layout = QGridLayout(programs_container)
        content_layout.addWidget(programs_container)

        control_panel = QWidget()
        control_panel.setObjectName("ControlPanel")
        control_layout = QHBoxLayout(control_panel)

        start_all_btn = QPushButton("🎮 Start Gaming Set")
        start_all_btn.clicked.connect(self.start_gaming_set)
        start_all_btn.setObjectName("GamingBtn")

        start_work_btn = QPushButton("💼 Start Work Set")
        start_work_btn.clicked.connect(self.start_work_set)
        start_work_btn.setObjectName("WorkBtn")

        control_layout.addWidget(start_all_btn)
        control_layout.addWidget(start_work_btn)
        control_layout.addStretch()

        content_layout.addWidget(control_panel)

        log_label = QLabel("📝 Logs:")
        log_label.setObjectName("LogLabel")

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setObjectName("LogText")

        content_layout.addWidget(log_label)
        content_layout.addWidget(self.log_text)

        # Основной layout
        main_layout = QVBoxLayout(w)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(custom_title_bar)
        main_layout.addWidget(content_widget)

        self.load_programs()
        self.apply_dark_style()

    def load_programs(self):
        programs = [

            # 🎮 Игровые программы
            {
                "name": "🦊 Firefox",
                "path": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                "args": [],
                "category": "gaming"
            },
            {
                "name": "🎵 Spotify",
                "path": "C:\\Users\\user\\AppData\\Roaming\\Spotify\\Spotify.exe",
                "args": [],
                "category": "gaming"
            },
            {
                "name": "🕹️ Steam",
                "path": "C:\\Program Files (x86)\\Steam\\steam.exe",
                "args": [],
                "category": "gaming"
            },
            {
                "name": "💬 Discord",
                "path": "C:\\Users\\user\\AppData\\Local\\Discord\\app-1.0.9212\\Discord.exe",
                "args": [],
                "category": "gaming"
            },
            {
                "name": "📧 Telegram",
                "path": "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe",
                "args": [],
                "category": "gaming"
            },
            {
                "name": "🎮 Epic Games",
                "path": "C:\\Program Files (x86)\\Epic Games\\Launcher\\Portal\\Binaries\\Win32\\EpicGamesLauncher.exe",
                "args": [],
                "category": "gaming"
            },

            # 💼 Рабочие программы
            {
                "name": "🐍 PyCharm",
                "path": "C:\\Program Files\\JetBrains\\PyCharm Community Edition 2024.3\\bin\\pycharm64.exe",
                "args": [],
                "category": "work"
            },
            {
                "name": "💻 Intellij IDEA",
                "path": "C:\\Program Files\\JetBrains\\IntelliJ IDEA Community Edition 2024.3\\bin\\idea64.exe",
                "args": [],
                "category": "work"
            },
            {
                "name": "🔌 Arduino IDE",
                "path": "C:\\Users\\user\\AppData\\Local\\Programs\\Arduino IDE\\Arduino IDE.exe",
                "args": [],
                "category": "work"
            },
            {
                "name": "📝 Notepad++",
                "path": "C:\\Program Files\\Notepad++\\notepad++.exe",
                "args": [],
                "category": "work"
            },
            {
                "name": "🟦 VS Code",
                "path": "C:\\Users\\user\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
                "args": [],
                "category": "work"
            },
            {
                "name": "🟪 Visual Studio",
                "path": "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\Common7\\IDE\\devenv.exe",
                "args": [],
                "category": "work"
            },

            # 🛠️ Системные утилиты
            {
                "name": "🧮 Калькулятор",
                "path": "calc.exe",
                "args": [],
                "category": "utils"
            },
            {
                "name": "📁 Проводник",
                "path": "explorer.exe",
                "args": [],
                "category": "utils"
            },
            {
                "name": "⚙️ CMD",
                "path": "C:\\Windows\\System32\\cmd.exe",
                "args": [],
                "category": "utils"
            }

        ]

        categories = {
            "gaming": "🎮 Игровые программы",
            "work": "💼 Рабочие программы",
            "utils": "🛠️ Системные утилиты"
        }

        row = 0
        col = 0

        for category_name, category_title in categories.items():
            category_label = QLabel(category_title)
            category_label.setObjectName("CategoryLabel")
            self.programs_layout.addWidget(category_label, row, 0, 1, 3)
            row += 1

            category_programs = [p for p in programs if p["category"] == category_name]

            for program in category_programs:
                self.create_program_button(program, row, col)
                col += 1
                if col >= 3:
                    col = 0
                    row += 1

            row += 1
            col = 0

    def create_program_button(self, program, row, col):
        btn = QPushButton(program["name"])
        btn.setObjectName("ProgramBtn")
        btn.setMinimumHeight(60)

        btn.program_data = program
        btn.is_running = False

        btn.clicked.connect(lambda checked, p=program, b=btn: self.launch_program_once(p, b))

        self.programs_layout.addWidget(btn, row, col)
        self.program_buttons[program["name"]] = btn

    def launch_program_once(self, program, button):
        if not button.is_running:
            self.launch_program(program, button)

    def launch_program(self, program, button):
        try:
            path = program["path"].replace("%USERNAME%", Path.home().name)

            if program["args"]:
                process = subprocess.Popen([path] + program["args"])
            else:
                process = subprocess.Popen(path)

            self.log_msg(f"✅ Запущено: {program['name']}")

        except Exception as e:
            self.log_msg(f"❌ Ошибка запуска {program['name']}: {str(e)}")

    def start_gaming_set(self):
        self.log_msg("🎮 Запуск игрового набора...")
        gaming_programs = ["🎵 Spotify", "🕹️ Steam", "💬 Discord", "📧 Telegram"]
        self.launch_program_set(gaming_programs, "🎮 Игровой набор запущен!")

    def start_work_set(self):
        self.log_msg("💼 Запуск рабочего набора...")
        work_programs = ["🦊 Firefox", "📧 Telegram", "💬 Discord", "🎵 Spotify"]
        self.launch_program_set(work_programs, "💼 Рабочий набор запущен!")

    def launch_program_set(self, program_names, success_message):
        for program_name in program_names:
            if program_name in self.program_buttons:
                btn = self.program_buttons[program_name]
                if not btn.is_running:
                    self.launch_program(btn.program_data, btn)
                    QApplication.processEvents()

        self.log_msg(success_message)

    # ==== Перетаскивание окна ====
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_start_position'):
            self.move(event.globalPosition().toPoint() - self.drag_start_position)
            event.accept()

    # ==== CSS GUI ====
    def apply_dark_style(self):
        self.setStyleSheet("""
        QWidget {
            background: #000000;
            color: #f1f2f6;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        #CustomTitleBar {
            background: #121212;
            border-bottom: 1px solid #333333;
        }

        #TitleBarLabel {
            font-size: 14pt;
            font-weight: bold;
            color: #ffffff;
            padding: 5px;
        }

        #MinimizeBtn, #CloseBtn {
            background-color: transparent;
            color: #ffffff;
            font-size: 20pt;
            font-weight: bold;
            border: none;
            border-radius: 3px;
        }

        #MinimizeBtn:hover {
            background-color: #333333;
        }

        #MinimizeBtn:pressed {
            background-color: #444444;
        }

        #CloseBtn:hover {
            background-color: #e81123;
        }

        #CloseBtn:pressed {
            background-color: #f1707a;
        }

        #TitleContainer {
            background: #000000;
            border-radius: 10px;
            margin: 5px;
            padding: 10px;
        }

        #TitleLabel {
            font-size: 25pt;
            font-weight: bold;
            color: #5046aa;
            margin-left: 15px;
        }

        #IconLabel {
            margin-right: 10px;
        }

        #LogLabel {
            font-size: 12pt;
            font-weight: bold;
            color: #ffffff;
            padding: 8px;
        }

        #CategoryLabel {
            font-size: 16pt;
            font-weight: bold;
            color: #ffffff;
            padding: 10px;
            background: #121212;
            border-radius: 8px;
            margin: 5px 0px;
        }

        #ProgramBtn {
            background-color: #212121;
            color: white;
            font-weight: 600;
            border-radius: 20px;
            padding: 15px 10px;
            font-size: 12pt;
            font-weight: bold;
            border: 2px solid #212121;
            margin: 2px;
        }

        #ProgramBtn:hover { 
            background-color: #2a2a2a; 
            border: 2px solid #2a2a2a;
        }

        #ProgramBtn:pressed { 
            background-color: #333333; 
            border: 2px solid #333333; 
        }

        #GamingBtn {
            background-color: #810a14;
            font-size: 15pt;
            font-weight: bold;
            padding: 12px 20px;
            border-radius: 8px;
            border: 2px solid #810a14;
        }

        #GamingBtn:hover {
            background-color: #9a0c18;
            border: 2px solid #9a0c18;
        }

        #GamingBtn:pressed {
            background-color: #b40e1b;
            border: 2px solid #b40e1b;
        }

        #WorkBtn {
            background-color: #0537b9;
            font-size: 15pt;
            font-weight: bold;
            padding: 12px 20px;
            border-radius: 8px;
            border: 2px solid #0537b9;
        }

        #WorkBtn:hover {
            background-color: #0642d4;
            border: 2px solid #0642d4;
        }

        #WorkBtn:pressed {
            background-color: #0752ff;
            border: 2px solid #0752ff;
        }

        QTextEdit {
            background-color: #000000;
            border: 4px solid #121212;
            border-radius: 8px;
            font-family: 'Consolas', monospace;
            font-size: 15pt;
            padding: 8px;
        }

        #ControlPanel {
            background: #121212;
            border-radius: 8px;
            padding: 10px;
            margin: 5px;
        }
        """)

    # ==== Log ====
    def log_msg(self, text):
        import time
        ts = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{ts}] {text}")

    def _invoke_ui_log(self, msg):
        QApplication.instance().postEvent(self, _CallEvent(lambda: self.log_msg(msg)))

    # ==== Miscellaneous ====
    def customEvent(self, event):
        if isinstance(event, _CallEvent):
            event.func()

    # ==== Error ====
    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)
        self.log_msg(f"ERROR: {msg}")


def main():
    app = QApplication(sys.argv)
    win = ProgramLauncher()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()