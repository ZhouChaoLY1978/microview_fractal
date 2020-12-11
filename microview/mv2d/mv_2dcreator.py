# -*- coding: utf-8 -*-
import numpy as np
from mv2d.mv_data import MvData
import scipy


class Mv2dCreator(object):
    """ 创建二维数据


    """
    def __init__(self):
        self.data = MvData()

    def create_data_wm(self, n: int, d: float, g: float, inter: float, random=True, gamma=1.5):
        """ 基于Weierstrass Mandelbrot函数生成分形数据

        :param n: 采样点数
        :param d: 分形维数，1<d<2
        :param g: 尺度系数
        :param inter: 采样间隔
        :param gamma
        :param random: 是否引入随机相位
        """
        data = np.zeros(n, dtype=float)
        smp_length = inter * (n-1)
        freq_index_min = -int((np.log(smp_length) / np.log(gamma)))
        freq_index_max = -int((np.log(inter) / np.log(gamma)))
        for f in range(freq_index_min, freq_index_max):
            if random:
                phi = np.random.rand()*np.pi*2  # [0, 2*np.pi) 均匀分布的随机相位
            else:
                phi = 0
            for i in range(0, n):
                data[i] += np.cos(2*np.pi*np.power(gamma, f)*i*inter+phi) / np.power(gamma, (2-d)*f)

        data = np.power(g, d-1) * data
        self.data.value = data
        self.data.interval = inter

    def create_data_dft(self, n: int, d: float, rq: float, inter: float, stable=True):
        """ 基于离散傅里叶变换（Discrete Fourier Transform, DFT）生成分形数据

        :param n: 采样点数，应为2的幂次方
        :param d: 分形维数，1<d<2
        :param rq: 轮廓采样点高度均方根偏差的期望值
        :param inter: 轮廓的采样间隔，存储在轮廓数据中，DFT时不需用到。
        :param stable: 生成轮廓的实际Rq值是否等于参数rq的值
        """
        # 判断采样点数n是否为2的幂次方，若n不是2的幂次方，则中断执行程序
        # 在GUI中，应用列表，保证输入为2的幂次方
        import math
        assert math.log(n, 2).is_integer(), "输入的采样点数不是2的幂次方，程序退出"
        # 判定分形维数是否在(1,2)之间
        assert 1 < d < 2, "分形维数d必须满足：1<d<2"

        tmp_1 = 5 - 2 * d
        i_n = np.arange(1, n//2)   # 索引n

        tem_s = np.sum(1/np.power(i_n, tmp_1))
        tmp_2 = n**2 / (2 * tem_s)
        cof = np.sqrt(rq**2 * tmp_2)    # 尺度系数C

        dft_cof = np.zeros(n, dtype=np.complex)   # 存储左侧离散傅里叶系数
        dft_cof[0] = 0
        dft_cof[n//2] = dft_cof[0]
        for i_k in np.arange(1, n//2):  # 索引k
            if not stable:
                r = cof * np.power(i_k, -tmp_1/2) * np.random.rand()
            else:
                r = cof * np.power(i_k, -tmp_1 / 2)
            p = np.random.uniform(0, 2*np.pi, 1)[0]
            dft_cof[i_k] = np.complex(r * np.cos(p), r * np.sin(p))

        dft_cof_conj = np.conj(dft_cof[1:n//2])[: : -1]
        dft_cof[n//2+1 : ] = dft_cof_conj

        self.data.value = np.real(scipy.ifft(dft_cof))
        self.data.interval = inter

    def create_data_mpd(self, n: int, d: float, inter: float, sigma: float = 1):
        """ 基于随机中点位移法生成分形数据

        :param n: 采样点数，采样点数与迭代层数的关系为 n=2^{lev}+1
        :param d: 分形维数，1<d<2
        :param inter: 采样间隔
        :param sigma: 期望的标准差
        """
        assert 1 < d < 2, "分形维数d必须满足：1<d<2"

        hurst = 2 - d   # 计算Hurst指数
        lev = int(np.log2(n))   # 迭代次数
        n = n + 1   # 计算轮廓的总点数比输入总点数多1个，后面将第0个点去除

        data = np.zeros(n, dtype=float)
        data[0] = 0
        data[n-1] = sigma * np.random.randn()

        mid_one = (n-1)//2   # 每次迭代时的第一个点的序号
                            # 此处为mid_one赋初值
        d_sigma = sigma * (np.power(0.5, 2*hurst) - 0.25)

        for i in range(0, lev):
            i_end = 2 * mid_one     # 每次迭代第1个区间尾端点的序号
            data[int(mid_one)] = 0.5*(data[0] + data[int(i_end)])+np.sqrt(d_sigma)*np.random.randn()
            i_inc = 2 * mid_one
            i_smp = mid_one + i_inc
            while True:
                if i_smp >= n-1:
                    break
                data[int(i_smp)]=0.5*(data[int(i_smp-i_inc/2)]+data[int(i_smp+i_inc/2)])+\
                            np.sqrt(d_sigma)*np.random.randn()
                i_smp = i_smp + i_inc
            mid_one = mid_one / 2
            d_sigma = np.power(0.5, 2*hurst)*d_sigma

            self.data.value = data[1: n-1]     # 舍去第1个点
            self.data.interval = inter

    def get_data(self):
        # assert self.data.data_value, "轮廓数据为None"
        return self.data


def test_main():
    mc = Mv2dCreator()

    # mc.create_data_wm(512,1.8,1,0.5)
    # mc.create_data_dft(1024, 1.3, 1, 1)
    mp = Mv2dParameter(mc.get_data())
    mc.create_data_mpd(1024, 1.5, 0.5, 0.2)
    data = mc.get_data()
    data.plot_data()



if __name__ == "__main__":
    test_main()


