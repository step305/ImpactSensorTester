from PyQt6 import QtCore, QtGui, QtWidgets
import main_mindow


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = main_mindow.TestWindow()
    ui.show()

    sys.exit(app.exec())
