import numpy as np

class Muscle:
    def __init__(self, p0, p1, p2, angle_func, rigidite=50.0, amortissement=10.0):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.angle_func = angle_func
        self.rigidite = rigidite
        self.amortissement = amortissement
        self.l1 = np.linalg.norm(self.p0.pos - self.p1.pos)
        self.l2 = np.linalg.norm(self.p2.pos - self.p1.pos)

    def update(self, t):
        theta = self.angle_func(t)  # angle cible en radians, déjà limité entre 10° et 170°

        # Direction du lien fixe p0→p1
        dir1 = self.p0.pos - self.p1.pos
        norm1 = np.linalg.norm(dir1)
        if norm1 < 1e-6:
            return
        dir1 /= norm1
        ortho = np.array([-dir1[1], dir1[0]])

        # Position cible du point p2 (toujours dans le même côté du plan)
        target_pos = self.p1.pos + self.l2 * (np.cos(theta) * dir1 + np.sin(theta) * ortho)

        # Force vers la position cible
        delta = target_pos - self.p2.pos
        force = self.rigidite * delta

        # Amortissement basé sur la vitesse perpendiculaire
        v_rel = self.p2.vitesse - self.p1.vitesse
        damping_force = -self.amortissement * np.dot(v_rel, ortho) * ortho
        force += damping_force

        self.p2.appliquer_force(force)
        self.p1.appliquer_force(-force)

    def get_angle(self):
        """Renvoie un angle toujours entre 0° et 180°"""
        v1 = self.p0.pos - self.p1.pos
        v2 = self.p2.pos - self.p1.pos
        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        if n1 < 1e-6 or n2 < 1e-6:
            return 0.0
        v1n = v1 / n1
        v2n = v2 / n2
        dot = np.clip(np.dot(v1n, v2n), -1.0, 1.0)
        return np.degrees(np.arccos(dot))
