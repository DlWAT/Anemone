import numpy as np
from factory import genome_to_creature

class Population:
    def __init__(self, genomes):
        self.genomes = genomes
        self.creatures = [genome_to_creature(g) for g in genomes]
        self.scores = np.zeros(len(self.creatures))

    def simulate(self, dt=0.02, steps=1000):
        self.trajectoires = [[] for _ in self.creatures]
        self.etats = [[] for _ in self.creatures]

        for step in range(steps):
            for i, c in enumerate(self.creatures):
                c.step(dt)
                self.trajectoires[i].append(c.points[0].pos.copy())
                self.etats[i].append([p.pos.copy() for p in c.points])

        self.scores = np.array([c.evaluate() for c in self.creatures])
        self.best_index = np.argmax(self.scores)
        self.worst_index = np.argmin(self.scores)

    def select_best(self, top_k=5):
        indices = np.argsort(self.scores)[::-1]
        return [self.genomes[i] for i in indices[:top_k]]
