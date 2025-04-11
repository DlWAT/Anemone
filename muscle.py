import numpy as np

class Muscle:
    def __init__(self, p0, p1, p2, angle_func, intensite=10.0):
        """
        Muscle triangulaire entre p0, p1 (pivot), p2.
        angle_func(t) donne l'angle (en radians) entre p0–p1–p2 au temps t.
        """
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.angle_func = angle_func
        self.intensite = intensite

        # Longueurs fixes à l'initialisation
        self.l0 = np.linalg.norm(p0.pos - p1.pos)
        self.l2 = np.linalg.norm(p2.pos - p1.pos)

    def update(self, t):
        theta = self.angle_func(t)  # Angle cible à appliquer (en radians)

        r0 = self.p0.pos - self.p1.pos
        norm_r0 = np.linalg.norm(r0)
        if norm_r0 < 1e-6:
            return

        dir0 = r0 / norm_r0
        ortho = np.array([-dir0[1], dir0[0]])

        # Positions cibles pour p0 et p2
        target_r0 = self.l0 * (np.cos(theta / 2) * dir0 + np.sin(theta / 2) * ortho)
        target_r2 = self.l2 * (np.cos(theta / 2) * dir0 - np.sin(theta / 2) * ortho)

        p0_target = self.p1.pos + target_r0
        p2_target = self.p1.pos + target_r2

        # Force de rappel (appliquée sous forme de variation de vitesse)
        force0 = self.intensite * (p0_target - self.p0.pos)
        force2 = self.intensite * (p2_target - self.p2.pos)

        self.p0.v += force0 / self.p0.masse
        self.p2.v += force2 / self.p2.masse
        self.p1.v -= (force0 + force2) / self.p1.masse


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

    # if angle > np.radians(angle_seuil_deg):
    #     return  # angle trop large : pas d'interaction

    aire = 0.5 * np.abs(np.cross(r0, r2))
    v0 = p0.v - p1.v
    v2 = p2.v - p1.v
    v_moy = 0.5 * (v0 + v2)
    f = -k_interaction * aire * v_moy

    p0.v += 0.5 * f / p0.masse
    p2.v += 0.5 * f / p2.masse
    p1.v -= f / p1.masse
