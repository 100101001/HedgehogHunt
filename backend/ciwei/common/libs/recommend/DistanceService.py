# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/12 上午1:36
@file: DistanceService.py
@desc: 
"""

import math

import numpy as np


class DistanceService:
    def __init__(self):
        """
        获得拟合函数
        """
        inv = 50 / 10000
        x = [10 + i * inv for i in range(10000)]
        y = [math.cos(i * math.pi / 180) for i in x]
        res = np.polyfit(x, y, 5)
        self.cos = np.poly1d(res)


    def calSimplifyDistance(self, lng1, lat1, lng2, lat2):

        """
        计算GPS间米制距离
        :param lng1:
        :param lat1:
        :param lng2:
        :param lat2:
        :return:
        """
        # 1) 三个参数
        dx = lng1 - lng2  # 经度差
        dy = lat1 - lat2  # 纬度差
        b = (lat1 + lat2) / 2  # 平均纬度

        # 角度转弧度值
        def toRadians(angle):
            return math.pi * angle / 180

        # 2) 计算东西方向距离和南北方向距离(单位：米)，东西距离采用三阶多项式
        # 夹角在一定范围内时,cos(x)可由泰勒多项式推导
        lx = 6367000.0 * toRadians(dx) * self.cos(b)
        # 夹角较小时 sin(x) ~ x
        ly = 6367000.0 * toRadians(dy)
        # 3) 用平面的矩形对角距离公式计算总距离
        return math.sqrt(lx * lx + ly * ly)

    # 上海市黄浦区南京西路399号###上海明天广场JW万豪酒店###31.23038###121.4697
    def filterNearbyGoods(self, goods_list=None, os_location=None):
        """
        从匹配的列表中筛选出距离500m内的
        :param goods_list: (1, )
        :param os_location:
        :return: [] 符合距离条件的物品
        """
        os_location = os_location.split("###")[-2:]
        ret_list = []
        for item in goods_list:
            location = item.location.split("###")[-2:]
            if self.calSimplifyDistance(lng1=os_location[1], lat1=os_location[0],
                                        lng2=location[1], lat2=location[0]) < 500:
                ret_list.append(item)
        return ret_list
