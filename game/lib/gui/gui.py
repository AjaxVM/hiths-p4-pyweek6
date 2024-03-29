import os
import copy

import pygame
from pygame.locals import *

from theme import make_theme, Theme

class App(object):
    def __init__(self, surface,
                 background_color=None):

        self.surface = surface

        self.widgets = []

        self.theme = None

        self.dirty = False
        self.background_color = background_color

    def move_to_top(self, other):
        i = self.widgets.index(other)
        self.widgets.insert(0, self.widgets.pop(i))
        self.dirty = True
        for i in self.widgets:
            if not i == other:
                i.not_active()
        return None

    def get_mouse_pos(self):
        return pygame.mouse.get_pos()

    def force_update(self):
        self.dirty = True

    def add_widget(self, widg):
        self.widgets.insert(0, widg)
        self.dirty = True
        return None

    def remove_widget(self, name):
        for i in self.widgets:
            if i.name == name:
                self.widgets.remove(i)
                break
        return None

    def event(self, event):
        for widg in self.widgets:
            ret = widg.event(event)
            if not ret is event:
                return ret
        return ret

    def get_events(self):
        return_events = []
        for event in pygame.event.get():
            return_events.append(self.event(event))
        return return_events

    def render(self):
        if self.dirty:
            if self.background_color:
                self.surface.fill(self.background_color)
            self.widgets.reverse()
            for i in self.widgets:
                i.render(self.surface)
            self.widgets.reverse()
            self.dirty = False
        return self.surface

        
def resize_image(image, size):
    if image == "noimage":
        return image
    x, y = size
    if x < image.get_width(): x = image.get_width()
    if y < image.get_height(): y = image.get_height()
    size = x, y
    bsize = (image.get_width() / 3,
             image.get_height() / 3)

    topleft = image.subsurface((0, 0), bsize)
    top = pygame.transform.scale(image.subsurface((bsize[0], 0), bsize),
                                 (size[0] - bsize[0] * 2, bsize[1]))
    topright = image.subsurface((bsize[0] * 2, 0), bsize)

    left = pygame.transform.scale(image.subsurface((0, bsize[1]), bsize),
                                  (bsize[0], size[1] - bsize[1] * 2))
    middle = pygame.transform.scale(image.subsurface((bsize[0], bsize[1]), bsize),
                                    (size[0] - bsize[0] * 2,
                                     size[1] - bsize[1] * 2))
    right = pygame.transform.scale(image.subsurface((bsize[0] * 2, bsize[1]), bsize),
                                   (bsize[0], size[1] - bsize[1] * 2))

    botleft = image.subsurface((0, bsize[1] * 2), bsize)
    bottom = pygame.transform.scale(image.subsurface((bsize[0], bsize[1] * 2), bsize),
                                    (size[0] - bsize[0] * 2, bsize[1]))
    botright = image.subsurface((bsize[0] * 2, bsize[1] * 2), bsize)

    new = pygame.Surface(size).convert_alpha()
    new.blit(topleft, (0, 0))
    new.blit(top, (bsize[0], 0))
    new.blit(topright, (size[0] - bsize[0], 0))

    new.blit(left, (0, bsize[1]))
    new.blit(middle, bsize)
    new.blit(right, (size[0] - bsize[0], bsize[1]))

    new.blit(botleft, (0, size[1] - bsize[1]))
    new.blit(bottom, (bsize[0], size[1] - bsize[1]))
    new.blit(botright, (size[0] - bsize[0], size[1] - bsize[1]))
    return new


class Widget(object):
    def __init__(self, parent, pos = (-1, -1), name="",
                 widget_pos="topleft", theme=None):
        self.name = name
        self.parent = parent
        self.parent.add_widget(self)

        self.theme = copy.copy(theme)
        if not self.theme:
            if self.parent:
                self.theme = copy.copy(self.parent.theme)

        x, y = pos
        if x == -1:
            x = int(self.parent.surface.get_width() / 2)
        if y == -1:
            y = int(self.parent.surface.get_height() / 2)
        self.pos = (x, y)

        self.widget_pos = widget_pos

        self.rect = pygame.Rect(0, 0, 1, 1)
        self.move()
        self.active = True

    def render(self, surface):
        pass

    def get_mouse_pos(self):
        return self.parent.get_mouse_pos()

    def force_update(self):
        self.parent.force_update()

    def event(self, event):
        return event

    def move(self, off=(0,0)):
        x, y = self.pos
        x += off[0]
        y += off[1]

        self.pos = (x, y)
        setattr(self.rect, self.widget_pos, self.pos)
        self.force_update()
        return None

    def combine_images(self, images):
        flags = images[-1].get_flags()
        width = 0
        height = 0
        for i in images:
            width += i.get_width()
            if i.get_height() > height:
                height = i.get_height()

        new = pygame.Surface((width, height), flags).convert_alpha()
        new.fill((0,0,0,0))
        lx = 0
        for i in images:
            new.blit(i, (lx, 0))
            lx += i.get_width()
        return new

    def not_active(self):
        pass


class Label(Widget):
    def __init__(self, parent, pos, name, text,
                 widget_pos="topleft", theme=None,
                 icon=None):
        Widget.__init__(self, parent, pos, name, widget_pos, theme)

        self.text = text

        self.over_width = None

        self.icon = icon
        if self.icon:
            self.icon = pygame.image.load(os.path.join(self.theme.theme, self.icon)).convert_alpha()

        self.make_image()
        self.active = True

    def make_image(self):
        if self.theme and self.theme.font["font"]:
            font = pygame.font.Font(self.theme.font["font"],
                                    self.theme.font["size"])
            tex = font.render(self.text, self.theme.font["aa"],
                              self.theme.label["text-color"])
            if self.icon:
                tex = self.combine_images([self.icon, tex])
            image = self.theme.label["image"]
            if image=="noimage":
                self.comp_image = tex
            elif image:
                bsize = (image.get_width() / 3,
                         image.get_height() / 3)
                rect = tex.get_rect()
                rect.width += bsize[0] * 2
                rect.height += bsize[1] * 2
                if self.over_width:
                    rect.width = self.over_width
                new = resize_image(image, rect.size)
                new.blit(tex, bsize)
                self.comp_image = new
            else:
                self.comp_image = tex
        else:
            if self.icon:
                self.comp_image = self.icon
            else:
                self.comp_image = pygame.Surface((1, 1))
        self.rect = self.comp_image.get_rect()
        self.move()
        return None

    def render(self, surface):
        if not self.active:
            return None
        surface.blit(self.comp_image, self.rect.topleft)
        return None

class Button(Widget):
    def __init__(self, parent, pos, name, text,
                 widget_pos="topleft",
                 theme=None, icon=None):
        Widget.__init__(self, parent, pos, name, widget_pos, theme)

        self.text = text

        self.over_width = None
        self.over_height = None

        self.icon = icon
        if self.icon:
            self.icon = pygame.image.load(os.path.join(self.theme.theme, self.icon)).convert_alpha()

        self.make_image()

        self.__mouse_hold_me = False
        self.active = True

    def not_active(self):
        self.change_image(self.regular)
        self.__mouse_hold_me = False

    def make_image(self):
        if self.theme and self.theme.font["font"]:
            font = pygame.font.Font(self.theme.font["font"],
                                    self.theme.font["size"])
            tex = font.render(self.text, self.theme.font["aa"],
                              self.theme.button["text-color"])
            if self.icon:
                tex = self.combine_images([self.icon, tex])

            #default button!
            image = self.theme.button["default"]
            if image=="noimage":
                self.regular = tex
            elif image:
                bsize = (image.get_width() / 3,
                         image.get_height() / 3)
                rect = tex.get_rect()
                rect.width += bsize[0] * 2
                rect.height += bsize[1] * 2
                if self.over_width:
                    rect.width = self.over_width
                if self.over_height:
                    rect.height = self.over_height
                new = resize_image(image, rect.size)
                new.blit(tex, bsize)
                self.regular = new
            else:
                self.regular = tex

            #hover button!
            image = self.theme.button["hover"]
            if image=="noimage":
                self.hover = tex
            elif image:
                bsize = (image.get_width() / 3,
                         image.get_height() / 3)
                rect = tex.get_rect()
                rect.width += bsize[0] * 2
                rect.height += bsize[1] * 2
                if self.over_width:
                    rect.width = self.over_width
                if self.over_height:
                    rect.height = self.over_height
                new = resize_image(image, rect.size)
                new.blit(tex, bsize)
                self.hover = new
            else:
                self.hover = tex

            #click button!
            image = self.theme.button["click"]
            if image=="noimage":
                self.click = tex
            elif image:
                bsize = (image.get_width() / 3,
                         image.get_height() / 3)
                rect = tex.get_rect()
                rect.width += bsize[0] * 2
                rect.height += bsize[1] * 2
                if self.over_width:
                    rect.width = self.over_width
                if self.over_height:
                    rect.height = self.over_height
                new = resize_image(image, rect.size)
                new.blit(tex, bsize)
                self.click = new
            else:
                self.click = tex
        else:
            if self.icon:
                self.regular = self.hover = self.click = self.icon
            else:
                self.regular = self.hover = self.click = pygame.Surface((1, 1))

        self.image = self.regular
        self.rect = self.image.get_rect()
        self.move()
        return None

    def render(self, surface):
        if not self.active:
            return None
        surface.blit(self.image, self.rect.topleft)
        return None

    def change_image(self, new):
        if not self.image == new:
            self.image = new
            self.force_update()
        return None

    def event(self, event):
        if not self.active:
            return event
        mpos = self.get_mouse_pos()
        if mpos and self.rect.collidepoint(mpos):
            if self.__mouse_hold_me:
                self.change_image(self.click)
            else:
                self.change_image(self.hover)
        else:
            self.change_image(self.regular)

        if event.type == MOUSEBUTTONDOWN:
            if mpos and self.rect.collidepoint(mpos):
                self.change_image(self.click)
                self.__mouse_hold_me = True
                self.parent.move_to_top(self)
                return None
            return event
        if event.type == MOUSEBUTTONUP:
            if self.__mouse_hold_me:
                self.__mouse_hold_me = False
                if mpos and self.rect.collidepoint(mpos):
                    self.change_image(self.regular)
                    self.parent.move_to_top(self)
                    return Event(Button, self.name, GUI_EVENT_CLICK)
                return None
            return event
        return event

class Area(Widget):
    def __init__(self, parent, name="", widget_pos="topleft",
                 theme=None, size=(50,50)):
        Widget.__init__(self, parent, (0,0), name, widget_pos, theme)

        self.widgets = []

        self.size = size
        self.draw_area = pygame.Surface(self.size).convert_alpha()
        self.draw_area.fill((0,0,0,0))
        self.surface = self.draw_area.subsurface((0,0), self.size)

        self.rect = self.draw_area.get_rect()

        self.hscroll_bar = None
        self.vscroll_bar = None
        self.block = None

        self.lock_add_widgets = False

        self.new_widgets = True
        self.active = True

    def not_active(self):
        if self.hscroll_bar:
            self.hscroll_bar.not_active()
        if self.vscroll_bar:
            self.vscroll_bar.not_active()
        for i in self.widgets:
            i.not_active()

    def get_mouse_pos(self):
        p = self.parent.get_mouse_pos()
        if p:
            if not self.rect.collidepoint(p):
                return False
            return p
        return None

    def make_vert(self, s, m, bsize):
        if self.vscroll_bar:
            if m > s:
                if not self.vscroll_bar.tot_size[1] == m:
                    self.vscroll_bar.tot_size = (self.vscroll_bar.tot_size[0],
                                                 m)
                    self.vscroll_bar.make_image()
            else:
                self.vscroll_bar = None
        else:
            if m > s:
                self.lock_add_widgets = True
                self.vscroll_bar = ScrollBar(self, (self.size[0], 0),
                                             "", "topright",
                                             None, (bsize[0], m),
                                             (bsize[0], s),
                                             0, 1)
                self.lock_add_widgets = False

    def make_horz(self, s, m, bsize):
        if self.hscroll_bar:
            if m > s:
                if not self.hscroll_bar.tot_size[0] == m:
                    self.hscroll_bar.tot_size = (m, self.vscroll_bar.tot_size[1])
                    self.hscroll_bar.make_image()
            else:
                self.hscroll_bar = None
        else:
            if m > s:
                self.lock_add_widgets = True
                self.hscroll_bar = ScrollBar(self, (0, self.size[1]),
                                             "", "bottomleft",
                                             None, (m, bsize[1]),
                                             (s, bsize[1]),
                                             0, 0)
                self.lock_add_widgets = False


    def calc_s(self, v, m):
        if v < m:
            return True
        return False

    def check_borders(self):
        width = 0
        height = 0
        for i in self.widgets:
            if not i in (self.hscroll_bar, self.vscroll_bar):
                if i.rect.right > width:
                    width = i.rect.right
                if i.rect.bottom > height:
                    height = i.rect.bottom

        sw, sh = self.size

        bsize = self.theme.scroll_bar["border"].get_size()
        oo = bsize[0] / 3 * 5, bsize[1] / 3 * 5

        need_v = False
        need_h = False
        if self.calc_s(sh, height):
            need_v = True
            if self.calc_s(sw - oo[0], width):
                need_h = True
        else:
            if self.calc_s(sw, width):
                need_h = True
                if self.calc_s(sh - oo[1], height):
                    need_v = True

        if need_h and need_v:
            self.make_horz(sw - oo[0], width, bsize)
            self.make_vert(sh - oo[1], height, bsize)
        elif need_h:
            self.make_horz(sw, width, bsize)
            self.vscroll_bar = None
        elif need_v:
            self.make_vert(sh, height, bsize)
            self.hscroll_bar = None
        else:
            self.hscroll_bar = None
            self.vscroll_bar = None

        if self.hscroll_bar and self.vscroll_bar:
            b = resize_image(self.theme.scroll_bar["border"], oo)
            self.block = (b, b.get_rect())
            self.block[1].bottomright = self.rect.bottomright
        else:
            self.block = None

        new = sw, sh
        self.surface = self.draw_area.subsurface((0,0), new)
        return None

    def add_widget(self, widg):
        if not self.lock_add_widgets:
            self.widgets.insert(0, widg)
            widg.parent = self
            self.new_widgets = True
            self.force_update()
        return None

    def move_to_top(self, other):
        if other == self.hscroll_bar or other == self.vscroll_bar:
            return None
        i = self.widgets.index(other)
        self.widgets.insert(0, self.widgets.pop(i))
        for i in self.widgets:
            if not i == other:
                i.not_active()
        self.force_update()
        return None

    def remove_widget(self, name):
        for i in self.widgets:
            if i.name == name:
                self.widgets.remove(i)
                self.new_widgets = True
                self.force_update()
                break
        return None

    def render(self, surface):
        if not self.active:
            return None
        if self.new_widgets:
            self.new_widgets = False
            self.check_borders()
        self.draw_area.fill((0,0,0,0))
        self.widgets.reverse()
        for i in self.widgets:
            i.render(self.surface)
        self.widgets.reverse()
        if self.vscroll_bar:
            self.vscroll_bar.render(self.draw_area)
        if self.hscroll_bar:
            self.hscroll_bar.render(self.draw_area)
        if self.block:
            self.draw_area.blit(*self.block)
        surface.blit(self.draw_area, (0,0))
        return None

    def move_horz(self, val):
        for i in self.widgets:
            if not (i == self.hscroll_bar or i == self.vscroll_bar):
                i.move((-val, 0))

    def move_vert(self, val):
        for i in self.widgets:
            if not (i == self.hscroll_bar or i == self.vscroll_bar):
                i.move((0, -val))

    def event(self, event):
        if not self.active:
            return event
        if self.vscroll_bar:
            e = self.vscroll_bar.event(event)
            if not e == event:
                if e and e.type == GUI_EVENT and e.action == GUI_SCROLL_EVENT:
                    self.move_vert(e.value)
                    return None
                return e

        if self.hscroll_bar:
            e = self.hscroll_bar.event(event)
            if not e == event:
                if e and e.type == GUI_EVENT and e.action == GUI_SCROLL_EVENT:
                    self.move_horz(e.value)
                    return None
                return e

        if self.block:
            if event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
                p = self.get_mouse_pos()
                if p:
                    if self.block[1].collidepoint(p):
                        self.not_active()
                        return None
                else:
                    return event

        for i in self.widgets:
            e = i.event(event)
            if not e == event:
                return e
        return event

class MenuList(Widget):
    def __init__(self, parent, pos, name="",
                 buttons=["None"],
                 widget_pos="topleft",
                 theme=None,
                 icons={"None":None}):
        Widget.__init__(self, parent, pos, name, widget_pos, theme)

        self.button_list = buttons
        self.icons = icons

        self.surface = pygame.Surface((1, 1))
        self.draw_area = pygame.Surface((1, 1))

        self.scroll_bar = None

        self.make_image()
        self.active = True

    def get_mouse_pos(self):
        p = self.parent.get_mouse_pos()
        if not p:
            return None
        x, y = p
        x -= self.rect.left + self.draw_area.get_offset()[0]
        y -= self.rect.top + self.draw_area.get_offset()[1]
        return x, y

    def make_image(self):
        buttons = []
        self.theme.button["default"] = self.theme.menu["entry-default"]
        self.theme.button["hover"] = self.theme.menu["entry-hover"]
        self.theme.button["click"] = self.theme.menu["entry-click"]
        self.theme.button["text-color"] = self.theme.menu["entry-text-color"]
        height = 0
        width = 0
        for i in self.button_list:
            try:
                x = self.icons[i]
            except:
                x = None
            new = Button(self, (0, height), i, i, icon=x)
            height += new.rect.height
            if new.rect.width > width:
                width = new.rect.width
            buttons.append(new)

        for i in buttons:
            i.over_width = width
            i.make_image()

        if self.theme:
            image = self.theme.menu["border"]
            bsize = (image.get_width() / 3,
                     image.get_height() / 3)
            width += 25
            image = resize_image(image, (width + bsize[0] * 2,
                                         height + bsize[1] * 2))
            self.surface = image
        else:
            bsize = (0,0)
            self.surface = pygame.Surface((width, height)).convert_alpha()

        self.border = bsize
        
        self.rect = self.surface.get_rect()
        self.move()

        if self.rect.bottom > self.parent.surface.get_height():
            dif = self.rect.bottom - self.parent.surface.get_height()
            self.rect.height -= dif
        if self.rect.right > self.parent.surface.get_width():
            dif = self.rect.right - self.parent.surface.get_width()
            self.rect.width -= dif

        if self.theme:
            self.surface = resize_image(self.theme.menu["border"],
                                        (self.rect.width,
                                         self.rect.height))
        else:
            self.surface = pygame.Surface((width, height)).convert_alpha()
            self.surface.fill((0,0,0,0))
        self.background = self.surface.subsurface(self.border,
                                        (self.rect.width - self.border[0] * 2,
                                         self.rect.height - self.border[1] * 2))
        self.back_copy = self.background.copy()

        self.Area = Area(self, size=(self.rect.width - self.border[0] * 2,
                                     self.rect.height - self.border[1] * 2))

        for i in buttons:
            self.Area.add_widget(i)

    def add_widget(self, *other):
        pass

    def move_to_top(self, other):
        pass

    def not_active(self):
        self.Area.not_active()

    def render(self, surface):
        if not self.active:
            return None
        self.background.blit(self.back_copy, (0,0))
        self.Area.render(self.background)
        surface.blit(self.surface, self.rect)
        return None

    def event(self, event):
        if not self.active:
            return event
        if event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
            mpos = self.parent.get_mouse_pos()
            if not (mpos and self.rect.collidepoint(mpos)):
                self.not_active()
                return event

        e = self.Area.event(event)
        if not e == event:
            self.force_update()
            if e:
                e.widget = MenuList
                e.entry = e.name
                e.name = self.name
                e.menu_action = "close"
            return e
        return event

class Menu(Widget):
    def __init__(self, parent, pos, name, text,
                 buttons=["None"], icons={"None":None},
                 widget_pos="topleft",
                 icon=None, theme=None):
        Widget.__init__(self, parent, pos, name, widget_pos, theme)

        self.text = text
        self.buttons = buttons
        self.icons = icons
        self.icon = icon

        self.surface = self.parent.surface

        self.make_image()

        self.widget_vis = False
        self.active = True

    def move_to_top(self, other):
        self.parent.move_to_top(self)

    def get_mouse_pos(self):
        return self.parent.get_mouse_pos()

    def not_active(self):
        self.window_vis = False
        self.other.not_active()
        self.button.not_active()

    def make_image(self):
        self.button = Button(self, self.pos, self.name, self.text,
                             self.widget_pos, icon=self.icon)

        self.other = MenuList(self, (self.pos[0], self.pos[1] + self.button.rect.height),
                              "", self.buttons, self.widget_pos, icons=self.icons)

        self.move()

    def add_widget(self, *other):
        pass

    def event(self, event):
        if not self.active:
            return event

        if self.widget_vis:
            x = self.other.event(event)
            if not x == event:
                self.force_update()
                if x:
                    if x.menu_action == "close":
                        self.widget_vis = False
                        self.force_update()
                    x.widget = Menu
                    x.name = self.name
                event = x
            else:
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mpos = self.get_mouse_pos()
                        if not (mpos and self.other.rect.collidepoint(mpos)):
                            self.widget_vis = False
                            self.force_update()
                            return event
                        else:
                            event = None
        else:
            x = self.button.event(event)
            if not x == event:
                self.force_update()
                if x:
                    if x.type == GUI_EVENT:
                        if x.widget == Button:
                            if x.action == GUI_EVENT_CLICK:
                                self.parent.move_to_top(self)
                                self.widget_vis = not self.widget_vis
                return x

        return event

    def render(self, surface):
        if not self.active:
            return None
        self.button.render(surface)
        if self.widget_vis:
            self.other.render(surface)
        return None

class TextInputBox(Widget):
    def __init__(self, parent, pos, name,
                 prompt, starting_text,
                 size = 25,
                 widget_pos="topleft", theme=None):
        Widget.__init__(self, parent, pos, name, widget_pos, theme)

        self.prompt = prompt
        self.text = starting_text

        self.size = size

        self.focused = False

        self.__mouse_hold_me = False
        self.__text_pos = len(self.text)

        self.make_image()
        self.active = True

    def not_active(self):
        if self.focused:
            self.force_update()
        self.focused = False
        self.make_text()

    def make_image(self):

        if self.theme:
            font = self.theme.font
            f = pygame.font.Font(font["font"], font["size"])
            width = f.size(self.prompt + ": " + "0" * (self.size + 1))[0]
            height = f.get_linesize()

            tex_surface = f.render(self.prompt + ": " + self.text, font["aa"],
                                   self.theme.input["entry-text-color"])

            image = self.theme.input["border"]

            if image and not image == "noimage":
                self.__surf_size = image.get_width() / 3, image.get_height() / 3
                surface = resize_image(image, (width + self.__surf_size[0] * 2,
                                               height + self.__surf_size[1] * 2))
            else:
                surface = pygame.Surface((width, height)).convert_alpha()
                surface.fill((0,0,0,0))

        self.surface = surface
        self.tex_surface = tex_surface
        self.rect = self.surface.get_rect()
        self.move()

    def make_text(self):

        if self.theme:
            font = self.theme.font
            f = pygame.font.Font(font["font"], font["size"])

            if self.focused:
                t = f.size(self.prompt + ": ")[0]
                miw, height = f.size(self.text[0:self.__text_pos])
                maw = f.size(self.text[0:self.__text_pos+1])[0]

                self.tex_surface = f.render(self.prompt + ": " + self.text + " ",
                                            font["aa"],
                                       self.theme.input["entry-text-color"])
                r, g, b = self.theme.input["entry-text-color"]
                r = 255 - r
                g = 255 - g
                b = 255 - b
                rc = pygame.Rect((t + miw, 0), (1, height))
                pygame.draw.rect(self.tex_surface, (r, g, b), rc, 1)
                
            else:
                self.tex_surface = f.render(self.prompt + ": " + self.text, font["aa"],
                                       self.theme.input["entry-text-color"])
            self.force_update()
            return None
        return None

    def render(self, surface):
        if not self.active:
            return None
        pos = self.rect.topleft
        surface.blit(self.surface, pos)
        surface.blit(self.tex_surface, (pos[0] + self.__surf_size[0],
                                        pos[1] + self.__surf_size[1]))
        return None

    def event(self, event):
        if not self.active:
            return event
        mpos = self.get_mouse_pos()
        if event.type == MOUSEBUTTONDOWN:
            if mpos and self.rect.collidepoint(mpos):
                self.__mouse_hold_me = True
                self.parent.move_to_top(self)
                self.force_update()
                return None
            else:
                self.__mouse_hold_me = False
                if self.focused:
                    self.force_update()
                self.focused = False
                return event
        if event.type == MOUSEBUTTONUP:
            if mpos and self.rect.collidepoint(mpos):
                self.parent.move_to_top(self)
                if self.__mouse_hold_me:
                    self.focused = True
                self.__mouse_hold_me = False
                self.make_text()
                return None
            else:
                if self.focused:
                    self.force_update()
                self.focused = False
                self.__mouse_hold_me = False
                self.make_text()
                return event

        if event.type == KEYDOWN:
            if self.focused:
                self.force_update()
                if event.key == K_BACKSPACE:
                    if not self.__text_pos == 0:
                        self.text = self.text[0:self.__text_pos-1] + self.text[self.__text_pos::]
                        self.__text_pos -= 1
                        self.make_text()
                elif event.key == K_DELETE:
                    if not self.__text_pos == len(self.text):
                        self.text = self.text[0:self.__text_pos] + self.text[self.__text_pos+1::]
                        self.make_text()
                elif event.key == K_HOME:
                    if not self.__text_pos == 0:
                        self.__text_pos = 0
                        self.make_text()
                elif event.key == K_END:
                    if not self.__text_pos == len(self.text):
                        self.__text_pos = len(self.text)
                        self.make_text
                elif event.key == K_LEFT:
                    if self.__text_pos > 0:
                        self.__text_pos -= 1
                        self.make_text()
                elif event.key == K_RIGHT:
                    if self.__text_pos < len(self.text):
                        self.__text_pos += 1
                        self.make_text()
                elif event.key == K_RETURN:
                    a = Event(TextInputBox, self.name, GUI_EVENT_INPUT)
                    a.string = self.text
                    self.text = ""
                    self.__text_pos = 0
                    self.make_text()
                    return a
                else:
                    if len(self.text) <= self.size:
                        char = event.unicode.encode('latin-1')
                        self.text = self.text[0:self.__text_pos] + char +\
                                    self.text[self.__text_pos::]
                        self.__text_pos += 1
                        self.make_text()
                    return None
                return None
            return event
        return event


class WindowBar(object):
    def __init__(self, parent, pos, width=None,
                 caption="", icon=None, attach_to=None, plain=False):

        self.parent = parent
        self.theme = copy.copy(self.parent.theme)
        self.theme.button = self.theme.window_bar

        self.bar = Button(self, pos, "", caption, "midbottom", icon=icon)
        self.bar.over_width = width
        self.bar.make_image()
        self.plain = plain

        self.__mouse_hold_me=False

        self.attach_to = attach_to

        self.minimized = False

        self.min_button = Button(self, self.bar.rect.midright, "", "_",
                                 "midright", theme=self.parent.theme)
        self.max_button = Button(self, self.bar.rect.midright, "", "+",
                                 "midright", theme=self.parent.theme)
        width = max([self.max_button.rect.width,
                     self.min_button.rect.width])
        self.min_button.over_width = width
        self.max_button.over_wdith = width
        self.min_button.make_image()
        self.max_button.make_image()
        self.active = True

    def add_widget(self, other):
        pass

    def move_to_top(self, other):
        self.moveup()

    def moveup(self):
        self.parent.force_update()

    def force_update(self):
        self.parent.force_update()

    def get_mouse_pos(self):
        return self.parent.get_mouse_pos()

    def event(self, event):
        if self.plain:
            return event
        if not self.active:
            return event
        mpos = self.get_mouse_pos()

        if mpos and self.bar.rect.collidepoint(mpos):
            if self.__mouse_hold_me:
                self.bar.change_image(self.bar.click)
            else:
                self.bar.change_image(self.bar.hover)
        else:
            self.bar.change_image(self.bar.regular)

        if self.minimized:
            e = self.max_button.event(event)
        else:
            e = self.min_button.event(event)
        if not e == event:
            self.force_update()
            if e:
                self.moveup()
                if e.type == GUI_EVENT:
                    self.minimized = not self.minimized
                    return None
            return e

        else:
            if event.type == MOUSEBUTTONDOWN:
                if mpos and self.bar.rect.collidepoint(mpos):
                    self.bar.change_image(self.bar.click)
                    self.__mouse_hold_me = True
                    self.moveup()
                    return None
                return event
            if event.type == MOUSEBUTTONUP:
                if self.__mouse_hold_me:
                    self.__mouse_hold_me = False
                    if mpos and self.bar.rect.collidepoint(mpos):
                        self.bar.change_image(self.bar.regular)
                        self.moveup()
                        return None
                    return None
                return event
            if event.type == MOUSEMOTION:
                if self.__mouse_hold_me:
                    self.bar.move(event.rel)
                    self.min_button.move(event.rel)
                    self.max_button.move(event.rel)
                    self.attach_to.move(event.rel)
        return event

    def render(self, surface):
        if self.plain:
            return None
        if not self.active:
            return None
        self.bar.render(surface)
        if self.minimized:
            self.max_button.render(surface)
        else:
            self.min_button.render(surface)
        return None

class Window(Widget):
    def __init__(self, parent, pos, name, widget_pos="topleft",
                 size=(50, 50), caption="",
                 icon=None, plain=False):
        Widget.__init__(self, parent, pos, name, widget_pos)

        self.size = size

        self.icon = icon

        self.caption = caption
        self.plain = plain

        self.widgets = []

        self.lock_add_widg = True
        self.Area = Area(self, size=size)
        self.lock_add_widg = False

        self.make_image()
        self.active = True

    def not_active(self):
        return self.Area.not_active()

    def get_mouse_pos(self):
        p = self.parent.get_mouse_pos()
        if not p:
            return None
        x, y = p
        if not self.rect.collidepoint((x, y)):
            return None
        x -= self.rect.left
        y -= self.rect.top
        x -= self.surface.get_offset()[0]
        y -= self.surface.get_offset()[1]
        return x, y

    def make_image(self):
        if self.theme:
            image = self.theme.window["border"]

            if image and not image == "noimage":
                w, h = image.get_width() / 3, image.get_height() / 3
                new = resize_image(image, (self.size[0] + w * 2,
                                           self.size[1] + h * 2))

                self.border = new
                self.surface = self.border.subsurface((w, h), self.size)
                self.border_offset = (w, h)
                self.__old_draw_area = self.surface.copy()
                self.rect = self.border.get_rect()
                setattr(self.rect, self.widget_pos, self.pos)
            else:
                self.border_offset = (0, 0)
                self.border = None
                self.surface = pygame.Surface(self.size).convert_alpha()
                self.surface.fill((0,0,0,0))
                self.__old_draw_area = self.surface.copy()
                self.rect = self.surface.get_rect()
                setattr(self.rect, self.widget_pos, self.pos)
        else:
            self.border_offset = (0, 0)
            self.border = None
            self.surface = pygame.Surface(self.size).convert_alpha()
            self.surface.fill((0,0,0,0))
            self.__old_draw_area = self.surface.copy()
            self.rect = self.surface.get_rect()
            setattr(self.rect, self.widget_pos, self.pos)

        self.drag_bar = WindowBar(self.parent, self.rect.midtop,
                                  self.rect.width, self.caption,
                                  self.icon, self,
                                  plain=self.plain)
        self.force_update()

    def event(self, event):
        if not self.active:
            return event
        e = self.drag_bar.event(event)
        if not e == event:
            self.parent.move_to_top(self)
            return e
        else:
            mpos = self.parent.get_mouse_pos()
            if self.drag_bar.minimized:
                self.not_active()
                return event
            if event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
                if not mpos and self.rect.collidepoint(mpos):
                    self.not_active()
                    return event
            
            e = self.Area.event(event)
            if not e == event:
                self.force_update()
                if e and e.type == GUI_EVENT:
                    new = Event(Window, self.name, None)
                    new.subevent = e
                    e = new
                    return e
            if event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
                if mpos and self.rect.collidepoint(mpos):
                    return None
            return e

    def move_to_top(self, other):
        self.parent.move_to_top(self)
        return None

    def add_widget(self, widg):
        if not self.lock_add_widg:
            self.Area.add_widget(widg)
        return None

    def remove_widget(self, name):
        self.Area.remove_widget(name)
        return None

    def render(self, surface):
        if not self.active:
            return None
        self.surface.fill((0,0,0,0))
        self.surface.blit(self.__old_draw_area, (0, 0))
        self.Area.render(self.surface)

        self.drag_bar.render(surface)
        if not self.drag_bar.minimized:
            pos = self.rect.topleft
            surface.blit(self.border, pos)
        return None


class ScrollBar(Widget):
    def __init__(self, parent, pos=(-1,-1), name="",
                 widget_pos="topleft", theme=None,
                 tot_size=(10,10), view_size=(10,10),
                 start_value=0, direction=0):
        Widget.__init__(self, parent, pos, name, widget_pos, theme)

        self.tot_size = tot_size
        self.view_size = view_size

        self.start_value = start_value
        self.current_value = start_value

        self.__mouse_hold_me = False

        self.direction = direction

        self.make_image()
        self.active = True

    def get_pos(self):
        return self.current_value - self.start_value

    def move_bar(self, new=(0,0)):
        if self.direction == 0:
            self.bar_rect.topleft = (self.current_value, 0)
        else:
            self.bar_rect.topleft = (0, self.current_value)

    def make_image(self):
        max_place = self.tot_size[self.direction] / self.view_size[self.direction]

        bsize = self.theme.scroll_bar["border"].get_size()
        bsize = bsize[0] / 3, bsize[1] / 3

        if self.direction == 0:
            big_bar = resize_image(self.theme.scroll_bar["border"],
                                   (self.view_size[0], bsize[1] * 5))
        else:
            big_bar = resize_image(self.theme.scroll_bar["border"],
                                   (bsize[0] * 5, self.view_size[1]))

        area = (big_bar.get_width() - bsize[0] * 2,
                big_bar.get_height() - bsize[1] * 2)

        render_area = big_bar.subsurface(bsize, area)
        old_render_area = render_area.copy()

        bar_size = ((area[0] / (self.tot_size[0] / area[0]) - bsize[0] * 2),
                    (area[1] / (self.tot_size[1] / area[1]) - bsize[1] * 2))

        if self.direction == 0:
            w = self.theme.scroll_bar["default"].get_width()
            if bar_size[0] < w:
                bar_size = w, bar_size[1]

        else:
            h = self.theme.scroll_bar["default"].get_height()
            if bar_size[1] < h:
                bar_size = bar_size[0], h

        bar_regular = resize_image(self.theme.scroll_bar["default"], bar_size)
        bar_hover = resize_image(self.theme.scroll_bar["hover"], bar_size)
        bar_click = resize_image(self.theme.scroll_bar["click"], bar_size)

        self.area_bar = big_bar
        self.draw_area = render_area
        self.__old_draw_area = old_render_area

        self.regular = bar_regular
        self.hover = bar_hover
        self.click = bar_click

        self.image = self.regular

        self.rect = self.area_bar.get_rect()
        self.bar_rect = self.image.get_rect()

        self.move()
        self.move_bar()

        self.min_value = 0
        if self.direction == 0:
            self.max_value = self.area_bar.get_width() - bar_size[0] - bsize[0] * 2
        else:
            self.max_value = self.area_bar.get_height() - bar_size[1] - bsize[1] * 2

    def render(self, surface):
        if not self.active:
            return None
        pos = self.rect.topleft
        self.draw_area.fill((0,0,0,0))
        self.draw_area.blit(self.__old_draw_area, (0,0))
        if not self.image == "noimage":
            p = self.bar_rect.topleft
            if self.direction == 0:
                p = p[0] + self.current_value, p[1]
            else:
                p = p[0], p[1] + self.current_value
            self.draw_area.blit(self.image, p)
        surface.blit(self.area_bar, pos)
        return None

    def get_value(self):
        p = 0
        if self.current_value:
            p = float(self.current_value) / self.max_value
        value = (self.tot_size[self.direction] - self.view_size[self.direction]) * p
        return value

    def change_image(self, new):
        if not self.image == new:
            self.image = new
            self.force_update()
        return None

    def not_active(self):
        self.change_image(self.regular)
        self.__mouse_hold_me = False
        return None

    def event(self, event):
        if not self.active:
            return event
        mpos = self.get_mouse_pos()
        if mpos and self.rect.collidepoint(mpos):
            if self.__mouse_hold_me:
                self.change_image(self.click)
            else:
                self.change_image(self.hover)
        else:
            self.change_image(self.regular)

        if event.type == MOUSEBUTTONDOWN:
            old_a = self.get_value()
            if event.button == 4:
                if self.current_value > self.min_value:
                    self.current_value -= 1
                self.force_update()
                x = Event(ScrollBar, self.name, GUI_SCROLL_EVENT)
                x.value = self.get_value() - old_a
                return x
            elif event.button == 5:
                if self.current_value < self.max_value:
                    self.current_value += 1
                self.force_update()
                x = Event(ScrollBar, self.name, GUI_SCROLL_EVENT)
                x.value = self.get_value() - old_a
                return x
            else:
                if mpos and self.rect.collidepoint(mpos):
                    self.change_image(self.click)
                    self.__mouse_hold_me = True
                    self.parent.move_to_top(self)
                    return None
                return event
        if event.type == MOUSEBUTTONUP:
            self.change_image(self.regular)
            if self.__mouse_hold_me:
                self.__mouse_hold_me = False
                return None
            elif event.button == 4:
                return None
            elif event.button == 5:
                return None
            return event
        if event.type == MOUSEMOTION:
            if self.__mouse_hold_me:
                amount = event.rel[self.direction]
                self.force_update()
                old_a = self.get_value()
                mpos = self.get_mouse_pos()
                if amount > 0:
                    if self.current_value < self.max_value:
                        self.current_value += amount
                        if self.current_value > self.max_value:
                            self.current_value = self.max_value
                if amount < 0:
                    if self.current_value > self.min_value:
                        self.current_value += amount
                        if self.current_value < self.min_value:
                            self.current_value = self.min_value
                #let's return a scroll bar event!
                x = Event(ScrollBar, self.name, GUI_SCROLL_EVENT)
                x.value = self.get_value() - old_a
                return x
            return event
        return event

#Defines
GUI_EVENT = "This is a string so we don't confuse Pygame ;)"
GUI_EVENT_CLICK = 0
GUI_EVENT_INPUT = 1
GUI_SCROLL_EVENT = 2

class Event(object):
    def __init__(self, widg=Widget, name="Name",
                 action=GUI_EVENT_CLICK):
        self.type = GUI_EVENT

        self.widget = widg
        self.name = name

        self.action = action
