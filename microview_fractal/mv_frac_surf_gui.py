# -*- coding: utf-8 -*-
import sys
import numpy as np
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
matplotlib.use('qt5agg')
from mv_data import MvData
from mv_3dcreator import Mv3dCreator
from mv_3dparameter import Mv3dParameter
from matplotlib.colors import LightSource


class MvFractalSurfaceGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = MvData()
        self.method = "离散傅里叶逆变换"
        # self.b_equal_axis = False     目前matplotlib暂不支持三维表面的等比例坐标轴显示
        self.b_detail = False

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
        self._set_get_para()
        self._set_button()
        self._set_show_para()

        self._create_surface()

    def _set_matplot_layout(self):
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = Axes3D(self.figure)
        matplotlib.rcParams["font.family"] = "STSong"

        self.toolbar = NavigationToolbar(self.canvas, self.c_widget)

        # self.cbx_equal = QCheckBox("等比例坐标")
        # self.cbx_equal.stateChanged.connect(lambda: self._equal_state())
        self.cbx_detail = QCheckBox("显示表面细节")
        self.cbx_detail.stateChanged.connect(lambda: self._show_detail())

        self.left_layout.addWidget(self.canvas)
        # self.left_layout.addWidget(self.cbx_equal)
        # 目前Axes3D尚不支持等比例坐标
        self.left_layout.addWidget(self.cbx_detail)
        self.left_layout.addWidget(self.toolbar)

    def _equal_state(self):
        self.b_equal_axis = self.cbx_equal.isChecked()
        self._redraw()

    def _show_detail(self):
        self.b_detail = self.cbx_detail.isChecked()
        self._redraw()

    def _set_model_method(self):
        ''' 选择建模算法 '''
        gp_method = QGroupBox("选择建模算法")
        gp_method.setMaximumHeight(120)
        self.radio_dft = QRadioButton("离散傅里叶逆变换")
        self.radio_rmd = QRadioButton("随机中点位移法")
        # self.radio_wm = QRadioButton("W-M函数法")
        self.radio_dft.setChecked(True)

        self.radio_dft.toggled.connect(lambda: self._select_method(self.radio_dft))
        self.radio_rmd.toggled.connect(lambda: self._select_method(self.radio_rmd))
        # self.radio_wm.toggled.connect(lambda: self._select_method(self.radio_wm))

        layout = QVBoxLayout()
        layout.addWidget(self.radio_dft)
        layout.addWidget(self.radio_rmd)
        # layout.addWidget(self.radio_wm)
        gp_method.setLayout(layout)
        self.right_layout.addWidget(gp_method)

    def _select_method(self, btn_method):
        if btn_method.isChecked():
            self.method = btn_method.text()
        if self.method == "离散傅里叶逆变换":
            self.lab_sq.setText("高度Sq：")
            self.chx_stable.setText("平稳分形")
            self.chx_stable.setDisabled(False)
            self.chx_stable.setChecked(True)
        elif self.method == "随机中点位移法":
            self.lab_sq.setText("高度Sa：")
            self.chx_stable.setDisabled(True)
            self.chx_stable.setChecked(False)


    def _set_get_para(self, method="离散傅里叶逆变换"):
        para_group = QGroupBox("输入建模参数")
        para_group.setMaximumHeight(150)
        # 设置4个标签 --------
        self.lab_dim = QLabel("分形维数：")
        self.lab_sq = QLabel("高度Sq：")
        self.lab_num = QLabel("采样点数：")
        self.lab_inter = QLabel("采样间隔：")
        # 设置4个编辑控件 --------
        self.edt_dim = QLineEdit()
        self.edt_dim.setText("2.2")
        reg = QRegExp("2+(.[0-9]{1,3})?$")
        p_validator = QRegExpValidator(self)
        p_validator.setRegExp(reg)
        self.edt_dim.setValidator(p_validator)
        self.edt_sq = QLineEdit()
        self.edt_sq.setText("1.0")
        self.cbx_num = QComboBox()
        self.cbx_num.addItems(["32x32", "64x64", "128x128", "256x256",
                               "512x512", "1024x1024", "2048x2048"])
        self.cbx_num.setCurrentIndex(2)
        self.edt_inter = QLineEdit()
        self.edt_inter.setText("1")
        self.chx_stable = QCheckBox("平稳分形")
        self.chx_stable.setChecked(True)

        form_layout = QFormLayout()
        form_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lab_dim)
        form_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.edt_dim)
        form_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.lab_sq)
        form_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.edt_sq)
        form_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.lab_num)
        form_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.cbx_num)
        form_layout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.lab_inter)
        form_layout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.edt_inter)
        form_layout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.chx_stable)

        para_group.setLayout(form_layout)
        self.right_layout.addWidget(para_group)

    def _set_button(self):
        self.btn_draw = QPushButton("绘图")
        self.btn_draw.setToolTip("单击开始绘图")
        self.btn_draw.setDefault(True)
        self.right_layout.addWidget(self.btn_draw)
        self.btn_draw.clicked.connect(self._create_surface)

    def _set_show_para(self):
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(4)
        self.table_widget.setColumnCount(2)
        self.right_layout.addWidget(self.table_widget)
        self.table_widget.setHorizontalHeaderLabels(['参数', '值'])
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.setColumnWidth(0, 80)
        self.table_widget.setMaximumHeight(180)
        item_1 = QTableWidgetItem("Sq")
        self.table_widget.setItem(0, 0, item_1)
        item_1 = QTableWidgetItem("Sa")
        self.table_widget.setItem(1, 0, item_1)
        item_1 = QTableWidgetItem("Ssk")
        self.table_widget.setItem(2, 0, item_1)
        item_1 = QTableWidgetItem("Sku")
        self.table_widget.setItem(3, 0, item_1)

    def _create_surface(self):
        sc = Mv3dCreator()
        dim = float(self.edt_dim.text())
        sqa = float(self.edt_sq.text())
        num = int(self.cbx_num.currentText().split('x')[0])
        si = float(self.edt_inter.text())
        if self.method == "离散傅里叶逆变换":
            stable = self.chx_stable.isChecked()
            sc.create_surf_dft(num, dim, sqa, si, stable)
        elif self.method == "随机中点位移法":
            sc.create_surf_rmd(num, dim, sqa, si)

        self.data = sc.get_data()
        self._redraw()

        paras = Mv3dParameter(self.data)
        sq = paras.get_Sq()
        item = QTableWidgetItem(str(sq))
        self.table_widget.setItem(0, 1, item)

        sa = paras.get_Sa()
        item = QTableWidgetItem(str(sa))
        self.table_widget.setItem(1, 1, item)

        ssk = paras.get_Ssk()
        item = QTableWidgetItem(str(ssk))
        self.table_widget.setItem(2, 1, item)

        sku = paras.get_Sku()
        item = QTableWidgetItem(str(sku))
        self.table_widget.setItem(3, 1, item)

    def _redraw(self):
        nx, ny = self.data.value.shape
        si = self.data.interval
        x = np.arange(0, nx*si, si)
        y = np.arange(0, ny*si, si)
        x, y = np.meshgrid(x, y)

        if self.b_detail or nx < 64:
            rst = 1
            cst = 1
        else:
            rst = nx // 64
            cst = ny // 64

        self.ax.cla()
        self.ax.plot_surface(x, y, self.data.value, rstride=rst,
                             cstride=cst, cmap=cm.gist_earth, shade=False)

        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    surf_gui = MvFractalSurfaceGui()
    surf_gui.show()
    sys.exit(app.exec_())