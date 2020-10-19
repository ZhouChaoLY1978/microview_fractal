# -*- coding: utf-8 -*-
import numpy as np
import scipy
from mv_data import MvData


class Mv3dCreator(object):
    """ 创建分形表面
    """
    def __init__(self):
        self.data = MvData()

    def create_surf_dft(self, n, d, sq, inter, stable=True):
        """ 基于离散傅里叶逆变换创建分形表面

        :param n: 采样点数，数值应为2的幂次方
        :param d: 分形维数，2<d<3
        :param sq: 表面采样点高度均方根偏差的期望值
        :param inter: 表面采样间隔，存储在表面数据中，建模时不使用
        :param stable: 是否生成平稳分形表面
        """
        pass

    def _get_fractal_cof_from_sq(self, n, d, sq):
        """ 由分形表面的Sq值计算表面的尺度系数C

        :param n: 采样点数
        :param d: 分形维数
        :param sq: 表面采样点高度均方根偏差的期望值
        """
        temp_sum = 0
        for u in range(0, n // 2):
            for v in range(0, n // 2):
                if u == 0 and v == 0:
                    continue
                temp_sum = temp_sum + np.power(u**2+v**2, d-4)

        c = (sq**2 * n**4) / (4 * temp_sum)
        return c
