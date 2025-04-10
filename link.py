import numpy as np

class Lien:
    def __init__(self, p1, p2, longueur_repos=None, intensite=1.0):
        self.p1 = p1
        self.p2 = p2
        self.longueur_repos = longueur_repos or np.linalg.norm(p2.pos - p1.pos)
        self.intensite = intensite

    def corriger(self):
        delta = self.p2.pos - self.p1.pos
        distance = np.linalg.norm(delta)
        if distance < 1e-8:
            return
        direction = delta / distance
        correction = (distance - self.longueur_repos) * direction * 0.5 * self.intensite
        self.p1.pos += correction
        self.p2.pos -= correction

    def resistance_fluide(self):
        delta = self.p2.pos - self.p1.pos
        distance = np.linalg.norm(delta)
        if distance < 1e-8:
            return
        direction = delta / distance
        v_moy = 0.5 * (self.p1.vitesse + self.p2.vitesse)

        v_para = -np.dot(v_moy, direction) * direction
        v_perp = v_moy - v_para

        k_para = 0.01
        k_perp = 0.5
        f_fluide = -k_para * v_para - k_perp * v_perp

        self.p1.appliquer_force(f_fluide * 0.5)
        self.p2.appliquer_force(f_fluide * 0.5)
