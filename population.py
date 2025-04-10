import numpy as np
from creature import Creature
from utils import random_angle_function

class Population:
    def __init__(self, size=10):
        self.size = size
        self.creatures = [Creature(random_angle_function()) for _ in range(size)]
        self.scores = np.zeros(size)

    def simulate(self, dt=0.02, steps=1000):
        self.trajectoires = [[] for _ in self.creatures]
        self.etats = [[] for _ in self.creatures]

        for step in range(steps):
            for i, c in enumerate(self.creatures):
                c.step(dt)
                self.trajectoires[i].append(c.p0.pos.copy())
                self.etats[i].append([p.pos.copy() for p in c.points])

        self.scores = np.array([c.evaluate() for c in self.creatures])
        self.best_index = np.argmax(self.scores)
        self.worst_index = np.argmin(self.scores)

    def select_best(self, top_k=5):
        indices = np.argsort(self.scores)[::-1]
        return [self.creatures[i] for i in indices[:top_k]]

    def next_generation(self, mutation_strength=0.1):
        top = self.select_best(top_k=self.size // 2)
        new_creatures = []
        for creature in top:
            for _ in range(2):  # deux enfants par parent
                mutated_func = self.mutate_func(creature.angle_func, mutation_strength)
                new_creatures.append(Creature(mutated_func))
        self.creatures = new_creatures[:self.size]

    def mutate_func(self, angle_func, strength):
        """Crée une nouvelle fonction en perturbant les coefficients de l’ancienne."""
        return random_angle_function()  # TODO : réutiliser + muter les anciens paramètres
