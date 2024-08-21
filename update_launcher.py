import sys
import os
import subprocess
import requests
import zipfile
from pathlib import Path

def download_and_extract_update(repo, current_version):
    url = f'https://api.github.com/repos/{repo}/releases/latest'
    try:
        response = requests.get(url)
        response.raise_for_status()
        latest_release = response.json()
        latest_version = latest_release['tag_name']

        if current_version != latest_version:
            download_url = latest_release['zipball_url']
            zip_path = 'latest_release.zip'
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            with open(zip_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    # Extract files directly to the current directory
                    source = zip_ref.open(member)
                    target = Path(member)
                    target.write_bytes(source.read())

            os.remove(zip_path)

            # Restart the application
            restart_application()
        else:
            print("No update needed.")
            sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def restart_application():
    """Restart the application."""
    python = sys.executable
    os.execl(python, python, *sys.argv)

if __name__ == '__main__':
    repo = 'natedavidson89/SOC_Hub'
    current_version = 'v1.0.0'
    download_and_extract_update(repo, current_version)
