
from garden import Garden
from garden_task import GardenTask
from pybrain.structure import RecurrentNetwork
from tako import Tako
from widget import *
import time

from multi_agent_experiment import *

import os, sys
import pygame
import math
from pygame.locals import *

garden_size = 8
tako_number = 3


class garden_game:

    def __init__(self):
        pygame.init()

        global env
        env = Garden(garden_size, tako_number)
        global task
        task = GardenTask(env)
        global experiment
        experiment = Continuous_MA_Experiment_Tako(task, env.tako_list)
        
        self.width = (garden_size * 50) + 400
        if garden_size < 8:
            self.height = 400
        else:
            self.height = (garden_size * 50)
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Garden')
        self.clock = pygame.time.Clock()

        self.neur_background = pygame.Surface(self.screen.get_size())
        self.neur_background.fill((200, 255, 200))

        self.selected_Tako = None
        self.neur = None
        self.selected_Neuron = None

    def MainLoop(self):
        self.load_sprites()
        while 1:
            for event in pygame.event.get():
                if event.type == QUIT: 
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    # returns x,y with origin in upper left
                    x = event.pos[0]
                    y = event.pos[1]
                    # if on the left part of the screen
                    if x < (garden_size * 50):
                        x = math.floor(x/50)
                        y = math.floor(y/50)
                        if type(env.garden_map[y][x]) == Tako:
                            self.selected_Tako = env.garden_map[y][x]
                            self.neur = None
                        else:
                            self.selected_Tako = None
                            self.neur = None
                    #if on the other part of the screen, see if clicked on neuron
                    else:
                        if self.selected_Tako is not None:
                            clicked_sprite = [s for s in self.neur_sprites if
                                              s.rect.collidepoint(event.pos)]
                            if clicked_sprite != []:
                                self.selected_Neuron = clicked_sprite[0]
                            else:
                                self.selected_Neuron = None
            #see if all are dead
            if len(env.tako_list) == 0:
                print("Tako are dead :(")
                return
            #let experiment go a step
            experiment.doInteractionsAndLearn(1)
            self.screen.blit(self.neur_background, (0, 0))
            #update sprites, then draw them
            self.tile_sprites.update()
            self.tako_spritelist.update()
            self.background_sprites.draw(self.screen)
            self.tile_sprites.draw(self.screen)
            self.tako_spritelist.draw(self.screen)

            if self.selected_Tako is not None:
                self.render_neural_labels()
                if self.neur == None:
                    self.neur = self.render_neurons()
                    self.neur_sprites = pygame.sprite.Group()
                    for i in range(len(self.neur)):
                        self.neur_sprites.add(self.neur[i])
                    pygame.sprite.RenderPlain(self.neur_sprites)
                    self.neur_sprites.draw(self.screen)
                else:
                    self.neur_sprites.update()
                    self.neur_sprites.draw(self.screen)
                for x in self.neur_sprites:
                    x.draw_overlay(self.selected_Neuron, self.screen)
                    x.draw_connections(self.selected_Tako.net,
                                       self.selected_Neuron, self.screen)
                #add text indicating selected neuron's activation
                if self.selected_Neuron is not None:
                    font = pygame.font.Font(None, 25)
                    text = font.render(("Selected neuron's activation:" +
                                        str(round(self.selected_Neuron.value, 3))), 1, (0, 0, 0))
                    textpos = text.get_rect(left = (garden_size*50 + 100))
                    self.screen.blit(text, textpos)
                    
            #oh, and display which step we're on
            if pygame.font:
                font = pygame.font.Font(None, 18)
                text = font.render(str(experiment.stepid), 1, (255, 255, 255))
                textpos = text.get_rect(centerx=(self.screen.get_width() * 0.25))
                self.screen.blit(text, textpos)
            # see if any are dead
            else:
                for tako in env.tako_list:
                    if tako.hunger <= 0:
                        env.tako_list.remove(tako)
            pygame.display.flip()
            #cap at x fps
            self.clock.tick(10)
            for tako in env.tako_list:
                tako.net.reset()

    def load_sound(name):
        class NoneSound:
            def play(self): pass
        if not pygame.mixer:
            return NoneSound()
        fullname = os.path.join('data', name)
        #try:
        sound = pygame.mixer.Sound(fullname)
        #except pygame.error, message:
         #   print 'Cannot load sound:', wav
          #  raise SystemExit, message
        return sound
    
    def load_sprites(self):
        self.dirt_background()
        self.tiles = get_tiles()
        self.tako_spritelist = pygame.sprite.Group()
        for i in range(len(env.tako_list)):
            self.tako_spritelist.add(Tako_Sprite(env.tako_list[i]))
        self.background_sprites = pygame.sprite.Group()
        for i in range(len(self.background)):
            self.background_sprites.add(self.background[i])
        self.background_sprites = pygame.sprite.RenderPlain(self.background)
        self.tile_sprites = Tile_Group((self.tiles))
        
    #sets background to a bunch of dirt tiles
    def dirt_background(self):
        self.background = []
        for y in range(garden_size):
            for x in range(garden_size):
                new_tile = Tile(Dirt(x, y))
                self.background.append(new_tile)

    def render_neural_labels(self):
        x_origin = (garden_size * 50) + 10
        y_origin = 50
        #this gets at layers
        for x in self.selected_Tako.agent.module.modules:
            font = pygame.font.Font(None, 36)
            text = font.render(str(x.name), 1, (0, 0, 0))
            textpos = text.get_rect()
            textpos.move_ip((x.x)*10 + x_origin, (x.y)*10 + y_origin)
            self.screen.blit(text, textpos)

    def render_neurons(self):
        net = self.selected_Tako.agent.module.modules
        spr_list = []
        for layer in net:
            neurons = layer.outputbuffer[0]
            if type(neurons) == list:
                neurons = neurons[0]
            neurons = neurons.tolist()
            for node in range(len(neurons)):
                new_sprite = Neuron_sprite(layer, node)
                spr_list.append(new_sprite)
        return spr_list
    

def get_tiles():
    tiles = []
    for x in range(len(env.obj_list)):
        new_tile = Tile(env.obj_list[x])
        tiles.append(new_tile)
    return tiles


class Neuron_sprite(pygame.sprite.Sprite):
    x_origin = (garden_size * 50) + 10
    y_origin = 50
    #takes a layer, neuron #
    def __init__(self, layer, node):
        pygame.sprite.Sprite.__init__(self)
        self.value = layer.outputbuffer[0][node]
        self.layer = layer
        self.node = node
        if node == 0:
            self.left = (layer.x * 10) + self.x_origin
            self.top = (layer.y * 10) + self.y_origin + 24
        else:
            if layer.orient == "vertical":
                self.left = (layer.x * 10) + self.x_origin
                self.top = ((layer.y * 10) + (node * 30)) + self.y_origin + 24
            elif layer.orient == "horizontal":
                self.left = ((layer.x * 10) + (node * 30)) + self.x_origin
                self.top = (layer.y * 10) + self.y_origin + 24
        self.image, self.rect = load_image("neuron.png", pygame.Color('#FF00FF'))
        self.rect = pygame.Rect((self.left, self.top), (20, 20))
        
    def update(self):
        self.value = self.layer.outputbuffer[0][self.node]
        
    #does colored overlay. takes selected neuron and screen to draw on
    def draw_overlay(self, selected, screen):
        if selected is not None:
            if selected == self:
                overlay = pygame.Surface((20, 20))
                overlay.fill(pygame.Color(self.layer.color))
                overlay.set_alpha(self.compute_alpha(self.value))
                screen.blit(overlay, (self.left, self.top))
            else:
                return
        else:
            overlay = pygame.Surface((20, 20))
            overlay.fill(pygame.Color(self.layer.color))
            overlay.set_alpha(self.compute_alpha(self.value))
            screen.blit(overlay, (self.left, self.top))

    #takes neuron's output, transforms to alpha value (0~255)
    #produces different alphas for -10 ~ 10
    def compute_alpha(self, value):
        alpha = int(value * 12.7)
        alpha += 127
        if alpha < 0:
            alpha = 0
        elif alpha > 255:
            alpha = 255
        return alpha

    #draw connections between neurons - needs screen to draw on
    #as well as connections to look through
    def draw_connections(self, net, selected, screen):
        #first see if there is a selected neuron
        if selected is not None:
            if selected != self:
                return False
        conns = net.connections
        conn = conns[self.layer]
        #if layer has connections
        if conn != []:
            #find all connections
            conn = conn[0]
            self.make_conns(conn, screen)
        #now to draw recurrent connections!
        if type(net) == RecurrentNetwork:
            for connection in net.recurrentConns:
                self.make_conns(connection, screen)
        
    def make_conns(self, conn, screen):
        for cc in range(len(conn.params)):
            #get list
            x = conn.whichBuffers(cc)
            #and make co-ordinates
            if x[0] == self.node:
                other = conn.outmod
                othernode = int(x[1])
                if othernode == 0:
                    otherleft = (other.x * 10) + self.x_origin
                    othertop = (other.y * 10) + self.y_origin + 24
                else:
                    if other.orient == "vertical":
                        otherleft = (other.x * 10) + self.x_origin
                        othertop = (((other.y * 10) + (othernode * 30))
                                    + self.y_origin + 24)
                    elif other.orient == "horizontal":
                        otherleft = (((other.x * 10) + (othernode * 30)) +
                                self.x_origin)
                        othertop = (other.y * 10) + self.y_origin + 24
                # compute color (white to black) depending on value
                shade = conn.params[cc]
                shade = self.compute_alpha(shade)
                shade = pygame.Color(shade, shade, shade)
                if self.layer.orient == "horizontal":
                    pygame.draw.line(screen, shade,
                                     ((self.left + 10), self.top - 2),
                                        (otherleft, othertop + 10), 2)
                else:
                    pygame.draw.line(screen, shade, ((self.left + 20),
                                        self.top + 9),
                                        (otherleft, othertop + 10), 2)
    
def print_net(network):
    for mod in network.modules:
        for conn in network.connections[mod]:
            print(conn)
            for cc in range(len(conn.params)):
                print(conn.whichBuffers(cc), conn.params[cc])
    for conn in network.recurrentConns:
        print(conn)
        for cc in range(len(conn.params)):
            print(conn.whichBuffers(cc), conn.params[cc])

def save_net(network, name):
    file = open("saved nets/" + name + ".txt", "a")
    for mod in network.modules:
        for conn in network.connections[mod]:
            file.write(str(conn) + "\n")
            for cc in range(len(conn.params)):
                string = [str(conn.whichBuffers(cc)), str(conn.params[cc])]
                string = str(string) + "\n"
                file.write(string)
            file.write("\n")
    for conn in network.recurrentConns:
        file.write(str(conn) + "\n")
        for cc in range(len(conn.params)):
                string = [str(conn.whichBuffers(cc)), str(conn.params[cc])]
                string = str(string) + "\n"
                file.write(string)
                file.write("\n")
    file.close()

def overwrite_net(network, name):
    with open("saved nets/" + name + ".txt") as file:
        for in_line in file:
            #this line can be
            #1) a newline
            #2) a connection name  
            if in_line[0] == "<":
                current_conn = None
                connection_name = in_line.split("'", maxsplit=3)[1]
                #network.connections maps layer to connections from layer
                for x in network.connections:
                    #then look through entries for connections (if they exist)
                    for conn in network.connections[x]:
                        #if we find the connection we're looking for
                        if conn.name == connection_name:
                            #that's the one we're going to work on
                            current_conn = conn
                            current_counter = 0
                if current_conn == None:
                    for conn in network.recurrentConns:
                        if conn.name == connection_name:
                            current_conn = conn
            #3) info about weights
            elif in_line[0] == "[":
                #first, grab weight
                weight = in_line.partition(" '")
                weight = weight[2][:-3]  #"']\n"
                weight = float(weight)
                #now, set weight
                current_conn.params[current_counter] = weight
                #put counter up, too
                current_counter += 1
            

class Tako_Sprite(pygame.sprite.Sprite):
    dir_map = {0: "north.png", 1: "east.png", 2: "south.png", 3: "west.png"}
    
    def __init__(self, tako):
        pygame.sprite.Sprite.__init__(self)
        img = self.dir_map[tako.direction]
        self.image, self.rect = load_image(img, pygame.Color('#FF00FF'))
        self.tako = tako
        self.rect = pygame.Rect((tako.x * 50), (tako.y * 50), 50, 50)

    def update(self):
        self.tako.update()
        if self.tako.hunger <= 0:
            return
        if task.last_action == 0:
            self.rect = pygame.Rect((self.tako.x * 50),
                                    (self.tako.y * 50), 50, 50)
        elif task.last_action == 1 or task.last_action == 2:
            self.image, temp = load_image(self.dir_map[self.tako.direction], -1)
            
                
class Tile_Group(pygame.sprite.Group):

    def update(self):
        if task.last_action == 3 or task.last_action == 4:
            news = get_tiles()
            self.empty()
            self.add(news)


class Tile(pygame.sprite.Sprite):
    #gets from obj: img (str), leftmost position, topmost position
    def __init__(self, obj):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(obj.display(), pygame.Color('#FF00FF'))
        self.rect = pygame.Rect(obj.x * 50, obj.y * 50, 50, 50)

    #def update(self):
        #if something is eaten or played with
     #   if task.last_action == 3 or task.last_action == 4:
        


def load_image(name, colorkey=None):
    fullname = os.path.join('img', name)
    #try:
    image = pygame.image.load(fullname)
    #except pygame.error, message:
    #    print 'Cannot load image:', name
    #    raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()
        

if __name__ == "__main__":
    MainWindow = garden_game()
    MainWindow.MainLoop()
