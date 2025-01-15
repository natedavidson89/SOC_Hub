import os
import requests
import shutil

# GitHub repository details
REPO_OWNER = 'natedavidson89'
REPO_NAME = 'SOC_Hub'
LATEST_RELEASE_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest'
DOWNLOAD_URL = f'https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/latest/download/main.exe'
INSTALLATION_PATH = os.path.dirname(os.path.realpath(__file__))  # Folder of the running script
CONFIG_PATH = os.path.join(os.getenv('LOCALAPPDATA'), 'SOC_Hub', 'config')  # Path to the config folder in AppData

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
    if response.status_code == 200:
        latest_version = response.json()['tag_name']  # Assuming the tag is the version number
        print(f"Latest version: {latest_version}")
        return latest_version
    else:
        print("Error fetching the latest release.")
        return None

def download_update():
    print(f"Downloading update from {DOWNLOAD_URL}")
    response = requests.get(DOWNLOAD_URL, stream=True)
    if response.status_code == 200:
        new_exe_path = os.path.join(INSTALLATION_PATH, 'main_new.exe')
        with open(new_exe_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        print(f"Update downloaded to {new_exe_path}")
        return new_exe_path
    else:
        print("Failed to download the update.")
        return None

def replace_old_exe(new_exe_path):
    old_exe_path = os.path.join(INSTALLATION_PATH, 'main.exe')
    backup_exe_path = os.path.join(INSTALLATION_PATH, 'main_backup.exe')
    
    # Backup the old executable
    if os.path.exists(old_exe_path):
        shutil.move(old_exe_path, backup_exe_path)
        print(f"Backup of old version created at {backup_exe_path}")
    
    # Replace with the new executable
    shutil.move(new_exe_path, old_exe_path)
    print(f"Replaced old executable with the new one.")

def update_version_file(new_version, version_file='version.txt'):
    """Update the version.txt file with the new version."""
    ensure_config_directory()
    try:
        with open(os.path.join(CONFIG_PATH, version_file), 'w') as file:
            file.write(new_version)
        print(f"Version updated to {new_version}.")
    except Exception as e:
        print(f"An error occurred while updating {version_file}: {e}")

def main():
    local_version = get_local_version()
    latest_version = get_latest_version()

    if latest_version and latest_version != local_version:
        print(f"New version available: {latest_version} (local: {local_version})")
        new_exe = download_update()
        if new_exe:
            replace_old_exe(new_exe)
            update_version_file(latest_version)  # Update version.txt with the new version

            # Optionally restart the application
            os.startfile(os.path.join(INSTALLATION_PATH, 'main.exe'))
            print("Application restarted.")
        else:
            print("Update failed.")
    else:
        print("No update is available or already on the latest version.")

if __name__ == "__main__":
    main()