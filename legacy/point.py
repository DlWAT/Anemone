import numpy as np

class Point:
    def __init__(self, x, y, masse=1.0):
        self.pos = np.array([x, y], dtype=float)
        self.v = np.zeros(2)
        self.f = np.zeros(2)
        self.masse = masse

    def update(self, dt, vmax=5.0):
        self.pos += self.v * dt
        speed = np.linalg.norm(self.v)
        if speed > vmax:
            self.v = self.v / speed * vmax
