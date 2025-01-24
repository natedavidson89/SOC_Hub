import os
import shutil
import sys
import time

def replace_executable(new_exe_path, old_exe_path, backup_exe_path):
    # Wait for the main application to exit
    time.sleep(2)  # Adjust the sleep time as needed

    # Backup the old executable
    if os.path.exists(old_exe_path):
        shutil.move(old_exe_path, backup_exe_path)
        print(f"Backup of old version created at {backup_exe_path}")

    # Replace with the new executable
    shutil.move(new_exe_path, old_exe_path)
    print(f"Replaced old executable with the new one.")

    # Restart the main application
    os.startfile(old_exe_path)
    print("Application restarted.")

if __name__ == "__main__":
    # Determine the base directory where the executable or script is located
    if getattr(sys, 'frozen', False):
        # If running as an executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # If running as a script
        base_dir = os.path.dirname(os.path.abspath(__file__))

    new_exe_path = os.path.join(base_dir, sys.argv[1])
    old_exe_path = os.path.join(base_dir, sys.argv[2])
    backup_exe_path = os.path.join(base_dir, sys.argv[3])
    replace_executable(new_exe_path, old_exe_path, backup_exe_path)