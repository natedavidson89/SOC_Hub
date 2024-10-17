import json
import httpx
import yaml
from datetime import datetime
import json
import os
from credentialsInput import CredentialsInputDialog
from PyQt5.QtWidgets import QApplication, QDialog
import time
from urllib.parse import urlparse, parse_qs

class AESOP_API:
    def __init__(self):
        self.credentials_file = "credentials.yml"
        self.credentials = self.load_credentials()
        self.aesopCredentials = self.credentials.get("aesop", {})
        self.aesopUsername = self.aesopCredentials.get("username", "")
        self.aesopPassword = self.aesopCredentials.get("password", "")
        self.keys = goFetch(aesopUsername=self.aesopUsername, aesopPassword=self.aesopPassword)
        print(self.keys)
       
    


        if not self.aesopUsername or not self.aesopPassword:
            self.collect_credentials()


    def load_credentials(self):
        if not os.path.exists(self.credentials_file):
            with open(self.credentials_file, "w") as file:
                yaml.dump({"aesop": {}}, file)
            return {"aesop": {}}
        else:
            with open(self.credentials_file, "r") as file:
                credentials = yaml.safe_load(file) or {}
                if "aesop" not in credentials:
                    credentials["aesop"] = {}
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
        with open("credentials.yml", "w") as file:
            yaml.dump(self.credentials, file)





def goFetch(aesopUsername, aesopPassword):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    import yaml

    # Setup Chrome options
    options = ChromeOptions()
    options.add_argument("--headless=new")  # Use --headless for headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems


    # Use webdriver-manager to manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Initialize ActionChains
    actions = ActionChains(driver)

    # Open the URL
    driver.get("https://login.frontlineeducation.com/login?signin=3ef4b029ed1af83af01001cb317a064d&productId=ABSMGMT&clientId=ABSMGMT#/login")

    # Wait for the page to load
    delay = 60
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, "Username")))
        print("Page is Ready!")
    except TimeoutException:
        print("Page took too long")

    # Load credentials from YAML file
    username = aesopUsername
    password = aesopPassword

    # Perform login
    driver.find_element(By.ID, "Username").send_keys(username)
    driver.find_element(By.ID, "Password").send_keys(password)
    driver.find_element(By.ID, "qa-button-login").click()
    print("Logged in successfully!")
    delay = 45
    try:
        myElem1 = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.NAME,"schoolFilter")))
        print("Page is Ready!")
        # time.sleep(2)
    except TimeoutException:
        print("Page took too long")

    # Handle AESOP Notification
    try:
        driver.find_element(By.ID, "ngdialog1")
        driver.execute_script('''angular.element('[ng-click = "button.action(ngDialogData.selectedId)"]').triggerHandler('click')''')
        print("Notification box closed successfully")
    except NoSuchElementException:
        print("No notification box present at login")


    driver.get('https://absenceadminweb.frontlineeducation.com/reports/employee/staff-list')
    delay = 60
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'vacancies')))
        print("Page is Ready!")
    except TimeoutException:
        print("Page took too long")

    # time.sleep(3)
    loggedInOrgIdKey = json.loads(driver.execute_script("return sessionStorage['loggedInOrgId']"))
    loggedInOrgId = loggedInOrgIdKey['data']
    print("logged in org ID")
    print(loggedInOrgId)
    # time.sleep(2)

    # test = json.loads(driver.execute_script("return sessionStorage"))
    # print("TESTING!!!!!!")
    # print(test)


    AESOPTokenKey = json.loads(driver.execute_script("return sessionStorage['token']"))
    AESOPToken = AESOPTokenKey['data']

    allDeets = driver.execute_script("return sessionStorage")
    authTokenKey = []
    for deet in allDeets:
        if len(deet) > 20:
            authTokenKey.append(deet)

    authTokengroup = json.loads(allDeets[f"{authTokenKey[0]}"])
    authToken = f"Bearer {authTokengroup['access_token']}"

    print(AESOPToken, authToken)

    keysDict = [{'AESOPToken' : AESOPToken, 'authToken': authToken, "loggedInOrgId": loggedInOrgId}]

    with open('keys.yml', 'w') as file:
        documents = yaml.dump(keysDict, file)
    driver.quit()
    return keysDict
