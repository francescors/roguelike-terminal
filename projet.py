import copy
import math
import random
import time

# exceptions 


def _find_getch():
   """Single char input, only works only on mac/linux/windows OS terminals"""
   try:
       import termios
   except ImportError:
       # Non-POSIX. Return msvcrt's (Windows') getch.
       import msvcrt
       return lambda: msvcrt.getch().decode('utf-8')
   # POSIX system. Create and return a getch that manipulates the tty.
   import sys, tty
   def _getch():
       fd = sys.stdin.fileno()
       old_settings = termios.tcgetattr(fd)
       try:
           tty.setraw(fd)
           ch = sys.stdin.read(1)
       finally:
           termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
       return ch
   return _getch

def sign(x):
    if x > 0:
        return 1
    return -1

class Coord(object):
    """Implementation of a map coordinate"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return '<' + str(self.x) + ',' + str(self.y) + '>'

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)

    def distance(self, other):
        """Returns the distance between two coordinates."""
        d = self - other
        return math.sqrt(d.x * d.x + d.y * d.y)

    cos45 = 1 / math.sqrt(2)

    def direction(self, other):
        """Returns the direction between two coordinates."""
        d = self - other
        cos = d.x / self.distance(other)
        if cos > Coord.cos45:
            return Coord(-1, 0)
        elif cos < -Coord.cos45:
            return Coord(1, 0)
        elif d.y > 0:
            return Coord(0, -1)
        return Coord(0, 1)

class Element(object):
    """Base class for game elements. Have a name.
        Abstract class."""

    def __init__(self, name, abbrv=""):
        self.name = name
        if abbrv == "":
            abbrv = name[0]
        self.abbrv = abbrv

    def __repr__(self):
        return self.abbrv

    def description(self):
        """Description of the element"""
        return self.name

    def meet(self, hero):
        """Makes the hero meet an element. Not implemented. """
        raise NotImplementedError('Abstract Element')

    def getName(self):
        """Return the name of the element"""
        return self.name


class Creature(Element):
    """A creature that occupies the dungeon.
        Is an Element. Has hit points and strength."""

    def __init__(self, name, hp, abbrv="", strength=1, armure=0, xp=0):
        Element.__init__(self, name, abbrv)
        self.hp = hp
        self.xp = xp
        self.strength = strength
        self._or = []
        self.armure = armure

    def description(self):
        """Description of the creature"""
        return Element.description(self) + " ♥︎:" + str(self.hp) + " "

    def meet(self, other):
        """The creature is encountered by an other creature.
            The other one hits the creature. Return True if the creature is dead."""
        self.hp -= (other.strength - self.armure)

        if self.name is "Ghost":
           self.abbrv = "G"

        theGame().addMessage("The " + other.name + " hits the " + self.description())
        
        if self.hp > 0:
           return False

        other.xp+=1
        if other.xp>=3:
           other.xp=0
           
           other.strength+=0.5
           other.niveau+=1

           other.hpmax+=1
           other.hp=other.hpmax
        return True

class CreatureR(Creature):
    """A creature that occupies the dungeon.
        Is an Element. Has hit points and strength.
        The creature does 2 actions"""

    def __init__(self, name, hp, abbrv="", strength=1, armure=0, xp=0):
        Creature.__init__(self, name, hp, abbrv, strength, armure, xp)


class Hero(Creature):
    """The hero of the game.
        Is a creature. Has an inventory of elements. """

    def __init__(self, name="Hero", hp=10, abbrv="★", strength=2, invisible=False, armure=0, count=0, hpmax=15, xp=0, niveau=0):
        Creature.__init__(self, name, hp, abbrv, strength, armure)
        self._inventory = []
        self.invisible = invisible
        self.count = count
        self.niveau = niveau
        self.xp = xp
        self.hpmax = hpmax
        self.armure = armure

    def description(self):
        """Description of the hero"""
        return Creature.description(self) + "inventaire" + str(self._inventory) + " or:" + str(len(self._or)) + " xp:" + str(self.xp) + " niv:" + str(self.niveau)+" armure:" + str(self.armure)

    def fullDescription(self):
        """Complete description of the hero"""
        res = ''
        for e in self.__dict__:
            if e[0] != '_':
                res += '> ' + e + ' : ' + str(self.__dict__[e]) + '\n'
        res += '> INVENTORY : ' + str([x.name for x in self._inventory])
        return res

    def checkEquipment(self, o):
        """Check if o is an Equipment."""
        if not isinstance(o, Equipment):
            raise TypeError('Not a Equipment')

    def take(self, elem):
        """The hero takes adds the equipment to its inventory"""
        self.checkEquipment(elem)
        if elem.getName() == "gold":
            self._or.append(elem)
            return True
        if self.checkInventory() == False:
            print("You have 10 items in your inventory, you need to remove one")
            return False
        self._inventory.append(elem)
        return True
         
    def checkInventory(self):
        """Check the number of elements in inventory"""
        """Verifie le nombre d'elements dans inventaire"""
        if len(self._inventory) < 10:
            return True
        return False

    def use(self, elem):
        """Use a piece of equipment"""
        if elem is None:
            return
        self.checkEquipment(elem)
        if elem not in self._inventory and elem not in self._or:
            raise ValueError('Equipment ' + elem.name + 'not in inventory')
        if elem.use(self):
            self._inventory.remove(elem)
            
    def remove(self, elem):
        """Remove a piece of equipment"""
        if elem is None:
            return
        self.checkEquipment(elem)
        if elem not in self._inventory:
            raise ValueError('Equipment ' + elem.name + 'not in inventory')
        self._inventory.remove(elem)


class Equipment(Element):
    """A piece of equipment"""

    def __init__(self, name, abbrv="", usage=None):
        Element.__init__(self, name, abbrv)
        self.usage = usage

    def meet(self, hero):
        """Makes the hero meet an element. The hero takes the element."""
        if hero.take(self)==True:
           theGame().addMessage("You pick up a " + self.name)
           return True
        return False

    def use(self, creature):
        """Uses the piece of equipment. Has effect on the hero according usage.
            Return True if the object is consumed."""
        if self.usage is None:
            theGame().addMessage("The " + self.name + " is not usable")
            return False
        else:
            theGame().addMessage("The " + creature.name + " uses the " + self.name)
            return self.usage(self, creature)

class Piege(Element):
    """ Pieges that occupies the dungeon"""

    def __init__(self, name, abbrv=".", deg=0.5):
        Element.__init__(self, name, abbrv)
        self.deg = deg

    def meet(self, other):
        """The creature is encountered by a piège.
            The piège hits the creature. Return True if the creature is dead."""
        other.hp -= self.deg
        theGame().addMessage("The " + other.name + " hit on a piege")
        return True

class Stairs(Element):
    """ Strairs that goes down one floor. """

    def __init__(self):
        super().__init__("Stairs", 'E')

    def meet(self, hero):
        """Goes down"""
        theGame().buildFloor()
        theGame().addMessage("The " + hero.name + " goes down")


class Room(object):
    """A rectangular room in the map"""

    def __init__(self, c1, c2):
        self.c1 = c1
        self.c2 = c2

    def __repr__(self):
        return "[" + str(self.c1) + ", " + str(self.c2) + "]"

    def __contains__(self, coord):
        return self.c1.x <= coord.x <= self.c2.x and self.c1.y <= coord.y <= self.c2.y

    def intersect(self, other):
        """Test if the room has an intersection with another room"""
        sc3 = Coord(self.c2.x, self.c1.y)
        sc4 = Coord(self.c1.x, self.c2.y)
        return self.c1 in other or self.c2 in other or sc3 in other or sc4 in other or other.c1 in self

    def center(self):
        """Returns the coordinates of the room center"""
        return Coord((self.c1.x + self.c2.x) // 2, (self.c1.y + self.c2.y) // 2)

    def randCoord(self):
        """A random coordinate inside the room"""
        return Coord(random.randint(self.c1.x, self.c2.x), random.randint(self.c1.y, self.c2.y))

    def randEmptyCoord(self, map):
        """A random coordinate inside the room which is free on the map."""
        c = self.randCoord()
        while map.get(c) != Map.ground or c == self.center():
            c = self.randCoord()
        return c

    def decorate(self, map):
        """Decorates the room by adding a random equipment and monster."""
        map.put(self.randEmptyCoord(map), theGame().randEquipment())
        map.put(self.randEmptyCoord(map), theGame().randMonster())

    def piege(self, map):
        """Decorates the rooms by adding a random trap."""
        map.put(self.randEmptyCoord(map), theGame().randPiege())


class Map(object):
    """A map of a game floor.
        Contains game elements."""

    ground = '.'  # A walkable ground cell
    dir = {'z': Coord(0, -1), 's': Coord(0, 1), 'd': Coord(1, 0), 'q': Coord(-1, 0)}  # four direction user keys
    empty = ' '  # A non walkable cell

    def __init__(self, size=20, hero=None):
        self._mat = []
        self._elem = {}
        self._rooms = []
        self._roomsToReach = []

        for i in range(size):
            self._mat.append([Map.empty] * size)
        if hero is None:
            hero = Hero()
        self._hero = hero
        self.generateRooms(7)
        self.reachAllRooms()
        self.put(self._rooms[0].center(), hero)
        
        for r in self._rooms:
            r.decorate(self)

        k = random.randint(1, 2)    
        for k in self._rooms:
            k.piege(self)

    def addRoom(self, room):
        """Adds a room in the map."""
        self._roomsToReach.append(room)
        for y in range(room.c1.y, room.c2.y + 1):
            for x in range(room.c1.x, room.c2.x + 1):
                self._mat[y][x] = Map.ground

    def findRoom(self, coord):
        """If the coord belongs to a room, returns the room elsewhere returns None"""
        for r in self._roomsToReach:
            if coord in r:
                return r
        return None

    def intersectNone(self, room):
        """Tests if the room shall intersect any room already in the map."""
        for r in self._roomsToReach:
            if room.intersect(r):
                return False
        return True

    def dig(self, coord):
        """Puts a ground cell at the given coord.
            If the coord corresponds to a room, considers the room reached."""
        self._mat[coord.y][coord.x] = Map.ground
        r = self.findRoom(coord)
        if r:
            self._roomsToReach.remove(r)
            self._rooms.append(r)

    def corridor(self, cursor, end):
        """Digs a corridors from the coordinates cursor to the end, first vertically, then horizontally."""
        d = end - cursor
        self.dig(cursor)
        while cursor.y != end.y:
            cursor = cursor + Coord(0, sign(d.y))
            self.dig(cursor)
        while cursor.x != end.x:
            cursor = cursor + Coord(sign(d.x), 0)
            self.dig(cursor)

    def reach(self):
        """Makes more rooms reachable.
            Start from one random reached room, and dig a corridor to an unreached room."""
        roomA = random.choice(self._rooms)
        roomB = random.choice(self._roomsToReach)

        self.corridor(roomA.center(), roomB.center())

    def reachAllRooms(self):
        """Makes all rooms reachable.
            Start from the first room, repeats @reach until all rooms are reached."""
        self._rooms.append(self._roomsToReach.pop(0))
        while len(self._roomsToReach) > 0:
            self.reach()

    def randRoom(self):
        """A random room to be put on the map."""
        c1 = Coord(random.randint(0, len(self) - 3), random.randint(0, len(self) - 3))
        c2 = Coord(min(c1.x + random.randint(3, 8), len(self) - 1), min(c1.y + random.randint(3, 8), len(self) - 1))
        return Room(c1, c2)

    def generateRooms(self, n):
        """Generates n random rooms and adds them if non-intersecting."""
        for i in range(n):
            r = self.randRoom()
            if self.intersectNone(r):
                self.addRoom(r)

    def __len__(self):
        return len(self._mat)

    def __contains__(self, item):
        if isinstance(item, Coord):
            return 0 <= item.x < len(self) and 0 <= item.y < len(self)
        return item in self._elem

    def __repr__(self):
        s = ""
        for i in self._mat:
            for j in i:
                s += str(j)
            s += '\n'
        return s

    def checkCoord(self, c):
        """Check if the coordinates c is valid in the map."""
        if not isinstance(c, Coord):
            raise TypeError('Not a Coord')
        if not c in self:
            raise IndexError('Out of map coord')

    def checkElement(self, o):
        """Check if o is an Element."""
        if not isinstance(o, Element):
            raise TypeError('Not a Element')

    def put(self, c, o):
        """Puts an element o on the cell c"""
        self.checkCoord(c)
        self.checkElement(o)
        if self._mat[c.y][c.x] != Map.ground:
            raise ValueError('Incorrect cell')
        if o in self._elem:
            raise KeyError('Already placed')
        self._mat[c.y][c.x] = o
        self._elem[o] = c

    def get(self, c):
        """Returns the object present on the cell c"""
        self.checkCoord(c)
        return self._mat[c.y][c.x]

    def pos(self, o):
        """Returns the coordinates of an element in the map """
        self.checkElement(o)
        return self._elem[o]

    def rm(self, c):
        """Removes the element at the coordinates c"""
        self.checkCoord(c)
        del self._elem[self._mat[c.y][c.x]]
        self._mat[c.y][c.x] = Map.ground

    def move(self, e, way):
        """Moves the element e in the direction way."""
        orig = self.pos(e)
        dest = orig + way
      
        if dest in self:
            if self.get(dest) == Map.ground:
                self._mat[orig.y][orig.x] = Map.ground
                self._mat[dest.y][dest.x] = e
                self._elem[e] = dest
            elif self.get(dest) != Map.empty and self.get(dest).meet(e) and self.get(dest) != self._hero:
                self.rm(dest)
                
    def moveAllMonsters(self):
        """Moves all monsters in the map.
            If a monster is at distance lower than 6 from the hero and the hero is visible, the monster advances."""
        h = self.pos(self._hero)

        if self._hero.invisible == True:
           self._hero.count += 1
           if self._hero.count > 5:
              self._hero.invisible = False
              self._hero.count = 0
           
        for e in self._elem:
            c = self.pos(e)

            if isinstance(e, Creature) and e != self._hero and c.distance(h) < 6 and self._hero.invisible == False:
                d = c.direction(h)

                if isinstance(e, CreatureR):
                   d = d + d
                   
                if self.get(c + d) in [Map.ground, self._hero]:
                    self.move(e, d)

def teleport(creature, unique):
    """Teleport the creature"""
    r = theGame()._floor.randRoom()
    c = r.randCoord()
    while not theGame()._floor.get(c) == Map.ground:
        c = r.randCoord()
    theGame()._floor.rm(theGame()._floor.pos(creature))
    theGame()._floor.put(c, creature)
    return unique 

def soin(creature):
    """Heal the creature"""
    creature.hp += 3
    return True

def invisible(creature, unique):
   """rend le Hero invisible s'il ne l'est pas ou vice versa"""
   creature.invisible = unique
   if unique == False:
      creature.count = 0
   return True

def parmure(creature):
   "puissance armure, degats reduits"
   creature.armure +=0.25
   return True

class Game(object):
    """ Class representing game state """

    """ available equipments """
    equipments = {0: [Equipment("invisible", "☾", usage=lambda self, hero: invisible(hero, True)), \
                      Equipment("gold", "♦︎")], \
                  1: [Equipment("armure","♣", usage=lambda self, hero : parmure(hero))], \
                  2: [Equipment("portoloin", "✈︎", usage=lambda self, hero: teleport(hero, True))], \
                  3: [Equipment("soin", "✙", usage=lambda self, hero: soin(hero))], \
                  }
    
    """ available monsters """
    monsters = {0: [CreatureR("Roblin", 6,armure=0.25), CreatureR("Bat", 4, "W",armure=0),Creature("Ghost",5,".",armure=0.25)],
                1: [Creature("Ork", 6, strength=2,armure=0.25), Creature("Blob", 10,armure=0.5)], 2: [Creature("Dragon", 25, strength=3,armure=1)]}

    """available trap """
    pieges = {0: [Piege("piege", ".", deg=1)], \
              1: [Piege("piege")]}
                  
    """ available actions """
    _actions = {'z': lambda h: theGame()._floor.move(h, Coord(0, -1)), \
                'q': lambda h: theGame()._floor.move(h, Coord(-1, 0)), \
                's': lambda h: theGame()._floor.move(h, Coord(0, 1)), \
                'd': lambda h: theGame()._floor.move(h, Coord(1, 0)), \

		'a': lambda h: theGame()._floor.move(h, Coord(-1, -1)), \
                'e': lambda h: theGame()._floor.move(h, Coord(1, -1)), \
                'w': lambda h: theGame()._floor.move(h, Coord(-1, 1)), \
                'c': lambda h: theGame()._floor.move(h, Coord(1, 1)), \

                'i': lambda h: theGame().addMessage(h.fullDescription()), \
                'k': lambda h: h.__setattr__('hp', 0), \
                'u': lambda h: h.use(theGame().select(h._inventory)), \
                'r': lambda h: h.remove(theGame().select(h._inventory)), \

                ' ': lambda hero: theGame().addMessage("Jeu crée par Francesco Orsi, groupe 1 \nAttention les monstres bougent"), \
                'h': lambda hero: theGame().addMessage("Actions disponibles : " + str(list(Game._actions.keys()))), \
                'b': lambda hero: theGame().addMessage("I am " + hero.name + " " + hero.abbrv), \
                }

    def __init__(self, level=1, hero=None):
        self._level = level
        self._messages = []
        if hero == None:
            hero = Hero()
        self._hero = hero
        self._floor = None

    def buildFloor(self):
        """Creates a map for the current floor."""
        self._floor = Map(hero=self._hero)
        self._floor.put(self._floor._rooms[-1].center(), Stairs())
        self._level += 1

    def addMessage(self, msg):
        """Adds a message in the message list."""
        self._messages.append(msg)

    def readMessages(self):
        """Returns the message list and clears it."""
        s = ''
        for m in self._messages:
            s += m + '. '
        self._messages.clear()
        return s

    def randElement(self, collect):
        """Returns a clone of random element from a collection using exponential random law."""
        x = random.expovariate(1 / self._level)
        for k in collect.keys():
            if k <= x:
                l = collect[k]
        return copy.copy(random.choice(l))

    def randEquipment(self):
        """Returns a random equipment."""
        return self.randElement(Game.equipments)

    def randMonster(self):
        """Returns a random monster."""
        return self.randElement(Game.monsters)

    def randPiege(self):
        """Returns a random piege."""
        return self.randElement(Game.pieges)

    def select(self, l):
        print("Choose item> " + str([str(l.index(e)) + ": " + e.name for e in l]))
        c = getch()
        if c.isdigit() and int(c) in range(len(l)):
            return l[int(c)]

    def play(self):
        """Main game loop"""
        self.buildFloor()
        print("--- Welcome Hero! ---")
        while self._hero.hp > 0:
            print()
            print(self._floor)
            print(self._hero.description())
            print(self.readMessages())
            c = getch()
            if c in Game._actions:
                Game._actions[c](self._hero)
            self._floor.moveAllMonsters()
        print("--- Game Over --- \nJeu crée par Francesco Orsi")


def theGame(game=Game()):
    """Game singleton"""
    return game


getch = _find_getch()
theGame().play()
