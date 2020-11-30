# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import PySide2
from PySide2 import QtWidgets
from PySide2.QtCore import QRegExp
from PySide2.QtGui import QRegExpValidator
from PySide2.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
import sys

class Pb_Toolbar(QMainWindow):
    def __init__(self):
        super().__init__()

        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("测试工具栏")
        self.setMinimumSize(800, 600)
        self.setMaximumSize(800, 600)

        self.central_layout = QVBoxLayout()

        self.c_widget = QWidget()
        self.c_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.c_widget)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = Axes3D(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self.c_widget)

        self.central_layout.addWidget(self.canvas)
        self.central_layout.addWidget(self.toolbar)

        self._draw_surface()

    def _draw_surface(self):
        X = np.arange(-4, 4, 0.25)
        Y = np.arange(-4, 4, 0.25)
        X, Y = np.meshgrid(X, Y)
        R = np.sqrt(X ** 2 + Y ** 2)
        Z = np.sin(R)
        self.ax.cla()
        self.ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=plt.get_cmap('rainbow'))
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pb = Pb_Toolbar()
    pb.show()
    sys.exit(app.exec_())