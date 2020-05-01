# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/28 下午7:48
@file: __init__.py
@desc:
"""


def func(a):
    return a+1

class B:
    def __init__(self, a):
        print(a)

class A:
    @staticmethod
    def func():
        return B

if __name__ == "__main__":
    a = A.func()("a")
    c = 1