import random 
import math

class Vector:
    # first parameter of a class method is alwyas
    # a self thing, it can be called anything

    def __init__(self, n1, n2, n3=None):
        if n3!=None:
            self.vect = [n1,n2,n3]
        else:
            self.vect = [n1, n2]
    # __init__ initialises the object, this is where attributes can be set 

    def sum(self, other, dt):
        if len(self.vect) == 3 and len(other.vect) == 3:
            return Vector(self.vect[0] + other.vect[0]*dt, self.vect[1] + other.vect[1]*dt, self.vect[2] + other.vect[2]*dt)
        return Vector(self.vect[0] + other.vect[0]*dt, self.vect[1] + other.vect[1]*dt)
    
    def minus(self, other, dt):
        return Vector(self.vect[0] - other.vect[0]*dt, self.vect[1] - other.vect[1]*dt)
    
    def scalarX(self, scalar): #Multiplies vector by scalar
        if len(self.vect) == 3:
            return Vector(self.vect[0]*scalar, self.vect[1]*scalar, self.vect[2]*scalar)
        return Vector(self.vect[0]*scalar, self.vect[1]*scalar)
    
    def cross(self,other): #Cross product of two vectors
        if len(self.vect) == 3 and len(other.vect) == 3:
            i = self.vect[1] * other.vect[2] - self.vect[2]*other.vect[1]
            j = self.vect[2]*other.vect[0] - self.vect[0]*other.vect[2]
            k = self.vect[0]*other.vect[1] - self.vect[1]*other.vect[0]
            return Vector(i,j,k)
    
    def dot(self, other): #dot product
        return self.vect[0] * other.vect[0] + self.vect[1] * other.vect[1]
    
    def modulus(self):
        return math.sqrt(self.vect[0]**2 + self.vect[1]**2)

    def unit(self):
        n = self.modulus()
        if n == 0:
            return Vector (0, 0)
        return Vector(self.vect[0] / n, self.vect[1] / n)
    
    
    #allows other files to access specific indexes of a vector
    def __getitem__(self, ind): 
        return self.vect[ind]

    def __str__(self):
        return f"{self.vect[0]}, {self.vect[1]}"
    # __str__ function transforms data into string
    
class Particle:
    def __init__(self, s=None, vel=None, acc=None, radius=None, colour=None, mass=None, isInvisible=None, isAir=None, charge=None, revFrequency=None, omega=None):
        self.s = s
        self.vel = vel
        self.acc = acc
        self.radius = radius
        self.colour = colour
        self.mass = mass
        self.isInvisible = isInvisible
        self.isAir = isAir
        self.charge = charge
        self.revFrequency = revFrequency
        self.omega = omega

    # def show(self, screen):
    #     pygame.draw.circle(screen, self.colour, (self.s[0], self.s[1]), self.radius/2)
    
    def newCollisionResponse(self, other, dt, e):
        relative_velocity = other.vel.minus(self.vel, 1)
        collision_normal = (other.s.minus(self.s, 1)).unit()
        velocity_along_normal = relative_velocity.dot(collision_normal)

        if velocity_along_normal > 0:
            return
        
        impulse_magnitude = velocity_along_normal * -(1+e)
        impulse_magnitude /= (1 / self.mass + 1 / other.mass)
        # this formula allows us to treat the 2-bodies as 1,
        # allowing us to find the magnitude of impulse that affects both
        # without having to deal with their accelerations (forces)

        impulse = collision_normal.scalarX(impulse_magnitude)
        self.vel = self.vel.minus(impulse.scalarX(1/self.mass), 1)
        other.vel = other.vel.sum(impulse.scalarX(1/other.mass), 1)

        self.seperateParticles(other, dt)

    def seperateParticles(self, other, dt):#Seperates the particles slightly after a collision, as they will be overlapping
        overlap = self.radius + other.radius - (self.s.minus(other.s, 1)).modulus()
        if overlap > 0:
            collision_normal = (other.s.minus(self.s, 1)).unit()
            self.s = self.s.minus(collision_normal.scalarX(overlap/2), dt)
            other.s = other.s.sum(collision_normal.scalarX(overlap/2), dt)
    
    def updatePosition(self, dt):
        self.s = self.s.sum(self.vel, dt)
    
    def updateVelocity(self, dt):
        self.vel = self.vel.sum(self.acc, dt)

    def boundaryCheck(self, boundarySize, e):
        #flips velocities if there is a collision with a boundary
        if self.s[0] - self.radius <= 0 and self.vel[0] <0:
            self.vel.vect[0] = -self.vel.vect[0]*e
            self.s.vect[0] = self.radius
        elif self.s[0] + self.radius >= boundarySize["width"] and self.vel[0] > 0:
            self.vel.vect[0] = -self.vel.vect[0]*e
            self.s.vect[0] = boundarySize["width"] - self.radius
        if self.s[1] - self.radius <= 0 and self.vel[1] <0:
            self.vel.vect[1] = -self.vel.vect[1]*e
            self.s.vect[1] = self.radius
        elif self.s[1] + self.radius >= boundarySize["height"] and self.vel[1] > 0:
            self.vel.vect[1] = -self.vel.vect[1]*e
            self.s.vect[1] = boundarySize["height"] - self.radius

    def collisionCheck(self, other, dt, e):
        distance = self.s.minus(other.s, 1)
        distance = distance.modulus()
        
        if distance <= self.radius + other.radius:
            #print(distance, self.radius + other.radius)
            #print(self.s.vect, " ", other.s.vect)
            self.colour = (255,0,0)
            other.colour = (255,0,0)
            self.newCollisionResponse(other, dt, e=e)

class Circle():
    def __init__(self, x , y, r):
        self.x = x
        self.y = y
        self.r = r 
    
    def contains(self, particle):
        #Method for determining if there is a particle within the circular area
        a = abs(self.x - particle.s[0])
        b = abs(self.y - particle.s[1])
        distance = math.sqrt(a**2 + b**2)
        return distance <= self.r

class Rectangle():
    def __init__(self, x, y, w, h):
        self.x = x 
        self.y = y
        self.w = w
        self.h = h
        # Rectangle with centre coordinate
        # left side x-coords = x-w
        # right side x-coords = x+w
        # top y-coords = y+h
        # bottom y-coords = y-h

    def contains(self, particle):
        return (particle.s[0] >= self.x - self.w and 
                particle.s[0] < self.x + self.w and 
                particle.s[1] >= self.y - self.h and 
                particle.s[1] < self.y + self.h)
        # Returns boolean value if a particle's centre coordinate is within the boundary

    def intersects(self, area):
        return (self.x + self.w > area.x - area.r or 
                self.y + self.h < area.y - area.r or
                self.x - self.w < area.x + area.r or
                self.y - self.h < area.y + area.r)
    #returns boolean value if two rectangular boundaries are intersecting
    
class QuadTree():
    def __init__(self, bound, n):
        self.boundary = bound
        self.max = n 
        self.particles = []
        self.divided = False 

    def insert(self, particle):
        #Method for adding a particle into the quadtree
        if self.boundary.contains(particle) == False:
            #Necessary to see which subdivision of the quadtree the particle needs to insert into
            return False
        
        if len(self.particles) < self.max and not self.divided:
            self.particles.append(particle)
            return True
        else:
            if not self.divided:
                self.subdivide()
                for p in self.particles:
                    self.insert_to_children(p)
                self.particles = []
            return self.insert_to_children(particle)
    
    def insert_to_children(self, particle):
        #attempts to insert particle into each subdivision, insert(particle) is only true if particle is within the subdivision
        if self.ne.insert(particle): return True
        elif self.nw.insert(particle): return True
        elif self.se.insert(particle): return True
        elif self.sw.insert(particle): return True 

    def subdivide(self):
        #creates 4 rectangular boundaries to subdivide the parent boundary
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.w
        h = self.boundary.h
        northeast = Rectangle(x + w/2, y - h/2, w/2, h/2)
        self.ne = QuadTree(northeast, self.max)
        northwest = Rectangle(x - w/2, y - h/2, w/2, h/2)
        self.nw = QuadTree(northwest, self.max)
        southeast = Rectangle(x + w/2, y + h/2, w/2, h/2)
        self.se = QuadTree(southeast, self.max)
        southwest = Rectangle(x - w/2, y + h/2, w/2, h/2)
        self.sw = QuadTree(southwest, self.max)
        self.divided = True 
        
    def query(self, area):
        #Method to find all particles within a given boundary
        #Traverses tree and checks which subdivisions intersect with the boundary
        #And out of these subdivisions, check which particles are within the boundary
        particlesFound = []

        if not self.boundary.intersects(area):
            return particlesFound
        else:
            for p in self.particles:
                if area.contains(p):
                    particlesFound.append(p)
        
        if self.divided:
            particlesFound += self.nw.query(area) 
            particlesFound += self.ne.query(area) 
            particlesFound += self.sw.query(area) 
            particlesFound += self.se.query(area) 

        return particlesFound
