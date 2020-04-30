# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/30 下午12:50
@file: __init__.py.py
@desc: 
"""


def func3(num=1):
    def func2(func):
        def f(**kwargs):
            out = func(**kwargs)
            if num == 1:
                q = out + 3
            else:
                q = out[0] + 3
            if num == 1:
                return q
            else:
                return (q, *out[1:])

        return f
    return func2



def func1(func):
    def f(num='888888', **kwargs):
        return func(num=num, **kwargs)
    return f

@func1
@func3(num=3)
def func(num=0):
    print(num)
    return 1, 2, 3

@func1
@func3()
def func4(num=1):
    print(num)
    return 1


if __name__ == "__main__":
    a = func()
    a = func4()
    print("hhh")
