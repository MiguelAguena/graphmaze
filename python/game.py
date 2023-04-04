from enum import Enum
import pygame


class Component():
    __color_scheme = {
        'black': (0, 0, 0)
    }

    @classmethod
    def set_color_scheme(cls, color_scheme):
        for key in color_scheme:
            cls.__color_scheme[key] = color_scheme[key]

    @classmethod
    def get_color_scheme_value(cls, color_code):
        return cls.__color_scheme[color_code]

    def __init__(self, parent=None):
        self.transparent = False
        self.color = 'black'
        self.add_parent(parent)

    def set_color(self, color):
        self.color = color

    def get_color(self):
        return pygame.Color(Container.__color_scheme[self.color])

    def set_transparent(self, is_transparent: bool = True):
        # if is_transparent:
        # breakpoint()
        self.transparent = is_transparent

    def get_screen(self):
        if isinstance(self.parent, Component):
            return self.parent.get_screen()
        else:
            return self.parent

    def add_parent(self, parent):
        self.remove_parent()
        self.parent: Container = parent
        if isinstance(self.parent, Component):
            parent.add_component(self)

    def remove_parent(self):
        if hasattr(self, 'parent') and self.parent:
            self.parent.unlink_child(self)
            self.parent = None


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


class FontSizeMode(Enum):
    ABSOLUTE = 0
    PERCENTAGEPARENTW = 1
    PERCENTAGEPARENTH = 2


class TextComponent(Component):
    def __init__(self, content: str, pos, alignment: BoxAlignment = BoxAlignment.TOPLEFT, parent=None):
        super().__init__(parent)
        self.content = content
        self.alignment = alignment
        self.set_font("Comic Sans MS", 12)
        self.pos = pos
        self.background = None
        self.font_size_mode = FontSizeMode.ABSOLUTE

    def set_font(self, family=None, size=None, mode: FontSizeMode = None):
        if family:
            self.font_family = family
        if size:
            self.font_size = size
        if mode:
            self.font_size_mode = mode

    def set_content(self, content):
        self.content = content

    def set_background(self, background):
        self.background = background

    def rescale(self):
        if self.font_size_mode == FontSizeMode.PERCENTAGEPARENTW:
            calc_font_size = self.font_size * \
                self.parent.children_cont.size_px[0] / 100
        elif self.font_size_mode == FontSizeMode.PERCENTAGEPARENTH:
            calc_font_size = self.font_size * \
                self.parent.children_cont.size_px[1] / 100
        else:
            calc_font_size = self.font_size
        self.font = pygame.font.SysFont(
            self.font_family, int(round(calc_font_size)))
        txt_x, txt_y = self.font.size(self.content)
        align_offset_x, align_offset_y = self.alignment.get_offset()
        if self.parent:
            self.tl_point_px = (
                self.pos[0] * self.parent.children_cont.size_px[0] +
                self.parent.children_cont.tl_point_px[0] -
                (align_offset_x * txt_x),
                self.pos[1] * self.parent.children_cont.size_px[1] + self.parent.children_cont.tl_point_px[1] - (align_offset_y * txt_y))
        else:
            sc_x, sc_y = self.get_screen().get_size()
            self.tl_point_px = (
                self.pos[0] * sc_x - (align_offset_x * txt_x),
                self.pos[1] * sc_y - (align_offset_y * txt_y))
        # self.size = (txt_x, txt_y)

    def render(self):
        if not self.transparent:
            txt_surface = self.font.render(
                self.content, True, self.get_color(), self.background)
            self.get_screen().blit(source=txt_surface, dest=self.tl_point_px)


class SegmentComponent(Component):
    def __init__(self, start_point, end_point, parent=None):
        super().__init__(parent)
        self.start_point = start_point
        self.end_point = end_point

    def rescale(self):
        sc_x, sc_y = self.get_screen().get_size()
        if isinstance(self.parent, Component):
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

    def render(self):
        if not self.transparent:
            pygame.draw.line(self.get_screen(), self.get_color(),
                             self.start_point_px, self.end_point_px)


class SegsLineComponent(Component):
    def __init__(self, points: list[tuple[int]], parent=False):
        super().__init__(parent)
        self.points = points

    def rescale(self):
        sc_x, sc_y = self.get_screen().get_size()
        self.points_px = list(map(lambda p: (
            p[0] * self.parent.children_cont.size_px[0] +
            self.parent.children_cont.tl_point_px[0],
            p[1] * self.parent.children_cont.size_px[1] + self.parent.children_cont.tl_point_px[1]) if self.parent else (p[0] * sc_x, p[1] * sc_y), self.points))

    def render(self):
        if not self.transparent:
            pygame.draw.lines(self.get_screen(), self.get_color(),
                              False, self.points_px)

    def set_points(self, points):
        self.points = points
        self.rescale()


class AreaComponent(Component):
    def __init__(self, tl_point, size, parent=None):
        super().__init__(parent)
        self.tl_point = tl_point
        self.size = size
        self.color = "black"

    def rescale(self):
        sc_x, sc_y = self.get_screen().get_size()
        if isinstance(self.parent, Component):
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

    def get_tl_point(self):
        return self.tl_point

    def get_size(self):
        return self.size


class RectComponent(AreaComponent):
    def __init__(self, tl_point, size, parent=None):
        super().__init__(tl_point, size, parent)
        self.width = 0

    def render(self):
        if not self.transparent:
            pygame.draw.rect(self.get_screen(), self.get_color(), pygame.Rect(
                self.tl_point_px, self.size_px), width=self.width)

    def set_width(self, width):
        self.width = width


class Container(RectComponent):
    def __init__(self, tl_point, size, parent=None, ratio=None):
        self.children_cont = ChildContainer(parent=self, ratio=ratio)
        super().__init__(tl_point, size, parent)

    def add_component(self, child: Component):
        if not isinstance(child, ChildContainer):
            self.children_cont.add_component(child)
        # self.rescale()

    def unlink_children(self):
        self.children_cont.unlink_children()

    def unlink_child(self, child):
        self.children_cont.unlink_child(child)

    def rescale(self):
        super().rescale()
        # if self.children_cont:
        self.children_cont.rescale()

    def set_color(self, color):
        self.children_cont.set_color(color)

    def set_width(self, width):
        self.children_cont.set_width(width)

    def render(self):
        # if not self.transparent:
        self.children_cont.render()

    def set_transparent(self, is_transparent: bool = True):
        super().set_transparent(is_transparent)
        if hasattr(self, 'children_cont') and self.children_cont:
            self.children_cont.set_transparent(is_transparent)


class ChildContainer(RectComponent):
    def __init__(self, parent=False, ratio=False):
        super().__init__((0, 0), (1, 1), parent)
        self.ratio = ratio
        self.children: list[Component] = []

    def add_component(self, child: Component):
        self.children.append(child)
        # child.set_transparent(self.transparent)

    def unlink_children(self):
        for c in self.children:
            c.remove_parent()

    def unlink_child(self, child):
        self.children.remove(child)

    def rescale(self):
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
            child.rescale()

    def render(self):
        super().render()
        if not self.transparent:
            for child in self.children:
                child.render()

    def set_transparent(self, is_transparent: bool = True):
        super().set_transparent(is_transparent)
        # for child in self.children:
        #     child.set_transparent(is_transparent)


class ImageContainer(Component):
    def __init__(self, pos, width, img_path: str, alignment: BoxAlignment = BoxAlignment.TOPLEFT, parent=None):
        super().__init__(parent)
        self.alignment = alignment
        self.pos = pos
        self.image = pygame.image.load(img_path)
        self.width = width

    def rescale(self):
        align_offset_x, align_offset_y = self.alignment.get_offset()
        img_x, img_y = self.image.get_size()
        if self.parent:
            self.scale = self.parent.children_cont.size_px[0] * self.width / img_x
            img_y *= self.scale
            img_x = self.parent.children_cont.size_px[0] * self.width
            self.tl_point_px = (
                self.pos[0] * self.parent.children_cont.size_px[0] +
                self.parent.children_cont.tl_point_px[0] -
                (align_offset_x * img_x),
                self.pos[1] * self.parent.children_cont.size_px[1] + self.parent.children_cont.tl_point_px[1] - (align_offset_y * img_y))
        else:
            sc_x, sc_y = self.get_screen().get_size()
            self.scale = sc_x * self.width / img_x
            img_y *= self.scale
            img_x = sc_x * self.width
            self.tl_point_px = (
                self.pos[0] * sc_x - (align_offset_x * img_x),
                self.pos[1] * sc_y - (align_offset_y * img_y))

    def render(self):
        if not self.transparent:
            self.get_screen().blit(source=pygame.transform.scale_by(
                self.image, self.scale), dest=self.tl_point_px)


class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (1600, 900), flags=pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        # self.dt = 0
        self.container = Container((0, 0), (1, 1), parent=self.screen)
        pygame.font.init()
        self._resize_screen()

    def get_container(self):
        return self.container

    def set_background_color(self, background_color):
        self.container.set_color(background_color)

    def tick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.WINDOWRESIZED:
                self._resize_screen()
        # self._verify_movement()
        self._render()
        self.clock.tick(60)
        return True

    def apply_change(self):
        self._render()

    def _resize_screen(self):
        # self.screen.fill(self.background_color)
        self.container.rescale()

    def _render(self):
        self.container.render()
        pygame.display.flip()

    # def _verify_movement(self):
    #     keys = pygame.key.get_pressed()
