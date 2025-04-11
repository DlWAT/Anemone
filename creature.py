import numpy as np
from muscle import interaction_hydrodynamique_triangle

class Creature:
    def __init__(self, points, liens, muscles):
        self.points = points
        self.liens = liens
        self.muscles = muscles
        self.temps = 0
        self.energie_totale = 0.0
        self.position_initiale = np.mean([p.pos for p in self.points], axis=0)

    def step(self, dt):
        for muscle in self.muscles:
            muscle.update(self.temps)

        for muscle in self.muscles:
            interaction_hydrodynamique_triangle(muscle.p0, muscle.p1, muscle.p2)

        for lien in self.liens:
            lien.appliquer_forces()

        for point in self.points:
            point.update(dt)

        Ek = sum(0.5 * p.masse * np.linalg.norm(p.v)**2 for p in self.points)
        self.energie_totale += Ek * dt
        self.temps += dt

    def evaluate(self):
        position_actuelle = np.mean([p.pos for p in self.points], axis=0)
        dist = np.linalg.norm(position_actuelle - self.position_initiale)
        energie = self.energie_totale + 1e-6
        penalite = 1.0 / (energie + 1e-6)
        return dist**2 / (energie + 0.1 * penalite)

    def get_positions(self):
        return np.array([p.pos for p in self.points])
