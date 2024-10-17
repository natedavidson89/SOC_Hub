import sys
import os
import requests
import zipfile
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import subprocess

class UpdateChecker(QThread):
    update_checked = pyqtSignal(dict)

    def __init__(self, repo, current_version):
        super().__init__()
        self.repo = repo
        self.current_version = current_version
        print("Checking for update....")
        print(self.current_version)

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
        self.repo = repo
        self.current_version = self.get_current_version()
        self.initUI()
        self.check_for_updates(repo)

    def initUI(self):
        self.setWindowTitle("Update Checker")
        self.setGeometry(200, 200, 200, 100)
        layout = QVBoxLayout()
        self.label = QLabel("Checking for updates...")
        layout.addWidget(self.label)
        self.setLayout(layout)

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
            self.label.setText(f"Update check failed: {update_info['error']}")
        else:
            latest_version = update_info['latest_version']
            print(f"Latest version: {latest_version}")
            if self.current_version != latest_version:
                self.label.setText(f"New version available: {latest_version}. Downloading update...")
                self.download_and_install_update(update_info['latest_release'])
            else:
                self.label.setText("You are already running the latest version.")

    def download_and_install_update(self, latest_release):
        download_url = latest_release['zipball_url']
        zip_path = 'latest_release.zip'

        try:
            # Download the latest release
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            with open(zip_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall()  # Extract to current directory

            # Clean up
            os.remove(zip_path)

            # Update version.txt
            latest_version = latest_release['tag_name']
            self.update_version_file(latest_version)

            # Restart the application
            self.restart_application()

        except Exception as e:
            print(f"An error occurred while downloading or extracting the update: {e}")

    def update_version_file(self, new_version, version_file='version.txt'):
        """Update the version.txt file with the new version."""
        try:
            with open(version_file, 'w') as file:
                file.write(new_version)
            print(f"Version updated to {new_version}.")
        except Exception as e:
            print(f"An error occurred while updating {version_file}: {e}")

    def restart_application(self):
        """Restart the application."""
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def closeEvent(self, event):
        if hasattr(self, 'update_checker') and self.update_checker.isRunning():
            self.update_checker.quit()
            self.update_checker.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    repo = 'natedavidson89/SOC_Hub'
    update_window = UpdateWindow(repo)
    update_window.show()
    sys.exit(app.exec_())
