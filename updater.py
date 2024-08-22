import sys
import requests
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import subprocess

class UpdateChecker(QThread):
    update_checked = pyqtSignal(dict)

    def __init__(self, repo, current_version):
        super().__init__()
        self.repo = repo
        self.current_version = current_version

    def run(self):
        url = f'https://api.github.com/repos/{self.repo}/releases/latest'
        try:
            response = requests.get(url)
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release['tag_name']
            self.update_checked.emit({
                'latest_version': latest_version,
                'latest_release': latest_release
            })
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            self.update_checked.emit({
                'error': str(e)
            })

    def launch_update_script(self):
        """Launch the updater_launcher.py script."""
        try:
            subprocess.Popen([sys.executable, 'update_launcher.py'], cwd='C:/Users/Nated/VSC Projects/SOC_Hub')
        except Exception as e:
            print(f"An error occurred while launching the update script: {e}")

class UpdateWindow(QWidget):
    def __init__(self, repo):
        super().__init__()
        self.current_version = self.get_current_version()
        self.initUI()
        self.check_for_updates(repo)

    def initUI(self):
        self.setWindowTitle("Update Checker")
        self.setGeometry(300, 300, 300, 200)

    def get_current_version(self):
        try:
            with open('version.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            return '0.0.0'

    def check_for_updates(self, repo):
        self.update_checker = UpdateChecker(repo, self.current_version)
        self.update_checker.update_checked.connect(self.handle_update_checked)
        self.update_checker.start()

    def handle_update_checked(self, update_info):
        if 'error' in update_info:
            print(f"Update check failed: {update_info['error']}")
        else:
            latest_version = update_info['latest_version']
            print(f"Latest version: {latest_version}")
            # Add logic to handle the update process here

    def closeEvent(self, event):
        if hasattr(self, 'update_checker') and self.update_checker.isRunning():
            self.update_checker.quit()
            self.update_checker.wait()
        event.accept()