import numpy as np

class Muscle:
    def __init__(self, p0, p1, p2, omega_func, intensite=10.0):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.omega_func = omega_func
        self.intensite = intensite

    def update(self, t):
        omega = self.omega_func(t)

        r0 = self.p0.pos - self.p1.pos
        r2 = self.p2.pos - self.p1.pos

        def rotation_2d(v):
            return np.array([-v[1], v[0]])

        v0 = omega * rotation_2d(r0)
        v2 = -omega * rotation_2d(r2)

        self.p0.v += v0
        self.p2.v += v2
        self.p1.v -= (v0 + v2)


def interaction_hydrodynamique_triangle(p0, p1, p2, k_interaction=0.3, angle_seuil_deg=70):
    """
    Force de réaction hydrodynamique simulée entre deux membres formant un angle aigu.
    """
    r0 = p0.pos - p1.pos
    r2 = p2.pos - p1.pos

    norm_r0 = np.linalg.norm(r0)
    norm_r2 = np.linalg.norm(r2)
    if norm_r0 < 1e-6 or norm_r2 < 1e-6:
        return

    cos_angle = np.dot(r0, r2) / (norm_r0 * norm_r2)
    angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))

    if angle > np.radians(angle_seuil_deg):
        return  # angle trop large : pas d'interaction

    aire = 0.5 * np.abs(np.cross(r0, r2))
    v0 = p0.v - p1.v
    v2 = p2.v - p1.v
    v_moy = 0.5 * (v0 + v2)
    f = -k_interaction * aire * v_moy

    p0.v += 0.5 * f / p0.masse
    p2.v += 0.5 * f / p2.masse
    p1.v -= f / p1.masse
