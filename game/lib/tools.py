import pygame, random
from pygame.locals import *
from world import Territory

from gui import gui
import combat


class HotseatUserBattle(object):
    def __init__(self, ship1, ship2, mgui):
        self.ship1 = ship1
        self.ship2 = ship2

        self.finished = False

        self.gui = mgui
        self.app = self.gui.app
        self.win = gui.Window(self.app, (320, 50), "UB-WINDOW", "midtop",
                              (300, 300), caption="Battle!",
                              plain=True)
##        self.win.border.set_alpha(175)

        self.button = gui.Button(self.win, (5, 300),
                                 "UB-Button!", "Leave", "bottomleft")
        self.button2 = gui.Button(self.win, (295, 300),
                                 "UB-Button2!", "Fire!", "bottomright")

        attack_options = {"long": ["ball", "chain"],
                          "medium": ["ball", "chain", "grape"],
                          "close": ["ball", "chain", "grape", "board"]}
        self.range = ship1.get_range(ship2)
        if not self.range:
            self.finished = True

        self.p1_attackc = gui.Menu(self.win, (3, self.button.rect.top-5), "UB-Menu1", "Select Cannonball",
                                   attack_options[self.range], widget_pos="bottomleft")
        self.p2_attackc = gui.Menu(self.win, (295, self.button.rect.top-5), "UB-Menu2", "Select Cannonball",
                                   attack_options[self.range], widget_pos="bottomright")

        self.p1_choice = None
        self.p2_choice = None

        self.gui.set_current(self.gui.bmr)
        self.gui.bmr.set_to(self.ship1, self.ship2, self.win)

    def event(self, event):
        if event.type == gui.GUI_EVENT:
            if event.widget == gui.Window:
                if event.name == "UB-WINDOW":
                    event = event.subevent
                    if event.action == gui.GUI_EVENT_CLICK:
                        if event.name == "UB-Button!":
                            self.finished = True
                        if event.name == "UB-Button2!":
                            if self.p1_choice and self.p2_choice:
                                print "attack"
                                #do attack code!
                        if event.widget == gui.Menu:
                            if event.name == "UB-Menu1":
                                self.p1_choice = event.entry
                                self.p1_attackc.text = event.entry
                                ov = self.p1_attackc.button.rect.width
                                self.p1_attackc.make_image()
                                self.p1_attackc.button.over_width = ov
                                self.p1_attackc.button.make_image()
                            if event.name == "UB-Menu2":
                                self.p2_choice = event.entry
                                self.p2_attackc.text = event.entry
                                ov = self.p2_attackc.button.rect.width
                                self.p2_attackc.make_image()
                                self.p2_attackc.button.over_width = ov
                                self.p2_attackc.button.make_image()

    def kill(self):
        self.app.widgets.remove(self.win)
        self.gui.set_current()


class SelectedTerritoryRender(object):
    def __init__(self, player, territory, world):
        self.territory = territory
        self.world = world
        self.player = player

    def render(self, screen):
        x, y = self.world.camera.get_offset()
        np = []
        for p in self.territory.points:
            px, py = p
            px -= x
            py -= y
            np.append((px, py))
        pygame.draw.polygon(screen, (255,255,0), np, 7)
        pygame.draw.polygon(screen, self.player.color, np, 3)


class ShipRangeRender(object):
    def __init__(self, ship, player, world):
        self.ship = ship
        self.player = player
        self.world = world

        self.range_circle = pygame.Surface([self.ship.long_range*2, self.ship.long_range*2]).convert()
        pygame.draw.circle(self.range_circle, [255, 255, 0],
                           [self.ship.long_range, self.ship.long_range],
                            self.ship.long_range, 3)
        pygame.draw.circle(self.range_circle, [255, 165, 0],
                           [self.ship.long_range, self.ship.long_range],
                            self.ship.medium_range, 3)
        pygame.draw.circle(self.range_circle, [255, 0, 0],
                           [self.ship.long_range, self.ship.long_range],
                            self.ship.close_range, 3)
        self.range_circle.set_colorkey(self.range_circle.get_at((0,0)), RLEACCEL)

        self.rerender()

    def rerender(self):
        self.move_circle = pygame.Surface([self.ship.speed*2, self.ship.speed*2]).convert()
        pygame.draw.circle(self.move_circle, [0, 255, 0], [self.ship.speed, self.ship.speed], self.ship.speed)

        m2 = self.move_circle.copy()
        m2.fill((0,0,0))
        p1 = self.ship.territory.capitol.pos
        p2 = self.ship.rect.center
        p2dif = p2[0] - self.ship.speed, p2[1] - self.ship.speed
        x = p1[0] - p2dif[0]
        y = p1[1] - p2dif[1]
        if self.ship.string:
            pygame.draw.circle(m2, [0, 255, 0], (x, y), self.ship.string)
        m2.set_colorkey((0, 255, 0), RLEACCEL)
        self.move_circle.blit(m2, (0,0))


        m3 = self.move_circle.copy()
        m3.fill((0,0,0))
        p = self.ship.rect.center
        np = []
        for i in self.ship.territory.points:
            x, y = i
            x -= p[0] - self.ship.speed
            y -= p[1] - self.ship.speed
            np.append((x, y))

        pygame.draw.polygon(m3, [0, 255, 0], np)
        m4 = m3.copy()
        m4.fill((0,0,0))
        pygame.draw.circle(m4, [0, 255, 0], [self.ship.speed, self.ship.speed], self.ship.speed)
        m4.set_colorkey((0, 255, 0), RLEACCEL)
        m3.blit(m4, (0,0))
        m3.set_colorkey((0,0,0), RLEACCEL)

        self.move_circle.blit(m3, (0,0))

        self.move_circle.set_colorkey((0,0,0), RLEACCEL)
        self.move_circle.set_alpha(175)

    def render(self, screen):
        ox, oy = self.world.camera.get_offset()
        x, y = self.ship.pos
        x -= ox
        y -= oy

        pos1 = (self.ship.rect.centerx - ox, self.ship.rect.centery - oy)
        pos2 = (self.ship.territory.capitol.pos[0] - ox, self.ship.territory.capitol.pos[1] - oy)
        if self.ship.can_move:
            screen.blit(self.move_circle, [x - self.ship.speed, y - self.ship.speed])
        if self.ship.can_attack:
            screen.blit(self.range_circle, [x - self.ship.long_range, y - self.ship.long_range])

        if not self.ship.rect.center in self.ship.territory.pixels:
            pygame.draw.line(screen, [random.randrange(255), random.randrange(255), random.randrange(255)], pos1, pos2, 3)

class TerritoryDrawer(object):
    def __init__(self, player, world):
        self.player = player
        self.world = world

        self.t = None
        self.active = False

    def update_event(self, event):
        if self.active:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    ox, oy = self.world.camera.get_offset()
                    x += ox
                    y += oy
                    x -= self.world.camera.screen_rect.left
                    y -= self.world.camera.screen_rect.top
                    pos = x, y
                    if self.world.mo.test_point(pos):
                        if not self.t:
                            self.t = Territory(self.player)
                            self.t.add_point(pos)
                        else:
                            if self.t.within_range(pos):
                                if len(self.t.points) == 1:
                                    return None
                                self.t.finish()
                                if self.world.mo.test_territory(self.t):
                                    self.world.mo.add(self.t)
                                self.t = None
                                self.active = False
                            else:
                                self.t.add_point(pos)

    def render(self, screen):
        if self.t:
            ox, oy = self.world.camera.get_offset()
            mx, my = pygame.mouse.get_pos()
            mx -= self.world.camera.screen_rect.left
            my -= self.world.camera.screen_rect.top
            mp = (mx, my)
            np = []
            for i in self.t.points:
                x, y = i
                x -= ox
                y -= oy
                np.append((x, y))

            if len(np) > 1:
                pygame.draw.lines(screen, self.player.color, False, np, 1)
            pygame.draw.line(screen, self.player.color, np[-1], mp, 3)
            for i in np:
                pygame.draw.rect(screen, self.player.color, [i[0]-10, i[1]-10, 20, 20])

class Minimap(object):
    def __init__(self, state, rect):
        self.state = state
        self.rect = rect

    def update(self):
        """Renders a minimap image and returns it."""
        # Make a Rect 2 px smaller than render size for a nice border
        mrect = pygame.Rect(0, 0, self.rect.width-2, self.rect.width-2)
        map = pygame.Surface((mrect.width, mrect.height))
        map.fill((14,98,212)) # Nice background
        ratio_x, ratio_y = (self.state.world.wsize[0] / mrect.width), \
                (self.state.world.wsize[1] / mrect.height)

        # render islands
        pygame.draw.circle(map, (255,0,0), mrect.center, 5)
        # render territories
        # render ships with appropriate color

        # render map view frame
        mx, my = self.state.world.camera.get_offset()
        view_rect = Rect(mx / ratio_x, my / ratio_y, \
                self.state.world.ssize[0] / ratio_x, \
                self.state.world.ssize[1] / ratio_y)
        pygame.draw.rect(map, (180,180,180), view_rect, 1)

        # Prepare final surface
        final_map = pygame.Surface((self.rect.width, self.rect.height))
        final_map.fill((0,0,0))
        final_map.blit(map, (1,1))
        return final_map

    def map_click(self, click_pos):
        """Called when the user has clicked somewhere on the minimap. Returns 
        coordinates on which the game screen should center."""
# get click
# update map view frame (necessary?)
        return (200,200)

