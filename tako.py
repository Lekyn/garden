from pybrain.rl.agents import LearningAgent
from pybrain.structure import LinearLayer, SigmoidLayer
from pybrain.structure import FeedForwardNetwork, FullConnection, IdentityConnection, RecurrentNetwork
from pybrain.structure.modules.neuronlayer import NeuronLayer
from pybrain.structure.parametercontainer import ParameterContainer
from widget import Widget
import scipy

# a Tako is a creature
# it has a neural net (agent)
# someday, it will have a genetics-like system
# it has drives (boredom, hunger, etc)
# someday, it will have an age

# it is meant to live in a Garden
class Tako(Widget):
    node = 4
    
    def __init__(self, dire, x, y, genome):
        self.direction = dire
        self.x = x
        self.y = y
        self.genome = genome
        self.hunger = 150
        self.boredom = 150
        self.pain = 0
        self.last_hunger = 150
        self.last_boredom = 150
        self.last_pain = 0
        self.last_obj = None
        #self.net = FeedForwardNetwork()
        self.net = RecurrentNetwork()
        self.net.sequential = False
        
    def make_net(self):
        net = FeedForwardNetwork()
        vision = LinearLayer(5, name="Vision")
        vision.x = 0
        vision.y = 0
        vision.color = '#FF0000'
        vision.orient = "vertical"
        action = LinearLayer(5, name="Action")
        action.x = 28
        action.y = 0
        action.color = '#00FFFF'
        action.orient = "vertical"
        drive = DrivesSquashLayer(3, name="Drive")
        drive.x = 0
        drive.y = 23
        drive.color = '#0000FF'
        drive.orient = "horizontal"
        
        net.addInputModule(vision)
        net.addInputModule(drive)
        net.addOutputModule(action)

        stm = LinearLayer(5, name="STM")
        stm.x = 18
        stm.y = 20
        stm.orient = "horizontal"
        stm.color = '#FF00FF'
        net.addModule(stm)

        vision_action = FullConnection(vision, action, name="vision->action")
        drive_action = FullConnection(drive, action, name="drive->action")

        net.addConnection(vision_action)
        net.addConnection(drive_action)

        test_stm = MaxOnlyConnection(action, stm, name="test_stm")
        net.addConnection(test_stm)

        net.sortModules()
        return net
    
    #drives go DOWN over time
    def update(self):
        self.last_hunger = self.hunger
        self.last_boredom = self.boredom
        self.last_pain = self.pain
        self.hunger -= 0.5
        self.boredom -= 0.5
        if self.pain > 0:
            self.pain = self.pain*.6
            if self.pain < 1:
                self.pain = 0
        
    #TODO: make this better
    def update_drives(self, drive, modifier):
        if drive == "hunger":
            self.hunger += modifier
            if self.hunger > 150:
                self.hunger = 150
        elif drive == "boredom":
            self.boredom += modifier
            if self.boredom > 150:
                self.boredom = 150
        elif drive == "pain":
            self.pain += modifier

        
    def modify(self, result):
        print(result)
        if result is not None:
            for x in range(len(result)):
                if x%2 == 0:
                    drive = result[x]
                else:
                    modifier = result[x]
                    self.update_drives(drive, modifier)



class MaxOnlyConnection(IdentityConnection, ParameterContainer):

    def __init__(self, *args, **kwargs):
        IdentityConnection.__init__(self, *args, **kwargs)
        ParameterContainer.__init__(self, self.indim)
        
    # only outputs the maximum from input buffer
    # used for short-term action memory (such that actual action is the only
    # one that gets input into memory)
    def _forwardImplementation(self, inbuf, outbuf):
        curmax = inbuf[0]
        maxnum = 0
        for x in range(len(inbuf)):
            if inbuf[x] > curmax:
                curmax = inbuf[x]
                maxnum = x
        outbuf[maxnum] = 1
        
    def _backwardImplementation(self, outerr, inerr, inbuf):
        inerr += outerr

    def whichBuffers(self, paramIndex):
        """Return the index of the input module's output buffer and
        the output module's input buffer for the given weight."""
        return paramIndex % self.inmod.outdim, paramIndex

class DrivesSquashLayer(NeuronLayer):

    def __init__(self, dim, name=None):
        super().__init__(dim, name)

    def _forwardImplementation(self, inbuf, outbuf):
        outbuf[:] = DrivesSquashLayer.squash(inbuf)

    # copied from sigmoid. Correct??
    def _backwardImplementation(self, outerr, inerr, outbuf, inbuf):
        inerr[:] = outbuf * (1 - outbuf) * outerr
        
    #returns squashed value inflecting on 75, range 5~0
    #TODO try variations on this sometime. maybe in genetics?
    def squash(x):
        return (5/(1+(scipy.exp(-x + 75))))


class STMLayer(NeuronLayer):

    def __init__(self, dim, name=None):
        super().__init__(dim, name)
        self.last_in = None
        self.mem = [0 for x in range(dim)]

    def _forwardImplementation(self, inbuf, outbuf):
        for x in range(len(inbuf)):
            if inbuf[x] == 1:
                self.last_in = x
        for x in range(len(self.mem)):
            if x != self.last_in:
                self.mem[x] = STMLayer.decay(self.mem[x])
            else:
                self.mem[x] += inbuf[x]
        outbuf[:] = self.mem
    
    # copied from linear. still have no idea what I'm doing
    def _backwardImplementation(self, outerr, inerr, outbuf, inbuf):
        inerr[:] = outerr

    def decay(x):
        x = x/2
        if x < 1:
            x = 0
        return x
    
