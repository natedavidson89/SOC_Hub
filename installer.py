import os
import shutil
import sys
import winshell
from PyQt5.QtWidgets import QApplication, QMessageBox

def copy_files(install_dir):
    source_dir = os.path.dirname(os.path.realpath(__file__))
    files_to_copy = ['dist/main.exe']  # Add other necessary files here

    for file in files_to_copy:
        source_file = os.path.join(source_dir, file)
        dest_file = os.path.join(install_dir, os.path.basename(file))
        if os.path.exists(source_file):
            shutil.copy2(source_file, dest_file)
            print(f"Copied {source_file} to {dest_file}")
        else:
            print(f"File {source_file} not found. Skipping.")

def create_shortcut(install_dir):
    desktop = winshell.desktop()
    target = os.path.join(install_dir, 'main.exe')
    shortcut_path = os.path.join(desktop, 'SOC Hub.lnk')
    with winshell.shortcut(shortcut_path) as shortcut:
        shortcut.path = target
        shortcut.description = "Shortcut to SOC Hub"
    print(f"Shortcut created at {shortcut_path}")

def main():
    app = QApplication(sys.argv)
    default_install_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'SOC_Hub')

    if not os.path.exists(default_install_dir):
        os.makedirs(default_install_dir)

    copy_files(default_install_dir)
    create_shortcut(default_install_dir)
    QMessageBox.information(None, "Installation Complete", f"The application has been installed to {default_install_dir}")

if __name__ == '__main__':
    main()