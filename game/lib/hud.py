import pygame
from pygame.locals import *

from gui import gui
import data, objects
from tools import Minimap


class TopBar(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app

        self.turn_label = gui.Label(self.app, (5, 3), "Topbar-Label1", " 0", icon="turn.png")
        self.turn_label.over_width = 100

        self.player_label = gui.Label(self.app, (110, 3), "Topbar-Label2", " 0", icon="player.png")
        self.player_label.over_width = 100

        self.string_label = gui.Label(self.app, (215, 3), "Topbar-Label3", " 0", icon="string.png")
        self.string_label.over_width = 100

        self.crew_label = gui.Label(self.app, (320, 3), "Topbar-Label4", " 0", icon="crew.png")
        self.crew_label.over_width = 100

        self.gold_label = gui.Label(self.app, (425, 3), "Topbar-Label5", " 0", icon="gold.png")
        self.gold_label.over_width = 100

        self.update()

    def update(self):
        player = self.state.get_current_player()
        self.turn_label.text = " "+str(self.state.turn)
        self.turn_label.theme.label["text-color"] = (0, 0, 0)
        self.turn_label.make_image()

        self.player_label.text = " "+str(self.state.uturn)
        color = self.state.get_current_player().color
        if color == (0, 255, 0):
            color = (0, 200, 0)
        self.player_label.theme.label["text-color"] = color
        self.player_label.make_image()

        self.string_label.text = " "+str(player.resources.string)
        self.string_label.theme.label["text-color"] = (0, 100, 255)
        self.string_label.make_image()

        self.crew_label.text = " "+str(player.resources.crew)
        self.crew_label.theme.label["text-color"] = (255, 0, 0)
        self.crew_label.make_image()

        self.gold_label.text = " "+str(player.resources.gold)
        self.turn_label.theme.label["text-color"] = (90, 90, 0)
        self.gold_label.make_image()

    def render_bg(self, screen):
        screen.blit(data.image("hud_bg_top.png"), (0,0))

class NormalBottomBar(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app

        self.end_turn_button = gui.Button(self.app, (635, 475), "NBB-ENDTURN", "End Turn", "bottomright")
        x, y = self.end_turn_button.rect.topright
        y -= 5
        self.draw_button = gui.Button(self.app, (x,  y), "NBB-DRAWTERR", "Expand", "bottomright")
        self.draw_button.over_width = self.end_turn_button.rect.width
        self.draw_button.make_image()

        self.minimap = Minimap(state, pygame.Rect(15, 390, 82, 82))

    def render_bg(self, screen):
        screen.blit(data.image("hud_bg_bottom.png"), (0,380))
        map = self.minimap.update()
        screen.blit(map, self.minimap.rect)

    def update(self):
        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            if self.minimap.rect.collidepoint(pos):
                # Localize passed click..
                self.minimap.map_click((pos[0] - self.minimap.rect.left,
                    pos[1] - self.minimap.rect.top))

class TerritoryBottomBar(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app

        self.button1 = gui.Button(self.app, (125, 390), "TBB-BUILD", "Build Ship", "topleft")

        self.inactive()

    def active(self):
        self.button1.active = True
        self._active = True

    def inactive(self):
        self.button1.active = False
        self._active = False

    def isactive(self): return self._active
    def render(self, screen): pass

class TerritoryBottomBarBUILD(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app

        self.buttons = []

        button1 = gui.Button(self.app, (125, 390),
                             "TBBB-junk", "Junk", "topleft",
                             icon="junk.png")
        button2 = gui.Button(self.app, (125, button1.rect.bottom+5),
                             "TBBB-frigate", "Frigate", "topleft",
                             icon="frigate.png")
        button3 = gui.Button(self.app, (button1.rect.right+5, 390),
                             "TBBB-juggernaut", "Juggernaut", "topleft",
                             icon="juggernaut.png")
        button4 = gui.Button(self.app, (button1.rect.right+5, button1.rect.bottom+5),
                             "TBBB-flyingdutchman", "Flying Dutchman", "topleft",
                             icon="flyingdutchman.png")
        button1.over_width = button4.rect.width
        button1.make_image()
        button2.over_width = button4.rect.width
        button2.make_image()
        button3.over_width = button4.rect.width
        button3.make_image()
        button3.rect.left = button1.rect.right + 5
        button4.rect.left = button1.rect.right + 5

        self.buttons.append(button1)
        self.buttons.append(button2)
        self.buttons.append(button3)
        self.buttons.append(button4)

        font = data.font("Pieces-of-Eight.ttf", 18)
        h = font.get_height()

        values = ("hull", "crew", "speed", "hold_capacity", "damage_multiplier", "cost")
        nh = h * (len(values) + 3)

        surfs = {}
        for i in objects.ship_types:
            if i in ["junk", "frigate", "juggernaut", "flyingdutchman"]: #hack, remove once we have all the ships in!!!
                new = pygame.Surface((250, nh)).convert()
                cur_i = 5
                new.blit(font.render("name: "+objects.ship_types[i]["fancy"], 1, (255, 255, 255)), (5, cur_i))
                cur_i += h
                for x in values:
                    new.blit(font.render(x.replace("_", " ")+": "+str(objects.ship_types[i][x]),
                                         1, (255, 255, 255)), (5, cur_i))
                    cur_i += h
                new.blit(font.render("crew cost: "+str(objects.ship_types[i]["crew"]), 1, (255, 255, 255)), (5, cur_i))
                new.set_alpha(150)
                surfs[i] = new

        self.r = pygame.Rect(0,0,250,nh)
        self.r.bottom = 380
        self.s = surfs

        self.inactive()

    def active(self):
        for i in self.buttons:
            i.active = True
        self._active = True

    def inactive(self):
        for i in self.buttons:
            i.active = False
        self._active = False

    def isactive(self): return self._active

    def render(self, screen):
        mpos = pygame.mouse.get_pos()
        for i in self.buttons:
            if i.rect.collidepoint(mpos):
                screen.blit(self.s[i.text.lower().replace(" ", "")], self.r)


class SelectShip(object):
    def __init__(self, state, app):
        self.state = state

        self.app = app
        self.button1 = gui.Button(self.app, (550, 475),
                             "SS-AddString", "Give 50 String", "bottomright")
        self.ship = None

        self.inactive()

    def active(self):
        self._active = True
        self.button1.active = True

    def inactive(self):
        self._active = False
        self.button1.active = False

    def isactive(self):
        return self._active

    def render(self, screen):
        if self.ship:
            font = data.font("Pieces-of-Eight.ttf", 18)
            screen.blit(font.render(objects.ship_types[self.ship.type]["fancy"], 1, (0,0,0)), (105, 380))
            screen.blit(self.ship.image, (110, 400))
            new = pygame.Surface((300, 100)).convert_alpha()
            new.fill((0,0,0,0))

            overs = []
            cur_x = 0
            cur_y = 5
            for i in ["Hull: %s/%s"%(self.ship.hull, self.ship.hull_max),
                      "Crew: %s/%s"%(self.ship.crew, self.ship.crew_max),
                      "Speed: %s/%s"%(self.ship.speed, self.ship.speed_max),
                      "String: %s"%(self.ship.string),
                      "BR",
                      "Hold:",
                      "Gold: %s"%self.ship.resources.gold,
                      "Crew: %s"%self.ship.resources.crew,
                      "String: %s"%self.ship.resources.string]:
                if i == "BR":
                    cur_x = max(overs)+15
                    cur_y = 5
                    continue
                v = font.render(i, 1, (0, 0, 0))
                overs.append(v.get_rect().width)
                r = v.get_rect()
                r.left = cur_x
                r.top = cur_y
                cur_y += r.height
                new.blit(v, r)
            screen.blit(new, (190, 390))
                

class BattleExplosionRender(object):
    def __init__(self):
        self.controller = None
        self._active = False

    def active(self):
        self._active = True

    def inactive(self):
        self._active = False

    def isactive(self):
        return self._active

    def render(self, screen):
        if self.controller:
            self.controller.render(screen)

class BattleMiscRender(object):
    def __init__(self, app):
        self.app = app
        self.widgets = []
        self.window = None
        self.inactive()

    def set_to(self, ship1, ship2, window):
        self.ship1 = ship1
        self.ship2 = ship2
        self.window = window

        x, y = self.window.rect.topleft

        font = data.font("Pieces-of-Eight.ttf", 18)
        h = font.get_height()
        values = ("hull", "crew", "speed", "damage_multiplier")
        nh = h * 6

        cur_i = 75

        self.l1_shipt = gui.Label(self.window, (5, cur_i), "L1_shipt",
                                 ship1.type)
        self.l1_shipt.theme.label["text-color"] = (255, 255, 255)
        self.l1_shipt.make_image()
        cur_i += h
        self.l1_hull = gui.Label(self.window, (5, cur_i), "L1_hull",
                                 "hull:"+str(ship1.hull)+"/"+str(ship1.hull_max))
        cur_i += h
        self.l1_crew = gui.Label(self.window, (5, cur_i), "L1_crew",
                                 "crew:"+str(ship1.crew)+"/"+str(ship1.crew_max))
        cur_i += h
        self.l1_speed = gui.Label(self.window, (5, cur_i), "L1_speed",
                                 "speed:"+str(ship1.speed)+"/"+str(ship1.speed_max))
        cur_i += h
        self.l1_dm = gui.Label(self.window, (5, cur_i), "L1_dm",
                               "damage multiplier:"+str(ship1.damage_multiplier))

        cur_i = 75
        self.l2_shipt = gui.Label(self.window, (165, cur_i), "L1_shipt",
                                 ship2.type)
        self.l2_shipt.make_image()
        cur_i += h
        self.l2_hull = gui.Label(self.window, (165, cur_i), "L1_hull",
                                 "hull:"+str(ship2.hull)+"/"+str(ship2.hull_max))
        cur_i += h
        self.l2_crew = gui.Label(self.window, (165, cur_i), "L1_crew",
                                 "crew:"+str(ship2.crew)+"/"+str(ship2.crew_max))
        cur_i += h
        self.l2_speed = gui.Label(self.window, (165, cur_i), "L1_speed",
                                 "speed:"+str(ship2.speed)+"/"+str(ship2.speed_max))
        cur_i += h
        self.l2_dm = gui.Label(self.window, (165, cur_i), "L1_dm",
                               "damage multiplier:"+str(ship2.damage_multiplier))

        self.select_type_msg = gui.Label(self.window, (75, 190), "attack_type",
                                 "Select attack type!")
        self.widgets = [self.l1_shipt, self.l1_hull, self.l1_crew, self.l1_speed, self.l1_dm,
                        self.l2_shipt, self.l2_hull, self.l2_crew, self.l2_speed, self.l2_dm,
                        self.select_type_msg]

    def active(self):
        self._active = True

    def inactive(self):
        for i in self.widgets:
            i.active = False
        self._active = False

    def isactive(self):
        return self._active

    def render(self, screen):
        if self.window and self.ship1 and self.ship2:
            x, y = self.window.rect.topleft
            screen.blit(self.ship1.image, (10+x, 10+y))
            screen.blit(self.ship2.image, (self.window.rect.width-10+x-self.ship2.rect.width, 10+y))

class BattleResultRender(object):
    def __init__(self):
        self.inactive()

    def set_to(self, ship1, ship2, battle, window):
        #attack_print((ship1, ship2), battle) # For debugging
        self.ship1 = ship1
        self.ship2 = ship2
        self.battle = battle
        self.window = window

        d1 = battle.results['damage'][ship1]
        d2 = battle.results['damage'][ship2]

        x, y = self.window.rect.topleft

        font = data.font("Pieces-of-Eight.ttf", 18)
        h = font.get_height()
        values = ("hull", "crew", "speed")
        nh = h * 9

        cur_i = 5
        surf1 = pygame.Surface((150, nh)).convert_alpha()
        surf1.fill((0,0,0,0))
        surf1.blit(font.render("Attacker", 1, (255, 255, 255)), (5, cur_i))
        cur_i += h
        surf1.blit(font.render(ship1.type, 1, (255, 255, 255)), (5, cur_i))
        cur_i += h
        surf1.blit(font.render("hull damage:"+str(d1[0]),
                               1, (255, 255, 255)), (5, cur_i))
        cur_i += h
        surf1.blit(font.render("hull:"+self._fix_zero(str(ship1.hull)+"/"+str(ship1.hull_max)),
                               1, (255, 255, 255)), (5, cur_i))
        cur_i += h+5
        surf1.blit(font.render("crew lost:"+str(d1[1]),
                               1, (255, 255, 255)), (5, cur_i))
        cur_i += h
        surf1.blit(font.render("crew: "+self._fix_zero(str(ship1.crew)+"/"+str(ship1.crew_max)),
                               1, (255, 255, 255)), (5, cur_i))
        cur_i += h+5
        surf1.blit(font.render("speed penalty:"+str(d1[2]),
                               1, (255, 255, 255)), (5, cur_i))
        cur_i += h
        surf1.blit(font.render("speed:"+self._fix_zero(str(ship1.speed)+"/"+str(ship1.speed_max)),
                               1, (255, 255, 255)), (5, cur_i))

        self.surf1 = surf1
        self.rect1 = surf1.get_rect()
        self.rect1.topleft = (3+x, 50+y)


        cur_i = 5
        surf2 = pygame.Surface((150, nh)).convert_alpha()
        surf2.fill((0,0,0,0))
        surf2.blit(font.render("Defender", 1, (255, 255, 255)), (5, cur_i))
        cur_i += h
        surf2.blit(font.render(ship2.type, 1, (255, 255, 255)), (5, cur_i))
        cur_i += h
        surf2.blit(font.render("hull damage:"+str(d2[0]),
                               1, (255, 255, 255)), (5, cur_i))
        cur_i += h
        surf2.blit(font.render("hull:"+self._fix_zero(str(ship2.hull)+"/"+str(ship2.hull_max)),
                               1, (255, 255, 255)), (5, cur_i))
        cur_i += h+5
        surf2.blit(font.render("crew lost:"+str(d2[1]),
                               1, (255, 255, 255)), (5, cur_i))
        cur_i += h
        surf2.blit(font.render("crew:"+self._fix_zero(str(ship2.crew)+"/"+str(ship2.crew_max)),
                               1, (255, 255, 255)), (5, cur_i))
        cur_i += h+5
        surf2.blit(font.render("speed penalty:"+str(d2[2]),
                               1, (255, 255, 255)), (5, cur_i))
        cur_i += h
        surf2.blit(font.render("speed:"+self._fix_zero(str(ship2.speed)+"/"+str(ship2.speed_max)),
                               1, (255, 255, 255)), (5, cur_i))

        self.surf2 = surf2
        self.rect2 = surf2.get_rect()
        self.rect2.topright = (307+x, 50+y)

        surf3 = pygame.Surface((250, 50)).convert_alpha()
        surf3.fill((0,0,0,0))

        if battle.results['captured'] == 0:
            ship1.sink()
            ship2.sink()
            surf3 = font.render("Both ships were sent to Davey Jones' Locker!",
                                1, (255, 255, 255))
        elif not ship1.is_alive() and not ship2.is_alive():
            ship1.sink()
            ship2.sink()
            surf3 = font.render("Both ships were sent to Davey Jones' Locker!",
                                1, (255, 255, 255))
        elif "winner" in battle.results:
            if not ship1.is_alive():
                ship1.sink()
                surf3 = font.render("Attacker was sent to Davey Jones' Locker!", 1, (255, 255, 255))
            elif not ship2.is_alive():
                ship2.sink()
                surf3 = font.render("Defender was sent to Davey Jones' Locker!", 1, (255, 255, 255))
            elif battle.results['captured'] != None:
                captured_ship = battle.results['captured']
                if captured_ship == ship1:
                    w = "attacking"
                    ship2.take_ship(ship1)
                elif captured_ship == ship2:
                    w = "defending"
                    ship1.take_ship(ship2)
                surf3 = font.render(("The "+w+" ship was captured!"),
                                    1, (255, 255, 255))
            else:
                pass
                #print 'battle results screwed'
        else:
            surf3 = font.render(("The battle was inconclusive."),
                                1, (255, 255, 255))
        self.surf3 = surf3
        self.rect3 = surf3.get_rect()
        self.rect3.center = (150+x, 260+y)

    def active(self):
        self._active = True

    def inactive(self):
        self._active = False

    def isactive(self):
        return self._active

    def render(self, screen):
        if self.window and self.ship1 and self.ship2 and self.battle:
            x, y = self.window.rect.topleft
            screen.blit(self.ship1.image, (10+x, 10+y))
            screen.blit(self.ship2.image, (self.window.rect.width-10+x-self.ship2.rect.width, 10+y))
            screen.blit(self.surf1, self.rect1)
            screen.blit(self.surf2, self.rect2)
            screen.blit(self.surf3, self.rect3)

    def _fix_zero(self, str):
        """Fixes up strings that are zero with just '*', which looks better in
        our font."""
        if str.startswith('0'): return '*'
        else: return str
        

class Hud(object):
    def __init__(self, screen, state):
        self.state = state
        self.state.gui = self

        self.app = gui.App(screen)
        self.app.theme = data.theme()

        self.status_bar = TopBar(self.state, self.app)
        self.normal_button_bar = NormalBottomBar(self.state, self.app)

        self.tbb = TerritoryBottomBar(self.state, self.app)
        self.tbbB = TerritoryBottomBarBUILD(self.state, self.app)
        self.ss = SelectShip(self.state, self.app)
        self.bmr = BattleMiscRender(self.app)
        self.brr = BattleResultRender()
        self.ber = BattleExplosionRender()

        self.special_states = [self.tbb, self.tbbB, self.ss, self.bmr, self.brr, self.ber]

    def set_current(self, x=None):
        for i in self.special_states:
            if i is x:
                i.active()
            else:
                i.inactive()

    def event(self, event):
        return self.app.event(event)

    def render(self):
        self.status_bar.update()
        self.status_bar.render_bg(self.app.surface)
        self.normal_button_bar.render_bg(self.app.surface)

        self.app.render()

        for i in self.special_states:
            if i.isactive():
                i.render(self.app.surface)

    def update(self):
        self.normal_button_bar.update()

def attack_print(ships, b):
    print 'Player', ships[0].owner.pnum, ships[0].type, ' vs. ',
    print 'Player', ships[1].owner.pnum, ships[1].type

    dmg = b.results['damage']
    print 'Damage: Ship', ships[0].owner.pnum, dmg[ships[0]], \
          'Ship', ships[1].owner.pnum, dmg[ships[1]]

    if b.results['captured'] != None and ships[0].is_alive() and ships[1].is_alive():
        if b.results['captured'] == 0:
            print 'Both crews were wiped out'
        else:
            print 'Ship', b.results['captured'].owner, 'was captured'

    print '--',
    print 'Ship 0:', ships[0].hull, ships[0].crew, ships[0].speed, \
          'Ship 1:', ships[1].hull, ships[1].crew, ships[1].speed
    if 'winner' in b.results:
        print 'Winner:', b.results['winner'].owner
    elif not (ships[0].is_alive() and ships[1].is_alive()):
        print 'Both ships sank'

