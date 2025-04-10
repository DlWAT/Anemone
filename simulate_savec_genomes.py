import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from factory import genome_to_creature

# === Paramètres de simulation ===
dt = 0.002
steps = 10000
frame_interval = 20
frames = range(0, steps, frame_interval)

# === Chargement des génomes ===
with open("worst_genome_all_time.json", "r") as f:
    genome_worst = json.load(f)

with open("best_genome_last_generation.json", "r") as f:
    genome_best = json.load(f)

# === Création des créatures ===
creature_worst = genome_to_creature(genome_worst)
creature_best = genome_to_creature(genome_best)

# === Simulation et enregistrement des positions ===
positions_worst = []
positions_best = []
links_worst = [(l.i, l.j) for l in creature_worst.liens]
links_best = [(l.i, l.j) for l in creature_best.liens]

for _ in range(steps):
    creature_worst.step(dt)
    creature_best.step(dt)
    positions_worst.append(np.array([p.pos.copy() for p in creature_worst.points]))
    positions_best.append(np.array([p.pos.copy() for p in creature_best.points]))

positions_worst = np.array(positions_worst)  # (steps, n_points, 2)
positions_best = np.array(positions_best)

# === Préparation de l’animation ===
fig, axs = plt.subplots(1, 2, figsize=(12, 6))
axs[0].set_title("Pire créature (score le plus bas)")
axs[1].set_title("Meilleure créature (dernière génération)")

for ax in axs:
    ax.set_xlim(-5, 15)
    ax.set_ylim(-5, 5)
    ax.grid(True)

# Deux objets matplotlib par créature : points + segments
points_plot = [axs[0].plot([], [], 'o')[0], axs[1].plot([], [], 'o')[0]]
lines_plot = [axs[0].plot([], [], 'k-')[0], axs[1].plot([], [], 'k-')[0]]

def init():
    for pt, ln in zip(points_plot, lines_plot):
        pt.set_data([], [])
        ln.set_data([], [])
    return points_plot + lines_plot

def update(frame):
    for idx, (positions, links) in enumerate([(positions_worst, links_worst), (positions_best, links_best)]):
        pts = positions[frame]

        if pts.shape[1] != 2:
            raise ValueError(f"Les positions ne sont pas de forme (n_points, 2), mais {pts.shape}")

        x = pts[:, 0]
        y = pts[:, 1]
        points_plot[idx].set_data(x, y)

        # Reconstruction des segments
        x_lines = []
        y_lines = []
        for i1, i2 in links:
            try:
                x1, y1 = pts[i1]
                x2, y2 = pts[i2]
                x_lines.extend([x1, x2, None])
                y_lines.extend([y1, y2, None])
            except Exception as e:
                print(f"Erreur pour lien ({i1}, {i2}) à la frame {frame}: {e}")
                continue

        lines_plot[idx].set_data(x_lines, y_lines)

    return points_plot + lines_plot


ani = FuncAnimation(fig, update, frames=frames, init_func=init, blit=True, interval=50)
plt.tight_layout()
plt.show()
