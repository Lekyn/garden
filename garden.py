from pybrain.rl.environments.environment import Environment
import random
from widget import *
from tako import *
import genome

class Garden(Environment):
    """ simulates a small environment containing
    rock o which cannot be eaten and is not fun to play with
    grass * which can be eaten and is not fun to play with
    toy x which cannot be eaten and is fun to play with
    dirt . which doesn"t do much of anything
    and a creature <>^v which faces some direction and can
    go forward
    turn left/right
    eat
    play
    as well as seeing what is directly in front and what is the left/right front
    """

    #Environment variables
    indim = 1
    outdim = 3

    syms = {"rock": "o", "toy": "x", "grass": "*"}
    rsyms = {"o": "rock", "x": "toy", "*": "grass"}
    dir_syms = {0: "^", 1: ">", 2: "v", 3: "<"}


    def __init__(self, size, num_tako):
        #create the map and add toy, grass, rock, creature
        if size < 3:
            raise ValueError
        self.size = size
        self.num_tako = num_tako
        self.reset()
 
    def reset(self):
        self.garden_map = [[Dirt() for x in range(self.size)]
                           for x in range(self.size)]
        self.obj_list = []
        self.tako_list = []
        self.add_item(Rock())
        self.add_item(Ball())
        self.add_item(Ball())
        gras = 0
        while (gras <= (2 * self.size)):
            self.add_item(Grass())
            gras += 1
        while (len(self.tako_list)) < self.num_tako:
            self.add_creature()
        
    def add_item(self, item):
        while True:
            x = random.randrange(0, (self.size))
            y = random.randrange(0, (self.size))
            if type(self.garden_map[y][x]) == Dirt:
                break
        self.garden_map[y][x] = item
        self.obj_list.append(item)
        item.x = x
        item.y = y

    def add_creature(self):
        while True:
            x = random.randrange(0, (self.size))
            y = random.randrange(0, (self.size))
            if type(self.garden_map[y][x]) == Dirt:
                break
        direction = random.randrange(0,3)
        tak_genome = genome.genome.build_default()
        Tak = tak_genome.build(direction, x, y)
        self.garden_map[y][x] = Tak
        self.tako_list.append(Tak)

    def getSensors(self, tako):
        # start with north
        #***
        viewpoint = [tako.x, tako.y]
        sensor = [Dirt, Dirt, Dirt]
        if tako.direction == 0:
            if tako.y == 0:
                viewpoint[1] = self.size
            vp1 = viewpoint[1] - 1
            # if x is 0 ie on extreme left
            if tako.x == 0:
                sensor[0] = self.garden_map[vp1][(self.size - 1)]
            else:
                sensor[0] = self.garden_map[vp1][(viewpoint[0] - 1)]
            sensor[1] = self.garden_map[vp1][viewpoint[0]]
            # if on extreme right
            if tako.x == (self.size - 1):
                sensor[2] = self.garden_map[vp1][0]
            else:
                sensor[2] = self.garden_map[vp1][(viewpoint[0] + 1)]
        #south
        elif tako.direction == 2:
            if tako.y == (self.size - 1):
                viewpoint[1] = -1
            vp1 = viewpoint[1] + 1
            # if x is on extreme right
            if tako.x == (self.size - 1):
                sensor[0] = self.garden_map[vp1][0]
            else:
                sensor[0] = self.garden_map[vp1][(viewpoint[0] + 1)]
            sensor[1] = self.garden_map[vp1][viewpoint[0]]
            # if on extreme left
            if tako.x == 0:
                sensor[2] = self.garden_map[vp1][(self.size - 1)]
            else:
                sensor[2] = self.garden_map[vp1][(viewpoint[0] - 1)]
        #east
        elif tako.direction == 1:
            # if x is extreme right
            if tako.x == (self.size - 1):
                viewpoint[0] = -1
            vp1 = viewpoint[0] + 1
            # if on extreme north
            if tako.y == 0:
                sensor[0] = self.garden_map[(self.size - 1)][vp1]
            else:
                sensor[0] = self.garden_map[(viewpoint[1] - 1)][vp1]
            sensor[1] = self.garden_map[viewpoint[1]][vp1]
            if tako.y == (self.size - 1):
                sensor[2] = self.garden_map[0][vp1]
            else:
                sensor[2] = self.garden_map[(viewpoint[1] + 1)][vp1]
        #west
        elif tako.direction == 3:
            if tako.x ==  0:
                viewpoint[0] = self.size
            vp1 = viewpoint[0] - 1
            # if on extreme south
            if tako.y == (self.size - 1):
                sensor[0] = self.garden_map[0][vp1]
            else:
                sensor[0] = self.garden_map[(viewpoint[1] + 1)][vp1]
            sensor[1] = self.garden_map[viewpoint[1]][vp1]
            if tako.y == 0:
                sensor[2] = self.garden_map[(self.size - 1)][vp1]
            else:
                sensor[2] = self.garden_map[(viewpoint[1] - 1)][vp1]
        return sensor

    def performAction(self, index, tako):
        result = function_array[index](self, tako, tako.last_obj)
        return result

    def forward(self, tako, obj=None):
        #get target square
        #print("forward ho")
        #print(self.garden_map)
        target = self.get_target(tako)
        targ = self.garden_map[target[1]][target[0]]
        result = targ.intersected()
        #check if it's dirt
        if type(self.garden_map[target[1]][target[0]]) == Dirt:
            self.garden_map[tako.y][tako.x] = Dirt()
            self.garden_map[target[1]][target[0]] = tako
            #***
            tako.y = target[1]
            tako.x = target[0]
        #print("did the forward thing")
        #print(self.garden_map)
        return result
    
    def turn_left(self, tako, obj):
        newdir = tako.direction
        newdir -= 1
        if newdir < 0:
            newdir = 3
        tako.direction = newdir
        return None

    def turn_right(self, tako, obj):
        newdir = tako.direction
        newdir += 1
        if newdir > 3:
            newdir = 0
        tako.direction = newdir
        return None

    #for now take eaten object out if grass
    def eat(self, tako, obj):
        target = self.get_target(tako)
        tako.last_obj = self.garden_map[target[1]][target[0]]
        if type(tako.last_obj) == Grass:
            self.obj_list.remove(tako.last_obj)
            self.garden_map[target[1]][target[0]] = Dirt()
            self.add_item(Grass())
        x = tako.last_obj
        result = x.eaten()
        return result

    #for now take played-with object out
    def play(self, tako, obj):
        target = self.get_target(tako)
        tako.last_obj = self.garden_map[target[1]][target[0]]
        x = tako.last_obj
        result = x.played()
        if type(self.garden_map[target[1]][target[0]]) == Ball:
            self.obj_list.remove(self.garden_map[target[1]][target[0]])
            self.garden_map[target[1]][target[0]] = Dirt()
            self.add_item(Ball()) 
        return result

    def get_target(self, tako):
        #***
        # target is def. x, y now, check that it's used as such
        target = [tako.x, tako.y]
        # looking north
        if tako.direction == 0:
            # if on extreme north edge
            if tako.y == 0:
                target[1] = self.size - 1
            else:
                target[1] = tako.y - 1
        #east
        elif tako.direction == 1:
            if tako.x == self.size - 1:
                target[0] = 0
            else:
                target[0] = tako.x + 1
        #south
        elif tako.direction == 2:
            if tako.y == self.size - 1:
                target[1] = 0
            else:
                target[1] = tako.y + 1
        #west
        elif tako.direction == 3:
            if tako.x == 0:
                target[0] = self.size - 1
            else:
                target[0] = tako.x - 1
        return target


function_array = [Garden.forward, Garden.turn_left, Garden.turn_right, Garden.eat, Garden.play]
