# -*- coding: utf-8 -*-
import sys

from PySide2.QtCore import QRegExp
from PySide2.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QGroupBox, QRadioButton, QLineEdit, QLabel, QCheckBox, QFormLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView,
                             QToolTip, QComboBox, QAction, QMessageBox)
from PySide2 import QtWidgets
from PySide2.QtGui import QFont, QRegExpValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
from mv_creator import MvCreator
from mv_parameter import MvParameter
from mv_data import MvData


class MvGui(QMainWindow):
    def __init__(self):
        super().__init__()
        QToolTip.setFont(QFont('Sans Serif', 12))
        self.method = "离散傅里叶逆变换"
        self.data = MvData()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self._int_ui()

    def _int_ui(self):
        self.setWindowTitle("分形轮廓建模及表征参数计算")
        self.setMinimumSize(800, 600)   # 固定界面尺寸
        self.setMaximumSize(800, 600)   # 固定界面尺寸

        self.status = self.statusBar()
        self.status.showMessage("分形轮廓建模及表征参数计算", 10000)

        self.menu = self.menuBar()
        menu_help = self.menu.addMenu("帮助")
        about = QAction("关于...", self)
        menu_help.addAction(about)
        menu_help.triggered[QAction].connect(self._help_process)

        self.glb_layout = QHBoxLayout()  # 设定全局布局
        self.v1_layout_left = QVBoxLayout()
        self.v1_layout_right = QVBoxLayout()

        self.c_widget = QWidget()
        self.c_widget.setLayout(self.glb_layout)
        self.setCentralWidget(self.c_widget)

        self._set_v1_left()     # 为matplotlib画布及工具栏进行布局
        self._set_v1_right_1()  # 为"选择算法区域"进行布局
        self._set_v1_right_2()  # 为”设计参数“区域进行布局
        self._set_v1_right_3()  # ”绘图“按钮布局
        self._set_v1_right_4()  # 基本参数显示区域布局
        self._set_v1_right_5()  # 图标区布局
        self.glb_layout.addLayout(self.v1_layout_left)
        self.glb_layout.addLayout(self.v1_layout_right)

        self._draw_fractal_profile()

    def _set_v1_left(self):
        self.toolbar = NavigationToolbar(self.canvas, self.c_widget)

        self.cbx_equal = QCheckBox("等比例坐标")
        self.cbx_equal.stateChanged.connect(lambda : self._equal_state())
        
        self.v1_layout_left.addWidget(self.canvas)
        self.v1_layout_left.addWidget(self.cbx_equal)
        self.v1_layout_left.addWidget(self.toolbar)

    def _set_v1_right_1(self):
        group_method = QGroupBox("选择建模算法")
        group_method.setMaximumHeight(120)
        self.radio_dft = QRadioButton("离散傅里叶逆变换")
        self.radio_rmd = QRadioButton("随机中点位移法")
        self.radio_wm = QRadioButton("W-M函数法")
        self.radio_dft.setChecked(True)

        self.radio_dft.toggled.connect(lambda: self._sel_method(self.radio_dft))
        self.radio_rmd.toggled.connect(lambda: self._sel_method(self.radio_rmd))
        self.radio_wm.toggled.connect(lambda: self._sel_method(self.radio_wm))

        layout_r1 = QVBoxLayout()
        layout_r1.addWidget(self.radio_dft)
        layout_r1.addWidget(self.radio_rmd)
        layout_r1.addWidget(self.radio_wm)
        group_method.setLayout(layout_r1)
        self.v1_layout_right.addWidget(group_method)

    def _set_v1_right_2(self):
        group_para = QGroupBox("输入建模参数")
        group_para.setMaximumHeight(150)
        self.lab_dim = QLabel("分形维数：")
        self.edt_dim = QLineEdit()
        self.edt_dim.setText("1.2")
        reg = QRegExp("1+(.[0-9]{1,3})?$")
        pValidator = QRegExpValidator(self)
        pValidator.setRegExp(reg)
        self.edt_dim.setValidator(pValidator)

        self.lab_sq = QLabel("高度Rq：")
        self.edt_sq = QLineEdit()
        self.edt_sq.setText("1.0")

        self.lab_num = QLabel("采样点数：")
        self.cbx_num = QComboBox()
        self.cbx_num.addItems(["64", "128", "256", "512", "1024", "2048", "4096"])
        self.cbx_num.setCurrentIndex(3)

        self.lab_inter = QLabel("采样间隔：")
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

        group_para.setLayout(form_layout)
        self.v1_layout_right.addWidget(group_para)

    def _set_v1_right_3(self):
        self.btn_draw = QPushButton("绘图")
        self.btn_draw.setToolTip("单击开始绘图")
        self.btn_draw.setDefault(True)      # 设置为默认按钮
        self.v1_layout_right.addWidget(self.btn_draw)
        self.btn_draw.clicked.connect(self._draw_fractal_profile)

    def _set_v1_right_4(self):
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(4)
        self.table_widget.setColumnCount(2)
        self.v1_layout_right.addWidget(self.table_widget)
        self.table_widget.setHorizontalHeaderLabels(['参数', '值'])
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.setColumnWidth(0, 80)
        self.table_widget.setMaximumHeight(180)
        item_1 = QTableWidgetItem("Rq")
        self.table_widget.setItem(0, 0, item_1)
        item_1 = QTableWidgetItem("Ra")
        self.table_widget.setItem(1, 0, item_1)
        item_1 = QTableWidgetItem("Rsk")
        self.table_widget.setItem(2, 0, item_1)
        item_1 = QTableWidgetItem("Rku")
        self.table_widget.setItem(3, 0, item_1)

    def _set_v1_right_5(self):
        self.adv_label = QLabel("图标区")
        self.v1_layout_right.addWidget(self.adv_label)

    def _draw_fractal_profile(self):
        profile_crtor = MvCreator()
        if self.method == "离散傅里叶逆变换":
            dim = float(self.edt_dim.text())
            sq = float(self.edt_sq.text())
            num = int(self.cbx_num.currentText())
            inter = float(self.edt_inter.text())
            is_stable = self.chx_stable.isChecked()
            profile_crtor.create_data_dft(num, dim, sq, inter, is_stable)
        elif self.method == "随机中点位移法":
            dim = float(self.edt_dim.text())
            sq = float(self.edt_sq.text())
            num = int(self.cbx_num.currentText())
            inter = float(self.edt_inter.text())
            profile_crtor.create_data_mpd(num, dim, inter, sq)
        else:
            dim = float(self.edt_dim.text())
            sq = float(self.edt_sq.text())
            num = int(self.cbx_num.currentText())
            inter = float(self.edt_inter.text())
            is_stable = self.chx_stable.isChecked()
            profile_crtor.create_data_wm(num, dim, sq, inter, is_stable)

        self.data = profile_crtor.get_data()

        self._redraw()

        paras = MvParameter(self.data)
        rq = paras.get_Rq()
        item_1 = QTableWidgetItem(str(rq))
        self.table_widget.setItem(0, 1, item_1)

        ra = paras.get_Ra()
        item_1 = QTableWidgetItem(str(ra))
        self.table_widget.setItem(1, 1, item_1)

        rsk = paras.get_Rsk()
        item_1 = QTableWidgetItem(str(rsk))
        self.table_widget.setItem(2, 1, item_1)

        rku = paras.get_Rku()
        item_1 = QTableWidgetItem(str(rku))
        self.table_widget.setItem(3, 1, item_1)

    def _redraw(self):
        is_equal = self.cbx_equal.isChecked()

        length = np.size(self.data.value)
        x = np.arange(0, self.data.interval * length, self.data.interval)
        y = self.data.value
        self.ax.cla()
        self.ax.plot(x, y)
        if is_equal:
            self.ax.axis('equal')
        else:
            self.ax.axis('auto')

        self.canvas.draw()

    def _equal_state(self):
        self._redraw()

    def _help_process(self, g):
        if g.text() == "关于...":
            QMessageBox.information(self, "关于", "作者：周超<p>邮箱：zandz1978@126.com<p>协议：GPL v3")

    def _sel_method(self, btn_method):
        if btn_method.isChecked():
            self.method = btn_method.text()
        if self.method == "离散傅里叶逆变换":

            self.lab_sq.setText("高度Rq：")
            self.chx_stable.setText("平稳分形")
            self.chx_stable.setDisabled(False)
            self.chx_stable.setChecked(True)
        elif self.method == "随机中点位移法":
            self.lab_sq.setText("尺度系数：")
            self.chx_stable.setDisabled(True)
            self.chx_stable.setChecked(False)
        else:
            self.lab_sq.setText("尺度系数：")
            self.chx_stable.setText("随机相位")
            self.chx_stable.setDisabled(False)
            self.chx_stable.setChecked(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mv_gui = MvGui()
    mv_gui.show()
    sys.exit(app.exec_())