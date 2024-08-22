from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys
from updater import UpdateWindow  # Import the UpdateWindow class

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.check_for_updates()  # Perform update check on initialization

    def initUI(self):
        self.setWindowTitle('Super SOC Hub')
        self.setGeometry(300, 300, 300, 200)

        self.layout = QVBoxLayout()

        # Main welcome label
        self.main_label = QLabel('Welcome to the Super SOC Hub', self)
        self.main_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.main_label)

        # Label for update status
        self.update_label = QLabel('', self)
        small_font = QFont()
        small_font.setPointSize(8)  # Set a smaller font size
        self.update_label.setFont(small_font)
        self.update_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.update_label)  # Add the update label to the layout

        self.setLayout(self.layout)
        self.show()

    def check_for_updates(self):
        repo = 'natedavidson89/SOC_Hub'
        self.update_window = UpdateWindow(repo)
        self.update_window.show()

    def closeEvent(self, event):
        if hasattr(self, 'update_window'):
            self.update_window.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()