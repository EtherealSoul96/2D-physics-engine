
from time import time

t0 = time()
def time_flag():
    global t0
    t1 = time()
    t2 = t1 - t0
    t0 = t1
    return t2

def print_time_flag(text=""):
    print(str(text), time_flag())


def rl(l):
    return range(len(l))

def print_list(l):
    for e in l:
        print(e)

def avg(l):
    return sum(l)/len(l)

class CircularList(list):
    def __init__(self, l):
        self.length = len(l)
        super().__init__(l)

    def __getitem__(self, item):
        return super().__getitem__(item % self.length)

    def __setitem__(self, key, value):
        super().__setitem__(key % len(self), value)

def my_sum(l):

    result = l[0]
    for e in l[1:]:
        result += e
    return result

def my_avg(l):
    return my_sum(l) / len(l)

def sign(n):
    if n > 0:
        return 1
    if n < 0:
        return -1
    return 0

def vector_list_to_normal_list(l):
    l2 = []
    for e in l:
        l2.append(e.x)
        l2.append(e.y)
    return l2

