import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QCheckBox, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from AERIES.AERIES_API import AeriesAPIz

class ClasslistsWindow(QMainWindow):
    """
    Window for displaying classlists.
    """
    def __init__(self, parent=None, ESYz=False, api=None):
        """
        Initializes the classlists window.

        :param parent: The parent window.
        :param ESYz: A boolean indicating whether this is for ESY classlists.
        :param api: The API object to use for data retrieval.
        """
        super().__init__(parent)
        self.ESYz = ESYz
        self.api = api
        # Query class list data from the API
        self.classListData = self.api.query("LIST STU TCH STU.ID STU.CID STU.LN STU.FN STU.BD STU.GR STU.AP2? STU.CU TCH.TE ")
        self.mergedClassAndServiceData = []
        # Group students by site
        self.studentGroupedBySite = self.studentsGroupedBySite(self.classListData)
        self.show_services = False
        self.student_windows = []

        self.scroll_area = QScrollArea(self)  # Create a new QScrollArea instance
        self.button_frame = QWidget()  # Create a new QWidget that will contain the buttons
        self.button_frame.setLayout(QGridLayout())  # Set the layout of the button_frame to QGridLayout
        self.scroll_area.setWidget(self.button_frame)  

        self.setWindowTitle("Teachers and Students")
        self.create_ui()

    def mergeClasslistAndServiceData(self, classlistData, serviceData):
        """
        Merges classlist data with service data.

        :param classlistData: The classlist data.
        :param serviceData: The service data.
        :return: The merged data.
        """
        merged_data = []

        # Create a dictionary to hold service data by ID
        service_dict = {}
        for item in serviceData:
            if item['ID_Number'] not in service_dict:
                service_dict[item['ID_Number']] = []
            if len(service_dict[item['ID_Number']]) < 7:
                if item['Description_CD'] != "Specialized Academic Instruction":
                    service_dict[item['ID_Number']].append(item['Description_CD'])

        # Merge the classlist data with the service data
        for demographic_item in classlistData:
            demographic_id = demographic_item['Student_ID']
            merged_item = demographic_item.copy()
            services = service_dict.get(demographic_id, [])
            merged_item['services'] = sorted(services)
            merged_data.append(merged_item)

        return merged_data

    def studentsGroupedBySite(self, data):
        """
        Groups students by their site.

        :param data: The data to group.
        :return: The grouped data.
        """
        grouped_by_site = {}
        for student in data:
            site = student['Description_STU_AP2']
            teacher = student['Teacher_name']
            teacherNumber = str(student['Tchr_Num'])  # Ensure this is a string
            if site not in grouped_by_site:
                grouped_by_site[site] = {}
            if teacher not in grouped_by_site[site]:
                grouped_by_site[site][teacher] = {"TeacherNumber": teacherNumber, "students": []}
            grouped_by_site[site][teacher]["students"].append(student)
        
        return grouped_by_site

    def fetch_and_merge_services(self):
        """
        Fetches service data and merges it with classlist data.
        """
        self.serviceData = self.api.query("LIST CSV ID CD? DU IF DT = 07/01/2023")
        self.mergedClassAndServiceData = self.mergeClasslistAndServiceData(self.classListData, self.serviceData)
        self.studentGroupedBySiteWithServices = self.studentsGroupedBySite(self.mergedClassAndServiceData)

    def display_students(self, teacher, students):
        """
        Displays a window with student information for a given teacher.

        :param teacher: The teacher's name.
        :param students: The list of students to display.
        """
        headers = ["First Name", "Last Name", "SSID", "Birthdate", "Grade"]
        if self.show_services:
            headers.extend(["Service 1", "Service 2", "Service 3", "Service 4", "Service 5", "Service 6", "Service 7"])

        student_window = QWidget()
        student_window.setWindowTitle(teacher)

        table = QTableWidget(len(students), len(headers))
        table.setHorizontalHeaderLabels(headers)

        for row, student in enumerate(students):
            student_data = [
                student["First_Name"],
                student["Last_Name"],
                student["State_Student_ID"],
                student["Birthdate"],
                student["Grade"]
            ]
            if self.show_services:
                services = student.get("services", [])
                student_data.extend(services + [""] * (7 - len(services)))

            for column, data in enumerate(student_data):
                item = QTableWidgetItem(data)
                table.setItem(row, column, item)

        layout = QVBoxLayout()
        layout.addWidget(table)
        student_window.setLayout(layout)
        student_window.setGeometry(100, 100, 800, 600)
        student_window.show()

        self.student_windows.append(student_window)

    def create_ui(self):
        """
        Creates the UI for the classlists window.
        """
        self.setGeometry(100, 100, 600, 400)

        self.toggle_button = QCheckBox("Show Services", self)
        self.toggle_button.stateChanged.connect(self.on_toggle_services)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.scroll_area)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.populate_teacher_buttons()

    def clear_layout(self, layout):
        """
        Clears all widgets from a layout.

        :param layout: The layout to clear.
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def populate_teacher_buttons(self):
        """
        Populates the UI with buttons for each teacher.
        """
        self.clear_layout(self.button_frame.layout())

        sorted_sites = sorted(self.studentGroupedBySite.items())
        midpoint = len(sorted_sites) // 2

        button_frame_layout = self.button_frame.layout()

        def add_site_buttons(site_data, column):
            """
            Adds buttons for each site to the UI.

            :param site_data: The site data to add.
            :param column: The column in which to add the buttons.
            """
            row = 0
            for site, teachers in site_data:
                header_label = QLabel(site)
                font = header_label.font()
                font.setBold(True)
                header_label.setFont(font)
                button_frame_layout.addWidget(header_label, row, column, 1, 2)
                row += 1

                for teacher, teacher_data in teachers.items():
                    students = teacher_data["students"]
                    teacher_number = str(teacher_data["TeacherNumber"])

                    button = QPushButton(teacher)
                    button.clicked.connect(lambda checked, t=teacher, s=students: self.display_students(t, s))

                    missing_submission_teachers = self.api.checkAttendanceSubmission()
                    missing_teacher_numbers = [str(teacher['TeacherNumber']) for teacher in missing_submission_teachers]
                    
                    if teacher_number in missing_teacher_numbers:
                        attendance_label = QLabel("🔴", self)
                    else:
                        attendance_label = QLabel("🟢", self)

                    button_frame_layout.addWidget(button, row, column)
                    button_frame_layout.addWidget(attendance_label, row, column + 1)
                    row += 1

        add_site_buttons(sorted_sites[:midpoint], 0)
        add_site_buttons(sorted_sites[midpoint:], 2)

        self.button_frame.adjustSize()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.adjustSize()
        self.adjustSize()

    def on_toggle_services(self):
        """
        Handles the toggle services checkbox state change.
        """
        self.show_services = self.toggle_button.isChecked()
        if self.show_services:
            self.fetch_and_merge_services()
            self.studentGroupedBySite = self.studentGroupedBySiteWithServices
        else:
            self.studentGroupedBySite = self.studentsGroupedBySite(self.classListData)

        self.populate_teacher_buttons()
