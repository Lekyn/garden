## A widget is a kind of object in a Garden
## It can be interactable or not
## It holds responses to different actions
## It will someday have a color and smell and weight

class Widget:
    #a widget has a position
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    # functions should be implemented in subclasses
    # if they are relevant to that widget type
    def eaten(self):
        return ("boredom", -1)

    def played(self):
        return ("boredom", -1)

    # if creature tries to walk into widget,
    def intersected(self):
        return ("boredom", -1)
    #finds appropriate graphics
    def display(self):
        return

class Dirt(Widget):
    node = 0
    #things can grow here eventually
    #creatures can walk on it
    def intersected(self):
        return

    def display(self):
        return "dirt.png"

class Grass(Widget):
    node = 1
    def eaten(self):
        return ("hunger", 30)

    def display(self):
        return "grass.png"

class Rock(Widget):
    node = 3
    def played(self):
        return ("boredom", -10)

    def display(self):
        return "rock.png"

    def eaten(self):
        return ("pain", 30)

class Ball(Widget):
    node = 2
    #should move eventually
    def played(self):
        return ("boredom", 30)

    def display(self):
        return "toy.png"
