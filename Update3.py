import os
import requests
import shutil
import sys
import subprocess

# GitHub repository details
REPO_OWNER = 'natedavidson89'
REPO_NAME = 'SOC_Hub'
LATEST_RELEASE_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest'
DOWNLOAD_URL = f'https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/latest/download/main.exe'

# Set the installation path to SOC_Hub within the local AppData folder
INSTALLATION_PATH = os.path.join(os.getenv('LOCALAPPDATA'), 'SOC_Hub')
CONFIG_PATH = os.path.join(INSTALLATION_PATH, 'config')  # Path to the config folder in AppData

def ensure_config_directory():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_PATH)
        print(f"Created config directory at {CONFIG_PATH}")

def get_local_version():
    ensure_config_directory()
    version_file = os.path.join(CONFIG_PATH, 'version.txt')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            version = f.read().strip()
            print(f"Current version: {version}")
            return version
    print("No version file found. Defaulting to version 0.0.0")
    return "0.0.0"  # Default if no version file exists

def get_latest_version():
    response = requests.get(LATEST_RELEASE_URL)
    response.raise_for_status()
    latest_version = response.json()['tag_name']
    print(f"Latest version: {latest_version}")
    return latest_version

def download_update():
    print(f"Downloading update from {DOWNLOAD_URL}")
    response = requests.get(DOWNLOAD_URL, stream=True)
    if response.status_code == 200:
        new_exe_path = os.path.join(os.getenv('TEMP'), 'main_new.exe')
        with open(new_exe_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        print(f"Update downloaded to {new_exe_path}")
        return new_exe_path
    else:
        print("Failed to download the update.")
        return None

def launch_updater(new_exe_path):
    old_exe_path = os.path.join(INSTALLATION_PATH, 'main.exe')
    backup_exe_path = os.path.join(INSTALLATION_PATH, 'main_backup.exe')
    updater_script = os.path.join(INSTALLATION_PATH, 'updater.py')

    # Launch the updater script using subprocess
    subprocess.Popen([sys.executable, updater_script, new_exe_path, old_exe_path, backup_exe_path])
    print("Updater script launched.")
    sys.exit()

def update_version_file(new_version, version_file='version.txt'):
    """Update the version.txt file with the new version."""
    version_file_path = os.path.join(CONFIG_PATH, version_file)
    with open(version_file_path, 'w') as f:
        f.write(new_version)
    print(f"Updated version file to {new_version}")

def main():
    local_version = get_local_version()
    latest_version = get_latest_version()

    if latest_version and latest_version != local_version:
        print(f"New version available: {latest_version} (local: {local_version})")
        new_exe = download_update()
        if new_exe:
            launch_updater(new_exe)
            update_version_file(latest_version)  # Update version.txt with the new version
        else:
            print("Update failed.")
    else:
        print("No update is available or already on the latest version.")

if __name__ == "__main__":
    main()