from classes import *

def generateQuadtree(space_size, particles):
    n = space_size/2
    bound = Rectangle(n,n,n,n)
    qtree = QuadTree(bound, 4)
    for p in particles:
        qtree.insert(p)
    return qtree

def updateParticle(p, dt):
    p.updateVelocity(dt)
    p.updatePosition(dt)

def checkCollisions(p, qtree, dt):
    circle = Circle(p.s[0], p.s[1], p.radius)
    found = qtree.query(circle)
    for other in found:
        if other.s.vect != p.s.vect:
            p.collisionCheck(other, dt)

