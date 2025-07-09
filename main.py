from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys
import subprocess
import os
import requests
import yaml

# from updater import UpdateWindow  # Import the UpdateWindow class
from AERIES.AERIES_API import *
from AERIES.classListWindow import *
# from AESOP.AESOP_API import *
from AERIES.aeriesWindow import *
import Update3

# CONFIG_FILE = 'config_path.txt'


class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.aeriesAPI = AeriesAPIz()
        # self.config_path = self.get_config_path()
        # self.load_credentials()
        

    def initUI(self):
        self.setWindowTitle('Super SOC Hub')
        self.setGeometry(400, 400, 400, 300)

        self.layout = QVBoxLayout()

        # Main welcome label
        self.main_label = QLabel('Welcome to the Super SOC Hub', self)
        self.main_label.setAlignment(Qt.AlignCenter)

         # Add ESY checkbox
        self.esy_checkbox = QCheckBox("ESY")
        self.esy_checkbox.stateChanged.connect(self.on_esy_checked)
        


        self.classList_button = QPushButton('Classlists', self)
        self.classList_button.clicked.connect(self.openClassListWindow)
        self.aeriesButton = QPushButton('Aeries', self)
        self.aeriesButton.clicked.connect(self.openAeriesWindow)
        self.aesopButton = QPushButton('AESOP', self)
        self.aesopButton.clicked.connect(self.openAesopWindow)
        self.workOrderButton = QPushButton('Work Orders', self)
        self.formsButton = QPushButton('Forms', self)

        self.layout.addWidget(self.main_label)
        self.layout.addWidget(self.esy_checkbox)
        self.layout.addWidget(self.classList_button) # Add the button to the layout
        self.layout.addWidget(self.aeriesButton)
        self.layout.addWidget(self.aesopButton)
        self.layout.addWidget(self.workOrderButton)
        self.layout.addWidget(self.formsButton)

        # Label for update status
        self.update_label = QLabel('', self)
        small_font = QFont()
        small_font.setPointSize(8)  # Set a smaller font size
        self.update_label.setFont(small_font)
        self.update_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.update_label)  # Add the update label to the layout

        self.setLayout(self.layout)
        self.show()


    # def handle_update_checked(self, update_info):
    #     if 'error' in update_info:
    #         self.update_label.setText(f"Update check failed: {update_info['error']}")
    #     else:
    #         latest_version = update_info['latest_version']
    #         if self.update_window.current_version != latest_version:
    #             self.update_label.setText(f"New version {latest_version} available. Updating...")
    #             # Call the download and install method
    #             self.update_window.download_and_install_update(update_info['latest_release'])
    #         else:
    #             self.update_label.setText(f"SOC Hub is up to date! {latest_version}")

    def openClassListWindow(self):
        self.classListWindow = ClasslistsWindow(api=self.aeriesAPI)
        self.classListWindow.show()

    def openAeriesWindow(self):
        print("Opening AERIES window")
        self.aeriesWindow = AeriesWindow(api=self.aeriesAPI)
        self.aeriesWindow.show()
    
    def openAesopWindow(self):
        print("Opening AESOP window")
        # self.aesopAPI = AESOP_API()

    def closeEvent(self, event):
        if hasattr(self, 'update_window'):
            self.update_window.close()
        event.accept()

    def on_esy_checked(self, state):
        if state == Qt.Checked:
            self.aeriesAPI = AeriesAPIz(ESY=True)
            print("ESY Checked")
        else:
            self.aeriesAPI = AeriesAPIz(ESY=False)

    # def get_config_path(self):
    #     if os.path.exists(CONFIG_FILE):
    #         with open(CONFIG_FILE, 'r') as file:
    #             return file.read().strip()
    #     else:
    #         return self.prompt_for_config_path()

    # def prompt_for_config_path(self):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.ShowDirsOnly
    #     directory = QFileDialog.getExistingDirectory(self, "Select Configuration Directory", options=options)
    #     if directory:
    #         with open(CONFIG_FILE, 'w') as file:
    #             file.write(directory)
    #         return directory
    #     else:
    #         QMessageBox.critical(self, "Error", "No directory selected. The application will exit.")
    #         sys.exit(1)

    # def load_credentials(self):
    #         credentials_file = os.path.join(self.config_path, 'credentials.yml')
    #         if os.path.exists(credentials_file):
    #             with open(credentials_file, 'r') as file:
    #                 credentials = yaml.safe_load(file)
    #             # Use credentials as needed
    #         else:
    #             QMessageBox.warning(self, "Missing Credentials", f"Please create a credentials.yml file in the {self.config_path} directory.")


def check_for_updates():
    config_dir = os.path.join(os.path.dirname(sys.executable), 'config')
    version_file_path = os.path.join(config_dir, 'version.txt')
    
    # Read the current version from version.txt
    with open(version_file_path, 'r') as version_file:
        current_version = version_file.read().strip()
    
    latest_version_url = "https://api.github.com/repos/natedavidson89/SOC_Hub/releases/latest"
    response = requests.get(latest_version_url)
    latest_version = response.json()["tag_name"]

    if current_version != latest_version:
        print(f"New version available: {latest_version} (local: {current_version})")
        updater_exe_path = os.path.join(os.path.dirname(sys.executable), 'updater.exe')
        os.startfile(updater_exe_path)
        sys.exit()

def main():
    check_for_updates()  # Check for updates before starting the main application
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
