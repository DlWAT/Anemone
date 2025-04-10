import numpy as np

class AngleDriver:
    def __init__(self, p0, p1, p2, l1, l2, angle_func, rigidite=50.0):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.l1 = l1
        self.l2 = l2
        self.angle_func = angle_func
        self.rigidite = rigidite

    def update(self, t, dt):
        theta = self.angle_func(t)

        # Direction normalisée du segment p0 → p1
        dir1 = self.p0.pos - self.p1.pos
        dir1 /= np.linalg.norm(dir1)

        # Vecteur orthogonal dans le plan 2D
        ortho = np.array([-dir1[1], dir1[0]])

        # Nouvelle position cible de p2
        target_vector = np.cos(theta) * dir1 + np.sin(theta) * ortho
        new_pos = self.p1.pos + self.l2 * target_vector

        # Force appliquée à p2 et réaction sur p1
        delta = new_pos - self.p2.pos
        force = self.rigidite * delta
        self.p2.appliquer_force(force)
        self.p1.appliquer_force(-force)


    def get_consigne_angle(self, t):
        return np.degrees(self.angle_func(t))
