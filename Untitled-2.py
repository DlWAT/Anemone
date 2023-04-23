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
density_water = 0.1 #kg/m^3
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
globals()[f"point_{0}"].x=850
globals()[f"point_{0}"].y=430

globals()[f"point_{1}"].x=820
globals()[f"point_{1}"].y=450

globals()[f"point_{2}"].x=870
globals()[f"point_{2}"].y=450
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
    pygame.time.delay(100)
    t+=0.01
    w=3
    mass=1
    
    totvx=0
    totvy=0
    if t!=0:
        area=1/2*(x1*(y2 - y0)* + x2*(y0 - y1) + x0*(y1 - y2))
    x0=globals()[f"point_{0}"].x
    y0=globals()[f"point_{0}"].y
    
    x1=globals()[f"point_{1}"].x
    y1=globals()[f"point_{1}"].y
    
    x2=globals()[f"point_{2}"].x
    y2=globals()[f"point_{2}"].y
    k=1
    
    force=0.1
    
    if t!=0:
        darea=(area-1/2*(x1*(y2 - y0)* + x2*(y0 - y1) + x0*(y1 - y2)))*0.0000001
        # print("dare : ",darea)
    else: darea=0
    dab2=np.sqrt((x2-x1)**2+(y2-y1)**2)
    alphaab=np.arccos((x2-x1)/dab2)
    
    vx1=0
    vy1=0
    vx2=0
    vy2=0    
    if dab2<0*radius:
        vtot=np.sqrt(globals()[f"point_{1}"].vx**2+globals()[f"point_{1}"].vy**2)
        vx1=np.cos(alphaab)*vtot*0
        vy1=np.sin(alphaab)*vtot*0
        
        vtot=np.sqrt(globals()[f"point_{2}"].vx**2+globals()[f"point_{2}"].vy**2)
        vx2=-np.cos(alphaab)*vtot*0
        vy2=-np.sin(alphaab)*vtot*0
    
    dab1=np.sqrt((x1-x0)**2+(y1-y0)**2)
    alpha1=math.atan2(y1-y0, x1-x0)
    
    dab2=np.sqrt((x2-x0)**2+(y2-y0)**2)
    alpha2=math.atan2(y2-y0, x2-x0)
    alphabis=(alpha1+alpha2)/2
    compx1=(x1-x0)/dab1 #cos(a)
    compy1=(y1-y0)/dab1 #sin(a)  
    compx2=(x2-x0)/dab2 #cos(a)
    compy2=(y2-y0)/dab2 #sin(a)
    Fmuscle=(0.02*np.sign(np.cos(w*t))-0.0*np.sign(np.cos(3*w*t))+0.0*np.sign(np.cos(2*w*t)))*1
    amort=2
    print("distances :", dab1,dab2)
    if t<0.01:
        Fmuscle=0
    globals()[f"point_{1}"].vx+=((100-dab1)*k*compx1-amort*globals()[f"point_{1}"].vx+vx1+Fmuscle*np.cos(alpha1-np.pi/2)*dab1-darea*np.cos((alpha1+alpha2)/2))*0.1
    globals()[f"point_{1}"].vy+=((100-dab1)*k*compy1-amort*1*globals()[f"point_{1}"].vy+vy1+Fmuscle*np.sin(alpha1-np.pi/2)*dab1-darea*np.sin((alpha1+alpha2)/2))*0.1
    
    globals()[f"point_{2}"].vx+=((100-dab2)*k*compx2-amort*1*globals()[f"point_{2}"].vx+vx2+Fmuscle*np.cos(alpha2+np.pi/2)*dab2-darea*np.cos((alpha1+alpha2)/2))*0.1
    globals()[f"point_{2}"].vy+=((100-dab2)*k*compy2-amort*1*globals()[f"point_{2}"].vy+vy2+Fmuscle*np.sin(alpha2+np.pi/2)*dab2-darea*np.sin((alpha1+alpha2)/2))*0.1
    print("Frottements : ",1*amort*((dab1*np.sin(alpha1)+dab2*np.sin(alpha2))*0+1)*globals()[f"point_{0}"].vy,0.005*amort*((dab1*np.cos(alpha1-np.pi/2)+dab2*np.cos(alpha2-np.pi/2)))*globals()[f"point_{0}"].vy)
    globals()[f"point_{0}"].vx+=(-(100-dab1)*k*compx1-(100-dab2)*k*compx2-0.005*amort*((dab1*np.sin(alpha1-np.pi/2)+dab2*np.sin(alpha2-np.pi/2)))*globals()[f"point_{0}"].vx-1*(Fmuscle*np.cos(alpha1-np.pi/2)*dab1+Fmuscle*np.cos(alpha2+np.pi/2)*dab2-darea*np.cos((alpha1+alpha2)/2)))*0.1
    globals()[f"point_{0}"].vy+=(-(100-dab1)*k*compy1-(100-dab2)*k*compy2-0.005*amort*((dab1*np.cos(alpha1-np.pi/2)+dab2*np.cos(alpha2-np.pi/2)))*globals()[f"point_{0}"].vy-1*(Fmuscle*np.sin(alpha1-np.pi/2)*dab1+Fmuscle*np.sin(alpha2+np.pi/2)*dab2-darea*np.cos((alpha1+alpha2)/2)))*0.1
    
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
        if i==0:
            gfxdraw.aacircle(win, x, y, radius, (255, 0, 0))
            gfxdraw.filled_circle(win, x, y, radius, (255, 0, 0))
        if i==1:
            gfxdraw.aacircle(win, x, y, radius, (0, 255, 0))
            gfxdraw.filled_circle(win, x, y, radius, (0, 255, 0))
        if i==2:
            gfxdraw.aacircle(win, x, y, radius, (0, 0, 255))
            gfxdraw.filled_circle(win, x, y, radius, (0, 0, 255))
        
        
    for i in range(nbr_pts):
        for j in range(1):
            pygame.draw.line(win, (255, 255, 0), (int(globals()[f"point_{i}"].x), int(globals()[f"point_{i}"].y)), (int(globals()[f"point_{j}"].x), int(globals()[f"point_{j}"].y)))
    
    # it refreshes the window
    pygame.display.update() 
  
# closes the pygame window 
pygame.quit()