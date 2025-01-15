import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QDialog, QFormLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from AERIES.AERIES_APIz import AeriesAPIz

class AeriesWindow(QMainWindow):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Aeries Window')
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.attendance_button = QPushButton('Attendance Reports', self)
        self.attendance_button.clicked.connect(self.openAttendanceReportWindow)

        self.layout.addWidget(self.attendance_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def openAttendanceReportWindow(self):
        self.attendance_report_window = AttendanceReportWindow(self.api)
        self.attendance_report_window.show()

class AttendanceReportWindow(QDialog):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Attendance Report')
        self.setGeometry(150, 150, 300, 200)

        layout = QFormLayout()

        self.label = QLabel('Attendance Report for which month?')
        self.input = QLineEdit(self)

        layout.addRow(self.label, self.input)

        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.submit)

        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def submit(self):
        month = self.input.text()
        print(f"Generating attendance report for {month}")
        # Here you can call the API method to generate the report
        self.api.attendanceReports(month)
        self.close()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     # api = AeriesAPIz()  # Assuming you have an AeriesAPI class
#     main_window = AeriesWindow(self.api)
#     main_window.show()
#     sys.exit(app.exec_())