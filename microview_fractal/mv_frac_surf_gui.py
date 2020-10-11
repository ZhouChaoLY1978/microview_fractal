# -*- coding: utf-8 -*-
import sys
import PySide2
from PySide2.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib
from mv_data import MvData


class MvFractalSurfaceGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = MvData()

        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("分形表面建模及表征参数计算")
        self.setMinimumSize(800, 600)
        self.setMaximumSize(800, 600)
        # self.setWindowIcon()
        self.status = self.statusBar()
        self.status.showMessage("分形表面建模及表征参数计算", 10000)

        self.glb_layout = QHBoxLayout()  # 全局布局
        self.left_layout = QVBoxLayout()  # 左侧布局
        self.right_layout = QVBoxLayout()  # 右侧布局
        self.glb_layout.addLayout(self.left_layout)
        self.glb_layout.addLayout(self.right_layout)

        # 设置c_widget为QMainWindow的中心控件，并将其布局设置为glb_layout
        self.c_widget = QWidget()
        self.c_widget.setLayout(self.glb_layout)
        self.setCentralWidget(self.c_widget)

        self._set_matplot_layout()
        self._set_model_method()

    def _set_matplot_layout(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        matplotlib.rcParams["font.family"] = "STSong"

        self.toolbar = NavigationToolbar(self.canvas, self.c_widget)

        self.cbx_equal = QCheckBox("等比例坐标")
        self.cbx_equal.stateChanged.connect(lambda: self._equal_state())

        self.left_layout.addWidget(self.canvas)
        self.left_layout.addWidget(self.cbx_equal)
        self.left_layout.addWidget(self.toolbar)

    def _equal_state(self):
        pass

    def _set_model_method(self):
        ''' 选择建模算法 '''
        gp_method = QGroupBox("选择建模算法")
        gp_method.setMaximumHeight(120)
        self.radio_dft = QRadioButton("离散傅里叶逆变换法")
        self.radio_rmd = QRadioButton("随机中点位移法")
        self.radio_wm = QRadioButton("W-M函数法")
        self.radio_dft.setChecked(True)

        self.radio_dft.toggled.connect(self._select_method)
        self.radio_rmd.toggled.connect(self._select_method)
        self.radio_wm.toggled.connect(self._select_method)

        layout = QVBoxLayout()
        layout.addWidget(self.radio_dft)
        layout.addWidget(self.radio_rmd)
        layout.addWidget(self.radio_wm)
        gp_method.setLayout(layout)
        self.right_layout.addWidget(gp_method)

    def _select_method(self):
        sender = self.sender()
        if sender.text() == "离散傅里叶逆变换法":
            print(sender.text())
        elif sender.text() == "随机中点位移法":
            print(sender.text())
        else:
            print(sender.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    surf_gui = MvFractalSurfaceGui()
    surf_gui.show()
    sys.exit(app.exec_())