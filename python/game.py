import pygame


class Component():
    def __init__(self, tl_point, parent=False):
        self.parent = parent
        self.tl_point = tl_point
        if parent:
            parent.add_component(self)
        self.show = True
        self.transparent = False

    def set_color(self, color):
        self.color = pygame.Color(color)

    def rescale(self, screen):
        sc_x, sc_y = screen.get_size()
        if self.parent:
            self.tl_point_px = (
                self.tl_point[0] * self.parent.children_cont.size_px[0] +
                self.parent.children_cont.tl_point_px[0],
                self.tl_point[1] * self.parent.children_cont.size_px[1] + self.parent.children_cont.tl_point_px[1])
        else:
            self.tl_point_px = (
                self.tl_point[0] * sc_x, self.tl_point[1] * sc_y)

    def set_show(self, show):
        self.show = show

    def set_transparent(self, is_transparent: bool = True):
        self.transparent = is_transparent


class AreaComponent(Component):
    def __init__(self, tl_point, size, parent=False):
        super().__init__(tl_point, parent)
        self.size = size
        self.color = "black"

    def rescale(self, screen):
        super().rescale(screen)
        if self.parent:
            self.size_px = (
                self.size[0] * self.parent.children_cont.size_px[0], self.size[1] * self.parent.children_cont.size_px[1])
        else:
            sc_x, sc_y = screen.get_size()
            self.size_px = (self.size[0] * sc_x, self.size[1] * sc_y)


class RectComponent(AreaComponent):
    def __init__(self, tl_point, size, parent=False):
        super().__init__(tl_point, size, parent)

    def render(self, screen):
        if self.show and not self.transparent:
            pygame.draw.rect(screen, self.color, pygame.Rect(
                self.tl_point_px, self.size_px))


class Container(RectComponent):
    def __init__(self, tl_point, size, parent=False, ratio=False):
        super().__init__(tl_point, size, parent)
        self.children_cont = ChildContainer(parent=self, ratio=ratio)

    def add_component(self, child: Component):
        if not isinstance(child, ChildContainer):
            self.children_cont.add_component(child)

    def rescale(self, screen):
        super().rescale(screen)
        self.children_cont.rescale(screen)

    def set_color(self, color):
        # super().set_color("white")
        self.children_cont.set_color(color)

    def render(self, screen):
        # super().render(screen)
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
        # super().rescale(screen)
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
        # pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode(
            (1600, 900), flags=pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.containers = containers
        self.background_color = "black"
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

        # pygame.draw.circle(self.screen, "red", self.player_pos, 40)

        self.dt = self.clock.tick(60) / 1000

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
        # if keys[pygame.K_w] | keys[pygame.K_UP]:
        #     self.player_pos.y -= 300 * self.dt
        # if keys[pygame.K_s] | keys[pygame.K_DOWN]:
        #     self.player_pos.y += 300 * self.dt
        # if keys[pygame.K_a] | keys[pygame.K_LEFT]:
        #     self.player_pos.x -= 300 * self.dt
        # if keys[pygame.K_d] | keys[pygame.K_RIGHT]:
        #     self.player_pos.x += 300 * self.dt
