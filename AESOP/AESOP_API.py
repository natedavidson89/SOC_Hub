import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import json
import httpx
import yaml
from datetime import datetime
import json
from credentialsInput import CredentialsInputDialog
from PyQt5.QtWidgets import QApplication, QDialog
from urllib.parse import urlparse, parse_qs

class AESOP_API:
    def __init__(self):
        self.credentials_file = "credentials.yml"
        print('credentials file: ', self.credentials_file)
        self.credentials = self.load_credentials()
        self.aesopCredentials = self.credentials.get("aesop", {})
        self.aesopUsername = self.aesopCredentials.get("username", "")
        self.aesopPassword = self.aesopCredentials.get("password", "")

        # Check if credentials are missing and collect them if necessary
        if not self.aesopUsername or not self.aesopPassword:
            print("AESOP credentials are missing. Collecting credentials...")
            self.collect_credentials()

        # Fetch keys after ensuring credentials are available
        self.keys = self.goFetch()
        print(self.keys)

    def load_credentials(self):
        print("Loading credentials...")
        if not os.path.exists(self.credentials_file):
            with open(self.credentials_file, "w") as file:
                yaml.dump({"aesop": {}}, file)
            return {"aesop": {}}
        else:
            with open(self.credentials_file, "r") as file:
                credentials = yaml.safe_load(file) or {}
                print('Existing credentials: ', credentials)
                if "aesop" not in credentials:
                    print("AESOP credentials not found in credentials file. Adding default structure.")
                    credentials["aesop"] = {}
                    # Save the updated credentials back to the file
                    with open(self.credentials_file, "w") as file:
                        yaml.dump(credentials, file)
                return credentials

    def collect_credentials(self):
        app = QApplication([])
        dialog = CredentialsInputDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.aesopUsername = dialog.username
            self.aesopPassword = dialog.password
            self.aesopSchool = dialog.school
            self.save_credentials()

    def save_credentials(self):
        self.credentials['aesop'] = {
            'username': self.aesopUsername,
            'password': self.aesopPassword,
        }
        with open(self.credentials_file, "w") as file:
            yaml.dump(self.credentials, file)

    def goFetch(self):
        import yaml
        import json

        from selenium import webdriver
        from selenium.webdriver import ChromeOptions
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager

        print("Going to fetch keys. Brb")

        chrome_install = ChromeDriverManager().install()
        folder = os.path.dirname(chrome_install)
        chromedriver_path = os.path.join(folder, "chromedriver.exe")
        print("chromedriver path: ", chromedriver_path)

        service = ChromeService(chromedriver_path)
        options = ChromeOptions()
        options.add_argument('ignore-certificate-errors')
        options.add_argument("--headless=new")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")

AESOP_API()
       