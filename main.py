from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys
import requests

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
        # Read the current version from version.txt
        try:
            with open('version.txt', 'r') as file:
                current_version = file.read().strip()
        except FileNotFoundError:
            current_version = '0.0.0'  # Default version if file is not found

        # Fetch the latest release from GitHub
        repo = 'natedavidson89/SOC_Hub'
        url = f'https://api.github.com/repos/{repo}/releases/latest'
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release['tag_name']
            
            # Compare versions and update the UI accordingly
            if current_version == latest_version:
                update_message = "SOC Hub is up to date."
            else:
                update_message = f"Updating to {latest_version}..."
                # Trigger an update process here if needed
                # self.download_latest_release(latest_release['zipball_url'])
            
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            update_message = "Failed to check for updates."

        # Update the UI with the result
        self.update_label.setText(update_message)

def main():
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
