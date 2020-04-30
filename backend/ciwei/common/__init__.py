# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2019/12/11 下午2:55
@file: __init__.py.py
@desc:
"""


def func(*member_Id, a=None, **kwargs):
    for i in member_Id:
        if i == 1:
            i = 2
        print(i)
    print(a)
    print(str(member_Id))
def warp(*args, **kwargs):
    func(*args, **kwargs)

class A:
    @staticmethod
    def _pri(a):
        print(a)

class B(A):
    @classmethod
    def p(cls):
        super()._pri("h")


if __name__ == '__main__':
    #warp([1,2,3,4],"hh", b="hh")
    B.p()