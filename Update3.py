import os
import requests
import shutil

# GitHub repository details
REPO_OWNER = 'natedavidson89'
REPO_NAME = 'SOC_Hub'
LATEST_RELEASE_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest'
DOWNLOAD_URL = f'https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/latest/download/main.exe'
INSTALLATION_PATH = os.path.dirname(os.path.realpath(__file__))  # Folder of the running script

def get_local_version():
    # Read the local version from a file or set a default version
    version_file = os.path.join(INSTALLATION_PATH, 'version.txt')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            return f.read().strip()
    return "0.0.0"  # Default if no version file exists

def get_latest_version():
    response = requests.get(LATEST_RELEASE_URL)
    if response.status_code == 200:
        return response.json()['tag_name']  # Assuming the tag is the version number
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
    current_exe_path = os.path.join(INSTALLATION_PATH, 'main.exe')
    backup_exe_path = os.path.join(INSTALLATION_PATH, 'main_backup.exe')

    # Create a backup of the current exe
    if os.path.exists(current_exe_path):
        shutil.move(current_exe_path, backup_exe_path)
        print(f"Backup of old version created at {backup_exe_path}")

    # Replace the old exe with the new one
    shutil.move(new_exe_path, current_exe_path)
    print(f"Updated {current_exe_path} with the new version.")

def main():
    local_version = get_local_version()
    latest_version = get_latest_version()

    if latest_version and latest_version != local_version:
        print(f"New version available: {latest_version} (local: {local_version})")
        new_exe = download_update()
        if new_exe:
            replace_old_exe(new_exe)

            # Optionally restart the application
            os.startfile(os.path.join(INSTALLATION_PATH, 'main.exe'))
            print("Application restarted.")
        else:
            print("Update failed.")
    else:
        print("No update is available or already on the latest version.")

if __name__ == "__main__":
    main()
