import numpy as np

class Muscle:
    def __init__(self, p0, p1, p2, omega_func, intensite=10.0):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.omega_func = omega_func
        self.intensite = intensite

    def update(self, t):
        omega = self.omega_func(t)

        r0 = self.p0.pos - self.p1.pos
        r2 = self.p2.pos - self.p1.pos

        def rotation_2d(v):
            return np.array([-v[1], v[0]])

        v0 = omega * rotation_2d(r0)
        v2 = -omega * rotation_2d(r2)

        self.p0.v += v0
        self.p2.v += v2
        self.p1.v -= (v0 + v2)
