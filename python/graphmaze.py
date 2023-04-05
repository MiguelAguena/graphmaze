from enum import Enum
import math
import os
import random
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

        self.player_img = game.ImageContainer((0.5, 0.5), 0.45, os.path.join(
            r"D:\USP\5_periodo\Labdig\Projeto\graphmaze\python\imgs", "player_light.png"), parent=self.visual_entity, alignment=game.BoxAlignment.TOPCENTER)

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
        self.paths[dir] = (room, path)

    def get_path(self, dir):
        return self.paths[dir]


class MazePath(MazeEntity):
    def __init__(self, room_from: MazeRoom, dir_from: MazeDirection, room_to: MazeRoom, dir_to: MazeDirection,
                 visited: bool = False, parent: game.Container = None) -> None:
        super().__init__(visited, parent)
        self.room_from = room_from
        self.dir_from = dir_from
        self.room_to = room_to
        self.dir_to = dir_to
        self.room_from.add_path(dir_from, room_to, self)
        self.room_to.add_path(dir_to, room_from, self)
        # self.visual_entity = game.SegsLineComponent([self.room_from.get_door_point(self.dir_from), self.room_from.get_door_point(self.dir_to)])
        self._calculate_points()
        self.visual_entity = game.SegsLineComponent(self.points)
        self.set_visited(visited)

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
                                    (n_col, n_line), visited=(room==0))
                if room == 0:
                    self.player_room: MazeRoom = new_room
                new_room.set_color('room')
                # breakpoint()
                new_room.set_has_player(room == player_pos)
                self.entities[room] = new_room
                saved_rooms.add(room)
        self.parent = None

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


class GraphMaze:
    def __init__(self) -> None:
        self.maps: list[MazeMap] = []
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
            'path': (255, 250, 224)
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

        self.game_inst.get_container().rescale()
        self.map: MazeMap = None

    def set_map(self, map: MazeMap):
        if self.map:
            self.map.unlink_parent()
        self.map : MazeMap = map
        self.map.link_parent(self.main_container)
        self.game_inst.get_container().rescale()

    def tick(self, delay: bool = False):
        self.game_inst.tick(delay)


    def run(self):
        self.running = True
        c = 0
        while self.running:
            self.running = self.game_inst.tick()
            # c += 1
            # if c% 10 == 0 and c > 200:
            #     self.map.move_player_through(MazeDirection(random.randint(0,3)))
            #     print("moved")