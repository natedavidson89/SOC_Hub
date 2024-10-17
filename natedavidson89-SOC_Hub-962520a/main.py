from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys
from updater import UpdateWindow  # Import the UpdateWindow class
from AERIES_API import *
from classListWindow import ClasslistsWindow
import yaml

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.check_for_updates()  # Perform update check on initialization

    def initUI(self):
        self.setWindowTitle('Super SOC Hub')
        self.setGeometry(400, 400, 400, 300)

        self.layout = QVBoxLayout()

        # Main welcome label
        self.main_label = QLabel('Welcome to the Super SOC Hub', self)
        self.main_label.setAlignment(Qt.AlignCenter)
        self.classList_button = QPushButton('Classlists', self)
        self.classList_button.clicked.connect(self.openClassListWindow)
        self.layout.addWidget(self.main_label)
        self.layout.addWidget(self.classList_button)  # Add the button to the layout


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
        self.update_window.update_checker.update_checked.connect(self.handle_update_checked)

    def handle_update_checked(self, update_info):
        if 'error' in update_info:
            self.update_label.setText(f"Update check failed: {update_info['error']}")
        else:
            latest_version = update_info['latest_version']
            self.update_label.setText(f"SOC Hub is up to date! {latest_version}")

    def openClassListWindow(self):
        self.aeriesAPI = AeriesAPI()
        self.classListWindow = ClasslistsWindow(api=self.aeriesAPI)
        self.classListWindow.show()
        

    def closeEvent(self, event):
        if hasattr(self, 'update_window'):
            self.update_window.close()
        event.accept()

   


def main():
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()