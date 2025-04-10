import numpy as np 

class Point:
    def __init__(self, x, y, masse=1.0):
        self.pos = np.array([x, y], dtype=float)
        self.vitesse = np.zeros(2)
        self.force = np.zeros(2)
        self.masse = masse

    def appliquer_force(self, f):
        self.force += f

    def update(self, dt, vmax=10.0):
        acceleration = self.force / self.masse
        self.vitesse += acceleration * dt
        speed = np.linalg.norm(self.vitesse)
        if speed > vmax:
            self.vitesse = self.vitesse / speed * vmax
        self.pos += self.vitesse * dt
        self.force[:] = 0.0
        
    def appliquer_frottement(self, dt, coef=5.0):
        self.vitesse -= coef * self.vitesse * dt

