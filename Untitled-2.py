# import pygame module in this program 
import pygame
from pygame import gfxdraw
import random
import numpy as np
import math
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

Cx=0.0016
pi = 3.1415926535
gravity = 9.82 #m/s^2
density_water = 1.0 #kg/m^3
density_air   = 1.29 #kg/m^3
drag_sphere   = 0.47

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
x0=globals()[f"point_{0}"].x
y0=globals()[f"point_{0}"].y

x1=globals()[f"point_{1}"].x
y1=globals()[f"point_{1}"].y

x2=globals()[f"point_{2}"].x
y2=globals()[f"point_{2}"].y

air=0.5*(x1*(y2-y0)+x2*(y0-y1)+x0*(y1-y2))
t=0
while run:
    # creates time delay of 10ms 
    pygame.time.delay(10)
    t+=0.01
    w=3
    mass=1
    for i in range(nbr_pts):
        totvx=0
        totvy=0
        x0=globals()[f"point_{0}"].x
        y0=globals()[f"point_{0}"].y
        
        x1=globals()[f"point_{1}"].x
        y1=globals()[f"point_{1}"].y
        
        x2=globals()[f"point_{2}"].x
        y2=globals()[f"point_{2}"].y
        k=0.5
        amort=1
        force=0.1
        
        if i>0:
            xi=globals()[f"point_{i}"].x
            yi=globals()[f"point_{i}"].y
            dab=np.sqrt((xi-x0)**2+(yi-y0)**2)
            dab2=np.sqrt((x2-x1)**2+(y2-y1)**2)
            compx=(xi-x0)/dab #cos(a)
            compy=(yi-y0)/dab #sin(a)
            Fmuscle=dab*force*0
            air2=0.5*(x1*(y2-y0)+x2*(y0-y1)+x0*(y1-y2))
            angle=0.5*(math.atan2((y2+y1)/2-y0,(x2+x1)/2-x0)-math.atan2(y0-y1,x0-x1))
            
            alpha=np.arcsin((yi-y0)/dab)
            print(alpha)
            
            globals()[f"point_{i}"].vx+=((100-dab)*k*compx-0.25*Cx*dab*np.sin(alpha)*globals()[f"point_{i}"].vx**2)*0.1
            globals()[f"point_{i}"].vy+=((100-dab)*k*compy-0.25*Cx*dab*np.cos(alpha)*globals()[f"point_{i}"].vy**2)*0.1
            globals()[f"point_{0}"].vx+=(-0.25*Cx*dab*np.sin(alpha)*globals()[f"point_{0}"].vx**2)*0.1
            globals()[f"point_{0}"].vy+=(-0.25*Cx*dab*np.cos(alpha)*globals()[f"point_{0}"].vy**2)*0.1
            
            #print(globals()[f"point_{i}"].vx)
            #print(globals()[f"point_{i}"].vy)
        else : 
                dab1=np.sqrt((x1-x0)**2+(y1-y0)**2)
                dab2=np.sqrt((x2-x0)**2+(y2-y0)**2)
                Fmuscle=dab2*force*1*0
                compx1=(x0-x1)/dab1 #cos(a)
                compy1=(y0-y1)/dab1
                compx2=(x0-x2)/dab2 #cos(a)
                compy2=(y0-y2)/dab2
                
                globals()[f"point_{0}"].vx+=(0.5*(100-dab1)*k*compx1+0.5*(100-dab2)*k*compx2)*0.1
                globals()[f"point_{0}"].vy+=(0.5*(100-dab1)*k*compy2+0.5*(100-dab2)*k*compy2)*0.1
        
    #globals()[f"point_{2}"].vx+=0.05*np.sin(w*t)
    #globals()[f"point_{2}"].vy+=0.05*np.cos(w*t)
    #globals()[f"point_{1}"].vx+=-0.05*np.sin(w*t)
    #globals()[f"point_{1}"].vy+=-0.05*np.cos(w*t)    
    
    globals()[f"point_{0}"].add_spd()
    globals()[f"point_{1}"].add_spd()
    globals()[f"point_{2}"].add_spd()
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