import random 
import math
import pygame

class Vector:
    # first parameter of a class method is alwyas
    # a self thing, it can be called anything

    def __init__(self, n1, n2):
        self.vect = [n1, n2]
    # __init__ initialises the object, this is where attributes can be set 

    def sum(self, other, dt):
        return Vector(self.vect[0] + other.vect[0]*dt, self.vect[1] + other.vect[1]*dt)
    
    def minus(self, other, dt):
        return Vector(self.vect[0] - other.vect[0]*dt, self.vect[1] - other.vect[1]*dt)
    
    def scalarX(self, scalar):
        return Vector(self.vect[0]*scalar, self.vect[1]*scalar)
    
    def dot(self, other):
        return self.vect[0] * other.vect[0] + self.vect[1] * other.vect[1]
    
    def modulus(self):
        return math.sqrt(self.vect[0]**2 + self.vect[1]**2)

    def unit(self):
        n = self.modulus()
        return Vector(self.vect[0] / n, self.vect[1] / n)
    
    #allows other files to access specific indexes of a vector
    def __getitem__(self, ind): 
        return self.vect[ind]

    def __str__(self):
        return f"{self.vect[0]}, {self.vect[1]}"
    # __str__ function transforms data into string
    
class Particle:
    def __init__(self, radius, colour, mass):
        self.s = Vector(random.randint(10, 390),random.randint(10, 390))
        self.vel = Vector(random.randint(-150, 150),random.randint(-150, 150))
        self.acc = Vector(0, 0)
        self.radius = radius
        self.colour = colour
        self.mass = mass
    
    def show(self, screen):
        pygame.draw.circle(screen, self.colour, (self.s[0], self.s[1]), self.radius)

    def collisionResponse(self, other):
        dist = self.s.minus(other.s, 1)
        line = dist.unit()
        
        #THE MATHS WORKS BUT CAN BE VASTLY IMPROED!
        dot1 = self.vel.dot(line) 
        b = line.modulus()**2
        c = dot1 / b 
        u1n = line.scalarX(c)
        u1t = self.vel.minus(u1n, 1)

        dot2 = other.vel.dot(line)
        c = dot2 / b
        u2n = line.scalarX(c)
        u2t = other.vel.minus(u2n, 1)

        a = u2n.scalarX(2*other.mass)
        b = self.mass - other.mass
        c = u1n.scalarX(b)
        d = a.sum(c, 1)
        v1n = d.scalarX(1/(self.mass + other.mass))
        a = u1n.scalarX(2*self.mass)
        b = other.mass - self.mass
        c = u2n.scalarX(b)
        d = a.sum(c, 1)
        v2n = d.scalarX(1/(self.mass + other.mass))

        overlap = 0.5 * (dist.modulus() - self.radius - other.radius)
        self.s.vect[0] = self.s.vect[0] - overlap*line.vect[0]
        self.s.vect[1] = self.s.vect[1] - overlap*line.vect[1]
        other.s.vect[0] = other.s.vect[0] + overlap*line.vect[0]
        other.s.vect[1] = other.s.vect[1] + overlap*line.vect[1]
        
        return [v1n.sum(u1t, 1), v2n.sum(u2t, 1)]
    
    def updatePosition(self, dt):
        self.s = self.s.sum(self.vel, dt)
    
    def updateVelocity(self, dt):
        self.vel = self.vel.sum(self.acc, dt)

    def boundaryCheck(self, boundarySize):
        if self.s[0] - self.radius <= 0 and self.vel[0] <0 or self.s[0] + self.radius >= boundarySize and self.vel[0] > 0:
            self.vel.vect[0] = -self.vel.vect[0]
        if self.s[1] - self.radius <= 0 and self.vel[1] <0 or self.s[1] + self.radius >= boundarySize and self.vel[1] > 0:
            self.vel.vect[1] = -self.vel.vect[1]

    def collisionCheck(self, other, dt):
        distance = self.s.minus(other.s, 1)
        distance = distance.modulus()
        if distance <= self.radius + other.radius:
            resolvedVs = self.collisionResponse(other)
            self.vel = resolvedVs[0]
            other.vel = resolvedVs[1]
            self.updatePosition(dt)
            other.updatePosition(dt) 

class Circle():
    def __init__(self, x , y, r):
        self.x = x
        self.y = y
        self.r = r 
    
    def contains(self, particle):
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
    
class QuadTree():
    def __init__(self, bound, n):
        self.boundary = bound
        self.max = n 
        self.particles = []
        self.divided = False 

    def insert(self, particle):
        if self.boundary.contains(particle) == False:
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
    # Using query range method, so get rid of this?
    def insert_to_children(self, particle):
        if self.ne.insert(particle): return True
        elif self.nw.insert(particle): return True
        elif self.se.insert(particle): return True
        elif self.sw.insert(particle): return True 

    def subdivide(self):
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

    def show(self, screen):
        pygame.draw.rect(screen, (255,255,255), pygame.Rect(self.boundary.x - self.boundary.w, self.boundary.y - self.boundary.h, self.boundary.w * 2, self.boundary.h * 2), 1)
        
        if self.divided == True:
            self.ne.show(screen)
            self.nw.show(screen)
            self.se.show(screen)
            self.sw.show(screen)
