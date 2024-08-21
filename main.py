from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys

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

        self.setLayout(self.layout)
        self.show()

    def check_for_updates(self):
        # Simulating update checking logic
        latest_release = {'updated': False}  # Replace this with actual update logic
        self.on_update_checked(latest_release)

    def on_update_checked(self, latest_release):
        if latest_release and isinstance(latest_release, dict):
            if latest_release.get('updated') is False:
                update_message = "SOC Hub is up to date."
            else:
                latest_version = latest_release.get('tag_name')
                if latest_version:
                    update_message = f"Updating to {latest_version}..."
                else:
                    update_message = "Unexpected response: 'tag_name' not found."
        else:
            update_message = "Failed to check for updates."

        # Add the update message to the window in smaller font
        update_label = QLabel(update_message, self)
        small_font = QFont()
        small_font.setPointSize(6)  # Set a smaller font size
        update_label.setFont(small_font)
        update_label.setAlignment(Qt.AlignCenter)  # Center the text
        self.layout.addWidget(update_label)  # Add the update label to the layout

def main():
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
