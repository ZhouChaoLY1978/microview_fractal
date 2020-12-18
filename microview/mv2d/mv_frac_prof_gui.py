# -*- coding: utf-8 -*-
import sys
import PySide2
from PySide2.QtCore import QRegExp
from PySide2.QtWidgets import *
from PySide2 import QtWidgets
from PySide2.QtGui import QFont, QRegExpValidator, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib
import numpy as np
from mv2d.mv_2dcreator import Mv2dCreator
from mv2d.mv_2dparameter import Mv2dParameter
from mv2d.mv_data2d import MvData2d


class MvFractalProfileGui(QMainWindow):
    def __init__(self):
        super().__init__()  # 调用基类的构造函数

        QToolTip.setFont(QFont('Sans Serif', 12))

        self.data = MvData2d()
        self.method = "离散傅里叶逆变换"
        # 初始化绘图环境
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        matplotlib.rcParams["font.family"] = "STSong"
        # --------

        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("分形轮廓建模及表征参数计算")
        self.setMinimumSize(800, 600)   # 固定界面尺寸
        self.setMaximumSize(800, 600)   # 固定界面尺寸
        # --------
        self.setWindowIcon(QIcon("../../icons/main_icon.png"))
        # --------
        self.status = self.statusBar()
        self.status.showMessage("分形轮廓建模及表征参数计算", 10000)
        # --------
        # 菜单 ---------
        self.menu = self.menuBar()
        help_menu = self.menu.addMenu("帮助")
        about_action = QAction("关于...", self)
        help_menu.addAction(about_action)
        help_menu.triggered[QAction].connect(self._help_process)
        # --------
        # 工具栏 --------
        exit_action = QAction(QIcon("../../icons/close.png"), "Exit", self)
        exit_action.setStatusTip("退出应用")
        exit_action.triggered.connect(self.close)
        self.toolbar = self.addToolBar("Exit")
        self.toolbar.addAction(exit_action)
        # --------
        # 设定全局布局和窗口的中心控件 --------
        self.glb_layout = QHBoxLayout()  # 设定全局布局
        self.left_layout_lev1 = QVBoxLayout()
        self.right_layout_lev1 = QVBoxLayout()
        self.glb_layout.addLayout(self.left_layout_lev1)
        self.glb_layout.addLayout(self.right_layout_lev1)

        self.c_widget = QWidget()
        self.c_widget.setLayout(self.glb_layout)
        self.setCentralWidget(self.c_widget)
        # --------
        self._set_matplotlib_layout()     # 为matplotlib画布及工具栏进行布局
        self._set_model_method()  # 为"选择算法区域"进行布局
        self._set_get_para()  # 为”分形参数“区域进行布局
        self._set_button()  # 功能按钮区布局
        self._set_show_para()  # 基本参数显示区域布局

        self._draw_fractal_profile()

    def _set_matplotlib_layout(self):
        self.toolbar = NavigationToolbar(self.canvas, self.c_widget)

        self.cbx_equal = QCheckBox("等比例坐标")
        self.cbx_equal.stateChanged.connect(lambda : self._equal_state())
        
        self.left_layout_lev1.addWidget(self.canvas)
        self.left_layout_lev1.addWidget(self.cbx_equal)
        self.left_layout_lev1.addWidget(self.toolbar)

    def _equal_state(self):
        self._redraw()

    def _set_model_method(self):
        group_method = QGroupBox("选择建模算法")
        group_method.setMaximumHeight(120)
        self.radio_dft = QRadioButton("离散傅里叶逆变换")
        self.radio_rmd = QRadioButton("随机中点位移法")
        self.radio_wm = QRadioButton("W-M函数法")
        self.radio_dft.setChecked(True)

        self.radio_dft.toggled.connect(lambda: self._select_method(self.radio_dft))
        self.radio_rmd.toggled.connect(lambda: self._select_method(self.radio_rmd))
        self.radio_wm.toggled.connect(lambda: self._select_method(self.radio_wm))

        layout = QVBoxLayout()
        layout.addWidget(self.radio_dft)
        layout.addWidget(self.radio_rmd)
        layout.addWidget(self.radio_wm)
        group_method.setLayout(layout)
        self.right_layout_lev1.addWidget(group_method)

    def _set_get_para(self, method="离散傅里叶逆变换"):
        para_group = QGroupBox("输入建模参数")
        para_group.setMaximumHeight(150)
        # 设置4个标签 ---------
        self.lab_dim = QLabel("分形维数：")
        if method == "离散傅里叶逆变换":
            self.lab_sq = QLabel("高度Rq：")
        else:
            self.lab_sq.setText("尺度系数：")
        self.lab_num = QLabel("采样点数：")
        self.lab_inter = QLabel("采样间隔：")
        # 设置4个编辑控件 --------
        self.edt_dim = QLineEdit()
        self.edt_dim.setText("1.2")
        reg = QRegExp("1+(.[0-9]{1,3})?$")
        pValidator = QRegExpValidator(self)
        pValidator.setRegExp(reg)
        self.edt_dim.setValidator(pValidator)

        self.edt_sq = QLineEdit()
        self.edt_sq.setText("1.0")

        self.cbx_num = QComboBox()
        self.cbx_num.addItems(["64", "128", "256", "512", "1024", "2048", "4096"])
        self.cbx_num.setCurrentIndex(3)

        self.edt_inter = QLineEdit()
        self.edt_inter.setText("1")

        self.chx_stable = QCheckBox("平稳分形")
        if method == "随机中点位移法":
            self.chx_stable.setDisabled(True)
            self.chx_stable.setChecked(False)
        else:
            self.chx_stable.setDisabled(False)
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
        self.right_layout_lev1.addWidget(para_group)

    def _set_button(self):
        func_btn_layout = QHBoxLayout()

        self.btn_draw = QPushButton("绘图")
        self.btn_draw.setToolTip("单击开始绘图")
        self.btn_draw.setDefault(True)      # 设置为默认按钮
        # self.right_layout_lev1.addWidget(self.btn_draw)
        self.btn_draw.clicked.connect(self._draw_fractal_profile)

        self.btn_export = QPushButton("导出...")
        self.btn_export.setToolTip("单击导出轮廓数据")
        # self.right_layout_lev1.addWidget(self.btn_export)
        self.btn_export.clicked.connect(self._exprot_profile_data)

        func_btn_layout.addWidget(self.btn_draw)
        func_btn_layout.addWidget(self.btn_export)
        self.right_layout_lev1.addLayout(func_btn_layout)

    def _exprot_profile_data(self):
        fname, ftype = QFileDialog.getSaveFileName(self, "保存文件", ".", "Text Files (*.txt)")
        np.savetxt(fname, self.data.value)
        QMessageBox.information(self, "信息", "完成数据导出")


    def _set_show_para(self):
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(4)
        self.table_widget.setColumnCount(2)
        self.right_layout_lev1.addWidget(self.table_widget)
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

    def _draw_fractal_profile(self):
        profile_crtor = Mv2dCreator()
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

        paras = Mv2dParameter(self.data)
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

        self.ax.cla()
        self.data.draw_profile(self.ax)

        if is_equal:
            self.ax.axis('equal')
        else:
            self.ax.axis('auto')

        self.ax.set_xlabel('profile direction')
        self.ax.set_ylabel('height')
        self.ax.set_title('分形轮廓')

        self.canvas.draw()

    def _help_process(self, g):
        if g.text() == "关于...":
            QMessageBox.information(self, "关于", "作者：周超<p>邮箱：zandz1978@126.com<p>版本：0.5<p>协议：GPL v3")

    def _select_method(self, btn_method):
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

    def closeEvent(self, event:PySide2.QtGui.QCloseEvent):
        reply = QMessageBox.question(self, '消息',
                                     "确认退出?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mv_gui = MvFractalProfileGui()
    mv_gui.show()
    sys.exit(app.exec_())