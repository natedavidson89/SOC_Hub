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

            if self.is_update_needed(latest_version):
                self.download_latest_release(latest_release['zipball_url'])
            else:
                self.update_checked.emit({'updated': False})
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            self.update_checked.emit(None)

    def is_update_needed(self, latest_version):
        return self.current_version != latest_version

    def download_latest_release(self, download_url):
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            zip_path = 'latest_release.zip'
            with open(zip_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            self.update_checked.emit({'updated': True})
            self.launch_update_script()
        except requests.RequestException as e:
            print(f"An error occurred during download: {e}")
            self.update_checked.emit(None)

    def launch_update_script(self):
        """Launch the updater_launcher.py script."""
        try:
            subprocess.Popen([sys.executable, 'updater_launcher.py'], cwd='C:/Users/Nated/VSC Projects/SOC_Hub')
        except Exception as e:
            print(f"An error occurred while launching the update script: {e}")

class UpdateWindow(QWidget):
    def __init__(self, repo, current_version):
        super().__init__()
        self.current_version = current_version
        self.initUI()
        self.check_for_updates(repo)

    def initUI(self):
        self.setWindowTitle("Update Checker")
        self.setGeometry(300, 300, 300, 200)
        layout = QVBoxLayout()
        self.label = QLabel("Updating...", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.show()

    def check_for_updates(self, repo):
        self.update_checker = UpdateChecker(repo, self.current_version)
        self.update_checker.update_checked.connect(self.on_update_checked)
        self.update_checker.start()

    def on_update_checked(self, update_info):
        if update_info is None:
            self.label.setText("Failed to fetch updates")
        elif update_info.get('updated') is True:
            self.label.setText("Update applied successfully. Restarting...")
        elif update_info.get('updated') is False:
            self.label.setText("SOC Hub is up to date")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    repo = 'natedavidson89/SOC_Hub'
    current_version = 'base'
    ex = UpdateWindow(repo, current_version)
    sys.exit(app.exec_())
