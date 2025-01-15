import os, sys
sys.path.append('./')
from PyPDF4 import PdfFileReader, PdfFileWriter, PdfFileMerger
import time
from datetime import datetime
from datetime import date
import glob2 as glob
import os.path
import fitz
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import shutil
import platform



class Reports():
    def __init__(self, month, schoolYear, schoolList, ATTREGDOR=None, ATTREGTN=None, PRINREP=None, ESY=False):
        print(f"Getting Month {month}...")
        self.ESY =ESY
        self.schoolYear = schoolYear
        self.sourceFiles = []
        self.month = month
        self.date = self.getDate()
        self.sourceFilesFolder = self.makeFolderLocations()
        self.AttRegDOR = ATTREGDOR
        self.AttRegTN = ATTREGTN
        self.PrincipalReport = PRINREP
        self.schoolList = schoolList
        self.processRawAttReports(self.AttRegDOR)
        self.processRawAttReports(self.AttRegTN)
        self.processRawAttReports(self.PrincipalReport)
        self.sortPages(self.month)
        self.fillPDFS(self.month)
        



    #Define PDF File Structure and Locations
    def makeFolderLocations(self): #Needs to add files and structure to users Desktop Directory
        # Path to the Attendance Reports folder on the user's Desktop
        attendanceReport_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Attendance Reports")
        
        # Create the Attendance Reports folder if it doesn't exist
        if not os.path.exists(attendanceReport_folder):
            os.mkdir(attendanceReport_folder)
        
        # Path to the school year folder
        school_year_folder = os.path.join(attendanceReport_folder, f"{self.schoolYear}")
        
        # Create the school year folder if it doesn't exist
        if not os.path.exists(school_year_folder):
            os.mkdir(school_year_folder)
        
        # Path to the current month's folder
        current_month_folder = os.path.join(school_year_folder, f"Month_{self.month}")
        
        # Create the current month's folder if it doesn't exist
        if not os.path.exists(current_month_folder):
            os.mkdir(current_month_folder)
        
        # Path to the source files folder within the current month's folder
        sourceFilesFolder = os.path.join(current_month_folder, "sourceFiles")
        
        # Create the source files folder if it doesn't exist
        if not os.path.exists(sourceFilesFolder):
            os.mkdir(sourceFilesFolder)
        
        return sourceFilesFolder

    def getDate(self):
        date = datetime.now()
        return date
    


    mergedAndSortedFiles = []

    def sortPages(self, month):
        # find path to each file
    
        folderPath = self.sourceFilesFolder

        # pypdf merge
        files = os.listdir(folderPath)
        types = ["PR_Report", "AR_By_DOR", "AR_By_Teacher"]
        schools = list(self.schoolList.keys())
        schoolIdx = 0
        while schoolIdx < len(schools):
            mergedPDF = PdfFileMerger()
           
            for PDF in [f"{folderPath}\\{types[0]}-{schools[schoolIdx]}.pdf",
                        f"{folderPath}\\{types[1]}-{schools[schoolIdx]}.pdf",
                        f"{folderPath}\\{types[2]}-{schools[schoolIdx]}.pdf"]:
                try: ##fixing school levels that don't exist in a given month
                    mergedPDF.append(PDF)
                except FileNotFoundError:
                    print(f"{folderPath}\\{types[0]}-{schools[schoolIdx]}.pdf not found!")
                    continue
          
      
            # Save the merged PDF to the specified location
            output_path = f"{self.sourceFilesFolder}\\Month_{month}\\{schools[schoolIdx]}.pdf"
            mergedPDF.write(output_path)
            mergedPDF.close()
            self.mergedAndSortedFiles.append(f"{self.sourceFilesFolder}\\{schools[schoolIdx]}.pdf")
        
            schoolIdx += 1
    def processRawAttReports(self,filepath):
        pdf = PdfFileReader(filepath, "rb")

        class Attendance_Report:
            def __init__(subSelf, page_num):
                subSelf.page_object = pdf.getPage(page_num)
                subSelf.text = subSelf.page_object.extractText()


                if "Principal's Monthly Attendance Report" in subSelf.text:
                    subSelf.reportType = "PR_Report"
                elif "Attendance Register by Teacher" in subSelf.text:
                    subSelf.reportType = "AR_By_Teacher"
                elif "Attendance Register by District of Residence" in subSelf.text:
                    subSelf.reportType = "AR_By_DOR"
                else:
                    raise Exception("Report type not recognized")



                if "SOUTH COUNTY ANNEX [COE]" in subSelf.text and "Middle 7-8" not in subSelf.text and "Elementary 4-6" not in subSelf.text:
                    subSelf.school = "SOUTH COUNTY ANNEX [COE]"
                elif "SOUTH COUNTY ANNEX [COE]" in subSelf.text and "Middle 7-8" in subSelf.text:
                    subSelf.school = "SOUTH COUNTY ANNEX [COE] Middle 7-8"
                elif "SOUTH COUNTY ANNEX [COE]" in subSelf.text and "Elementary 4-6" in subSelf.text:
                    subSelf.school = "SOUTH COUNTY ANNEX [COE] Elementary 4-6"
                elif "WILCOX HIGH [COE]" in subSelf.text:
                    subSelf.school = "WILCOX HIGH [COE]"
                elif "PIEDMONT HILLS HIGH [COE]" in subSelf.text and "Middle" in subSelf.text:
                    subSelf.school = "PIEDMONT HILLS HIGH [COE] Middle 7-8"
                elif "PIEDMONT HILLS HIGH [COE]" in subSelf.text and "Middle" not in subSelf.text:
                    subSelf.school = "PIEDMONT HILLS HIGH [COE]"
                elif "SANTA TERESA HIGH [COE]" in subSelf.text:
                    subSelf.school = "SANTA TERESA HIGH [COE]"
                elif "SILVER CREEK HIGH [COE]" in subSelf.text:
                    subSelf.school = "SILVER CREEK HIGH [COE]"
                elif "MONTA VISTA HIGH [COE]" in subSelf.text:
                    subSelf.school = "MONTA VISTA HIGH [COE]"
                elif "GATEWAY ELEMENTARY [COE]" in subSelf.text and "Elementary K-3\nAttendance Category:" in subSelf.text:
                    subSelf.school = "GATEWAY ELEMENTARY [COE] Elementary K-3"
                elif "GATEWAY ELEMENTARY [COE]" in subSelf.text and "Elementary 4-6\nAttendance Category:" in subSelf.text and "Track:\nGILROY" in subSelf.text:
                    subSelf.school = "GATEWAY ELEMENTARY [COE] Elementary 4-6 Track GILROY"
                elif "GATEWAY ELEMENTARY [COE]" in subSelf.text and "Elementary 4-6\nAttendance Category:" in subSelf.text:
                    subSelf.school = "GATEWAY ELEMENTARY [COE] Elementary 4-6 Track GATEWAY ELEM"
                elif "GATEWAY ELEMENTARY [COE]" in subSelf.text and "Middle 7-8\nAttendance Category:" in subSelf.text:
                    subSelf.school = "GATEWAY ELEMENTARY [COE] Middle 7-8" 
                elif "GATEWAY ELEMENTARY [COE]" in subSelf.text and "High School 9-12\nAttendance Category:" in subSelf.text:
                    subSelf.school = "GATEWAY ELEMENTARY [COE] High School 9-12"
                elif "WESTMONT HIGH [COE]" in subSelf.text:
                    subSelf.school = "WESTMONT HIGH [COE]"
                elif "GILROY HIGH [COE]" in subSelf.text and "High School 9-12" in subSelf.text:
                    subSelf.school = "GILROY HIGH [COE] High School 9-12"
                elif "GILROY HIGH [COE]" in subSelf.text and "Middle" in subSelf.text:
                    subSelf.school = 'GILROY HIGH [COE] Middle 7-8'
                else:
                    subSelf.school = "Undefined"
                    print("Match for filename not found")

      
                subSelf.fileName = f"\\{subSelf.reportType}-{subSelf.school}.pdf"






        page_num = 0

        while page_num < pdf.numPages:
            ## Setup
            pdf = PdfFileReader(
                open(filepath, "rb"))
            info = pdf.getDocumentInfo()
            number_of_pages = pdf.getNumPages()
            ########################################################################
            newPDF = PdfFileWriter()
            rep_page = Attendance_Report(page_num)
            newPDF.addPage(pdf.pages[page_num])
            try:
                nextRepPage = Attendance_Report(page_num + 1)
                if rep_page.school == nextRepPage.school:
                    newPDF.addPage(pdf.pages[page_num+1])
                    try:
                        nextNextRepPage = Attendance_Report(page_num + 2)
                        if rep_page.school == nextNextRepPage.school:
                            newPDF.addPage(pdf.pages[page_num+2])
                            page_num +=1
                        else:
                            pass
                    except IndexError:
                        pass
                    page_num += 1
                else:
                    pass
            except IndexError:
                pass

            ### new class object to self.sourceFiles

            with open(self.sourceFilesFolder + rep_page.fileName, "wb") as f:
                newPDF.write(f)

            page_num += 1

    classTotalsPerSite = {
        "GATEWAY ELEMENTARY": "1",
        "GILROY HIGH": "1",
        "MONTA VISTA": "2",
        "PIEDMONT HILLS": "2",
        "SANTA TERESA HIGH": "3",
        "SILVER CREEK HIGH": "2",
        "SOUTH COUNTY ANNEX": "1",
        "WESTMONT HIGH": "1",
        "WILCOX HIGH": "1"}

    def pdfMathAndFill(self, pathToPdf):
        page_Fitz = fitz.open(pathToPdf)

        for page in page_Fitz:
            # color code for font
            magenta4 = (0.5450980392156862, 0.0, 0.5450980392156862)

            totalDays = page.get_text(clip=[463, 352, 478, 364])
            accTestTotal = page.get_text(clip=[512, 458, 527, 471])
            unenrolledTotal = page.get_text(clip=[539, 385, 545, 398])
            print("unenrolledTotal is: ", unenrolledTotal)
            totalAbs = page.get_text(clip=[435, 385, 445, 397])

            classNum = "0"  # Default value
            for key in self.classTotalsPerSite:
                if key in page_Fitz.name:
                    classNum = self.classTotalsPerSite[key]
                    print("classNum is: " + classNum)

            print("------------------ ", page_Fitz.name, " ---------------------")
            if int(totalDays) + int(totalAbs) + int(unenrolledTotal) == int(accTestTotal):
                print("Success! Attendance numbers match!")
                print("Filling sheet....")
                page.insert_text(fitz.Point(271, 229), classNum, fontname="helv", fontsize=14, color=magenta4)  # Num 1
                page.insert_text(fitz.Point(271, 335), classNum, fontsize=14, color=magenta4)  # Num 2
                page.insert_text(fitz.Point(268, 430), str(accTestTotal) + " \u2713", fontsize=14,
                                 color=magenta4)  # Accuracy Check
                page.insert_text(fitz.Point(243, 585), "x3966", fontsize=14, color=magenta4)  # Phone ext
                page.insert_text(fitz.Point(514, 562), str(date.today()), fontsize=14, color=magenta4)
            else:
                print("NOOOOO!!!! Accuracy check failure :(")
                #raise ArithmeticError("Your math sucks. You need to seriously fix something in AERIES")
                
            break
        try: ##dont save if 0 pages because this kind of school does not exist in given month
            page_Fitz.saveIncr()
        except ValueError:
            print("No pages to do math and fill in for this file")
            pass
    def fillPDFS(self, month):
        for file in self.mergedAndSortedFiles:
            self.pdfMathAndFill(file)
        
        print(f"Month {month} sucessfully completed!")



def main():
    valid_month_numbers = set(map(str, range(1, 13)))

    user_input = input("Enter a month or month number (separated by spaces if multiple): ").split()

    for input_value in user_input:
        if input_value in valid_month_numbers:
            Reports(input_value)
        else:
            print(f"Invalid input: {input_value}. Please enter a valid month number (1-12).")

if __name__ == "__main__":
    main()

