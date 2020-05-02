

class A:
    id= 1
    def sr(self, a):
        self.id= a


if __name__ == "__main__":
    a = A()
    b= A()
    a.__dict__ = {'id': 3}

    b.__dict__ = {'id': 5}
    a.sr(4)
    c = A.id
    A.id = 4
    c = A()
    d = A()
    print('')