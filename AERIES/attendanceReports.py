import os, sys
sys.path.append('./')
from PyPDF4 import PdfFileReader, PdfFileWriter, PdfFileMerger
# import time
from datetime import datetime
from datetime import date
import glob2 as glob
import os.path

# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import threading
# import shutil
# import platform



class Reports():
    def __init__(self, month, schoolYear, schoolList, ATTREGDOR=None, ATTREGTN=None, PRINREP=None, ESY=False):
        print(f"Getting Month {month}...")
        self.ESY =ESY
        self.schoolYear = schoolYear
        self.sourceFiles = []
        self.month = month
        self.date = self.getDate()
        self.monthStorageFolder, self.sourceFilesFolder = self.makeFolderLocations()
        self.AttRegDOR = ATTREGDOR
        self.AttRegTN = ATTREGTN
        self.PrincipalReport = PRINREP
        self.schoolList = schoolList
        self.processRawAttReports(self.AttRegDOR)
        self.processRawAttReports(self.AttRegTN)
        self.processRawAttReports(self.PrincipalReport)
        self.sortPages(self.month)
        self.fillPDFS(self.month)
        
    
    def makeFolderLocations(self): # add if for no one drive at all for Josue and Firl
        # Path to the Attendance Reports folder on the user's OneDrive Desktop
        attendanceReportFolderNoOneDrive = os.path.join(os.path.expanduser("~"),"Desktop", "Attendance Reports")
        attendanceReport_folder_sccoe = os.path.join(os.path.expanduser("~"), "OneDrive - Santa Clara County Office of Education", "Desktop", "Attendance Reports")
        attendanceReport_folder_default = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "Attendance Reports")

        # Check if the SCCOE folder exists, otherwise use the default folder
        if os.path.exists(os.path.join(os.path.expanduser("~"), "OneDrive - Santa Clara County Office of Education", "Desktop")):
            attendanceReport_folder = attendanceReport_folder_sccoe
        elif os.path.exists(os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")):
            attendanceReport_folder = attendanceReport_folder_default
        else:
            attendanceReport_folder = attendanceReportFolderNoOneDrive

        print("Attendance Report Folder: ", attendanceReport_folder)
        
        # Create the Attendance Reports folder and its parent directories if they don't exist
        os.makedirs(attendanceReport_folder, exist_ok=True)
        
        # Path to the school year folder
        school_year_folder = os.path.join(attendanceReport_folder, f"{self.schoolYear}")
        
        # Create the school year folder if it doesn't exist
        os.makedirs(school_year_folder, exist_ok=True)
        
        # Path to the current month's folder
        current_month_folder = os.path.join(school_year_folder, f"Month_{self.month}")
        
        # Create the current month's folder if it doesn't exist
        os.makedirs(current_month_folder, exist_ok=True)
        
        # Path to the source files folder within the current month's folder
        sourceFilesFolder = os.path.join(current_month_folder, "sourceFiles")
        
        # Create the source files folder if it doesn't exist
        os.makedirs(sourceFilesFolder, exist_ok=True)
        
        return current_month_folder, sourceFilesFolder
    
    
    
    def getDate(self):
        date = datetime.now()
        return date
    


    mergedAndSortedFiles = []

    def sortPages(self, month):
        # Find path to each file
        folderPath = self.sourceFilesFolder

        # pypdf merge
        files = os.listdir(folderPath)
        types = ["PR_Report", "AR_By_DOR", "AR_By_Teacher"]
        schools = self.schoolList
        print("SCHOOLS: ", schools)

        undefined_mergedPDF = PdfFileMerger()
        undefined_files_exist = False

        for school_name, info in schools.items():
            print("sorting school_name is: ", school_name)
            mergedPDF = PdfFileMerger()
            for report_type in types:
                pdf_filename = f"{folderPath}\\{report_type}-{school_name} {info['trackName']}.pdf"
                # print("pdf_filename is: ", pdf_filename)
                try:
                    mergedPDF.append(pdf_filename)
                except FileNotFoundError:
                    print(f"{pdf_filename} not found!")
                    continue

            # Save the merged PDF to the specified location
            output_path = f"{self.monthStorageFolder}\\{school_name} {info['trackName']}.pdf"
            # print("output_path is: ", output_path)
            mergedPDF.write(output_path)
            mergedPDF.close()
            self.mergedAndSortedFiles.append(output_path)

        # Handle undefined files
        undefined_files = [file for file in files if "undefined" in file.lower()]
        for report_type in types:
            for file in undefined_files:
                if report_type in file:
                    undefined_files_exist = True
                    pdf_filename = os.path.join(folderPath, file)
                    # print("undefined pdf_filename is: ", pdf_filename)
                    try:
                        undefined_mergedPDF.append(pdf_filename)
                    except FileNotFoundError:
                        print(f"{pdf_filename} not found!")
                        continue

        if undefined_files_exist:
            # Save the merged undefined PDF to the specified location
            undefined_output_path = f"{self.monthStorageFolder}\\Undefined.pdf"
            # print("undefined_output_path is: ", undefined_output_path)
            undefined_mergedPDF.write(undefined_output_path)
            undefined_mergedPDF.close()
            self.mergedAndSortedFiles.append(undefined_output_path)

            
    def processRawAttReports(self,filepath):
        pdf = PdfFileReader(filepath, "rb")

        class Attendance_Report:
            def __init__(subSelf, page_num):
                subSelf.page_object = pdf.getPage(page_num)
                subSelf.text = subSelf.page_object.extractText()
                # print("SubSelf.text is: ", subSelf.text)


                if "Principal's Monthly Attendance Report" in subSelf.text:
                    subSelf.reportType = "PR_Report"
                elif "Attendance Register by Teacher" in subSelf.text:
                    subSelf.reportType = "AR_By_Teacher"
                elif "Attendance Register by District of Residence" in subSelf.text:
                    subSelf.reportType = "AR_By_DOR"
                else:
                    raise Exception("Report type not recognized")



                subSelf.school = "Undefined"
                subSelf.track = "Undefined"

                # print("School List Items: ", self.schoolList.items())

                for school, info in self.schoolList.items():
                    # print("school is: ", school)
                    if info['site'] in subSelf.text:
                        # print("site is: ", info['site'])
                        # if not info['gradeLevels']:
                        # subSelf.school = info['site']
                        #     break
                        
                        if info['grades'] in subSelf.text and f"Track:\n{info['trackName']}" in subSelf.text:
                            subSelf.school = f"{school}"
                            subSelf.track = info['trackName']
                            break
                        # if subSelf.school != "Undefined":
                        #     break

                        # print('this school is: ', subSelf.school)

                if subSelf.school == "Undefined":
                    print("Match for filename not found fool!")

      
                subSelf.fileName = f"\\{subSelf.reportType}-{subSelf.school} {subSelf.track}.pdf"


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


    
    def fillPDFS(self, month):
        print("MERGED AND SORTED FILES: ", self.mergedAndSortedFiles)  
        for file in self.mergedAndSortedFiles:
            filename = os.path.basename(file)
            classNum = "Undefined"  # Default value
            for key, info in self.schoolList.items():
                if key in filename:
                    site_name = info['site']
                    grade_level = info['grades']
                    classNum = info['classes']
                    break

            # print('ClassNum is: ', classNum)
            self.pdfMathAndFill(file, classNum)
        
        print(f"Month {month} successfully completed!")
    
    
    def pdfMathAndFill(self, pathToPdf, classNum):
        import fitz
        # Open the PDF file
        pdf_document = fitz.open(pathToPdf)
        
        # Check if the PDF has at least one page
        if pdf_document.page_count > 0:
            # Get the first page
            first_page = pdf_document[0]
            
            # Perform the filling operation on the first page
            magenta4 = (0.5450980392156862, 0.0, 0.5450980392156862)

            totalDays = first_page.get_text(clip=[463, 352, 478, 364])
            accTestTotal = first_page.get_text(clip=[512, 458, 527, 471])
            unenrolledTotal = first_page.get_text(clip=[539, 385, 545, 398])
            totalAbs = first_page.get_text(clip=[435, 385, 445, 397])

            # Ensure the variables contain valid integer values
            try:
                totalDays = int(totalDays) if totalDays else 0
                accTestTotal = int(accTestTotal) if accTestTotal else 0
                unenrolledTotal = int(unenrolledTotal) if unenrolledTotal else 0
                totalAbs = int(totalAbs) if totalAbs else 0
            except ValueError as e:
                print(f"Error converting text to integer: {e}")

            print("------------------ ", pdf_document.name, " ---------------------")
            if int(totalDays) + int(totalAbs) + int(unenrolledTotal) == int(accTestTotal):
                print("Success! Attendance numbers match!")
                print("Filling sheet....")
                first_page.insert_text(fitz.Point(271, 229), str(classNum), fontname="helv", fontsize=14, color=magenta4)  # Num 1
                first_page.insert_text(fitz.Point(271, 335), str(classNum), fontsize=14, color=magenta4)  # Num 2
                first_page.insert_text(fitz.Point(268, 430), str(accTestTotal) + " \u2713", fontsize=14, color=magenta4)  # Accuracy Check
                first_page.insert_text(fitz.Point(243, 585), "x3966", fontsize=14, color=magenta4)  # Phone ext
                first_page.insert_text(fitz.Point(514, 562), str(date.today()), fontsize=14, color=magenta4)

        try:
            pdf_document.saveIncr()
        except ValueError:
            print("No pages to do math and fill in for this file")
            pass
    
        pdf_document.close()
    




# def main():
#     valid_month_numbers = set(map(str, range(1, 13)))

#     user_input = input("Enter a month or month number (separated by spaces if multiple): ").split()

#     for input_value in user_input:
#         if input_value in valid_month_numbers:
#             Reports(input_value, "2024-2025", schoolList)
#         else:
#             print(f"Invalid input: {input_value}. Please enter a valid month number (1-12).")

# # if __name__ == "__main__":
# #     main()

