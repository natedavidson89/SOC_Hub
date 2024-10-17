import time
import httpx
import json
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse
import re
import yaml
from credentialsInput import CredentialsInputDialog
from PyQt5.QtWidgets import QApplication, QDialog

def extract_double_underscore_values(html):
    # Use regex to find all occurrences of strings starting with __ and followed by | and a value
    pattern = r"\|(__[A-Z0-9_]+)\|([^\|]+)\|"
    matches = re.findall(pattern, html)
    
    # Create a dictionary from the matches
    values_dict = {match[0]: match[1] for match in matches}
    return values_dict

def parse_redirect_instruction(response_text):
    # Look for the redirect instruction pattern in the response text
    marker = "pageRedirect||"
    start = response_text.find(marker)
    if start != -1:
        # Extract the URL part after the marker
        start += len(marker)
        end = response_text.find("|", start)
        if end == -1: end = len(response_text)
        redirect_url = response_text[start:end]
        # Decode the URL
        redirect_url = redirect_url.replace("%2f", "/").replace("%253f", "?").replace("%3d", "=").replace("%25253f", "?")
        return redirect_url
    return None


def find_elements_and_save_as_dictionary(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    elements_dictionary = {}
    elements = soup.find_all(id=lambda x: x and "__" in x)
    for element in elements:
        element_id = element.get('id')
        element_value = element.get('value', element.text)
        elements_dictionary[element_id] = element_value
    
    # print(elements_dictionary)

    return elements_dictionary

class AeriesAPI:
    def __init__(self, ESY=False):
        self.credentials = yaml.safe_load(open("credentials.yml", "r"))
        self.aesopCredentials = self.credentials.get("AESOP", {})
        self.aesopUsername = self.aesopCredentials.get("username", "")
        self.aesopPassword = self.aesopCredentials.get("password", "")
        self.aesopSchool = self.aesopCredentials.get("schoolNumber", "")

        if not self.aesopUsername or not self.aesopPassword or not self.aesopSchool:
            self.collect_credentials()

        self.ESY = ESY
        self.school = self.aesopSchool if self.ESY == False else f"2{self.aesopSchool}"
        self.database = "Special Ed" if self.ESY == False else "Summer/ESY"
        self.client = self.login()

    def collect_credentials(self):      
        app = QApplication([])
        dialog = CredentialsInputDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.aesopUsername = dialog.username
            self.aesopPassword = dialog.password
            self.aesopSchool = dialog.school
            self.save_credentials()

    def save_credentials(self):
        self.credentials['AESOP'] = {
            'username': self.aesopUsername,
            'password': self.aesopPassword,
            'schoolNumber': self.aesopSchool
        }
        with open("credentials.yml", "w") as file:
            yaml.dump(self.credentials, file)

    def login(self):
        client = self.login1()
        client2 = self.login2(client)        
        client3 = self.login3(client2)
        #print("client cookies: ", client.cookies)
        return client3

    def login1(self):
        url = "https://santaclaracoe.aeries.net/admin/Login.aspx"
        data = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            # "__VIEWSTATE": "zFkTXE9Xh0URjRaucsjqFxO50lGlPnvU+4e+0yVE8Q5sBpgdIftiXw2oHF43sQtRrjp4RXqcnZWqrorrCs4B0Bw3cMVgycCYmg0e+gFyy25Yn2KZC5sbD4osMvZM6MQcBUNq6j9pb4PhcB2ujqVrf+1FW9QN58sNolbTOsac0L/+2GFA/ot2DFD21ay9i+udNBjayR2GSoUjE+g6bGHK7nmtkmOBQZRtajteb35hQns1g8kt2HXgtW1DJJ/kkyAVMdOT2c2KKBZYK8w9s7S7FCi5t0S0iBq+H3X6Ws3zFHwL7IfDQHYWlH/hFr8lVnTgVa3b69IMbMr5uslTHUXJVQN1bcPRnQ2Qrp76sSiE+7LqCtoulgZAjKxCXb//2HUiaeF44YzG+BQWzAcb832wx2RdH/BPJhHPhIA+9CgatCvKTkfP8e6yiooCUSwekxNwZgIfXyTo8lk0MSMTt+OHF+sf4AEU3VuOrdasp4tHWXFpZ0bwZxHUgbdZ3Nnowxaqsdagz1BsMrkkLy0mbbLonlhYWjS37OJQBnGfLFOn/QIXXM82ZjPd0miGowaa0663jmWnNho4Oo1r+EuUZ7NWwVIYZU4mO63z6svBRm82Yrok3KrdsHjIPkz3cCklK0zF+G+tDY5NxNC1MenRzJaNLw==",
            # "__VIEWSTATEGENERATOR": "1D3207DC",
            # "__VIEWSTATEENCRYPTED": "",
            "SelectedLogin": "0",
            "SelectedSchool": "",
            "SelectedDatabase": self.database,
            "SelectedYear": "2024-25",
            "ActiveDirectoryUsername": "0",
            "ReturnPage": "",
            "Username_Aeries": self.aesopUsername,
            "Password_Aeries": self.aesopPassword,
            "Database_Aeries": self.database,
            "Year_Aeries": "2024-2025",
            "btnSignIn_Aeries": "Sign In"
        }

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            # "cookie": "s=fbkrno0gjuab4pljf14kbixi; AWSALB=Rm3BwMWz4W3gQdtWPuoa4owh4Ac04Bdya2So1INuTyS/VEJukgsEuQsfeaHY6Yo0cg+htCU3HoxRwHGXKBNdDMhOq//bBnngKMmEfVofu1isdSW0gJ9297YCc3+e; AWSALBCORS=Rm3BwMWz4W3gQdtWPuoa4owh4Ac04Bdya2So1INuTyS/VEJukgsEuQsfeaHY6Yo0cg+htCU3HoxRwHGXKBNdDMhOq//bBnngKMmEfVofu1isdSW0gJ9297YCc3+e",
            "origin": "https://santaclaracoe.aeries.net",
            "referer": "https://santaclaracoe.aeries.net/admin/Login.aspx",
            "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }

        client = httpx.Client()
        response = client.post(url, headers=headers, data=data)
        #print("login cookies: ", response.cookies)

        # print(response.status_code)
        # for cookie in client.cookies.jar:
        #     print(f"{cookie.name}: {cookie.value}")

        return client

    def login2(self, client):
        url = "https://santaclaracoe.aeries.net/admin/Login.aspx"
        data = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "SelectedLogin": "0",
            "SelectedSchool": "",
            "SelectedDatabase": self.database,
            "SelectedYear": "2024-2025",
            "ActiveDirectoryUsername": "0",
            "ReturnPage": "",
            "Username_Aeries": self.aesopUsername,
            "Password_Aeries": self.aesopPassword,
            "Database_Aeries": self.database,
            "Year_Aeries": "2024-2025",
            "btnSignIn_Aeries": "Sign In"
        }

        response = client.post(url, data=data)

        # print(response.status_code)
        # for cookie in client.cookies.jar:
        #     print(f"{cookie.name}: {cookie.value}")

        return client

    def login3(self, client):
        url = "https://santaclaracoe.aeries.net/admin/Login.aspx"
        data = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "SelectedLogin": "0",
            "SelectedSchool": self.school,
            "SelectedDatabase": self.database,
            "SelectedYear": "2024-2025",
            "ActiveDirectoryUsername": "0",
            "ReturnPage": "",
            "School_Aeries": self.school,
            "btnContinueIn_Aeries": "Continue"
        }

        response = client.post(url, data=data)

        # print(response.status_code)
        # for cookie in client.cookies.jar:
        #     print(f"{cookie.name}: {cookie.value}")

        return client
    
    def query(self, queryString):
        self.sendQuery(queryString)
        data = self.getQuery()
        #print(data)
        return data

    def sendQuery(self, queryString):
        url = "https://santaclaracoe.aeries.net/admin/Query.aspx"
        
        data = {
            "ctl00_NavigationTree_ExpandState": "nunnnnnnunnnnnnnnunnnnnnnnnnunnnunnnnnunnnnnnnununnnnnnnnnunnnnnnnnnnnnnnnnunnunnnnnnunnnnunnunnnnnunnnnunnnnnnnnununnnnnnnnnnnnununnunnnnnnnununuunuunnnunnnnnunn",
            "ctl00_NavigationTree_SelectedNode": "",
            "ctl00$SC": self.school,
            "ctl00$SN": "1",
            "ctl00$PID": "80008",
            "ctl00$ShowStuSearch": "false",
            "ctl00$chkHighlightStateReportingFields": "on",
            "ctl00$CurrentDBGroup": self.database,
            "ctl00$MainContent$subPageHead$RedFlagValue": "",
            "ctl00$MainContent$txtInput": queryString,
            "ctl00$MainContent$btnRun": "Run",
            "ctl00$MainContent$txtTables": " |STU|TCH|",
            "ctl00$MainContent$txtExtendedTables": "",
            "ctl00$MainContent$txtQueryLoadSort": "QN",
            "ctl00$chkIncInactiveStus": "on",
            "ctl00$chkFuzzySearch": "on",
            "StudentSearchLimiter": "250",
            "ctl00$txtStudentGroups": "0",
            "ctl00$StuSearchReverseFilter": "",
            "ctl00$Last10Students": "False",
            "ctl00$StuSearchValue": "",
            "ctl00$hfLinkClicked": "0",
            "__LASTFOCUS": "",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": ""
        }
        response = self.client.post(url, data=data)
        #print("send query response: ", response)
        #print(response.text)
        return response

    def getQuery(self):
        url = "https://santaclaracoe.aeries.net/admin/api/query/getqueryresults"
        response = self.client.get(url)
        #print("Query Response: ", response)
        # print(response.json()["Data"])
        return response.json()["Data"]

    def checkAttendanceSubmission(self, startDate=None, endDate=None):
        # Get today's date
        today = datetime.today()
        
        # Format the date without zero padding
        formatted_date = f"{today.month}-{today.day}-{today.year}"

        # If startDate is not provided, set it to today's date
        if startDate is None:
            startDate = formatted_date

        # If endDate is not provided, set it to the same as startDate
        if endDate is None:
            endDate = startDate

        # Define the URL
        url = f"https://santaclaracoe.aeries.net/admin/Attendance/GetAttSubmission/StartDate/{startDate}/EndDate/{endDate}/StartTime/08-00/EndTime/15-00/Onlymissing/true/PdLow/-1/PdHigh/-1/track/ALL"

        # Define the headers
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-US,en;q=0.9",
            "priority": "u=1, i",
            "referer": "https://santaclaracoe.aeries.net/admin/AttendanceSubmissionLog.aspx",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest",
            # Uncomment and properly format any necessary headers
            "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }

        # Make the GET request
        response = self.client.get(url, headers=headers)

        #print(response.json())

        return response.json()

# test = AeriesAPI()
# test.login()
# test.query("LIST STU LN FN ")