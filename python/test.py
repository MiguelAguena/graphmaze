import multiprocessing
import time


def add(ob):
    while True:
        ob.set_val(ob.val + 1)
        
        print("set to ",ob.val)
        time.sleep(3)


def sud(ob):
    while True:
        print(ob.val)
        time.sleep(3)


class Teste:
    def __init__(self) -> None:
        self.val = 0

    def set_val(self, val):
        self.val = val


if __name__ == '__main__':
    ob = Teste()
    ob.set_val(30)
    # p1 = multiprocessing.Process(name='p1', target=add, args=(ob, True))
    p1 = multiprocessing.Process(name='p2', target=add, args=(ob,))
    p = multiprocessing.Process(name='p', target=sud, args=(ob,))
    p1.start()
    p.start()
    # p2.start()
