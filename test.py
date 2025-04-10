import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# === Classe Point ===
class Point:
    def __init__(self, x, y, masse=1.0):
        self.pos = np.array([x, y], dtype=float)
        self.v = np.zeros(2)
        self.f = np.zeros(2)
        self.masse = masse

    def update(self, dt, vmax=5.0):
        self.pos += self.v * dt
        speed = np.linalg.norm(self.v)
        if speed > vmax:
            self.v = self.v / speed * vmax

# === Muscle avec vitesse angulaire directe ===
class MuscleAngulaireDirect:
    def __init__(self, p0, p1, p2, omega_func, facteur=1.0):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.omega_func = omega_func
        self.facteur = facteur

    def update(self, t):
        omega = self.omega_func(t) * self.facteur

        r0 = self.p0.pos - self.p1.pos
        r2 = self.p2.pos - self.p1.pos

        def rotation_2d(v):
            return np.array([-v[1], v[0]])

        v0 = omega * rotation_2d(r0)
        v2 = -omega * rotation_2d(r2)

        self.p0.v += v0
        self.p2.v += v2
        self.p1.v -= (v0 + v2)

# === Correction de distance rigide
def corriger_distance(pA, pB, L):
    delta = pB.pos - pA.pos
    dist = np.linalg.norm(delta)
    if dist == 0:
        return
    direction = delta / dist
    erreur = dist - L
    correction = 0.5 * erreur * direction
    pA.pos += correction
    pB.pos -= correction

    v_rel = pB.v - pA.v
    radial = np.dot(v_rel, direction)
    pA.v += 0.5 * radial * direction
    pB.v -= 0.5 * radial * direction

# === Frottement fluide orienté
def appliquer_frottement_oriente(pA, pB, k_para=0.02, k_perp=0.2):
    delta = pB.pos - pA.pos
    dist = np.linalg.norm(delta)
    if dist < 1e-8:
        return

    u = delta / dist
    u_perp = np.array([-u[1], u[0]])

    v_moy = 0.5 * (pA.v + pB.v)
    v_norm = np.linalg.norm(v_moy)
    if v_norm < 1e-8:
        return

    v_dir = v_moy / v_norm

    cos_theta = np.dot(u, v_dir)
    sin_theta = np.dot(u_perp, v_dir)

    f = -v_norm * (k_para * cos_theta * u + k_perp * sin_theta * u_perp)

    pA.v += (f / pA.masse) * 0.5
    pB.v += (f / pB.masse) * 0.5

# === Somme de sinusoïdes pour la vitesse angulaire
def omega_func(t):
    if t < 0.5:
        return -np.pi  # rotation rapide de 90° → 0°
    elif t < 1.2:
        return 0.0     # pause à 0°
    elif t < 2.5:
        return 1.5 * np.sin(4 * np.pi * (t - 1.2))  # oscillations rapides (2 Hz)
    elif t < 3.5:
        return 0.3 * np.sin(2 * np.pi * (t - 2.5))  # amortissement lent
    else:
        return 0.0     # repos


# === Initialisation
L = 1.0
p0 = Point(-L, 0)
p1 = Point(0, 0)
p2 = Point(+L, 0)

muscle = MuscleAngulaireDirect(p0, p1, p2, omega_func, facteur=1.0)

dt = 0.005
steps = 2000
positions = []

for step in range(steps):
    t = step * dt

    muscle.update(t)

    appliquer_frottement_oriente(p0, p1)
    appliquer_frottement_oriente(p1, p2)

    for p in [p0, p1, p2]:
        p.update(dt)

    corriger_distance(p0, p1, L)
    corriger_distance(p1, p2, L)

    positions.append([p0.pos.copy(), p1.pos.copy(), p2.pos.copy()])

positions = np.array(positions)

# === Animation ===
fig, ax = plt.subplots()
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_aspect('equal')
line, = ax.plot([], [], 'o-', lw=2)
text = ax.text(0.05, 0.9, '', transform=ax.transAxes)

def init():
    line.set_data([], [])
    text.set_text('')
    return line, text

def update(frame):
    pts = positions[frame]
    x = pts[:, 0]
    y = pts[:, 1]
    line.set_data(x, y)
    text.set_text(f't = {frame*dt:.2f}s')
    return line, text

ani = FuncAnimation(fig, update, frames=len(positions), init_func=init, blit=True, interval=20)
plt.title("Somme de sinusoïdes + frottement fluide orienté")
plt.grid()
plt.show()
