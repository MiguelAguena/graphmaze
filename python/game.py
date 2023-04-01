from enum import Enum
import pygame


class Component():
    def __init__(self, parent=None):
        self.parent = parent
        if parent:
            parent.add_component(self)
        self.show = True
        self.transparent = False
        self.color = 'black'

    def set_color(self, color):
        self.color = pygame.Color(color)

    def set_show(self, show):
        self.show = show

    def set_transparent(self, is_transparent: bool = True):
        self.transparent = is_transparent


class BoxAlignment(Enum):
    TOPLEFT = 0
    TOPCENTER = 1
    TOPRIGHT = 2
    CENTERLEFT = 3
    CENTER = 4
    CENTERRIGHT = 5
    BOTTOMLEFT = 6
    BOTTOMCENTER = 7
    BOTTOMRIGHT = 8

    def get_offset(self):
        return ((self.value % 3)*0.5, ((self.value-(self.value % 3)) / 6))


class TextComponent(Component):
    def __init__(self, content: str, pos, alignment: BoxAlignment = BoxAlignment.TOPLEFT, parent=None):
        super().__init__(parent)
        self.content = content
        self.alignment = alignment
        self.set_font("Comic Sans MS", 12)
        self.pos = pos
        self.background = None

    def set_font(self, family=None, size=None):
        if family:
            self.font_family = family
        if size:
            self.font_size = size

    def set_content(self, content):
        self.content = content

    def set_background(self, background):
        self.background = background

    def rescale(self, screen):
        self.font = pygame.font.SysFont(self.font_family, self.font_size)
        txt_x, txt_y = self.font.size(self.content)
        align_offset_x, align_offset_y = self.alignment.get_offset()
        if self.parent:
            self.tl_point_px = (
                self.pos[0] * self.parent.children_cont.size_px[0] +
                self.parent.children_cont.tl_point_px[0] -
                (align_offset_x * txt_x),
                self.pos[1] * self.parent.children_cont.size_px[1] + self.parent.children_cont.tl_point_px[1] - (align_offset_y * txt_y))
        else:
            sc_x, sc_y = screen.get_size()
            self.tl_point_px = (
                self.pos[0] * sc_x - (align_offset_x * txt_x),
                self.pos[1] * sc_y - (align_offset_y * txt_y))
        # self.size = (txt_x, txt_y)

    def render(self, screen):
        txt_surface = self.font.render(
            self.content, True, self.color, self.background)
        screen.blit(source=txt_surface, dest=self.tl_point_px)


class SegmentComponent(Component):
    def __init__(self, start_point, end_point, parent=None):
        super().__init__(parent)
        self.start_point = start_point
        self.end_point = end_point

    def rescale(self, screen):
        sc_x, sc_y = screen.get_size()
        if self.parent:
            self.start_point_px = (
                self.start_point[0] * self.parent.children_cont.size_px[0] +
                self.parent.children_cont.tl_point_px[0],
                self.start_point[1] * self.parent.children_cont.size_px[1] + self.parent.children_cont.tl_point_px[1])

            self.end_point_px = (
                self.end_point[0] * self.parent.children_cont.size_px[0] +
                self.parent.children_cont.tl_point_px[0],
                self.end_point[1] * self.parent.children_cont.size_px[1] + self.parent.children_cont.tl_point_px[1])
        else:
            self.end_point_px = (
                self.end_point[0] * sc_x, self.end_point[1] * sc_y)
            self.start_point_px = (
                self.start_point[0] * sc_x,
                self.start_point[1] * sc_y)

    def render(self, screen):
        if self.show and not self.transparent:
            pygame.draw.line(screen, self.color,
                             self.start_point_px, self.end_point_px)


class SegsLineComponent(Component):
    def __init__(self, points: list[int], parent=False):
        super().__init__(parent)
        self.points = points

    def rescale(self, screen):
        sc_x, sc_y = screen.get_size()
        self.points_px = list(map(lambda p: (
            p[0] * self.parent.children_cont.size_px[0] +
            self.parent.children_cont.tl_point_px[0],
            p[1] * self.parent.children_cont.size_px[1] + self.parent.children_cont.tl_point_px[1]) if self.parent else (p[0] * sc_x, p[1] * sc_y), self.points))

    def render(self, screen):
        if self.show and not self.transparent:
            pygame.draw.lines(screen, self.color, False, self.points_px)


class AreaComponent(Component):
    def __init__(self, tl_point, size, parent=None):
        super().__init__(parent)
        self.tl_point = tl_point
        self.size = size
        self.color = "black"

    def rescale(self, screen):
        sc_x, sc_y = screen.get_size()
        if self.parent:
            self.tl_point_px = (
                self.tl_point[0] * self.parent.children_cont.size_px[0] +
                self.parent.children_cont.tl_point_px[0],
                self.tl_point[1] * self.parent.children_cont.size_px[1] + self.parent.children_cont.tl_point_px[1])
            self.size_px = (
                self.size[0] * self.parent.children_cont.size_px[0], self.size[1] * self.parent.children_cont.size_px[1])
        else:
            self.size_px = (self.size[0] * sc_x, self.size[1] * sc_y)
            self.tl_point_px = (
                self.tl_point[0] * sc_x, self.tl_point[1] * sc_y)


class RectComponent(AreaComponent):
    def __init__(self, tl_point, size, parent=None):
        super().__init__(tl_point, size, parent)
        self.width = 0

    def render(self, screen):
        if self.show and not self.transparent:
            pygame.draw.rect(screen, self.color, pygame.Rect(
                self.tl_point_px, self.size_px), width=self.width)

    def set_width(self, width):
        self.width = width


class Container(RectComponent):
    def __init__(self, tl_point, size, parent=None, ratio=None):
        super().__init__(tl_point, size, parent)
        self.children_cont = ChildContainer(parent=self, ratio=ratio)

    def add_component(self, child: Component):
        if not isinstance(child, ChildContainer):
            self.children_cont.add_component(child)

    def rescale(self, screen):
        super().rescale(screen)
        self.children_cont.rescale(screen)

    def set_color(self, color):
        self.children_cont.set_color(color)

    def set_width(self, width):
        self.children_cont.set_width(width)

    def render(self, screen):
        if self.show:
            self.children_cont.render(screen)

    def set_transparent(self, is_transparent: bool = True):
        super().set_transparent(is_transparent)
        self.children_cont.set_transparent(is_transparent)


class ChildContainer(RectComponent):
    def __init__(self, parent=False, ratio=False):
        super().__init__((0, 0), (1, 1), parent)
        self.ratio = ratio
        self.children = []

    def add_component(self, child: Component):
        self.children.append(child)

    def rescale(self, screen):
        if self.ratio:
            if (self.parent.size_px[0] / self.parent.size_px[1]) > self.ratio:
                self.size_px = (
                    self.parent.size_px[1] * self.ratio, self.parent.size_px[1])
                self.tl_point_px = (self.parent.tl_point_px[0] + (
                    self.parent.size_px[0] - self.parent.size_px[1] * self.ratio)/2, self.parent.tl_point_px[1])
            else:
                self.size_px = (
                    self.parent.size_px[0], self.parent.size_px[0] / self.ratio)
                self.tl_point_px = (self.parent.tl_point_px[0], self.parent.tl_point_px[1] + (
                    self.parent.size_px[1] - self.parent.size_px[0] / self.ratio)/2)
        else:
            self.size_px = self.parent.size_px
            self.tl_point_px = self.parent.tl_point_px

        for child in self.children:
            child.rescale(screen)

    def render(self, screen):
        super().render(screen)
        if self.show:
            for child in self.children:
                child.render(screen)


class Game:

    def __init__(self, containers):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (1600, 900), flags=pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        # self.dt = 0
        self.containers = containers
        self.background_color = "black"
        pygame.font.init()
        self._resize_screen()

    def set_background_color(self, background_color):
        self.background_color = background_color
        self._resize_screen()

    def tick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.WINDOWRESIZED:
                self._resize_screen()

        self._verify_movement()

        self.screen.fill(self.background_color)
        self._render()

        self.clock.tick(60)
        # self.dt = self.clock.tick(60) / 1000

        return True

    def apply_change(self):
        self._render()

    def _resize_screen(self):
        self.screen.fill(self.background_color)
        self._update_containers()

    def _update_containers(self):
        for c in self.containers:
            c.rescale(self.screen)

    def _render(self):
        for container in self.containers:
            container.render(self.screen)
        pygame.display.flip()

    def _verify_movement(self):
        keys = pygame.key.get_pressed()
