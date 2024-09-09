from classes import * # Importing classes
import pygame # Importing pygame
import math 

def generateQuadtree():
    n = space_size/2
    bound = Rectangle(n,n,n,n)
    qtree = QuadTree(bound, 4)
    for p in particles:
        qtree.insert(p)
    return qtree

pygame.init() # Initialising pygame
space_size = 400 # Dimensions of screen
screen = pygame.display.set_mode([space_size, space_size]) # Drawing window

# Simulation data
rate = 60 # 60 frames per second
dt = 1/rate # Proportion of change per second to enact each frame
clock = pygame.time.Clock()

running = True
particles = []
for p in range(0,100):
    particles.append(Particle(10, (0,150,0), 1))

area = Rectangle(200,200,100,100)

while running:
    screen.fill((20,20,20)) # Background RGB colour value
    for event in pygame.event.get(): # Handles user clicking close window button
        if event.type == pygame.QUIT:
            running = False
    
    qtree = generateQuadtree()
    qtree.show(screen)
    for p in particles:
        p.show(screen)
        p.colour = (0,0,255)

    for p in particles:
        p.updateVelocity(dt)
        p.updatePosition(dt)
        p.boundaryCheck(space_size)

    # checks and resolves all particle collisions
    for p in particles:  
        circle = Circle(p.s[0], p.s[1], p.radius*2)
        found = qtree.query(circle)

        for other in found: # will only run this if other particles are within given range
            if other.s.vect != p.s.vect:
                p.collisionCheck(other, dt)

    pygame.display.flip()
    clock.tick(rate) # Sets frame rate

pygame.quit() 



#methods for broad phase (determining which particles to check are colliding)
# check with every other particle O(n^2)

# order the particles by a list of the range of x coordinates they are in
# go through one by one and determine if the ranges overlap
# report possible active collision 
# check next particle in ordered list that isn't active
# if not overlapping any others, don't report it's active 

#methods for narrow phase 
# discrete collision detection
# checking if distance of 2 particles is less than sum of radii
# continuous
# computing line between a particle and where it will be projected in the next frame
# seeing if any lines overlap 

#methods for solving collisions
# conservation


#KD tree
# class KD tree
# init with point, left and right point
# method build_tree taking array of points, depth = 0
# sort by x axis
# median = len(point) // 2
# return a KD tree node 
# point = points(median), left point = buildtree(points(left of median), depth +1 )
#, right point = buildtree(points(right of median), depth + 1)