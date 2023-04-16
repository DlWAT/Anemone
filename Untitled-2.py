# import pygame module in this program 
import pygame
from pygame import gfxdraw
import random
import numpy as np
# activate the pygame library .  
# initiate pygame and give permission  
# to use pygame's functionality.  
pygame.init()

# create the display surface object  
# of specific dimension..e(500, 500).  
win = pygame.display.set_mode((1500, 950))
  
# set the pygame window name 
pygame.display.set_caption("Moving rectangle")
  
# object current co-ordinates 
x = 200
y = 200
  
# dimensions of the object 
width = 20
height = 20
radius = 10
# velocity / speed of movement
vel = 1
nbr_pts=3
# Indicates pygame is running
run = True
class Point():
    def __init__(self) -> None:
        self.x=0
        self.y=0
        self.vx=0
        self.vy=0
    
    def add_spd(self):
        self.x=self.x+self.vx
        self.y=self.y+self.vy
# infinite loop
for i in range(nbr_pts):
        globals()[f"point_{i}"]=Point()
        globals()[f"point_{i}"].x=random.randint(300,500)
        globals()[f"point_{i}"].y=random.randint(300,500) 
while run:
    # creates time delay of 10ms 
    pygame.time.delay(50)
    
    for i in range(nbr_pts):
        totvx=0
        totvy=0
        if i>0:
            
            globals()[f"point_{i}"].vx=(-0.5+random.random())*1+(100-(globals()[f"point_{i}"].x-globals()[f"point_{0}"].x))*0
            globals()[f"point_{i}"].vy=(-0.5+random.random())*1+(100-(globals()[f"point_{i}"].y-globals()[f"point_{0}"].y))*0
            totvx=+globals()[f"point_{i}"].vx
            totvy=+globals()[f"point_{i}"].vy
            print(globals()[f"point_{i}"].vx,globals()[f"point_{i}"].vy)
        globals()[f"point_{i}"].add_spd()
        
    globals()[f"point_{0}"].vx=-totvx/nbr_pts
    globals()[f"point_{0}"].vy=-totvy/nbr_pts
    # iterate over the list of Event objects  
    # that was returned by pygame.event.get() method.  
    for event in pygame.event.get():
          
        # if event object type is QUIT  
        # then quitting the pygame  
        # and program both.  
        if event.type == pygame.QUIT:
              
            # it will make exit the while loop 
            run = False
    
    win.fill((0, 0, 0))
      
    # drawing object on screen which is rectangle here 
    #pygame.draw.circle(win, (255, 0, 0), (x, y ),radius)
    for i in range(nbr_pts):
        x=int(globals()[f"point_{i}"].x)
        y=int(globals()[f"point_{i}"].y)
        gfxdraw.aacircle(win, x, y, radius, (255, 0, 0))
        gfxdraw.filled_circle(win, x, y, radius, (255, 0, 0))
        
        gfxdraw.aacircle(win, x, y, radius, (255, 0, 0))
        gfxdraw.filled_circle(win, x, y, radius, (255, 0, 0))
        
    for i in range(nbr_pts):
        for j in range(1):
            pygame.draw.line(win, (255, 255, 0), (int(globals()[f"point_{i}"].x), int(globals()[f"point_{i}"].y)), (int(globals()[f"point_{j}"].x), int(globals()[f"point_{j}"].y)))
    
    # it refreshes the window
    pygame.display.update() 
  
# closes the pygame window 
pygame.quit()