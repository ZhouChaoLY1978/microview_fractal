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


class MvData(object):
    """ 自定义的数据类型
    """
    def __init__(self, value=None, interval=1.0):
        self.__value = value        # ndarray，存储数据
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


if __name__ == "__main__":
    md = MvData()
    values = np.array([[1, 2, 3, 4, 5], [3, 4, 5, 6, 7]])

    md.value = values
    md.interval = 0.5

    print(md.value)
    print(md.interval)


