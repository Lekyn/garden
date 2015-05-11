from random import randint, gauss, uniform
from pybrain.structure import LinearLayer, FullConnection, IdentityConnection
from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import ENAC
import tako


#TODO uh, might want to do some sanity checking
#f.e. connection genes are not gonna read properly
#if they are *before* lobes....

class genome:
    #TODO do both strands need to be equal? *shouldn't* have to be
    def __init__(self, strand_1, strand_2):
        self.strand_1 = strand_1
        self.strand_2 = strand_2

    def __str__(self):
        result = "Strand 1: "
        for gene in self.strand_1:
            result = result + gene.__str__()
        result = result + "\nStrand 2: "
        for gene in self.strand_2:
            result = result + gene.__str__()
        return result

    def mutate(self):
        for gene in self.strand_1:
            gene.mutate()
        for gene in self.strand_2:
            gene.mutate()

    def recombine(self, other_genome):
        parent1_strand = []
        parent2_strand = []
        #pick a crossover point (that is to say, pick last gene before crossover)
        #ie anything between 0 and strand len-1
        crossover = randint(0, (len(self.strand_1) - 1))
        print(crossover)
        #then pick strand1 up to there and strand2 after there
        x = 0
        while x <= crossover:
            parent1_strand.append(self.strand_1[x])
            x += 1
        while x < len(self.strand_2):
            parent1_strand.append(self.strand_2[x])
            x += 1
        #repeat for other parent's genome
        crossover = randint(0, (len(other_genome.strand_1) - 1))
        print(crossover)
        x = 0
        while x <= crossover:
            parent2_strand.append(other_genome.strand_1[x])
            x += 1
        while x < len(other_genome.strand_2):
            parent2_strand.append(other_genome.strand_2[x])
            x += 1
        #and mutate
        result = genome(parent1_strand, parent2_strand)
        result.mutate()
        #then return the genome so we can do something with it
        return result

    #use genome to build a new Tako
    #TODO do both strands need to be equal? they shouldn't have to be
    def build(self, direction, x, y):
        new_tako = tako.Tako(direction, x, y, self)
        for gen in range(len(self.strand_1)):
            self.strand_1[gen].read(self.strand_2[gen], new_tako)
        #take care of net & make agent
        new_tako.net.sortModules()
        learner = ENAC()
        new_tako.agent = LearningAgent(new_tako.net, learner)
        return new_tako

    #for testing
    def build_default():
        gen = genome([],[])
        #let's make mutable fields for synapse genes!
        #all set at mutation rate of 15 (= 5%) for now
        drive_action_muts = []
        action_vision_muts = []
        stm_muts = []
        stm_action_muts = []
        with open("synapses_list.txt") as file:
            current_list = drive_action_muts
            for in_line in file:
                if in_line == "driveaction\n":
                    current_list = drive_action_muts
                elif in_line == "actionvision\n":
                    current_list = action_vision_muts
                elif in_line == "STM\n":
                    current_list = stm_muts
                elif in_line == "STMaction\n":
                    current_list = stm_action_muts
                elif in_line[0:3] == "min":
                    minimum = float(in_line[7:])
                elif in_line[0:3] == "max":
                    maximum = float(in_line[7:])
                    mut = mutable_field(minimum, maximum, 15, 0.3, 0.3)
                    current_list.append(mut)
        gen.strand_1.append(lobe_gene(1, False, False, False, '#FF0000', 0, 0,
                                      "vertical", "Vision", 5, LinearLayer, "input"))
        gen.strand_1.append(lobe_gene(1, False, False, False, '#00FFFF', 28, 0,
                                      "vertical", "Action", 5, LinearLayer, "output"))
        gen.strand_1.append(lobe_gene(1, False, False, False, '#0000FF', 0, 23,
                                      "horizontal", "Drive", 3, tako.DrivesSquashLayer, "input"))
        gen.strand_1.append(lobe_gene(1, False, False, False, '#FF00FF', 18, 20,
                                      "horizontal","STM", 5, tako.STMLayer, "middle"))
        gen.strand_1.append(connection_gene(1, False, False, False, "vision->action",
                                            "Vision", "Action", FullConnection, False))
        gen.strand_1.append(connection_gene(1, False, False, False, "drive->action",
                                            "Drive", "Action", FullConnection, False))
        gen.strand_1.append(connection_gene(1, False, False, False, "test_stm",
                                            "Action", "STM", tako.MaxOnlyConnection, False))
        gen.strand_1.append(connection_gene(1, False, False, False, "test_recur",
                                            "STM", "Action", IdentityConnection, True))
        for x in range(len(drive_action_muts)):
            dom = randint(0, 10)
            new_synapse = synapse_gene(dom, True, False, False, "drive->action",
                                       x, drive_action_muts[x])
            gen.strand_1.append(new_synapse)
        for x in range(len(action_vision_muts)):
            dom = randint(0, 10)
            new_synapse = synapse_gene(dom, True, False, False, "vision->action",
                                       x, action_vision_muts[x])
            gen.strand_1.append(new_synapse)
        for x in range(len(stm_muts)):
            dom = randint(0, 10)
            new_synapse = synapse_gene(dom, True, False, False, "test_stm",
                                       x, stm_muts[x])
            gen.strand_1.append(new_synapse)
        for x in range(len(stm_action_muts)):
            dom = randint(0, 10)
            new_synapse = synapse_gene(dom, True, False, False, "test_recur",
                                        x, stm_action_muts[x])
            gen.strand_1.append(new_synapse)
        #duplicate on other chromosome
        for x in range(len(gen.strand_1)):
            gen.strand_2.append(gen.strand_1[x])
        return gen
        
class gene:

    #all genes have:
    #a dominance rating (int)
    #a mutability (bool) determines if can mutate
    #a duplicability (bool)
    #a cutability (bool) determines if can be cut from genome
    #specific mutable parts/rates are determined by subclasses
    def __init__(self, dominance, mutability, duplicate, cut):
        self.dominance = dominance
        self.mutability = mutability
        self.duplicate = duplicate
        self.cut = cut

    #defined in subclasses
    def mutate(self):
        return

    #uses genes to build a new Tako
    #might also be used during life to switch-on genes
    #defined in subclasses                         
    def read(self, other_gene, tako):
        return

class lobe_gene(gene):

    #woo, lots of args
    #color is taken as a hex-format string
    #x, y are int
    #orient, name are strings
    #num is number of neurons (int)
    #subtype is brain lobe class (might change later to be more flexible?)
    #io = input or output or middle layer (string)
    def __init__(self, dominance, mutability, duplicate, cut,
                 color, x, y, orient, name, num, subtype, io):
        super().__init__(dominance, mutability, duplicate, cut)
        self.color = color
        self.x = x
        self.y = y
        self.orient = orient
        self.name = name
        self.num = num
        self.subtype = subtype
        self.io = io

    def __str__(self):
        result = "\n" + self.name
        result = result + " " + str(self.subtype) + " " + str(self.num) + " "
        return result

    #TODO: implement if I can think of way it could reasonably mutate
    def mutate(self):
        if self.mutability:
            return
        
    def read(self, other_gene, tako):
        #check if this gene is being read
        #brain lobes do not co-dominate
        read_gene = self
        if self.dominance < other_gene.dominance:
            read_gene = other_gene
        #if they have the same dominance, let's randomly decide
        elif self.dominance == other_gene.dominance:
            x = randint(0, 1)
            if x == 0:
                read_gene = other_gene
        #okay, let's make a brain lobe!
        new_layer = read_gene.subtype(read_gene.num, name=read_gene.name)
        new_layer.x = read_gene.x
        new_layer.y = read_gene.y
        new_layer.color = read_gene.color
        new_layer.orient = read_gene.orient
        if self.io == "input":
            tako.net.addInputModule(new_layer)
        elif self.io == "output":
            tako.net.addOutputModule(new_layer)
        else:
            tako.net.addModule(new_layer)
        
        
class connection_gene(gene):

    # name, input_lobe, output_lobe are strings
    # subtype is connection class (might change later?)
    # recur is bool that marks whether or not this is a recurrent connection
    def __init__(self, dominance, mutability, duplicate, cut,
                 name, input_lobe, output_lobe, subtype, recur):
        super().__init__(dominance, mutability, duplicate, cut)
        self.name = name
        self.input_lobe = input_lobe
        self.output_lobe = output_lobe
        self.subtype = subtype
        self.recur = recur

    def __str__(self):
        result = "\n" + self.name
        result = result + " " + str(self.subtype) + " "
        return result

    # TODO implement if need be
    def mutate(self):
        if self.mutability:
            return

    def read(self, other_gene, tako):
        #check if this gene is being read
        #connections do not co-dominate
        read_gene = self
        if self.dominance < other_gene.dominance:
            read_gene = other_gene
        #if they have the same dominance, let's randomly decide
        elif self.dominance == other_gene.dominance:
            x = randint(0, 1)
            if x == 0:
                read_gene = other_gene
        #okay, let's make a connection~
        for x in tako.net.modules:
            if x.name == read_gene.input_lobe:
                incoming = x
            elif x.name == read_gene.output_lobe:
                outgoing = x
        new_connect = read_gene.subtype(incoming, outgoing, name = read_gene.name)
        if not self.recur:
            tako.net.addConnection(new_connect)
        else:
            tako.net.addRecurrentConnection(new_connect)


class synapse_gene(gene):

    #these determine the range of STARTING values for each synapse
    #though of course learning can change them considerably
    #parent_conn (str) = connection this synapse is in
    #connect_num = which connection this gene controls
    #mut_field (mutable_field) contains max value, min value, mut rate, sigma(=0.3),
    #    minimum difference (=0.3)
    def __init__(self, dominance, mutability, duplicate, cut, parent_conn,
                 connect_num, mut_field):
        super().__init__(dominance, mutability, duplicate, cut)
        self.parent_conn = parent_conn
        self.connect_num = connect_num
        self.mut_field = mut_field

    def __str__(self):
        result = "\n" + self.parent_conn
        result = result + " " + str(self.connect_num) + " " + self.mut_field.__str__()
        return result

    def mutate(self):
        if self.mutability:
            self.mut_field.check_mutate()

    def read(self, other_gene, tako):
        #check if this gene is being read
        #synapses DO co-dominate
        read_gene = self
        if self.dominance < other_gene.dominance:
            read_gene = other_gene
        #if they have same dominance, we'll average min/max values
        if self.dominance == other_gene.dominance:
            avg_min = (self.mut_field.minimum + other_gene.mut_field.minimum) / 2
            avg_max = (self.mut_field.maximum + other_gene.mut_field.maximum) / 2
            weight = uniform(avg_min, avg_max)
        else:
            weight = uniform(read_gene.mut_field.minimum, read_gene.mut_field.maximum)
        #now find connection so we can overwrite synapse
        connection = None
        for layer in tako.net.connections:
            for conn in tako.net.connections[layer]:
                if conn.name == self.parent_conn:
                    connection = conn
        #else it's a recurrent layer
        if connection == None:
            for layer in tako.net.recurrentConns:
                if layer.name == self.parent_conn:
                    connection = layer
        connection.params[self.connect_num] = weight
            
    
#class for fields that mutate
#for now, just synapse, but could have color or something in future
class mutable_field:
    #minimum (float) is current min value
    #maximum (float) is current maximum value
    #rate (int) is mutation rate (out of 300)
    #sig (float) is sigma for mutation
    #dif (float) is minimum difference (max and min can't get closer than this)
    def __init__(self, minimum, maximum, rate, sig, min_dif):
        self.maximum = maximum
        self.minimum = minimum
        self.rate = rate
        self.sig = sig
        self.min_dif = min_dif

    def __str__(self):
        result = "Min: " + str(self.minimum) + " Max: " + str(self.maximum)
        result = result + " Rate: " + str(self.rate)
        return result

    def check_mutate(self):
        rolled_num = randint(0, 300)
        if rolled_num < self.rate:
            return False
        else:
            self.mutate()
            return True

    def mutate(self):
        x = randint(0, 20)
        #if mutating the rate, use different sigma
        if x == 20:
            sigma = 0.8
        else:
            sigma = self.sig
        change = gauss(0, sigma)
        if x <= 9:
            self.minimum = self.minimum + change
        elif x <= 19:
            self.maximum = self.maximum + change
        else:
            #rate is int
            self.rate = round(self.rate + change)
            #check not too high/low
            if self.rate < 0:
                self.rate = 0
            elif self.rate > 300:
                self.rate = 300
            #check to make sure not too close to each other
        if self.maximum - self.minimum < self.min_dif:
            if x <= 9:
                self.minimum = self.maximum - self.min_dif
            else:
                self.maximum = self.minimum + self.min_dif
