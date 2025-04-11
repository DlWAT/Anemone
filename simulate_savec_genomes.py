import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from factory import genome_to_creature

# === Chargement ===
with open("best_genome_last_generation.json", "r") as f:
    genome = json.load(f)

creature = genome_to_creature(genome)

# === Simulation ===
dt = 0.01
steps = 2000
positions = []
barycentres = []

for _ in range(steps):
    creature.step(dt)
    pts = np.array([p.pos.copy() for p in creature.points])
    positions.append(pts)
    barycentres.append(np.mean(pts, axis=0))

positions = np.array(positions)
barycentres = np.array(barycentres)

# === Animation ===
fig, ax = plt.subplots()
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.set_aspect('equal')
ax.grid(True)

# Plots
creature_plot, = ax.plot([], [], 'o-', lw=2, color='blue')  # corps
bary_trace, = ax.plot([], [], '-', color='green', alpha=0.5, lw=1)  # trajectoire
bary_point, = ax.plot([], [], 'ro')  # point rouge = centre actuel

def update(frame):
    pts = positions[frame]
    x = pts[:, 0]
    y = pts[:, 1]
    creature_plot.set_data(x, y)

    bary_trace.set_data(barycentres[:frame+1, 0], barycentres[:frame+1, 1])
    bary_point.set_data([barycentres[frame, 0]], [barycentres[frame, 1]])

    return creature_plot, bary_trace, bary_point


ani = FuncAnimation(fig, update, frames=len(positions), init_func=lambda: update(0),
                    blit=True, interval=20)
plt.title("Créature + Trajectoire du centre (barycentre)")
plt.tight_layout()
plt.show()
