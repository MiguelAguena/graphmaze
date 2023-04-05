from multiprocessing.managers import BaseManager
import multiprocessing
import os
import time
import serial
import json
import csv


class CustomManager(BaseManager):
    pass


class DirList():
    def __init__(self):
        self.list = []

    def set_list(self, values):
        self.list = list(values)

    def get_list(self):
        return self.list


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
            print(cur_list)
            last_val = cur_list


def arduino_pro(shared):
    ser = arduino_init()
    while True:
        data = arduino_read(ser)
        if data:
            shared.set_list(list(data.values()))


if __name__ == '__main__':
    CustomManager.register('DirList', DirList)
    with CustomManager() as manager:
        shared = manager.DirList()

        ard_comm = multiprocessing.Process(
            target=arduino_pro, name="arduino_comm", args=(shared,))
        ard_pr = multiprocessing.Process(
            target=arduino_print, name="arduino_print", args=(shared,))
        ard_comm.start()
        ard_pr.start()
        ard_comm.join()
