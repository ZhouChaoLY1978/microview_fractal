# -*- coding: utf-8 -*-
"""
作者：周超
单位：福州大学
邮箱：zandz1978@126.com
最后编辑时间：
"""
import numpy as np
import matplotlib.pyplot as plt


class MvData2d(object):
    """ 自定义的数据类型
    """
    def __init__(self, value=None, interval=1.0):
        self.__value = value        # 一维ndarray，存储轮廓高度数据
        self.__interval = interval  # float, 采样间隔

    @property
    def interval(self):
        return self.__interval

    @interval.setter
    def interval(self, interval):
        if interval <= 0:
            raise ValueError("采样间隔值必须大于0")
        self.__interval = interval

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def draw_profile(self, ax1):
        """ 根据成员变量中的数据，绘制轮廓

        :param ax1: 绘制图形的axes
        :param param_dict: 存储赋给ax.plot的绘图参数
        """
        sn = np.size(self.__value)  # 轮廓采样点数
        x_value = np.arange(0, self.__interval * sn, self.__interval)
        profile = ax1.plot(x_value, self.__value)
        return profile


if __name__ == "__main__":
    md = MvData2d()
    values = np.array([1, 2, 3, 4, 5])

    md.value = values
    md.interval = 0.5

    fig, ax = plt.subplots(1, 1)
    md.draw_profile(ax)
    fig.show()



