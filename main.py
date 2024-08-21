from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
import sys

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        label = QLabel('Welcome to the Super SOC Hub', self)
        layout.addWidget(label)

        self.setLayout(layout)
        self.setWindowTitle('Super SOC Hub')
        self.show()

def main():
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
