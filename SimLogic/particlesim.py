from SimLogic.classes import *

def generateQuadtree(space_size, particles):
    #Generates and inserts particles into a quadtree
    x = space_size["width"] / 2
    y = space_size["height"] / 2
    bound = Rectangle(x, y, x, y)
    qtree = QuadTree(bound, 4)
    for p in particles:
        qtree.insert(p)
    return qtree

def updateParticle(p, dt):
    #Calculates new positions and velocities
    p.updatePosition(dt)
    p.updateVelocity(dt)

def checkCollisions(p, qtree, dt, e):
    circle = Circle(p.s[0], p.s[1], p.radius*2)
    found = qtree.query(circle)
    for other in found:
        if other.s.vect != p.s.vect:
            p.collisionCheck(other, dt, e)

