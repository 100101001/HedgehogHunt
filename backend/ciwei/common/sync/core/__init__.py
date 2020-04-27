# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/26 下午3:10
@file: __init__.py.py
@desc: 
"""


def func(*args, b=1):
    for i in args:
        print(i)
    print("b.{}".format(b))


if __name__ == '__main__':
    func(1, b=5)
