import numpy as np
import matplotlib.pyplot as plt
from point import Point
from link import Lien
from muscle import Muscle  # muscle = contrôleur à angle imposé

# Fonction d'angle cible en radians
def angle_target(t):
    base = 90
    amp1 = 30 * np.sin(2 * np.pi * 0.5 * t )
    amp2 = 15 * np.sin(2 * np.pi * 0.25 * t + 1 )
    total = base + amp1 + amp2
    return np.radians(np.clip(total, 10, 170))

# Création des points
p0 = Point(0, 0)
p1 = Point(1, 0)
p2 = Point(2, 1.0)
points = [p0, p1, p2]

# Liens rigides
liens = [Lien(p0, p1), Lien(p1, p2)]

# Muscle avec angle imposé
muscle = Muscle(p0, p1, p2, angle_func=angle_target, rigidite=200.0)

# Simulation
dt = 0.02
steps = 1000
E_kin = []
angles = []
angles_target = []

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
    
    if step % 10 == 0:
        plt.clf()
        x = [p0.pos[0], p1.pos[0], p2.pos[0]]
        y = [p0.pos[1], p1.pos[1], p2.pos[1]]
        plt.plot(x[:2], y[:2], 'bo-', linewidth=2)
        plt.plot(x[1:], y[1:], 'ro-', linewidth=2)
        plt.title(f"t = {t:.2f} s")
        plt.xlim(-3, 5)
        plt.ylim(-3, 3)
        plt.gca().set_aspect('equal')
        plt.pause(0.01)

# Courbes finales
temps = np.arange(steps) * dt

plt.figure()
plt.plot(temps, E_kin, label="Énergie cinétique")
plt.xlabel("Temps (s)")
plt.ylabel("Énergie")
plt.title("Évolution de l'énergie cinétique")
plt.legend()
plt.grid()

plt.figure()
plt.plot(temps, angles, label="Angle réel (°)")
plt.plot(temps, angles_target, '--', label="Angle cible (°)")
plt.xlabel("Temps (s)")
plt.ylabel("Angle")
plt.title("Évolution de l'angle de l'articulation")
plt.legend()
plt.grid()

plt.show()
