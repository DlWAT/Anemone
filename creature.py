import numpy as np 

class Creature:
    def __init__(self, points, liens, muscles):
        self.points = points
        self.liens = liens
        self.muscles = muscles
        self.temps = 0
        self.energie_totale = 0.0
        self.position_initiale = self.points[0].pos.copy()

    def step(self, dt):
        for muscle in self.muscles:
            muscle.update(self.temps)

        for p in self.points:
            p.update(dt)
            # p.appliquer_frottement(dt, coef=5.0)

        for lien in self.liens:
            lien.resistance_fluide()
            lien.corriger()

        Ek = sum(0.5 * p.masse * np.linalg.norm(p.vitesse)**2 for p in self.points)
        self.energie_totale += Ek * dt
        self.temps += dt

    def reset(self):
        raise NotImplementedError("Reset not implemented for genome-based Creature.")

    def evaluate(self):
        dist = np.linalg.norm(self.points[0].pos - self.position_initiale)
        energie = self.energie_totale + 1e-6
        penalite = 1.0 / (energie + 1e-6)  # explose quand l’énergie est trop faible

        return dist / (energie + 0.1 * penalite)


    def get_positions(self):
            return np.array([p.pos for p in self.points])