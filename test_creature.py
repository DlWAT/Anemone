import numpy as np
import matplotlib.pyplot as plt
from point import Point
from link import Lien
from muscle import Muscle

# Angle cible en radians : somme de sinusoïdes asymétrique
def angle_target(t):
    base = 90
    amp1 = 30 * np.sin(2 * np.pi * 0.5 * t)
    amp2 = 15 * np.sin(2 * np.pi * 0.25 * t + 1)
    total = base + amp1 + amp2
    return np.radians(np.clip(total, 10, 170))

# Création des points
p0 = Point(0, 0)
p1 = Point(1, 0)
p2 = Point(2, 1.0)
points = [p0, p1, p2]

# Liens rigides
liens = [Lien(p0, p1), Lien(p1, p2)]

# Muscle (angle imposé entre les 3 points)
muscle = Muscle(p0, p1, p2, angle_func=angle_target, rigidite=50.0, amortissement=10.0)


# Paramètres de simulation
dt = 0.0002
steps = 100000
E_kin = []
angles = []
angles_target = []
positions = []

# Simulation
for step in range(steps):
    t = step * dt
    muscle.update(t)

    for p in points:
        p.update(dt)

    for lien in liens:
        lien.resistance_fluide()
        lien.corriger()

    E_k = sum(0.5 * p.masse * np.linalg.norm(p.vitesse)**2 for p in points)
    E_kin.append(E_k)
    angles.append(muscle.get_angle())
    angles_target.append(np.degrees(angle_target(t)))
    positions.append(p0.pos.copy())

    # Affichage temps réel
    if step % 100 == 0:
        plt.clf()
        x = [p.pos[0] for p in points]
        y = [p.pos[1] for p in points]
        plt.plot(x[:2], y[:2], 'bo-', linewidth=2)
        plt.plot(x[1:], y[1:], 'ro-', linewidth=2)
        plt.title(f"t = {t:.2f} s")
        plt.xlim(-3, 5)
        plt.ylim(-3, 3)
        plt.gca().set_aspect('equal')
        plt.pause(0.01)

# Analyse post-simulation
temps = np.arange(steps) * dt
positions = np.array(positions)
distances = np.linalg.norm(positions - positions[0], axis=1)

# Courbe énergie cinétique
plt.figure()
plt.plot(temps, E_kin, label="Énergie cinétique")
plt.xlabel("Temps (s)")
plt.ylabel("Énergie")
plt.title("Évolution de l'énergie cinétique")
plt.legend()
plt.grid()

# Courbe angle réel vs cible
plt.figure()
plt.plot(temps, angles, label="Angle réel (°)")
plt.plot(temps, angles_target, '--', label="Angle cible (°)")
plt.xlabel("Temps (s)")
plt.ylabel("Angle")
plt.title("Évolution de l'angle de l'articulation")
plt.legend()
plt.grid()

# Distance parcourue
plt.figure()
plt.plot(temps, distances, label="Distance parcourue")
plt.xlabel("Temps (s)")
plt.ylabel("Distance")
plt.title("Distance du point de tête")
plt.legend()
plt.grid()

plt.show()
