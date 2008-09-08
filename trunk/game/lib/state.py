

class InputController(object):
    """A class that handles the player based on user input"""
    def __init__(self, state, player):
        self.state = state
        self.player = player

    def event(self, event):
        if self.player.is_turn():
            self.player.event(event)

    def update(self):
        pass


class AIController(object):
    def __init__(self, state, player):
        self.state = state
        self.player = player

    def event(self, event):
        pass

    def update(self):
        if self.player.is_turn():
            self.think()

    def think(self):
        print "thinking..."
        self.player.end_turn()


class NetworkController(object):
    """Think we could make this the way to interact with the network?
       Maybe if we make it so that each controller action is then announced to
       all other controllers - then that can be sent across the network.
       Also, then this controller will have functions callable by a client, but will only
       listen if it this players turn.
       Thoughts?"""
    def __init__(self, state, player):
        self.state = state
        self.player = player

    def event(self, event):
        pass

    def update(self):
        pass

class Player(object):
    def __init__(self, state, controller, num=0):
        self.state = state
        self.controller = controller(state, self)
        self.num = num

    def is_turn(self):
        return self.state.uturn == self.num

    def end_turn(self):
        self.state.next_player_turn()

class State(object):
    def __init__(self, world):
        self.world = world
        self.players = []
        self.turn = 0
        self.uturn = 0 #which users turn it is
        self.pt_index = 0 #this is the index available for the next player

    def add_player(self, control_type=InputController):
        self.player.append(Player(self, control_type, self.pt_index))
        self.pt_index += 1

    def event(self, event):
        for i in self.players:
            i.controller.event(event)

    def update(self):
        for i in self.players:
            i.controller.update()

    def next_player_turn(self):
        self.uturn += 1
        if self.uturn == len(self.players):
            self.uturn = 0
            self.turn += 1
