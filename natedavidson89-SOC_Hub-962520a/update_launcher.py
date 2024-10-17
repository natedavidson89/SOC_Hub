import sys
import os
import requests
import zipfile
from pathlib import Path

def get_current_version(version_file='version.txt'):
    """Read the current version from version.txt."""
    try:
        if Path(version_file).exists():
            with open(version_file, 'r') as file:
                version = file.read().strip()
                return version
        else:
            return None
    except Exception as e:
        print(f"An error occurred while reading {version_file}: {e}")
        return None

def download_and_extract_update(repo):
    """Download and extract update if necessary."""
    current_version = get_current_version()
    if current_version is None:
        print("version.txt is missing or cannot be read.")
        sys.exit(1)

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

            # Update the version.txt file with the latest version
            update_version_file(latest_version)

            # Restart the application
            restart_application()
        else:
            print("No update needed.")
            sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def update_version_file(new_version, version_file='version.txt'):
    """Update the version.txt file with the new version."""
    try:
        with open(version_file, 'w') as file:
            file.write(new_version)
        print(f"Version updated to {new_version}.")
    except Exception as e:
        print(f"An error occurred while updating {version_file}: {e}")

def restart_application():
    """Restart the application."""
    python = sys.executable
    os.execl(python, python, *sys.argv)

if __name__ == '__main__':
    repo = 'natedavidson89/SOC_Hub'
    download_and_extract_update(repo)
