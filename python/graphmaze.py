from enum import Enum
import math
import os
import random
import sys
import game


class MazeEntity:
    def __init__(self, visited: bool = False, parent: game.Container = None) -> None:
        self.parent = parent
        self.visual_entity: game.Component = None
        self.set_visited(visited)
        self.color = "black"

    def link_parent(self, parent):
        self.visual_entity.add_parent(parent)

    def unlink_parent(self):
        if self.visual_entity:
            self.visual_entity.remove_parent()

    def set_color(self, color):
        self.color = color
        if self.visual_entity:
            self.visual_entity.set_color(color)

    def set_visited(self, visited=True):
        self.visited = visited
        if self.visual_entity:
            self.visual_entity.set_transparent(not visited)


class MazeDirection(Enum):
    DOWN = 0
    LEFT = 1
    UP = 2
    RIGHT = 3


class MazeRoom(MazeEntity):
    def __init__(self, code, pos: tuple[int], visited: bool = False, parent: game.Container = None) -> None:
        # pos: (col, line)s
        super().__init__(visited, parent)
        self.code = code
        self.pos = pos

        self.visual_entity = game.Container(
            ((4*pos[0]+1)/32, (4*pos[1]+1)/16), (1/16, 1/8), parent=parent)
        self.visual_entity.set_color('room')
        self.visual_entity.set_width(1)

        square_text = game.TextComponent(
            str(code+1), (0.5, 0), game.BoxAlignment.TOPCENTER, self.visual_entity)
        square_text.set_color('room')
        square_text.set_font(
            size=30, mode=game.FontSizeMode.PERCENTAGEPARENTH)
        self.text_ent = square_text

        self.player_img = game.ImageComponent((0, 0.5), 0.45, os.path.join(
            r"D:\USP\5_periodo\Labdig\Projeto\graphmaze\python\imgs", "player_light.png"), parent=self.visual_entity, alignment=game.BoxAlignment.TOPLEFT)

        self.monster_img = game.ImageComponent((0.5, 0.5), 0.45, os.path.join(
            r"D:\USP\5_periodo\Labdig\Projeto\graphmaze\python\imgs", "monster.png"), parent=self.visual_entity, alignment=game.BoxAlignment.TOPLEFT)

        self.set_has_player(False)
        self.set_has_monster(False)

        self.paths = {
            MazeDirection.UP: None,
            MazeDirection.DOWN: None,
            MazeDirection.LEFT: None,
            MazeDirection.RIGHT: None,
        }

        self.set_visited(visited)

    def set_has_player(self, has_player: bool = True):
        self.player_img.set_transparent(not has_player)
        self.has_player = has_player

    # @classmethod
    # def get_lane_point(cls, pos):

    def get_door_point(self, direction: MazeDirection):
        tl_point = self.visual_entity.get_tl_point()
        size = self.visual_entity.get_size()
        if direction == MazeDirection.RIGHT:
            return (tl_point[0]+size[0], tl_point[1]+(3*size[1]/4))
        if direction == MazeDirection.LEFT:
            return (tl_point[0], tl_point[1]+(size[1]/4))
        if direction == MazeDirection.UP:
            return (tl_point[0]+(3 * size[0]/4), tl_point[1])
        if direction == MazeDirection.DOWN:
            return (tl_point[0]+(size[0]/4), tl_point[1] + size[1])

    def add_path(self, dir: MazeDirection, room, path):
        if self.paths[dir] and isinstance(self.path[dir][3], game.CircleComponent):
            self.path[dir][3].remove_parent()
        path_circle: game.CircleComponent = path.get_circle(room)
        path_circle.add_parent(self.visual_entity)
        if dir == MazeDirection.UP:
            path_circle.set_center((0.5, -0.05))
        if dir == MazeDirection.DOWN:
            path_circle.set_center((0.5, 1.05))
        if dir == MazeDirection.LEFT:
            path_circle.set_center((-0.05, 0.5))
        if dir == MazeDirection.RIGHT:
            path_circle.set_center((1.05, 0.5))
        self.paths[dir] = (room, path, path_circle)

    def get_path(self, dir):
        return self.paths[dir]

    def set_has_monster(self, has_monster):
        self.monster_img.set_transparent(not has_monster)
        self.has_monster = has_monster


class MazePath(MazeEntity):
    def __init__(self, room_from: MazeRoom, dir_from: MazeDirection, room_to: MazeRoom, dir_to: MazeDirection,
                 visited: bool = False, parent: game.Container = None) -> None:
        super().__init__(visited, parent)
        self.room_from = room_from
        self.dir_from = dir_from
        self.room_to = room_to
        self.dir_to = dir_to
        # self.visual_entity = game.SegsLineComponent([self.room_from.get_door_point(self.dir_from), self.room_from.get_door_point(self.dir_to)])
        self._calculate_points()
        self.visual_entity = game.SegsLineComponent(self.points)
        self.start_circle: game.CircleComponent = game.CircleComponent(
            (0.5, 0.5), (0.05))
        self.end_circle: game.CircleComponent = game.CircleComponent(
            (0.5, 0.5), (0.05))
        self.start_circle.set_color("path_circle")
        self.end_circle.set_color("path_circle")
        self.room_from.add_path(dir_from, room_to, self)
        self.room_to.add_path(dir_to, room_from, self)
        self.set_visited(visited)

    def get_circle(self, room) -> game.CircleComponent:
        if room == self.room_from:
            return self.start_circle
        elif room == self.room_to:
            return self.end_circle
        return None

    def set_visited(self, visited=True):
        super().set_visited(visited)
        if hasattr(self, 'start_circle') and self.start_circle:
            self.start_circle.set_transparent(visited)
            self.end_circle.set_transparent(visited)

    def __str__(self) -> str:
        return f"{self.room_from.code+1}({self.dir_from.name}) -> {self.room_to.code+1}({self.dir_to.name})"

    def _calculate_points(self):
        self._calculate_lanes()

        def get_lane_coord(dir, num, factor):
            last_lane = 8
            if dir == 0:
                last_lane = 4
            if num == 0:
                lane_lims = (0, 1/(32 if dir == 1 else 16))
            elif num == last_lane:
                lane_lims = (1 - 1/(32 if dir == 1 else 16), 1)
            else:
                lane_lims = (-1/(32 if dir == 1 else 16) + num*(1/(8 if dir == 1 else 4)),
                             1/(32 if dir == 1 else 16) + num*(1/(8 if dir == 1 else 4)))
            return lane_lims[0] + ((lane_lims[1] - lane_lims[0]) * factor)
        points = []
        cur_point = self.room_from.get_door_point(self.dir_from)
        last_point = self.room_to.get_door_point(self.dir_to)
        points.append(cur_point)
        cur_dir = self.start_lane_dir
        for l in self.lanes:
            lane_coord = get_lane_coord(cur_dir, l, random.uniform(0.25, 0.75))
            nex_point = [0, 0]
            nex_point[int(not cur_dir)] = lane_coord
            nex_point[cur_dir] = cur_point[cur_dir]
            cur_point = tuple(nex_point)
            cur_dir = int(not cur_dir)
            points.append(cur_point)
        if len(self.lanes) != 0:
            nex_point = [0, 0]
            nex_point[cur_dir] = points[-1][cur_dir]
            nex_point[int(not cur_dir)] = last_point[int(not cur_dir)]
            points.append(tuple(nex_point))
        points.append(last_point)
        self.points = points
        # self.visual_entity = game.SegsLineComponent(points)

    def _calculate_lanes(self) -> list[tuple[int]]:
        def get_lane(pos, dir):
            if dir == MazeDirection.UP:
                return (pos[0] + 0.5, pos[1])
            elif dir == MazeDirection.DOWN:
                return (pos[0] + 0.5, pos[1] + 1)
            if dir == MazeDirection.LEFT:
                return (pos[0], pos[1] + 0.5)
            elif dir == MazeDirection.RIGHT:
                return (pos[0] + 1, pos[1] + 0.5)
        start_pos = get_lane(self.room_from.pos, self.dir_from)
        end_pos = get_lane(self.room_to.pos, self.dir_to)
        cur_dir = 0 if start_pos[0] % 1 == 0.5 else 1
        start_lane_dir = cur_dir
        cur_pos = start_pos
        # points = []
        lanes = []
        while cur_pos != end_pos:
            # points.append(cur_pos)
            lanes.append(cur_pos[int(not cur_dir)])
            if cur_pos[int(not cur_dir)] == end_pos[int(not cur_dir)]:
                nex_pos = end_pos
            else:
                nex_pos = [0, 0]
                nex_pos[int(not cur_dir)] = cur_pos[int(not cur_dir)]
                if cur_pos[cur_dir] < end_pos[cur_dir]:
                    nex_pos[cur_dir] = math.floor(end_pos[cur_dir])
                else:
                    nex_pos[cur_dir] = math.ceil(end_pos[cur_dir])
                nex_pos = tuple(nex_pos)
            assert cur_pos != nex_pos, "Not changing"
            cur_pos = nex_pos
            cur_dir = int(not cur_dir)
        # points.append(cur_pos)
        self.start_lane_dir = start_lane_dir
        self.lanes = lanes


class MazeMap:
    def __init__(self, distribution: tuple[tuple[int]], links: tuple[tuple[int, MazeDirection, int, MazeDirection]], player_pos=0) -> None:
        super().__init__()
        self.rooms_num: int = 32

        self.entities: list[MazeEntity] = list(
            map(lambda _: None, range(32)))
        saved_rooms = set()

        for n_col, col in enumerate(distribution):
            for n_line, room in enumerate(col):
                assert room not in saved_rooms, f"Distribution has repeated rooms {room}"
                new_room = MazeRoom(room,
                                    (n_col, n_line), visited=False)
                # if room == 0:
                #     self.player_room: MazeRoom = new_room
                new_room.set_color('room')
                # breakpoint()
                new_room.set_has_player(room == player_pos)
                self.entities[room] = new_room
                saved_rooms.add(room)
        self.parent = None
        self.player_room: MazeRoom = None
        self.monster_room: MazeRoom = None
        for link in links:
            new_link = MazePath(
                self.entities[link[0]], link[1], self.entities[link[2]], link[3], visited=False)
            new_link.set_color("path")
            self.entities.append(new_link)
            # print(new_link.get_points())

        # lanes = [cols_num+1, lines_num+1]
        # lanes = list(map(lambda n: list(map(lambda _: 0, range(n))), lanes))
        # print(lanes)

        # for link in self.entities[32:]:
        #     print(link.get_points())

    def unlink_parent(self):
        if self.parent:
            self.parent = None
            for ent in self.entities:
                ent.unlink_parent()

    def move_player_through(self, dir: MazeDirection):
        path_data = self.player_room.get_path(dir)
        print(self.player_room.paths)
        if path_data:
            path_data[0].set_visited(True)
            path_data[1].set_visited(True)
            self.player_room.set_has_player(False)
            self.player_room = path_data[0]
            self.player_room.set_has_player(True)

    def link_parent(self, parent: game.Container):
        self.parent = parent
        for ent in self.entities:
            ent.link_parent(parent)

    def move_player_state(self, state):
        if state[1] < 4:
            path_data = self.entities[state[2]].get_path(
                MazeDirection(state[1]))
            if path_data:
                path_data[1].set_visited(True)
        self.set_player_pos(state[2])

    def set_player_pos(self, pos):
        if self.player_room:
            self.player_room.set_has_player(False)
        self.player_room = self.entities[pos]
        self.player_room.set_has_player(True)
        self.player_room.set_visited(True)

    def set_monster_pos(self, pos):
        if self.monster_room:
            self.monster_room.set_has_monster(False)
        self.monster_room = self.entities[pos]
        self.monster_room.set_has_monster(True)

    def clear(self):
        for ent in self.entities:
            ent.set_visited(False)


class GraphMaze:
    def __init__(self) -> None:
        self.running = False

        self.game_inst = game.Game()
        self.game_inst.set_background_color('background')
        game.Container.set_color_scheme({
            # 'primary': (239, 51, 64),
            # 'secondary': (241, 180, 32),
            # 'light': (255, 250, 224),
            # 'dark': (0, 12, 32)

            'room': (255, 250, 224),
            'black': (0, 0, 0),
            'background': (0, 12, 32),
            'side_container': (255, 250, 224),
            'side_container_title': (255, 250, 224),
            'path': (255, 250, 224),
            'monster_warning': (176, 63, 63),
            'warning_won': (130, 230, 94),
            'path_circle': (255, 250, 224)
        })

        self.main_container = game.Container(
            (1/20, 1/20), (13/20, 18/20), ratio=2, parent=self.game_inst.get_container())
        self.main_container.set_color('background')

        # test_segs = game.SegsLineComponent(
        #     [(0, 0), (0, 0.5), (1, 0.5), (1, 1)], main_container)
        # test_segs.set_color(color_scheme['light'])

        self.side_container = game.Container(
            (15/20, 1/20), (4/20, 18/20), parent=self.game_inst.get_container())
        self.side_container.set_color('side_container')
        self.side_container.set_width(2)

        title_box = game.TextComponent(
            "Graphmaze", (0.5, 0.01), game.BoxAlignment.TOPCENTER, self.side_container)
        title_box.set_color('side_container_title')
        title_box.set_font(size=15, mode=game.FontSizeMode.PERCENTAGEPARENTW)

        #  = game.TextComponent("O Monstro está na sala 32")
        self.monster_box = game.TextComponent(
            "Monstro está na sala 32", (0.5, 0.5), game.BoxAlignment.TOPCENTER, self.side_container)
        self.monster_box.set_color('side_container_title')
        self.monster_box.set_font(
            size=8, mode=game.FontSizeMode.PERCENTAGEPARENTW)

        self.monster_warning = game.TextComponent(
            "Fuja...", (0.5, 0.7), game.BoxAlignment.TOPCENTER, self.side_container)
        self.monster_warning.set_color('monster_warning')
        self.monster_warning.set_font(
            size=15, mode=game.FontSizeMode.PERCENTAGEPARENTW)

        self.monster_scare = game.ImageComponent((0.5, 0.5), 0.5, os.path.join(
            r"D:\USP\5_periodo\Labdig\Projeto\graphmaze\python\imgs", "monster.png"), parent=self.main_container, alignment=game.BoxAlignment.CENTER)
        self.monster_scare.set_is_priority(True)
        self.monster_scare.set_transparent(True)

        self.game_inst.get_container().rescale()
        self.map: MazeMap = None
        self.maps: list[MazeMap] = [

            MazeMap((
                (0, 1, 2, 3),
                (17, 16, 5, 4),
                (19, 15, 6, 8),
                (20, 21, 7, 18),
                (22, 23, 9, 14),
                (24, 25, 10, 12),
                (26, 28, 11, 13),
                (27, 29, 30, 31)
            ), ((5, MazeDirection.LEFT, 2, MazeDirection.RIGHT),
                (4, MazeDirection.LEFT, 3, MazeDirection.RIGHT),
                (8, MazeDirection.LEFT, 4, MazeDirection.RIGHT),
                (6, MazeDirection.LEFT, 5, MazeDirection.RIGHT),
                (7, MazeDirection.LEFT, 6, MazeDirection.RIGHT),
                (9, MazeDirection.LEFT, 7, MazeDirection.RIGHT),
                (10, MazeDirection.LEFT, 9, MazeDirection.RIGHT),
                (11, MazeDirection.LEFT, 10, MazeDirection.RIGHT),
                (13, MazeDirection.LEFT, 12, MazeDirection.RIGHT),
                (19, MazeDirection.LEFT, 17, MazeDirection.RIGHT),
                (20, MazeDirection.LEFT, 19, MazeDirection.RIGHT),
                (22, MazeDirection.LEFT, 20, MazeDirection.RIGHT),
                (23, MazeDirection.LEFT, 21, MazeDirection.RIGHT),
                (24, MazeDirection.LEFT, 22, MazeDirection.RIGHT),
                (25, MazeDirection.LEFT, 23, MazeDirection.RIGHT),
                (26, MazeDirection.LEFT, 24, MazeDirection.RIGHT),
                (28, MazeDirection.LEFT, 25, MazeDirection.RIGHT),
                (27, MazeDirection.LEFT, 26, MazeDirection.RIGHT),
                (29, MazeDirection.LEFT, 28, MazeDirection.RIGHT),
                (5, MazeDirection.DOWN, 4, MazeDirection.UP),
                (16, MazeDirection.DOWN, 5, MazeDirection.UP),
                (21, MazeDirection.DOWN, 7, MazeDirection.UP),
                (17, MazeDirection.DOWN, 16, MazeDirection.UP),
                (16, MazeDirection.RIGHT, 15, MazeDirection.LEFT),
                (1, MazeDirection.UP, 0, MazeDirection.DOWN),
                (2, MazeDirection.UP, 1, MazeDirection.DOWN),
                (3, MazeDirection.UP, 2, MazeDirection.DOWN),
                (18, MazeDirection.UP, 7, MazeDirection.DOWN),
                (14, MazeDirection.UP, 9, MazeDirection.DOWN),
                (12, MazeDirection.UP, 10, MazeDirection.DOWN),
                (13, MazeDirection.UP, 11, MazeDirection.DOWN),
                (21, MazeDirection.UP, 20, MazeDirection.DOWN),
                (28, MazeDirection.UP, 26, MazeDirection.DOWN),
                (30, MazeDirection.UP, 29, MazeDirection.DOWN),
                (31, MazeDirection.UP, 30, MazeDirection.DOWN)
                )),

            MazeMap(((0, 1, 3, 9), (2, 6, 7, 8), (4, 13, 10, 14), (5, 12, 11, 16),
                     (15, 22, 20, 18), (17, 24, 23, 25), (19, 30, 29, 26), (21, 28, 27, 31)), (
                    (2, MazeDirection.LEFT, 0, MazeDirection.RIGHT),
                    (4, MazeDirection.LEFT, 2, MazeDirection.RIGHT),
                    (9, MazeDirection.LEFT, 6, MazeDirection.RIGHT),
                    (10, MazeDirection.LEFT, 7, MazeDirection.RIGHT),
                    (9, MazeDirection.UP, 8, MazeDirection.RIGHT),
                    (12, MazeDirection.DOWN, 10, MazeDirection.RIGHT),
                    (15, MazeDirection.LEFT, 11, MazeDirection.RIGHT),
                    (13, MazeDirection.LEFT, 12, MazeDirection.RIGHT),
                    (16, MazeDirection.LEFT, 14, MazeDirection.RIGHT),
                    (19, MazeDirection.LEFT, 15, MazeDirection.RIGHT),
                    (18, MazeDirection.LEFT, 16, MazeDirection.RIGHT),
                    (20, MazeDirection.LEFT, 18, MazeDirection.RIGHT),
                    (21, MazeDirection.LEFT, 19, MazeDirection.RIGHT),
                    (24, MazeDirection.LEFT, 23, MazeDirection.RIGHT),
                    (25, MazeDirection.RIGHT, 24, MazeDirection.RIGHT),
                    (27, MazeDirection.LEFT, 26, MazeDirection.RIGHT),
                    (29, MazeDirection.UP, 27, MazeDirection.RIGHT),
                    (30, MazeDirection.LEFT, 28, MazeDirection.RIGHT),
                    (3, MazeDirection.DOWN, 0, MazeDirection.UP),
                    (5, MazeDirection.UP, 2, MazeDirection.UP),
                    (11, MazeDirection.UP, 10, MazeDirection.UP),
                    (17, MazeDirection.UP, 15, MazeDirection.UP),
                    (18, MazeDirection.UP, 16, MazeDirection.UP),
                    (22, MazeDirection.DOWN, 20, MazeDirection.UP),
                    (24, MazeDirection.DOWN, 23, MazeDirection.UP),
                    (28, MazeDirection.DOWN, 27, MazeDirection.UP),
                    (30, MazeDirection.RIGHT, 28, MazeDirection.UP),
                    (4, MazeDirection.RIGHT, 0, MazeDirection.LEFT),
                    (5, MazeDirection.LEFT, 1, MazeDirection.LEFT),
                    (9, MazeDirection.RIGHT, 8, MazeDirection.LEFT),
                    (13, MazeDirection.RIGHT, 12, MazeDirection.LEFT),
                    (25, MazeDirection.LEFT, 23, MazeDirection.LEFT),
                    (31, MazeDirection.LEFT, 28, MazeDirection.LEFT),
                    (1, MazeDirection.UP, 0, MazeDirection.DOWN),
                    (3, MazeDirection.UP, 1, MazeDirection.DOWN),
                    (6, MazeDirection.UP, 2, MazeDirection.DOWN),
                    (5, MazeDirection.DOWN, 4, MazeDirection.DOWN),
                    (7, MazeDirection.UP, 6, MazeDirection.DOWN),
                    (8, MazeDirection.UP, 7, MazeDirection.DOWN),
                    (9, MazeDirection.DOWN, 8, MazeDirection.DOWN),
                    (14, MazeDirection.UP, 10, MazeDirection.DOWN),
                    (23, MazeDirection.DOWN, 11, MazeDirection.DOWN),
                    (17, MazeDirection.DOWN, 15, MazeDirection.DOWN),
                    (18, MazeDirection.DOWN, 16, MazeDirection.DOWN),
                    (22, MazeDirection.UP, 20, MazeDirection.DOWN),
                    (26, MazeDirection.DOWN, 25, MazeDirection.DOWN),
                    (29, MazeDirection.DOWN, 27, MazeDirection.DOWN)
                    ))
        ]
        self.set_map(0)

    def set_map(self, map_id: int):
        if not hasattr(self, 'map_id') or self.map_id != map_id:
            self.map_id = map_id
            self._set_map_obj(self.maps[map_id])

    def set_monster_pos(self, mon_pos):
        self.monster_box.set_content(f"Monstro está na sala {mon_pos+1}")
        self.map.set_monster_pos(mon_pos)

    def set_mode(self, mode):
        self.monster_box.set_transparent(mode == 0)
        self.monster_warning.set_transparent(mode == 0)

    def _set_map_obj(self, map: MazeMap):

        if self.map:
            self.map.unlink_parent()
        self.map: MazeMap = map
        self.map.link_parent(self.main_container)
        self.game_inst.get_container().rescale()

    def set_lost(self, lost):
        if lost:
            self.monster_box.set_transparent(True)
            self.monster_warning.set_content("Perdeu")
            self.monster_scare.set_transparent(False)
        else:
            self.monster_scare.set_transparent(True)
            self.monster_warning.set_content("Fuja...")

    def set_won(self, won):
        if won:
            self.monster_warning.set_content("Escapou!")
            self.monster_warning.set_color("warning_won")
        else:
            self.monster_warning.set_color("monster_warning")

    def tick(self, delay: bool = False):
        return self.game_inst.tick(delay)

    def run(self):
        self.running = True
        c = 0
        while self.running:
            self.running = self.game_inst.tick(True)
            c += 1
            if c % 20 == 0:
                self.map.move_player_through(
                    MazeDirection(random.randint(0, 3)))

    def change_state(self, cur_state):
        #   0   mode
        #   1   arrival
        #   2   jogador
        #   3   monstro
        #   4   mapa
        #   5   perdeu
        if cur_state[1] == 7:
            for m in self.maps:
                m.clear()
            self.set_map(0)
        elif cur_state[1] == 6:
            self.set_map(cur_state[4])
        self.map.move_player_state(cur_state)
        self.set_monster_pos(cur_state[3])
        self.set_mode(cur_state[0])
        self.set_lost(cur_state[5])
        self.set_won(cur_state[2] == 31)
