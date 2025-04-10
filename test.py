import matplotlib.pyplot as plt
import numpy as np
from creature import Creature

# Paramètres
dt = 0.02
steps = 1000
n_creatures = 100

# Création des créatures
population = [Creature() for _ in range(n_creatures)]
trajectoires = [[] for _ in range(n_creatures)]
states = [[] for _ in range(n_creatures)]  # pour animation

# Simulation
for step in range(steps):
    for i, c in enumerate(population):
        c.step(dt)
        trajectoires[i].append(c.p0.pos.copy())
        states[i].append([(p.pos.copy(), p1.vitesse.copy()) for p, p1 in zip(c.points, c.points)])  # pos pour animation

# Évaluation
scores = [c.evaluate() for c in population]
indices_trie = np.argsort(scores)[::-1]
meilleur_index = indices_trie[0]
meilleure_creature = population[meilleur_index]
traj = np.array(trajectoires[meilleur_index])
etats = states[meilleur_index]

# Animation de la meilleure
fig, ax = plt.subplots()
line1, = ax.plot([], [], 'bo-', lw=2)
line2, = ax.plot([], [], 'ro-', lw=2)
ax.set_xlim(-3, 5)
ax.set_ylim(-3, 3)
ax.set_aspect('equal')

def animate(i):
    p0, p1, p2 = [etat[0] for etat in etats[i]]
    x = [p0[0], p1[0], p2[0]]
    y = [p0[1], p1[1], p2[1]]
    line1.set_data(x[:2], y[:2])
    line2.set_data(x[1:], y[1:])
    ax.set_title(f"t = {i*dt:.2f}s")
    return line1, line2

import matplotlib.animation as animation
ani = animation.FuncAnimation(fig, animate, frames=steps, interval=10, blit=True)
plt.show()

# Affichage résumé final
print(f"Score max : {scores[meilleur_index]:.4f}")
print(f"Distance parcourue : {np.linalg.norm(traj[-1] - traj[0]):.2f}")
print(f"Énergie totale : {meilleure_creature.energie_totale:.2f}")
