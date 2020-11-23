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
        fractal_coef = self._get_fractal_cof_from_sq(n, d, sq)
        fs_coef = np.zeros((n, n), dtype=complex)
        surface = np.zeros((n, n))

        sqrt_coef = np.sqrt(fractal_coef)

        for u in range(1, n//2):
            for v in range(1, n//2):
                phase1 = np.random.uniform(0, 2 * np.pi)
                phase2 = np.random.uniform(0, 2 * np.pi)
                if stable:
                    mag1 = sqrt_coef * np.power(u**2 + v**2, (d-4)/2)
                    mag2 = mag1
                else:
                    mag1 = np.random.normal(0, 1) * sqrt_coef * np.power(u**2 + v**2, (d-4)/2)
                    mag2 = np.random.normal(0, 1) * sqrt_coef * np.power(u**2 + v**2, (d-4)/2)

                value_1 = np.complex(mag1 * np.cos(phase1), mag1 * np.sin(phase1))
                value_2 = np.complex(mag2 * np.cos(phase2), mag2 * np.sin(phase2))
                fs_coef[u, v] = value_1
                fs_coef[n-u, n-v] = np.conj(value_1)
                fs_coef[u, n-v] = value_2
                fs_coef[n-u, v] = np.conj(value_2)

        for i in range(1, n//2):
            phase_u = np.random.uniform(0, 2 * np.pi)
            phase_v = np.random.uniform(0, 2 * np.pi)
            if stable:
                mag_u = sqrt_coef * np.power(i ** 2, (d - 4) / 2)
                mag_v = sqrt_coef * np.power(i ** 2, (d - 4) / 2)
            else:
                mag_u = np.random.normal(0, 1) * sqrt_coef * np.power(i ** 2, (d - 4) / 2)
                mag_v = np.random.normal(0, 1) * sqrt_coef * np.power(i ** 2, (d - 4) / 2)

            value_u = np.complex(mag_u * np.cos(phase_u), mag_u * np.sin(phase_u))
            value_v = np.complex(mag_v * np.cos(phase_v), mag_v * np.sin(phase_v))
            fs_coef[i, 0] = value_u
            fs_coef[n-i, 0] = np.conj(value_u)
            fs_coef[0, i] = value_v
            fs_coef[0, n-i] = np.conj(value_v)

        surface = (np.fft.ifft2(fs_coef)).real
        return surface

    def _get_fractal_cof_from_sq(self, n, d, sq):
        """ 由分形表面的Sq值计算表面的尺度系数C

        :param n: 采样点数
        :param d: 分形维数
        :param sq: 表面采样点高度均方根偏差的期望值
        """

        temp_sum_1 = 0
        for u in range(1, n // 2):
            for v in range(0, n // 2):
                temp_sum_1 = temp_sum_1 + np.power(u**2+v**2, d-4)

        temp_sum_2 = 0
        for u in range(0, n // 2):
            for v in range(1, n // 2):
                temp_sum_2 = temp_sum_2 + np.power(u**2+v**2, d-4)

        c = (sq**2 * n**4) / (2 * temp_sum_1 + 2 * temp_sum_2)
        return c

if __name__ == "__main__":
    test = Mv3dCreator()
    s = test.create_surf_dft(8, 2.2, 1, 1)
    print(s)