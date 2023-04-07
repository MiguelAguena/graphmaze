import serial
import json
from enum import Enum
import time
import game
import graphmaze
import multiprocessing
from multiprocessing.managers import BaseManager


class CustomManager(BaseManager):
    pass


class DirList():
    def __init__(self):
        self.list = []
        self.running = True

    def set_list(self, values):
        self.list = list(values)

    def get_list(self):
        return self.list

    def set_running(self, running):
        self.running = running

    def get_running(self):
        return self.running


def arduino_init():
    port = "COM5"
    ser = serial.Serial(port, 9600, timeout=2)
    return ser


def arduino_read(ser):
    read_val_str = ser.readline().decode()
    if read_val_str and read_val_str != "\r\n":
        data = json.loads(read_val_str)
        return data
    else:
        return False


def arduino_print(shared):
    last_val = []
    while True:
        cur_list = shared.get_list()
        if cur_list != last_val:
            last_val = cur_list


def arduino_pro(shared):
    try:
        ser = arduino_init()
        while shared.get_running():
            data = arduino_read(ser)
            if data:
                shared.set_list(list(data.values()))
    except Exception as e:
        print(e)
    finally:
        shared.set_running(False)


def game_pro(shared):
    maze = graphmaze.GraphMaze()
    cur_list = shared.get_list()
    last_val = []
    try:
        while shared.get_running() and maze.tick(True):
            cur_list = shared.get_list()
            if cur_list != last_val:
                maze.change_state(cur_list)
            last_val = cur_list
    except Exception as e:
        print(e)
    finally:
        shared.set_running(False)


if __name__ == '__main__':

    # color_scheme = {
    #     'primary': (239, 51, 64),
    #     'secondary': (241, 180, 32),
    #     'light': (255, 250, 224),
    #     'dark': (0, 12, 32)
    # }

    # maze.run()
    CustomManager.register('DirList', DirList)
    with CustomManager() as manager:
        shared = manager.DirList()
        ard_comm = multiprocessing.Process(
            target=arduino_pro, name="arduino_comm", args=(shared,))
        game_pro_inst = multiprocessing.Process(
            target=game_pro, name="game_pro", args=(shared,))
        ard_comm.start()
        game_pro_inst.start()
        ard_comm.join()
