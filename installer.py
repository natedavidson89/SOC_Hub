import os
import shutil
import sys
import winshell
import filecmp
from PyQt5.QtWidgets import QApplication, QMessageBox

def copy_files(install_dir):
    # Determine the base directory where the executable or script is located
    base_dir = os.path.dirname(os.path.realpath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    files_to_copy = ['main.exe', 'version.txt', 'updater.py']  # Add other necessary files here

    config_dir = os.path.join(install_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)

    for file in files_to_copy:
        source_file = os.path.join(base_dir, file)
        if file == 'version.txt':
            dest_file = os.path.join(config_dir, os.path.basename(file))
        else:
            dest_file = os.path.join(install_dir, os.path.basename(file))
        
        if os.path.exists(source_file):
            if os.path.abspath(source_file) != os.path.abspath(dest_file):
                if os.path.exists(dest_file) and not filecmp.cmp(source_file, dest_file, shallow=False):
                    os.remove(dest_file)
                    print(f"Deleted existing file {dest_file}")
                shutil.copy2(source_file, dest_file)
                print(f"Copied {source_file} to {dest_file}")
            else:
                print(f"Source and destination are the same for {source_file}, skipping copy.")
        else:
            print(f"Source file {source_file} does not exist")

def create_shortcut(install_dir):
    desktop = winshell.desktop()
    target = os.path.join(install_dir, 'main.exe')
    shortcut_path = os.path.join(desktop, 'SOC Hub.lnk')
    with winshell.shortcut(shortcut_path) as shortcut:
        shortcut.path = target
        shortcut.description = "Shortcut to SOC Hub"
        shortcut.working_directory = install_dir
        shortcut.icon_location = (target, 0)
    print(f"Shortcut created at {shortcut_path}")

def main():
    app = QApplication(sys.argv)
    
    # Get the local AppData folder path
    local_appdata = os.getenv('LOCALAPPDATA')
    if not local_appdata:
        QMessageBox.critical(None, "Installation Error", "Could not find the local AppData folder.")
        sys.exit(1)
    
    # Set the install_dir to SOC_Hub within the local AppData folder
    install_dir = os.path.join(local_appdata, 'SOC_Hub')
    os.makedirs(install_dir, exist_ok=True)
    
    copy_files(install_dir)
    create_shortcut(install_dir)
    QMessageBox.information(None, "Installation Complete", "SOC Hub has been installed successfully.")
    sys.exit(0)

if __name__ == '__main__':
    main()