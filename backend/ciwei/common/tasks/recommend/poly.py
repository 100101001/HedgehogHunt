# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/12 上午1:44
@file: poly.py
@desc: 
"""
import math

import numpy as np

if __name__ == "__main__":
    inv = 50 / 10000
    x = [10 + i * inv for i in range(10000)]
    y = [math.cos(i * math.pi / 180) for i in x]
    res = np.polyfit(x, y, 5)
    cos = np.poly1d(res)
    b = cos(40)