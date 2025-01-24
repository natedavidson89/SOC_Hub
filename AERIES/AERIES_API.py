import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime
import httpx
import json
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse
import re
import yaml
from credentialsInput import CredentialsInputDialog
from PyQt5.QtWidgets import QApplication, QDialog
import os
from AERIES.attendanceReports import Reports

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

class AeriesAPIz:
    def __init__(self, ESY=False):
        self.credentials_file = "credentials.yml"
        self.credentials = self.load_credentials()
        self.aeriesCredentials = self.credentials.get("aeries", {})
        self.aeriesUsername = self.aeriesCredentials.get("username", "")
        self.aeriesPassword = self.aeriesCredentials.get("password", "")
        self.aeriesSchool = self.aeriesCredentials.get("schoolNumber", "")
        self.schoolYear = self.getSchoolYear()


        if not self.aeriesUsername or not self.aeriesPassword or not self.aeriesSchool:
            self.collect_credentials()

        self.ESY = ESY
        self.school = self.aeriesSchool if self.ESY == False else f"2{self.aeriesSchool}"
        self.database = "Special Ed" if self.ESY == False else "Summer/ESY"
        self.client = self.login()

    def getSchoolYear(self):
        currentDate = datetime.now()
        if currentDate.month >= 7:
            return f"{currentDate.year}-{currentDate.year+1}"
        else:
            return f"{currentDate.year-1}-{currentDate.year}"
        

    def load_credentials(self):
        if not os.path.exists(self.credentials_file):
            with open(self.credentials_file, "w") as file:
                yaml.dump({"aeries": {}}, file)
            return {"aeries": {}}
        else:
            with open(self.credentials_file, "r") as file:
                credentials = yaml.safe_load(file) or {}
                if "aeries" not in credentials:
                    credentials["aeries"] = {}
            return credentials

    def collect_credentials(self):      
        app = QApplication([])
        dialog = CredentialsInputDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.aeriesUsername = dialog.username
            self.aeriesPassword = dialog.password
            self.aeriesSchool = dialog.school
            self.save_credentials()

    def save_credentials(self):
        self.credentials['aeries'] = {
            'username': self.aeriesUsername,
            'password': self.aeriesPassword,
            'schoolNumber': self.aeriesSchool
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
            "SelectedYear": self.schoolYear,
            "ActiveDirectoryUsername": "0",
            "ReturnPage": "",
            "Username_Aeries": self.aeriesUsername,
            "Password_Aeries": self.aeriesPassword,
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

        # print(data)

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
            "Username_Aeries": self.aeriesUsername,
            "Password_Aeries": self.aeriesPassword,
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
        # print(data)
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
        # print("send query response: ", response)
        #print(response.text)
        return response

    def getQuery(self):
        url = "https://santaclaracoe.aeries.net/admin/api/query/getqueryresults"
        response = self.client.get(url)
        # print("Query Response: ", response)
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
    
    def addSCIA(self):
        url = "https://santaclaracoe.aeries.net/admin/UserDefinedStudentData.aspx?TC=NOTO"

        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "accept-encoding": "gzip, deflate, br, zstd",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://santaclaracoe.aeries.net",
            "priority": "u=1, i",
            "referer": "https://santaclaracoe.aeries.net/admin/UserDefinedStudentData.aspx?TC=NOTO",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "x-microsoftajax": "Delta=true",
            "x-requested-with": "XMLHttpRequest"
        }

        data = {
            "ctl00$TheMasterScriptManager": "ctl00$MainContent$subCustom$EditCustom_UpdatePanel|ctl00$MainContent$subCustom$btnInitEditPanel",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "ctl00_NavigationTree_ExpandState": "nunnnnnnennnnnnnnnunnnnnnnnnnunnnunnnnnunnnnnnnnunnennnnnnnnnunnnnnnnnnnnnnnnnnunnunnnnnnnnnunnunnnnunnunnnnnnunnnnunnnnnnnnnununnnnnnnnnnnnununnnunnnnnnnununuunuunnnunnnnnunn",
            "ctl00_NavigationTree_SelectedNode": "ctl00_NavigationTreet58",
            "__LASTFOCUS": "",
            "ctl00$SC": self.school,
            "ctl00$SN": "115",
            "ctl00$PID": "88454",
            "ctl00$ShowStuSearch": "false",
            "ctl00$chkHighlightStateReportingFields": "on",
            "ctl00$CurrentDBGroup": self.database,
            "ctl00$MainContent$subPageHead$PageFlagEditable": "True",
            "page-flag-SC": self.school,
            "page-flag-SN": "115",
            "page-flag-Name": "NOTO",
            "ctl00$MainContent$subPageHead$pageFlagCommentInput": "",
            "ctl00$MainContent$subPageHead$RedFlagValue": "",
            "ctl00$MainContent$subCustom$hfSummarySQ": "0",
            "ctl00$MainContent$subCustom$rptSummary$ctl00$txtSQ": "6",
            "ctl00$MainContent$subCustom$rptSummary$ctl01$txtSQ": "5",
            "ctl00$MainContent$subCustom$rptSummary$ctl02$txtSQ": "4",
            "ctl00$MainContent$subCustom$rptSummary$ctl03$txtSQ": "3",
            "ctl00$MainContent$subCustom$rptSummary$ctl04$txtSQ": "1",
            "ctl00$MainContent$subCustom$txtMO$txtControlValue": "",
            "ctl00$MainContent$subCustom$txtMO$txtValue": "",
            "ctl00$MainContent$subCustom$txtYR$txtControlValue": "",
            "ctl00$MainContent$subCustom$txtYR$txtValue": "",
            "ctl00$MainContent$subCustom$txtSD$txtKendoDatePicker": "",
            "ctl00$MainContent$subCustom$txtEOC": "",
            "ctl00$MainContent$subCustom$txtDA": "",
            "ctl00$MainContent$subCustom$txtDAC": "",
            "ctl00$MainContent$subCustom$txtTAT$txtControlValue": "",
            "ctl00$MainContent$subCustom$txtTAT$txtValue": "",
            "ctl00$MainContent$subCustom$txtTAN": "",
            "ctl00$MainContent$subCustom$txtTHR": "",
            "ctl00$MainContent$subCustom$txtTST$txtControlValue": "",
            "ctl00$MainContent$subCustom$txtTST$txtValue": "",
            "ctl00$MainContent$subCustom$txtTPC": "",
            "ctl00$MainContent$subCustom$txtSAT$txtControlValue": "",
            "ctl00$MainContent$subCustom$txtSAT$txtValue": "",
            "ctl00$MainContent$subCustom$txtSAN": "",
            "ctl00$MainContent$subCustom$txtSHR": "",
            "ctl00$MainContent$subCustom$txtSST$txtControlValue": "",
            "ctl00$MainContent$subCustom$txtSST$txtValue": "",
            "ctl00$MainContent$subCustom$txtSPC": "",
            "ctl00$MainContent$subCustom$txtMAT$txtControlValue": "",
            "ctl00$MainContent$subCustom$txtMAT$txtValue": "",
            "ctl00$MainContent$subCustom$txtMAN": "",
            "ctl00$MainContent$subCustom$txtMHR": "",
            "ctl00$MainContent$subCustom$txtMST$txtControlValue": "",
            "ctl00$MainContent$subCustom$txtMST$txtValue": "",
            "ctl00$MainContent$subCustom$txtMPC": "",
            "ctl00$MainContent$subStuTopAll$subQuickCON$ddlSort": "ContactOrder",
            "ctl00$chkIncInactiveStus": "on",
            "ctl00$chkFuzzySearch": "on",
            "StudentSearchLimiter": "250",
            "ctl00$txtStudentGroups": "0",
            "ctl00$StuSearchReverseFilter": "",
            "ctl00$Last10Students": "False",
            "ctl00$StuSearchValue": "",
            "ctl00$hfLinkClicked": "0",
            "__ASYNCPOST": "true",
            "ctl00$MainContent$subCustom$btnInitEditPanel": ""
        }


        print("data: ", data )

        response = self.client.post(url, headers=headers, data=data, follow_redirects=True)

        

        print("response1 text: ", response.text)
       
        url2 = "https://santaclaracoe.aeries.net/admin/UserDefinedStudentData.aspx?TC=NOTO"

        headers2 = {
            "accept": "*/*",
            "host": "",
            "connection": "",
            # "content-length": "",
            # "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://santaclaracoe.aeries.net",
            # "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://santaclaracoe.aeries.net/admin/UserDefinedStudentData.aspx?TC=NOTO",
            "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "x-microsoftajax": "Delta=true",
            "x-requested-with": "XMLHttpRequest"
        }

        data2 = {
            "ctl00$TheMasterScriptManager": "ctl00$MainContent$subCustom$EditCustom_UpdatePanel|ctl00$MainContent$subCustom$btnUpdateCustom",
            "ctl00_NavigationTree_ExpandState": "nunnnnnnennnnnnnnnunnnnnnnnnnunnnunnnnnunnnnnnnnunnennnnnnnnnunnnnnnnnnnnnnnnnnunnunnnnnnnnnunnunnnnunnunnnnnnunnnnunnnnnnnnnununnnnnnnnnnnnununnnunnnnnnnununuunuunnnunnnnnunn",
            "ctl00_NavigationTree_SelectedNode": "ctl00_NavigationTreet58",
            "ctl00$SC": self.school,
            "ctl00$SN": "115",
            "ctl00$PID": "88454",
            "ctl00$ShowStuSearch": "false",
            "ctl00$chkHighlightStateReportingFields": "on",
            "ctl00$CurrentDBGroup": self.database,
            "ctl00$MainContent$subPageHead$PageFlagEditable": "True",
            "page-flag-SC": self.school,
            "page-flag-SN": "115",
            "page-flag-Name": "NOTO",
            "ctl00$MainContent$subPageHead$pageFlagCommentInput": "",
            "ctl00$MainContent$subPageHead$RedFlagValue": "",
            "ctl00$MainContent$subCustom$hfSummarySQ": "0",
            "ctl00$MainContent$subCustom$rptSummary$ctl00$txtSQ": "6",
            "ctl00$MainContent$subCustom$rptSummary$ctl01$txtSQ": "5",
            "ctl00$MainContent$subCustom$rptSummary$ctl02$txtSQ": "4",
            "ctl00$MainContent$subCustom$rptSummary$ctl03$txtSQ": "3",
            "ctl00$MainContent$subCustom$rptSummary$ctl04$txtSQ": "1",
            "ctl00$MainContent$subCustom$txtMO$txtControlValue": "JUL",
            "ctl00$MainContent$subCustom$txtMO$txtValue": "JUL",
            "ctl00$MainContent$subCustom$txtYR$txtControlValue": "2024",
            "ctl00$MainContent$subCustom$txtYR$txtValue": "2024",
            "ctl00$MainContent$subCustom$txtSD$txtKendoDatePicker": "01/11/2021",
            "ctl00$MainContent$subCustom$txtEOC": "",
            "ctl00$MainContent$subCustom$txtDA": "kk",
            "ctl00$MainContent$subCustom$txtDAC": "",
            "ctl00$MainContent$subCustom$txtTAT$txtControlValue": "TN",
            "ctl00$MainContent$subCustom$txtTAT$txtValue": "TN",
            "ctl00$MainContent$subCustom$txtTAN": "yttt",
            "ctl00$MainContent$subCustom$txtTHR": "",
            "ctl00$MainContent$subCustom$txtTST$txtControlValue": "",
            "ctl00$MainContent$subCustom$txtTST$txtValue": "",
            "ctl00$MainContent$subCustom$txtTPC": "4321",
            "ctl00$MainContent$subCustom$txtSAT$txtControlValue": "",
            "ctl00$MainContent$subCustom$txtSAT$txtValue": "",
            "ctl00$MainContent$subCustom$txtSAN": "",
            "ctl00$MainContent$subCustom$txtSHR": "",
            "ctl00$MainContent$subCustom$txtSST$txtControlValue": "",
            "ctl00$MainContent$subCustom$txtSST$txtValue": "",
            "ctl00$MainContent$subCustom$txtSPC": "",
            "ctl00$MainContent$subCustom$txtMAT$txtControlValue": "",
            "ctl00$MainContent$subCustom$txtMAT$txtValue": "",
            "ctl00$MainContent$subCustom$txtMAN": "",
            "ctl00$MainContent$subCustom$txtMHR": "",
            "ctl00$MainContent$subCustom$txtMST$txtControlValue": "",
            "ctl00$MainContent$subCustom$txtMST$txtValue": "",
            "ctl00$MainContent$subCustom$txtMPC": "",
            "ctl00$MainContent$subStuTopAll$subQuickCON$ddlSort": "ContactOrder",
            "ctl00$chkIncInactiveStus": "on",
            "ctl00$chkFuzzySearch": "on",
            "StudentSearchLimiter": "250",
            "ctl00$txtStudentGroups": "0",
            "ctl00$StusearchReverseFilter": "",
            "ctl00$Last10Students": "False",
            "ctl00$StuSearchValue": "",
            "ctl00$hfLinkClicked": "0",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATEENCRYPTED": "",
            "__ASYNCPOST": "true",
            "ctl00$MainContent$subCustom$btnUpdateCustom": "Save"
        }
        
        print("Data2: ", data2)

    
        redirect_url2 = "https://santaclaracoe.aeries.net"+"/admin/Login.aspx?page=UserDefinedStudentData.aspx?TC=NOTO"



        response_redirect2 = self.client.post(redirect_url2, headers=headers2, data=data2)  # Use the appropriate headers

        # Convert the httpx request to a curl command
        method = response_redirect2.request.method
        headers = ["'{}: {}'".format(k, v) for k, v in response_redirect2.request.headers.items()]
        headers = " -H ".join(headers)
        data = response_redirect2.request.content.decode()

        curl_command = "curl -X {method} -H {headers} -d '{data}' '{url}'".format(
            method=method, headers=headers, data=data, url=url2)

        print(curl_command)
       
    def attendanceManager(self):
         # Get the current date
        current_date = datetime.now()


        
        # Format the date as M-D-YYYY without leading zeros
        formatted_date = f"{current_date.month}-{current_date.day}-{current_date.year}"
        
        url = f'https://santaclaracoe.aeries.net/admin/Attendance/GetAttendanceManagementData?sort=&group=&filter=&Filters.Startdate=08%2F07%2F2024&Filters.EndDate={current_date.month}%2F{current_date.day}%2F{current_date.year}&Filters.onlyUnverifedABS=true&Filters.SelectedABS=&Filters.SelectedSTU='#&_=1727726359162' 
        headers ={
            "Accept": "application.json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json; charset=UTF-8",
            "Priority": "u=1, i",
            "Referer": "https://santaclaracoe.aeries.net/admin/AttendanceManagement.aspx",
            "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        }
        payload = {
            "sort": "",
            "group": "",
            "filter": "",
            "Filters.Startdate": "08%2F07%2F2024",
            "Filters.EndDate": current_date.strftime("%m-%d-%Y"),
            "Filters.onlyUnverifiedABS": "true",
            "Filters.SelectedABS": "",
            "Filters.SelectedSTU": "",
        }

        response = self.client.get(url, headers=headers, params=payload)

        data = response.json()["Data"]["Data"]
        print(data)

        

        def convert_json_date(json_date):
            # Extract the timestamp from the JSON date string
            timestamp = int(re.search(r'\d+', json_date).group())
            
            # Convert milliseconds to seconds
            timestamp_seconds = timestamp / 1000
            
            # Create a datetime object from the timestamp
            date = datetime.fromtimestamp(timestamp_seconds)
            
            # Format the date as M-D-YYYY
            formatted_date = date.strftime("%m-%d-%Y")
            
            return formatted_date

        for ABS in data:
            if ABS["HasNote"] == False:
                print("No note found for this absence")
                pass
               
                
                    
            else:
                print("Note found for this absence")
                DT = convert_json_date(ABS["AttDay"])
                SC = self.school
                SN = ABS["SN"]
                urlgetNote = f"https://santaclaracoe.aeries.net/admin/AttendanceNote.aspx?SC={SC}&SN={SN}&DT={DT}&INSERT=1"
                headersgetNote = {
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "accept-encoding": "gzip, deflate, br, zstd",
                    "accept-language": "en-US,en;q=0.9",
                    "priority": "u=1, i",
                    "referer": f"https://santaclaracoe.aeries.net/admin/AttendanceManagement.aspx",
                    "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
                }
                payloadgetNote = {
                    "SC": SC,
                    "SN": SN,
                    "DT": DT,
                    "INSERT": "1",
                }
                # responsegetNote = self.client.get(urlgetNote, headers=headersgetNote, params=payloadgetNote)

                def get_comment_text(urlgetNote, headersgetNote, payloadgetNote):
                    responsegetNote = self.client.get(urlgetNote, headers=headersgetNote, params=payloadgetNote)
                    # print(responsegetNote.text)  # For debugging purposes

                    # Parse the HTML response
                    soup = BeautifulSoup(responsegetNote.text, 'html.parser')

                    # Find the parent div with class "CommentDisplay" and get its inner text
                    comment_element = soup.find("div", class_="CommentDisplay")
                    if comment_element:
                        comment_text = comment_element.get_text(strip=True)
                        print("Comment Text:", comment_text)
                        return comment_text
                    else:
                        print("No element with class='CommentDisplay' found.")
                        return None
                attendanceNote = get_comment_text(urlgetNote, headersgetNote, payloadgetNote)
                ABS["AttendanceNoteText"] = attendanceNote
                #absence code
                if "sick" in attendanceNote.lower() or "covid" in attendanceNote.lower() or "quarantine" in attendanceNote.lower() or "fever" in attendanceNote.lower() or "cough" in attendanceNote.lower() or "ill" in attendanceNote.lower() or "seizure" in attendanceNote.lower() or "seizures" in attendanceNote.lower() or "illness" in attendanceNote.lower() or"not feeling well" in attendanceNote.lower() or "cold" in attendanceNote.lower():
                    absenceCode = "B"
                    print("B ", attendanceNote)
                elif "tired" in attendanceNote.lower() or "slept" in attendanceNote.lower() or "unexcused" in attendanceNote.lower() or "none" in attendanceNote.lower() or "absent" in attendanceNote.lower() or "parent choice" in attendanceNote.lower() or "choice" in attendanceNote.lower() or "no call" in attendanceNote.lower() or "no transportation" in attendanceNote.lower() or "unknown" in attendanceNote.lower() or "esy 2021" in attendanceNote.lower() or "personal" in attendanceNote.lower() or "no reason" in attendanceNote.lower():
                    absenceCode = "U"
                    print("U ", attendanceNote)
                elif "doctor" in attendanceNote.lower() or "dentist" in attendanceNote.lower() or "appt" in attendanceNote.lower() or "appointment" in attendanceNote.lower() or "appointments" in attendanceNote.lower():
                    absenceCode = "D"
                    print("D ", attendanceNote)
                elif "pending is" in attendanceNote.lower():
                    absenceCode = "Q"
                    print("Q ", attendanceNote)
                elif "vacation" in attendanceNote.lower():
                    absenceCode = "V"
                    print("V", attendanceNote)
                else:
                    print("Unable to decipher reason: ", attendanceNote)
                    absenceCode = input(f"Unable to decipher reason: {attendanceNote}\n Please enter absence code: ")

                def fillAbsenceCode(absenceCode):
                    url = "https://santaclaracoe.aeries.net/admin/Attendance/UpdateAtt"
                    headers = {
                        "accept": "application/json, text/javascript, */*; q=0.01",
                        "accept-encoding": "gzip, deflate, br, zstd",
                        "accept-language": "en-US,en;q=0.9",
                        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "origin": "https://santaclaracoe.aeries.net",
                        "priority": "u=1, i",
                        "referer": "https://santaclaracoe.aeries.net/admin/AttendanceManagement.aspx",
                        "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
                    }
                    payload = {
                        "PID": ABS["ID"],
                        "DY": ABS["AttDy"],
                        "PeriodSuffix": "L", #Is this needed?
                        "AbsValue": absenceCode,
                        "FillingPeriod": ""
                    }
                    response = self.client.post(url, headers=headers, data=payload)
                fillAbsenceCode(absenceCode)

    def attendanceReports(self, reportMonth):

        download_destinations = {}

        def fetchReports():
            reportTypes = {
                "Attendance Register by Teacher": {"reportName": "PrintAttendanceRegisterSCCOE", "groupCode": "rbTN" } , 
                "Attendance Register by DOR": {"reportName": "PrintAttendanceRegisterSCCOE", "groupCode": "rbDR" } ,
                "Principal's Report": {"reportName": "PrintPrincipalsMonthlyAttendanceReportSCCOE"} }
            

            for reportTypeKey, ReportTypeValue in reportTypes.items():
                currentClient = self.client

                print("currrently in download destinations: ", download_destinations)
                print("Fetching report: ", reportTypeKey)
                def setReport():
                    url = f"https://santaclaracoe.aeries.net/admin/RunSCCOEReport.aspx?rptname={ReportTypeValue['reportName']}"

                    headers = {
                        "accept": "*/*",
                        "accept-encoding": "gzip, deflate, br, zstd",
                        "accept-language": "en-US,en;q=0.9",
                        "cache-control": "no-cache",
                        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "origin": "https://santaclaracoe.aeries.net",
                        "priority": "u=1, i",
                        "referer": f"https://santaclaracoe.aeries.net/admin/RunSCCOEReport.aspx?rptname={ReportTypeValue['reportName']}",
                        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": '"Windows"',
                        "sec-fetch-dest": "empty",
                        "sec-fetch-mode": "cors",
                        "sec-fetch-site": "same-origin",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                        "x-microsoftajax": "Delta=true",
                        "x-requested-with": "XMLHttpRequest",
                    }


                    data = {
                        "ctl00$TheMasterScriptManager": "ctl00$MainContent$ctl03$upRunReport|ctl00$MainContent$ctl03$btnRunReport",
                        "__EVENTTARGET": "",
                        "__EVENTARGUMENT": "",
                        "ctl00_NavigationTree_ExpandState": "nunnnnnnunnnnnnnnnununnnnnnnnnnunnnunnnnnnnunnnnnnnnunnnunnnnnnnnnunnnnnnnnnnnnnnnnnunnunnnnnnnnnunnunnnnunnunnnunnnnnnnnunnnnunnnunnnnnnnnnnununnnnnnnnnnnnnununnnunnnnnnnununuunuunnnunnnnnunn",
                        "ctl00_NavigationTree_SelectedNode": "",
                        "ctl00$UserMayKeepSkipRecords": "true",
                        "ctl00$KeepSkipStatus": "False",
                        "ctl00$UserEmulationStatus": "False",
                        "ctl00$NextUIPageStatus": "false",
                        "ctl00$SC": self.school,
                        "ctl00$SN": "216",
                        "ctl00$PID": "88454",
                        "ctl00$CurrentDBGroup": "Special Ed",
                        "ctl00$chkHighlightStateReportingFields": "on",
                        "ctl00$ShowStuSearch": "false",
                        "ctl00$MainContent$txtReportTypes": "PDF",
                        "ctl00$MainContent$txtReportDeliveryTypes": "None",
                        "ctl00$MainContent$ctl03$opnMonth": reportMonth,
                    
                        "ctl00$chkIncInactiveStus": "on",
                        "ctl00$chkFuzzySearch": "on",
                        "StudentSearchLimiter": "250",
                        "ctl00$txtStudentGroups": "0",
                        "ctl00$StuSearchReverseFilter": "",
                        "ctl00$Last10Students": "False",
                        "ctl00$StuSearchValue": "",
                        "ctl00$hfLinkClicked": "0",
                        "__ASYNCPOST": "true",
                        "ctl00$MainContent$ctl03$btnRunReport": "Run Report",

                    }
                    if ReportTypeValue["reportName"] != "PrintPrincipalsMonthlyAttendanceReportSCCOE":
                        data["ctl00$MainContent$ctl03$Group"] = ReportTypeValue["groupCode"]
                        # print("Group Code is: ", ReportTypeValue["groupCode"] )
                        # print("payload data: ", data)

                    #get Viewstate
                    VSresponse = currentClient.get(url, headers=headers)
                    soup = BeautifulSoup(VSresponse.text, 'html.parser')

                    # Find all hidden input fields
                    hidden_fields = {}
                    for hidden_input in soup.find_all("input", type="hidden"):
                        name = hidden_input.get("name")
                        value = hidden_input.get("value", "")
                        hidden_fields[name] = value

                    # Add the hidden fields to the data dictionary
                    data.update(hidden_fields)
                    # time.sleep(3)
                    
                    # Make the request                
                    response = currentClient.post(url, headers=headers, data=data)
                    #         # Save the request as a curl command
                    # method = response.request.method
                    # headers_list = ["'{}: {}'".format(k, v) for k, v in response.request.headers.items()]
                    # headers_str = " -H ".join(headers_list)
                    # data_str = "&".join([f"{k}={v}" for k, v in data.items()])
                    # curl_command = f"curl -X {method} -H {headers_str} -d '{data_str}' '{url}'"

                    # # Save the curl command to a file
                    # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    # curl_file_path = os.path.join(os.path.expanduser("~"), "Downloads", f'{reportTypeKey}_Month{reportMonth}_{timestamp}.txt')
                    # with open(curl_file_path, "w") as curl_file:
                    #     curl_file.write(curl_command)
                    # print(f"Curl command saved to {curl_file_path}")


                    # Check response
                    if response.status_code == 200:
                        pass
                        # print("Request successful")
                        # print(response.text)  # Or process response as needed
                    else:
                        print(f"Request failed with status code {response.status_code}")

                
                
                def fetchViewStateRequest():

                    url = "https://santaclaracoe.aeries.net/admin/ViewReport.aspx"

                    # Define the headers as provided in the curl command
                    headers = {
                        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                        "accept-language": "en-US,en;q=0.9",
                        # "cookie": "AeriesNet=LastIdentityProvider=0&LastDatabaseGroup=Special Ed&LastDatabaseYear=2024-2025&LastSchool=14&LastSC_14=14&LastSN_14=216&LastID_14=88454; s=j2pgttn1b4umoxkqt0j1m3ey; _sg_b_v=17%3B2916%3B1730152094; _pk_ref.1.0f3d=%5B%22%22%2C%22%22%2C1730155903%2C%22https%3A%2F%2Faeries.sccoe.org%2F%22%5D; _pk_ses.1.0f3d=1; _pk_id.1.0f3d=6c5b9fc4d855af96.1717796329.20.1730155979.1730152179.; AWSALB=kOxntdTL3NSZKVDyy4Klnz14i2mOm/CGF9f4nqMjBzHzMQsBmDHVEMX5GOvhfppFo3IfnfAxxrtkForoh4/d18XGzF9Xw2h6hnYA5ONckNMHScsiblfY4Xrng+OF; AWSALBCORS=kOxntdTL3NSZKVDyy4Klnz14i2mOm/CGF9f4nqMjBzHzMQsBmDHVEMX5GOvhfppFo3IfnfAxxrtkForoh4/d18XGzF9Xw2h6hnYA5ONckNMHScsiblfY4Xrng+OF",
                        "priority": "u=0, i",
                        "referer": f"https://santaclaracoe.aeries.net/admin/RunSCCOEReport.aspx?rptname={ReportTypeValue['reportName']}",
                        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": '"Windows"',
                        "sec-fetch-dest": "iframe",
                        "sec-fetch-mode": "navigate",
                        "sec-fetch-site": "same-origin",
                        "sec-fetch-user": "?1",
                        "upgrade-insecure-requests": "1",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
                    }
                    
                    data = {}
                    # Perform the GET request with httpx
                    response = currentClient.get(url, headers=headers)

                    #         # Save the request as a curl command
                    # method = response.request.method
                    # headers_list = ["'{}: {}'".format(k, v) for k, v in response.request.headers.items()]
                    # headers_str = " -H ".join(headers_list)
                    # data_str = "&".join([f"{k}={v}" for k, v in data.items()])
                    # curl_command = f"curl -X {method} -H {headers_str} -d '{data_str}' '{url}'"

                    # # Save the curl command to a file
                    # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    # curl_file_path = os.path.join(os.path.expanduser("~"), "Downloads", f'{reportTypeKey}_Month{reportMonth}_{timestamp}.txt')
                    # with open(curl_file_path, "w") as curl_file:
                    #     curl_file.write(curl_command)
                    # print(f"Curl command saved to {curl_file_path}")


                    # Check the response status and print the content
                    if response.status_code == 200:
                        pass
                        # print("Request successful!")
                        # print(response.text)  # or response.content if you're handling binary data
                    else:
                        print(f"Request failed with status code: {response.status_code}")

                    # Parse the HTML response with BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find all hidden input fields
                    hidden_fields = {}
                    for hidden_input in soup.find_all("input", type="hidden"):
                        name = hidden_input.get("name")
                        value = hidden_input.get("value", "")
                        hidden_fields[name] = value

                    # print("Hidden fields:", hidden_fields)

                    return hidden_fields

                
                def checkForCompletion():

                    url = "https://santaclaracoe.aeries.net/admin/GeneralFunctions.asmx/CurrentReportStatus"
                    headers = {
                        "accept": "*/*",
                        "accept-language": "en-US,en;q=0.9",
                        "content-type": "application/json; charset=UTF-8",
                        # "cookie": ("AeriesNet=LastIdentityProvider=0&LastDatabaseGroup=Special Ed&LastDatabaseYear=2024-2025&"
                        #         "LastSchool=14&LastSC_14=14&LastSN_14=216&LastID_14=88454; s=j2pgttn1b4umoxkqt0j1m3ey; "
                        #         "_pk_ref.1.0f3d=%5B%22%22%2C%22%22%2C1730152088%2C%22https%3A%2F%2Faeries.sccoe.org%2F%22%5D; "
                        #         "_pk_ses.1.0f3d=1; a=897E13D343F23140A891174A7D11BA1AC6E613D4F0DEF952FCB32A9FF435D9CB7D1390B8353500E696039B41AA6DBA0A24BE7A64BDF318254DA88B6475B4C36E7E0728DCAEEF6CC1CC60D244AF31D58589115E5AF6937A6F74C3CBD369CCF2191B681E4DC73D379232249A61D4006F42C519935A502421B391BBF354843749FBA8A2CF57DFB59A5DCE3616E50A4742BE067E6064EB95B8041A4656D3BE9BCBDE920194AC4AEF5DC0673012883F5AA861318D2D0793495AD994A93A22BDA8D442F0F4853F7AA1B7EB34B3D02A13B53A49; "
                        #         "_sg_b_v=17%3B2916%3B1730152094; _pk_id.1.0f3d=6c5b9fc4d855af96.1717796329.19.1730152179.1728336276.; "
                        #         "AWSALB=QkSE6e0DwltMw5KXFGMcVAWr7c3+d9ix9ZkrcBECDDXSBS52hCEPiKmVlEgDVVQY6huHK7A6q4z7vUzlorgkJRi2XF6Mvh6e5i7ro/FtFESyBLNAyFYeBXOUYaNW; "
                        #         "AWSALBCORS=QkSE6e0DwltMw5KXFGMcVAWr7c3+d9ix9ZkrcBECDDXSBS52hCEPiKmVlEgDVVQY6huHK7A6q4z7vUzlorgkJRi2XF6Mvh6e5i7ro/FtFESyBLNAyFYeBXOUYaNW"),
                        "origin": "https://santaclaracoe.aeries.net",
                        "priority": "u=1, i",
                        "referer": "https://santaclaracoe.aeries.net/admin/ViewReport.aspx",
                        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": '"Windows"',
                        "sec-fetch-dest": "empty",
                        "sec-fetch-mode": "cors",
                        "sec-fetch-site": "same-origin",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                        "x-requested-with": "XMLHttpRequest"
                    }
                    payload = {"s": "s"}

                    # Loop to make request every 3 seconds until the response contains {"d": "Completed"}
                    while True:
                        response = currentClient.post(url, headers=headers, json=payload)
                        response_data = response.json()


                        # print("Response:", response_data)  # Print the response to monitor progress
                        if response_data.get("d") == "Completed":
                            print("Report status is 'Completed'.")

                            data = {}
                            #         # Save the request as a curl command
                            # method = response.request.method
                            # headers_list = ["'{}: {}'".format(k, v) for k, v in response.request.headers.items()]
                            # headers_str = " -H ".join(headers_list)
                            # data_str = "&".join([f"{k}={v}" for k, v in data.items()])
                            # curl_command = f"curl -X {method} -H {headers_str} -d '{data_str}' '{url}'"

                            # # Save the curl command to a file
                            # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                            # curl_file_path = os.path.join(os.path.expanduser("~"), "Downloads", f'{reportTypeKey}_Month{reportMonth}_{timestamp}.txt')
                            # with open(curl_file_path, "w") as curl_file:
                            #     curl_file.write(curl_command)
                            # print(f"Curl command saved to {curl_file_path}")


                            break
                        else:
                            print("report loading...")

                        time.sleep(3)  # Wait for 3 seconds before the next request


                def fetchReport():
                    hidden_fields = fetchViewStateRequest()
                    url = "https://santaclaracoe.aeries.net/admin/ViewReport.aspx"

                    headers = {
                        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                        "accept-language": "en-US,en;q=0.9",
                        "cache-control": "no-cache",
                        "content-type": "application/x-www-form-urlencoded",
                        # "cookie": "AeriesNet=LastIdentityProvider=0&LastDatabaseGroup=Special Ed&LastDatabaseYear=2024-2025&LastSchool=14&LastSC_14=14&LastSN_14=216&LastID_14=88454; s=j2pgttn1b4umoxkqt0j1m3ey; _pk_ref.1.0f3d=[\"\",\"\",1730152088,\"https://aeries.sccoe.org\"]; _pk_ses.1.0f3d=1; a=897E13D343F23140A891174A7D11BA1AC6E613D4F0DEF952FCB32A9FF435D9CB7D1390B8353500E696039B41AA6DBA0A24BE7A64BDF318254DA88B6475B4C36E7E0728DCAEEF6CC1CC60D244AF31D58589115E5AF6937A6F74C3CBD369CCF2191B681E4DC73D379232249A61D4006F42C519935A502421B391BBF354843749FBA8A2CF57DFB59A5DCE3616E50A4742BE067E6064EB95B8041A4656D3BE9BCBDE920194AC4AEF5DC0673012883F5AA861318D2D0793495AD994A93A22BDA8D442F0F4853F7AA1B7EB34B3D02A13B53A49; _sg_b_p=/admin/Default.aspx; _sg_b_v=17;2916;1730152094; _pk_id.1.0f3d=6c5b9fc4d855af96.1717796329.19.1730152179.1728336276.; AWSALB=zXwMGXbo1pMC9YHjDdBRcGZNaESQ1ibzJKOw99IMeo1dXd1o8IG0CrXl9bkdXQY2lHxkDjE/uQhnGz64vUOgeQs1ApyY+U/yelT2Cam/PnbjbCQwzvuH9YA6YhNl; AWSALBCORS=zXwMGXbo1pMC9YHjDdBRcGZNaESQ1ibzJKOw99IMeo1dXd1o8IG0CrXl9bkdXQY2lHxkDjE/uQhnGz64vUOgeQs1ApyY+U/yelT2Cam/PnbjbCQwzvuH9YA6YhNl",
                        "origin": "https://santaclaracoe.aeries.net",
                        "priority": "u=0, i",
                        "referer": "https://santaclaracoe.aeries.net/admin/ViewReport.aspx",
                        "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": "\"Windows\"",
                        "sec-fetch-dest": "iframe",
                        "sec-fetch-mode": "navigate",
                        "sec-fetch-site": "same-origin",
                        "sec-fetch-user": "?1",
                        "upgrade-insecure-requests": "1",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
                    }

                    data = {
                        # "__VIEWSTATE": "N7vC0MGU2NGULibBoRptGBKeYAlWaEg4YHrq/9QlOiBjGki8CT0rfoMbTg5z/+wySW699T/5a+6BVDcJCET6SruxcdzcD6jgvTS9Gm5GH5sZXz4ksoAjqJjPBY/HQdiGVv8KA/84r4j4HDVCy4LVQ39VDQYc7VOMtlHMGz72JQ904B64bNjpI9CCrIdKZlUHrmYI03sykXpHHF5terHCcA69WcXQKn9k4Ef4NWam4YlL7heFemsCaVSoTi5Cy1v1g8h0HvjnvM5BnFelJl1KZxbKw29u6nHJuwoNS8rnyLYaLw5gnAP1WQWjVsuJjZvgcyGMuvpSjYrWpNUkEspPlwDu/Sy5xKOU/u2INAo1OVZjIeoxbOffOssFNt43K06Biigrcife6lBdRBjgBMEoZw==",
                        # "__VIEWSTATEGENERATOR": "029DB52E",
                        # "__VIEWSTATEENCRYPTED": "",
                        "btnDisplay": "Download Report"
                    }
                    data.update(hidden_fields)

                    # print("Data: ", data)

                    # Specify the download destination
                    download_path = os.path.join(os.path.expanduser("~"), "Downloads", f'{reportTypeKey}_Month_{reportMonth}_.pdf')


                # Request the file as a stream
                    with currentClient.stream("POST", url, headers=headers, data=data) as response:
                        if response.status_code == 200:
                            with open(download_path, "wb") as file:
                                for chunk in response.iter_bytes():
                                    file.write(chunk)
                            print("File downloaded successfully")


                            # # Save the request as a curl command
                            # method = response.request.method
                            # headers_list = ["'{}: {}'".format(k, v) for k, v in response.request.headers.items()]
                            # headers_str = " -H ".join(headers_list)
                            # data_str = "&".join([f"{k}={v}" for k, v in data.items()])
                            # curl_command = f"curl -X {method} -H {headers_str} -d '{data_str}' '{url}'"

                            # # Save the curl command to a file
                            # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                            # curl_file_path = os.path.join(os.path.expanduser("~"), "Downloads", f'{reportTypeKey}_Month{reportMonth}_{timestamp}.txt')
                            # with open(curl_file_path, "w") as curl_file:
                            #     curl_file.write(curl_command)
                            # print(f"Curl command saved to {curl_file_path}")


                        else:
                            print(f"Failed to download file. Status code: {response.status_code}")

                    

                    download_destinations.update({reportTypeKey: download_path})
                    print("Download Destinations: ", download_destinations)

                    # time.sleep(10)

                    # response = self.client.stream("POST", url, headers=headers, data=data)
                    # print("Fetch Response: ")
                    # print(response.text)
                    # print("Response Headers: ", response.headers)

                    return download_path

                def runReportFetcher():
                    setReport()
                    # deets = fetchViewStateRequest()
                    checkForCompletion()
                    time.sleep(1)
                    downloads_location = fetchReport()
                    print("Downloads Location: ", downloads_location)

                    return downloads_location
                
                # Run the report fetcher and store the result in the download_destinations dictionary
                download_destinations[reportTypeKey] = runReportFetcher()
                print("Download Destinations Final: ", download_destinations)

        fetchReports()    
        
        def processReports():
            print('pass')

        def getSiteNames():
            # Define the grade ranges and their corresponding names
            grade_ranges = {
                range(0, 4): "Elementary K-3",
                range(4, 7): "Elementary 4-6",
                range(7, 9): "Middle 7-8",
                range(9, 15): "High School 9-12"
            }

            def get_grade_range_name(grade):
                for grade_range, name in grade_ranges.items():
                    if grade in grade_range:
                        return name
                return "Unknown"

            r = self.query("LIST STU TCH STU.AP2? STU.GR TCH.TE IF STU.CU = TCH.TN ")

            # Initialize a dictionary to store the counts
            site_teacher_counts = {}

            # Iterate over the results
            for item in r:
                description = item.get('Description_STU_AP2')
                teacher_name = item.get('Teacher_name')
                grade = item.get('Grade')

                # Debug print statements
                # print(f"Description: {description}, Teacher: {teacher_name}, Grade: {grade}")


                if description and teacher_name and grade:
                    grade_range_name = get_grade_range_name(int(grade))
                    description_with_grade = f"{description} {grade_range_name}"

                    if description_with_grade not in site_teacher_counts:
                        site_teacher_counts[description_with_grade] = set()
                    site_teacher_counts[description_with_grade].add(teacher_name)

            # Convert the sets to counts
            site_teacher_counts = {k: len(v) for k, v in site_teacher_counts.items()}

            # Print the dictionary
            # print('counts: ', site_teacher_counts)
            
            return site_teacher_counts
        
        def get_site_info():
            data = self.query("LIST STU TCH STU.AP2? STU.GR STU.TR STU.TR? TCH.TE IF STU.CU = TCH.TN ")
            # Define the grade ranges and their corresponding names
            grade_ranges = {
                range(0, 4): "Elementary K-3",
                range(4, 7): "Elementary 4-6",
                range(7, 9): "Middle 7-8",
                range(9, 15): "High School 9-12"
            }

            # Initialize a dictionary to store the results
            site_info = {}

            # Iterate over the data
            for item in data:
                description = item.get('Description_STU_AP2')
                grade = item.get('Grade')
                track = item.get('Track')
                trackName = item.get('Description_STU_TR')
                teacher = item.get('Teacher_name')

                if description and grade and track and teacher:
                    grade = int(grade)
                    grade_level = None
                    for grade_range, name in grade_ranges.items():
                        if grade in grade_range:
                            grade_level = name
                            break

                    if grade_level:
                        key = f"{description} {grade_level} Track {track}"
                        if key not in site_info:
                            site_info[key] = {'site': description, 'classes': set(), 'grades': grade_level, 'trackName': trackName}
                        site_info[key]['classes'].add(teacher)

            # Convert the sets to counts
            for key in site_info:
                site_info[key]['classes'] = len(site_info[key]['classes'])

            # print("site info: ", site_info)
            return site_info

        def getAttendanceReports():
            
            # dwnload_locs = runReportFetcher()
            print('intializing report processesing process')
            Reports(reportMonth, "2024-25", get_site_info(), download_destinations["Attendance Register by DOR"], download_destinations["Attendance Register by Teacher"], download_destinations["Principal's Report"], False)
            

        getAttendanceReports()

    def getSiteNames(self):
        # Define the grade ranges and their corresponding names
        grade_ranges = {
            range(0, 4): "Elementary K-3",
            range(4, 7): "Elementary 4-6",
            range(7, 9): "Middle 7-8",
            range(9, 15): "High School 9-12"
        }

        def get_grade_range_name(grade):
            for grade_range, name in grade_ranges.items():
                if grade in grade_range:
                    return name
            return "Unknown"

        r = self.query("LIST STU TCH STU.AP2? STU.GR TCH.TE IF STU.CU = TCH.TN ")

        # Initialize a dictionary to store the counts
        site_teacher_counts = {}

        # Iterate over the results
        for item in r:
            description = item.get('Description_STU_AP2')
            teacher_name = item.get('Teacher_name')
            grade = item.get('Grade')

             # Debug print statements
            # print(f"Description: {description}, Teacher: {teacher_name}, Grade: {grade}")


            if description and teacher_name and grade:
                grade_range_name = get_grade_range_name(int(grade))
                description_with_grade = f"{description} {grade_range_name}"

                if description_with_grade not in site_teacher_counts:
                    site_teacher_counts[description_with_grade] = set()
                site_teacher_counts[description_with_grade].add(teacher_name)

        # Convert the sets to counts
        site_teacher_counts = {k: len(v) for k, v in site_teacher_counts.items()}

         # Print the dictionary
        # print('counts: ', site_teacher_counts)
        
        return site_teacher_counts
# test = AeriesAPIz()
# # # # test.login()
# # # # test.query("LIST STU LN FN ")
# test.attendanceReports(6)