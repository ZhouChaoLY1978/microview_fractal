# -*- coding: utf-8 -*-
"""
作者：周超
单位：福州大学
邮箱：zandz1978@126.com
最后编辑时间：

author: ZHOU Chao
organization: Fuzhou university
e-mail: zandz1978@126.com
last edited:
"""
import numpy as np
from mv2d.mv_data import MvData


class Mv2dParameter(object):
    """ 计算表征参数
    """

    def __init__(self, data: MvData = None):
        """ 构造函数

        :param data: 二维数据，MvData类型
        """
        self.data = data
        self.para_dict = {}  # 存储已计算的表征参数

    def get_Rq(self, digits=4) -> float:
        """ 计算轮廓的均方根偏差（root mean square deviation） Rq

        :return: float 轮廓的均方根偏差（root mean square deviation） Rq
        """
        data_value = self.data.value
        Rq = np.sqrt(np.mean(np.power(data_value, 2)))
        Rq = np.round(Rq, digits)
        self.para_dict.setdefault('Rq', Rq)
        return Rq

    def get_Ra(self, digits=4) -> float:
        """ 计算轮廓的算术平均偏差（arithmetical mean deviation） Ra

        :return: float 轮廓的算术平均偏差（arithmetical mean deviation） Ra
        """
        data_value = self.data.value
        Ra = np.mean(np.abs(data_value))
        Ra = np.round(Ra, digits)
        self.para_dict.setdefault('Ra', Ra)
        return Ra

    def get_Rsk(self, digits=4) -> float:
        """ 计算轮廓的偏斜度（skewness） Rsk

        :return: float 轮廓的偏斜度（skewness） Rsk
        """
        data_value = self.data.value
        rq = self.get_Rq()
        h3 = np.power(data_value, 3)  # 数据值的三次方
        Rsk = np.mean(h3) / np.power(rq, 3)
        Rsk = np.round(Rsk, digits)
        self.para_dict.setdefault('Rsk', Rsk)
        return Rsk

    def get_Rku(self, digits=4) -> float:
        """ 计算轮廓的陡度（kurtosis） Rku

        :return: float 轮廓的陡度（kurtosis） Rku
        """
        data_value = self.data.value
        rq = self.get_Rq()
        h4 = np.power(data_value, 4)  # 数据值的四次方
        Rku = np.mean(h4) / np.power(rq, 4)
        Rku = np.round(Rku, digits)
        self.para_dict.setdefault('Rku', Rku)
        return Rku
