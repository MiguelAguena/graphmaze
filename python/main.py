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
            print(data)
            shared.set_list(list(data.values()))


def game_pro(shared):

    distribution = ((0, 1, 3, 9), (2, 6, 7, 8), (4, 13, 10, 14), (5, 12, 11, 16),
                    (15, 22, 20, 18), (17, 24, 23, 25), (19, 30, 29, 26), (21, 28, 27, 31))

    links = (
        (2, graphmaze.MazeDirection.LEFT, 0, graphmaze.MazeDirection.RIGHT),
        (4, graphmaze.MazeDirection.LEFT, 2, graphmaze.MazeDirection.RIGHT),
        (9, graphmaze.MazeDirection.LEFT, 6, graphmaze.MazeDirection.RIGHT),
        (10, graphmaze.MazeDirection.LEFT, 7, graphmaze.MazeDirection.RIGHT),
        (9, graphmaze.MazeDirection.UP, 8, graphmaze.MazeDirection.RIGHT),
        (12, graphmaze.MazeDirection.DOWN, 10, graphmaze.MazeDirection.RIGHT),
        (15, graphmaze.MazeDirection.LEFT, 11, graphmaze.MazeDirection.RIGHT),
        (13, graphmaze.MazeDirection.LEFT, 12, graphmaze.MazeDirection.RIGHT),
        (16, graphmaze.MazeDirection.LEFT, 14, graphmaze.MazeDirection.RIGHT),
        (19, graphmaze.MazeDirection.LEFT, 15, graphmaze.MazeDirection.RIGHT),
        (18, graphmaze.MazeDirection.LEFT, 16, graphmaze.MazeDirection.RIGHT),
        (20, graphmaze.MazeDirection.LEFT, 18, graphmaze.MazeDirection.RIGHT),
        (21, graphmaze.MazeDirection.LEFT, 19, graphmaze.MazeDirection.RIGHT),
        (24, graphmaze.MazeDirection.LEFT, 23, graphmaze.MazeDirection.RIGHT),
        (25, graphmaze.MazeDirection.RIGHT, 24, graphmaze.MazeDirection.RIGHT),
        (27, graphmaze.MazeDirection.LEFT, 26, graphmaze.MazeDirection.RIGHT),
        (29, graphmaze.MazeDirection.UP, 27, graphmaze.MazeDirection.RIGHT),
        (30, graphmaze.MazeDirection.LEFT, 28, graphmaze.MazeDirection.RIGHT),
        (3, graphmaze.MazeDirection.DOWN, 0, graphmaze.MazeDirection.UP),
        (5, graphmaze.MazeDirection.UP, 2, graphmaze.MazeDirection.UP),
        (11, graphmaze.MazeDirection.UP, 10, graphmaze.MazeDirection.UP),
        (17, graphmaze.MazeDirection.UP, 15, graphmaze.MazeDirection.UP),
        (18, graphmaze.MazeDirection.UP, 16, graphmaze.MazeDirection.UP),
        (22, graphmaze.MazeDirection.DOWN, 20, graphmaze.MazeDirection.UP),
        (24, graphmaze.MazeDirection.DOWN, 23, graphmaze.MazeDirection.UP),
        (28, graphmaze.MazeDirection.DOWN, 27, graphmaze.MazeDirection.UP),
        (30, graphmaze.MazeDirection.RIGHT, 28, graphmaze.MazeDirection.UP),
        (4, graphmaze.MazeDirection.RIGHT, 0, graphmaze.MazeDirection.LEFT),
        (5, graphmaze.MazeDirection.LEFT, 1, graphmaze.MazeDirection.LEFT),
        (9, graphmaze.MazeDirection.RIGHT, 8, graphmaze.MazeDirection.LEFT),
        (13, graphmaze.MazeDirection.RIGHT, 12, graphmaze.MazeDirection.LEFT),
        (25, graphmaze.MazeDirection.LEFT, 23, graphmaze.MazeDirection.LEFT),
        (31, graphmaze.MazeDirection.LEFT, 28, graphmaze.MazeDirection.LEFT),
        (1, graphmaze.MazeDirection.UP, 0, graphmaze.MazeDirection.DOWN),
        (3, graphmaze.MazeDirection.UP, 1, graphmaze.MazeDirection.DOWN),
        (6, graphmaze.MazeDirection.UP, 2, graphmaze.MazeDirection.DOWN),
        (5, graphmaze.MazeDirection.DOWN, 4, graphmaze.MazeDirection.DOWN),
        (7, graphmaze.MazeDirection.UP, 6, graphmaze.MazeDirection.DOWN),
        (8, graphmaze.MazeDirection.UP, 7, graphmaze.MazeDirection.DOWN),
        (9, graphmaze.MazeDirection.DOWN, 8, graphmaze.MazeDirection.DOWN),
        (14, graphmaze.MazeDirection.UP, 10, graphmaze.MazeDirection.DOWN),
        (23, graphmaze.MazeDirection.DOWN, 11, graphmaze.MazeDirection.DOWN),
        (17, graphmaze.MazeDirection.DOWN, 15, graphmaze.MazeDirection.DOWN),
        (18, graphmaze.MazeDirection.DOWN, 16, graphmaze.MazeDirection.DOWN),
        (22, graphmaze.MazeDirection.UP, 20, graphmaze.MazeDirection.DOWN),
        (26, graphmaze.MazeDirection.DOWN, 25, graphmaze.MazeDirection.DOWN),
        (29, graphmaze.MazeDirection.DOWN, 27, graphmaze.MazeDirection.DOWN)
    )

    maze = graphmaze.GraphMaze()
    map1 = graphmaze.MazeMap(distribution, links)
    maze.set_map(map1)
    cur_list = shared.get_list()
    last_val = []
    while True:
        cur_list = shared.get_list()
        if cur_list != last_val:
            map1.move_player_state(cur_list)
        last_val = cur_list
        maze.tick(True)


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
