# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/16 上午3:06
@file: DistanceService.py
@desc: 
"""

import math

import numpy as np

from application import app


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

    def filterNearbyGoods(self, goods_list=None, found_location=""):
        """
        从匹配的列表中筛选出距离500m内的
        :param goods_list: [{id, lng, lat}, {id,lng,lat}]
        :param found_location: "上海市黄浦区南京西路399号###上海明天广场JW万豪酒店###31.23038###121.4697"
        :return: [] 符合距离条件的物品
        """
        found_gps = found_location.split("###")[-2:]
        ret_list = []
        for item in goods_list:
            lng2 = item.get('lng')
            lat2 = item.get('lat')
            if not lng2 or not lat2:
                # 失主不知道丢哪里了
                ret_list.append(item)
                continue
            distance = self.calSimplifyDistance(lng1=eval(found_gps[1]), lat1=eval(found_gps[0]),
                                                lng2=eval(str(lng2)), lat2=eval(str(lat2)))
            app.logger.warn('物品' + str(item.get('id')) + '距离捡到的物品距离为: ' + str(distance))
            if distance < 150:
                # 直线距离300m内的才算数
                ret_list.append(item)
        return ret_list


if __name__ == "__main__":
    pass
