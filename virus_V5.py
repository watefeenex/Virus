"""
Nipun Jasti
14 April 2019
Implementing a simple simulation demonstrating the spread of viruses
within a population
Version 5
"""

import turtle
import random
import math

"""
This is a helper class to implement spatial hash algorithm
"""
class EfficientCollision:
    def __init__(self):
        self.dict = {}
        self.grid_size = 20

    """
    Empty the dictionary
    """
    def empty_dict(self):
        self.dict = {}

    """
    Return hash key of the position
    Args:
        x - horizontal position of person object
        y - vertical position of person object
    """
    def hash(self, x, y):
        return (x//self.grid_size, y//self.grid_size)

    """
    Add current person to the dictionary.
    It first hash the person's position and then insert the key to the dictionary.
    Args:
        person - person object to be added to the dictionary
    """
    def add(self, person):
        person_x, person_y = person.location
        grid_x, grid_y = self.hash(person_x, person_y)

        key = (grid_x, grid_y)

        #Add current person to current spatial hash key
        if key in self.dict.keys():
            self.dict[key].append(person)
        else:
            self.dict[key] = [person]


"""
This class represents a virus
"""
class Virus:
    def __init__(self, colour, duration):
        self.colour = colour
        self.duration = duration

"""
This class represents a person
"""
class Person:
    """
    Initialize the person object.
    Args:
        world_size - The size of the world in form of a tuple (width, height)
    """
    def __init__(self, world_size):
        self.world_size = world_size
        self.radius = 7
        self.location = (0, 0)
        self.destination = self._get_random_location()

        self.cured()

    """    
    Random locations are used to assign a destination for the person.
    The possible locations should not be closer than 1 radius to the edge of the world.
    """
    def _get_random_location(self):
        width, height = self.world_size

        random_x = random.randint(-width//2 + self.radius, width//2 - self.radius)
        random_y = random.randint(-height//2 + self.radius, height//2 - self.radius)

        return (random_x, random_y)
 
    """
    Draw a person using a dot.  Use virus' color if the person is infected
    """
    def draw(self):
        current_x, current_y = self.location

        turtle.penup()
        turtle.goto(current_x, current_y)
        turtle.pendown()

        if self.virus == None:
            turtle.dot(2 * self.radius)
        else:
            turtle.dot(2 * self.radius, self.virus.colour)

    """
    Check if current person collide with other person
    Args:
        other - Other person to be checked
    """
    def collides(self, other):
        self_x, self_y = self.location
        other_x, other_y = other.location
        
        #Calculate the squared distance using pythagoras' formula
        squared_distance = (self_x - other_x)**2 + (self_y - other_y)**2

        return squared_distance <= (2 * self.radius)**2

    """
    Return list of people infected by current person. If current person is not infected, return empty list
    Args:
        list_of_others - List of other people to check for collisions
    """
    def collision_list(self, list_of_others):
        collided = []

        if self.virus != None:
            for other in list_of_others:
                if self.collides(other):
                    collided.append(other)

        return collided

    """
    Infect a person with the given virus
    Args:
        virus - The virus that infect the person
    """
    def infect(self, virus):
        self.virus = virus

    """
    Returns true if current position is within 1 radius from destination
    """
    def reached_destination(self):
        current_x, current_y = self.location
        destination_x, destination_y = self.destination

        #Calculate the squared distance using pythagoras's formula
        squared_distance = (current_x - destination_x)**2 + (current_y - destination_y)**2

        #If the distance is within a radius of the dot, it has reached the destination
        return squared_distance <= self.radius**2

    """
    Increase hours of sickness, check if duration of virus is reached.  If the duration is reached then the person is cured
    """
    def progress_illness(self):
        if self.virus != None:
            self.hours_of_sickness += 1
            if self.hours_of_sickness >= self.virus.duration:
                self.cured()

    """
    Updates the person each hour.
    - Moves each person by calling the move method
    - If the destination is reached then set a new destination
    - Progress person's illness
    """
    def update(self):
        if self.reached_destination():
            self.destination = self._get_random_location()

        self.progress_illness()
        self.move()
        
    """
    Moves person towards the destination
    """
    def move(self):
        current_x, current_y = self.location
        turtle.setposition(current_x, current_y)

        #Use turtle.towards() function to find the direction of movement
        destination_x, destination_y = self.destination
        direction = turtle.towards(destination_x, destination_y)

        #Calculate person's new position after moving half radius towards the destination
        next_x = current_x + self.radius//2 * math.sin(math.radians(direction))
        next_y = current_y + self.radius//2 * math.cos(math.radians(direction))

        self.location = (next_x, next_y)

    """
    Cure a person from infection   
    """
    def cured(self):
        self.virus = None
        self.hours_of_sickness = 0
      
class World:
    """
    Initialize the world object.
    Args:
        width - the width of the world
        height - the height of the world
        n - the number of people in the world
    """
    def __init__(self, width, height, n):
        self.size = (width, height)
        self.hours = 0
        self.people = []
        self.eff_collision = EfficientCollision()

        for i in range(n):
            self.add_person()
    
    """
    Add a person to the list
    """
    def add_person(self):
        self.people.append(Person(self.size))

    """
    Choose a random person to infect and infect with a Virus
    """
    def infect_person(self):
        #Filter all healthy people
        healthy = list(filter(lambda person: person.virus == None, self.people))

        #Take random index from the healthy people
        index = random.randint(0, len(healthy) - 1)

        #Infect person which are indicated by the index
        healthy[index].infect(Virus("red", random.randint(0, 1000)))

    """
    Remove all infections from all people
    """
    def cure_all(self):
        for person in self.people:
            person.cured()

    """
    Infect people who are collided by infected people
    This implements brute force O(n^2) solution
    """
    def update_infections_slow(self):
        for person in self.people:

            #For each person, check wether it is collided by current person
            infected = person.collision_list(self.people)
            for other_person in infected:
                other_person.infect(Virus("red", random.randint(0, 1000)))

    """
    Infect people who are collided by infected people
    This implements spatial hash O(n) solution
    """
    def update_infections_fast(self):
        for person in self.people:
            current_x, current_y = person.location
            
            #Get the grid position of current person
            grid_x, grid_y = self.eff_collision.hash(current_x, current_y)

            #Dictionary key of current grid position
            key = (grid_x, grid_y)

            #Get all people which are within the same grid
            neighbors = self.eff_collision.dict[key]

            #Check for collisions for people in the same grid
            infected = person.collision_list(neighbors)

            #Infect each people which are collided by infected person
            for other_person in infected:
                other_person.infect(Virus("red", random.randint(0, 1000)))

    """
    Simulate the world
    """
    def simulate(self):
        #Increase the hour
        self.hours += 1

        #Empty the efficient collision dictionary
        self.eff_collision.empty_dict()

        #Update the state of each person and also add their new position to efficient collision dictionary
        for person in self.people:
            person.update()
            self.eff_collision.add(person)
        
        # self.update_infections_slow()
        self.update_infections_fast()

    """
    Draw the world and the people inside it
    """
    def draw(self):
        turtle.clear()

        width, height = self.size

        #Draw the box
        turtle.penup()
        turtle.goto(-width//2, height//2)
        turtle.pendown()

        turtle.goto(width//2, height//2)
        turtle.goto(width//2, -height//2)
        turtle.goto(-width//2, -height//2)
        turtle.goto(-width//2, height//2)

        #Draw each person
        for person in self.people:
            person.draw()

        #Draw the hours and infected count
        turtle.penup()
        turtle.goto(-width//2, height//2)

        hours_text = "Hours " + str(self.hours)
        turtle.write(hours_text, False)

        turtle.penup()

        turtle.goto(0, height//2)
        infections_text = "Infected " + str(self.count_infected())
        turtle.write(infections_text, False)

    """    
    Count the number of infected people
    """
    def count_infected(self):
        infected = list(filter(lambda person: person.virus != None, self.people))
        return len(infected)
    
class GraphicalWorld:
    """ Handles the user interface for the simulation

    space - starts and stops the simulation
    'z' - resets the application to the initial state
    'x' - infects a random person
    'c' - cures all the people
    """
    def __init__(self):
        self.WIDTH = 800
        self.HEIGHT = 600
        self.TITLE = 'The Virus'
        self.MARGIN = 50 #gap around each side
        self.PEOPLE = 200 #number of people in the simulation
        self.framework = AnimationFramework(self.WIDTH, self.HEIGHT, self.TITLE)
        
        self.framework.add_key_action(self.setup, 'z') 
        self.framework.add_key_action(self.infect, 'x')
        self.framework.add_key_action(self.cure, 'c')
        self.framework.add_key_action(self.toggle_simulation, 'space') 
        self.framework.add_tick_action(self.next_turn)
        
        self.world = None

    def setup(self):
        """ Reset the simulation to the initial state """
        print('resetting the world')        
        self.framework.stop_simulation()
        self.world = World(self.WIDTH - self.MARGIN * 2, self.HEIGHT - self.MARGIN * 2, self.PEOPLE)
        self.world.draw()
        
    def infect(self):
        """ Infect a person, and update the drawing """
        print('infecting a person')
        self.world.infect_person()
        self.world.draw()

    def cure(self):
        """ Remove infections from all the people """
        print('cured all people')
        self.world.cure_all()
        self.world.draw()

    def toggle_simulation(self):
        """ Starts and stops the simulation """
        if self.framework.simulation_is_running():
            self.framework.stop_simulation()
        else:
            self.framework.start_simulation()           

    def next_turn(self):
        """ Perform the tasks needed for the next animation cycle """
        self.world.simulate()
        self.world.draw()
        
## This is the animation framework
## Do not edit this framework
class AnimationFramework:
    """This framework is used to provide support for animation of
       interactive applications using the turtle library.  There is
       no need to edit any of the code in this framework.
    """
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.simulation_running = False
        self.tick = None #function to call for each animation cycle
        self.delay = 1 #smallest delay is 1 millisecond      
        turtle.title(title) #title for the window
        turtle.setup(width, height) #set window display
        turtle.hideturtle() #prevent turtle appearance
        turtle.tracer(0, 0) #prevent turtle animation
        turtle.listen() #set window focus to the turtle window
        turtle.mode('logo') #set 0 direction as straight up
        turtle.penup() #don't draw anything
        turtle.setundobuffer(None)
        self.__animation_loop()

    def start_simulation(self):
        self.simulation_running = True
        
    def stop_simulation(self):
        self.simulation_running = False

    def simulation_is_running(self):
        return self.simulation_running
    
    def add_key_action(self, func, key):
        turtle.onkeypress(func, key)

    def add_tick_action(self, func):
        self.tick = func

    def __animation_loop(self):
        try:
            if self.simulation_running:
                self.tick()
            turtle.ontimer(self.__animation_loop, self.delay)
        except turtle.Terminator:
            pass


gw = GraphicalWorld()
gw.setup()
turtle.mainloop() #Need this at the end to ensure events handled properly
