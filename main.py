from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QMainWindow
from PyQt5.QtCore import Qt
import sys
from updater import UpdateChecker  # Import the UpdateChecker class from update_checker.py

class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.check_for_updates()  # Perform update check on initialization

    def initUI(self):
        # Create a central widget and set layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Welcome label
        self.welcome_label = QLabel('Welcome to the Super SOC Hub', self)
        self.welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.welcome_label)
        
        # Update status label
        self.update_status_label = QLabel('', self)  # Empty initially
        self.update_status_label.setAlignment(Qt.AlignCenter)
        self.update_status_label.setStyleSheet('font-size: 12px;')  # Smaller font size
        layout.addWidget(self.update_status_label)
        
        # Set central widget and window properties
        self.setCentralWidget(central_widget)
        self.setWindowTitle('Super SOC Hub')
        self.setGeometry(100, 100, 300, 200)  # Adjust size and position as needed
        self.show()

    def check_for_updates(self):
        # Create and start the UpdateChecker thread
        repo = 'natedavidson89/SOC_Hub'  # Replace with your GitHub repo
        self.update_checker = UpdateChecker(repo)
        self.update_checker.update_checked.connect(self.on_update_checked)
        self.update_checker.start()

    def on_update_checked(self, latest_release):
        if latest_release:
            self.update_status_label.setText(f"Latest release: {latest_release['tag_name']}")
        else:
            self.update_status_label.setText("SOC Hub is up to date")

def main():
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
