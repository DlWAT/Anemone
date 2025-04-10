import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from genome_utils import genome_to_creature

# === Chargement ===
with open("best_genome_last_generation.json", "r") as f:
    genome = json.load(f)

creature = genome_to_creature(genome)

# === Simulation ===
dt = 0.01
steps = 2000
positions = []

for _ in range(steps):
    creature.step(dt)
    positions.append(np.array([p.pos.copy() for p in creature.points]))

positions = np.array(positions)

# === Animation ===
fig, ax = plt.subplots()
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.set_aspect('equal')
line, = ax.plot([], [], 'o-', lw=2)

def update(frame):
    pts = positions[frame]
    x = pts[:, 0]
    y = pts[:, 1]
    line.set_data(x, y)
    return line,

ani = FuncAnimation(fig, update, frames=len(positions), blit=True, interval=20)
plt.title("Créature avec frottements + muscles physiques")
plt.grid()
plt.show()
