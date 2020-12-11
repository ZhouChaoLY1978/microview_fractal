# -*- coding: utf-8 -*-
import numpy as np
from mv2d.mv_data2d import MvData2d

class Mv3dParameter(object):

    def __init__(self, data: MvData2d=None):
        self.data = data
        self.para_dict = {}

    def get_Sq(self, digits=4) -> float:
        data_value = self.data.value
        Sq = np.sqrt(np.mean(np.power(data_value, 2)))
        Sq = np.round(Sq, digits)
        self.para_dict.setdefault('Sq', Sq)
        return Sq

    def get_Sa(self, digits=4) -> float:
        data_value = self.data.value
        Sa = np.mean(np.abs(data_value))
        Sa = np.round(Sa, digits)
        self.para_dict.setdefault('Sa', Sa)
        return Sa

    def get_Ssk(self, digits=4) -> float:
        data_value = self.data.value
        Sq = self.get_Sq()
        h3 = np.power(data_value, 3)
        Ssk = np.mean(h3) / np.power(Sq, 3)
        Ssk = np.round(Ssk, digits)
        self.para_dict.setdefault('Ssk', Ssk)
        return Ssk

    def get_Sku(self, digits=4) -> float:
        data_value = self.data.value
        Sq = self.get_Sq()
        h4 = np.power(data_value, 4)
        Sku = np.mean(h4) / np.power(Sq, 4)
        Sku = np.round(Sku, digits)
        self.para_dict.setdefault('SKu', Sku)
        return Sku
