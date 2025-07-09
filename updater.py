import os
import sys
import shutil
import requests

def download_file(download_url, save_path):
    response = requests.get(download_url, stream=True)
    with open(save_path, 'wb') as file:
        shutil.copyfileobj(response.raw, file)
    print(f"Downloaded {os.path.basename(save_path)} to {save_path}")

def main():
    # URLs to download the new main.exe
    main_exe_url = "https://github.com/natedavidson89/SOC_Hub/releases/latest/download/main.exe"
    
    new_exe_path = os.path.join(os.path.dirname(sys.executable), 'new_main.exe')
    
    # Download the new main.exe
    download_file(main_exe_url, new_exe_path)
    
    # Paths to the current main.exe and version.txt
    current_exe_path = os.path.join(os.path.dirname(sys.executable), 'main.exe')
    config_dir = os.path.join(os.path.dirname(sys.executable), 'config')
    current_version_path = os.path.join(config_dir, 'version.txt')
    
    # Delete the current main.exe
    if os.path.exists(current_exe_path):
        os.remove(current_exe_path)
        print(f"Deleted old main.exe at {current_exe_path}")
    
    # Move the new main.exe to replace the old one
    shutil.move(new_exe_path, current_exe_path)
    print(f"Moved new main.exe to {current_exe_path}")

    # Fetch the latest version tag from GitHub
    latest_version_url = "https://api.github.com/repos/natedavidson89/SOC_Hub/releases/latest"
    response = requests.get(latest_version_url)
    latest_version = response.json()["tag_name"]
    
    # Update version.txt with the latest version tag
    with open(current_version_path, 'w') as version_file:
        version_file.write(latest_version)
    print(f"Updated version.txt to {latest_version}")

    # Restart the main.exe
    os.startfile(current_exe_path)
    sys.exit()

if __name__ == '__main__':
    main()