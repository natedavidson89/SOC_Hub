from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout

class CredentialsInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter AERIES Credentials")
        self.setGeometry(100, 100, 300, 200)

        self.layout = QVBoxLayout()

        self.form_layout = QFormLayout()
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.school_input = QLineEdit(self)

        self.form_layout.addRow("Username:", self.username_input)
        self.form_layout.addRow("Password:", self.password_input)
        self.form_layout.addRow("School Number:", self.school_input)

        self.layout.addLayout(self.form_layout)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.submit_credentials)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)

    def submit_credentials(self):
        self.username = self.username_input.text()
        self.password = self.password_input.text()
        self.school = self.school_input.text()
        self.accept()