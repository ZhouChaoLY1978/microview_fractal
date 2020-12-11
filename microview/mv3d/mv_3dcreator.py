# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from mv2d.mv_data2d import MvData2d


class Mv3dCreator(object):
    """ 创建分形表面
    """
    def __init__(self):
        self.data = MvData2d()

    def create_surf_rmd(self, n:int, d:float, sa:float, si:float):
        """ 基于随机中点位移法创建分形表面

        :param n: 采样点数，数值应为2的幂次方
        :param d: 分形维数，2<d<3
        :param si: 采样间隔
        :param sa: 构建表面的Sa值
        """
        lev = int(np.log2(n))
        surf = np.zeros((n+1, n+1))
        st_dev = 1
        stp = n // 2
        hurst = 3 - d
        # 初始化四个角点的坐标值
        surf[0, 0] = st_dev * np.random.normal()
        surf[0, n] = st_dev * np.random.normal()
        surf[n, 0] = st_dev * np.random.normal()
        surf[n, n] = st_dev * np.random.normal()
        #
        for lv in range(lev):

            st_dev = st_dev * np.power(0.5, 0.5*hurst)
            for i in range(stp, n, 2*stp):
                for j in range(stp, n, 2*stp):
                    surf[i, j] = self._avg_4(st_dev, surf[i-stp, j-stp], surf[i+stp, j-stp],
                                             surf[i-stp, j+stp], surf[i+stp, j+stp])
            for i in range(0, n+1, stp):
                for j in range(0, n+1, stp):
                    if np.fabs(surf[i,j]) > 0.00001 :
                        continue
                    if i == 0:
                        surf[i, j] = self._avg_3(st_dev, surf[i, j-stp], surf[stp, j], surf[i, j+stp])
                    elif i == n:
                        surf[i, j] = self._avg_3(st_dev, surf[n, j-stp], surf[n-stp, j], surf[n, j+stp])
                    elif j == 0:
                        surf[i, j] = self._avg_3(st_dev, surf[i-stp, j], surf[i, stp], surf[i+stp, j])
                    elif j == n:
                        surf[i, j] = self._avg_3(st_dev, surf[i-stp, j], surf[i, n-stp], surf[i+stp, n])
                    else:
                        surf[i, j] = self._avg_4(st_dev, surf[i, j-stp], surf[i, j+stp],
                                             surf[i-stp, j], surf[i+stp, j])
            stp = stp // 2

        # 使表面的平均高度为0
        surf = surf[0:n, 0:n]
        h_mean = np.mean(surf)
        surf = surf - h_mean
        sa_surf = np.round(np.mean(np.abs(surf)),4)
        sa = np.round(sa, 4)
        ratio = sa / sa_surf
        surf = surf * ratio

        self.data.value = surf
        self.data.interval = si


    def _avg_4(self, st_dev, f1, f2, f3, f4):
        val = (f1+f2+f3+f4)/4 + st_dev * np.random.normal()
        return val

    def _avg_3(self, st_dev, f1, f2, f3):
        val = (f1+f2+f3)/3 + st_dev * np.random.normal()
        return val


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

        sqrt_coef = np.sqrt(fractal_coef)

        for u in range(1, n//2):
            for v in range(1, n//2):
                phase1 = np.random.uniform(0, 2 * np.pi)
                phase2 = np.random.uniform(0, 2 * np.pi)
                if stable:
                    mag1 = sqrt_coef * np.power(u**2 + v**2, (d-4)/2)
                    mag2 = mag1
                else:
                    mag1 = np.random.randn() * sqrt_coef * np.power(u**2 + v**2, (d-4)/2)
                    mag2 = np.random.randn() * sqrt_coef * np.power(u**2 + v**2, (d-4)/2)

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
                mag_u = np.random.randn() * sqrt_coef * np.power(i ** 2, (d - 4) / 2)
                mag_v = np.random.randn() * sqrt_coef * np.power(i ** 2, (d - 4) / 2)

            value_u = np.complex(mag_u * np.cos(phase_u), mag_u * np.sin(phase_u))
            value_v = np.complex(mag_v * np.cos(phase_v), mag_v * np.sin(phase_v))
            fs_coef[i, 0] = value_u
            fs_coef[n-i, 0] = np.conj(value_u)
            fs_coef[0, i] = value_v
            fs_coef[0, n-i] = np.conj(value_v)

        surface = (np.fft.ifft2(fs_coef)).real
        self.data.value = surface
        self.data.interval = inter

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

    def show_surface(self, surf, n, i):
        x = np.arange(0, n*i, i)
        y = np.arange(0, n*i, i)
        x, y = np.meshgrid(x, y)

        fig = plt.figure()
        ax = Axes3D(fig)
        ax.plot_surface(x, y, surf, rstride=1, cstride=1, cmap=cm.viridis)
        plt.show()

    def get_data(self):
        return self.data


if __name__ == "__main__":
    test = Mv3dCreator()
    n = 128
    # test.create_surf_dft(128, 2.2, 1, 1)
    test.create_surf_rmd(n, 2.2, 1, 10)
    print(test.get_data().value)
    print(np.mean(np.abs(test.get_data().value)))
    test.show_surface(test.get_data().value, n, 1)
