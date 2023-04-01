import serial
import json
from enum import Enum
import time
import game


class Move(Enum):
    RESET = 7
    RESTART = 4
    DIREITA = 3
    CIMA = 2
    ESQUERDA = 1
    BAIXO = 0


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


color_scheme = {
    'primary': (239, 51, 64),
    'secondary': (241, 180, 32),
    'light': (255, 250, 224),
    'dark': (0, 12, 32)
}

if __name__ == '__main__':
    # arduino = arduino_init()
    # while True:
    #     for i in range(100):
    #         time.sleep(0.001)
    #         print(f"\r{i}", end="")
    #         if True:
    #             data = arduino_read(arduino)
    #             if data:
    #                 print(f"\r{data}")

    main_container = game.Container(
        (1/20, 1/20), (13/20, 18/20), ratio=2)
    main_container.set_transparent()
    # main_container.set_color(color_scheme['primary'])

    squares = []
    for x in range(8):
        for y in range(4):
            in_square = game.Container(
                ((4*x+3)/36, (4*y+3)/20), (1/18, 1/10), parent=main_container)
            in_square.set_color(color_scheme['light'])
            in_square.set_width(1)
            square_text = game.TextComponent(
                str(x*4+y), (0.5, 0.5), game.BoxAlignment.CENTER, in_square)
            square_text.set_color(color_scheme['light'])
            squares.append(in_square)

    test_segs = game.SegsLineComponent(
        [(0, 0), (0, 0.5), (1, 0.5), (1, 1)], main_container)
    test_segs.set_color(color_scheme['light'])

    # in_square = game.RectComponent((0,0), (1,1/2), parent=main_container)

    # in_square = game.RectComponent(
    #     (1/16, 1/8), (1/4, 1/2), parent=main_container)
    # in_square.set_color("black")

    side_container = game.Container(
        (15/20, 1/20), (4/20, 18/20))
    side_container.set_color(color_scheme['light'])

    title_box = game.TextComponent(
        "Graphmaze", (0.5, 0.01), game.BoxAlignment.TOPCENTER, side_container)
    title_box.color = color_scheme['dark']
    title_box.set_font(size=36)

    containers = [main_container, side_container]

    game_inst = game.Game(containers)
    game_inst.set_background_color(color_scheme['dark'])
    running = True

    c = 0
    while running:
        running = game_inst.tick()
        if c % 10 == 0:
            squares[(c//10) % 32].set_show(False)
            squares[(c//10 + 31) % 32].set_show(True)
        c += 1
