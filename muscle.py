import numpy as np

class Muscle:
    def __init__(self, p0, p1, p2, angle_func, rigidite=100.0):
        """
        Contrôleur imposant une position angulaire (cinématique) et générant une force équivalente
        :param p0, p1, p2: Points formant l'articulation (p1 est le pivot central)
        :param angle_func: Fonction cible d'angle (en radians)
        :param rigidite: Intensité du rappel (force = rigidite * écart)
        """
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.angle_func = angle_func
        self.rigidite = rigidite
        self.l1 = np.linalg.norm(self.p0.pos - self.p1.pos)
        self.l2 = np.linalg.norm(self.p2.pos - self.p1.pos)

    def update(self, t):
        theta = self.angle_func(t)

        dir1 = self.p0.pos - self.p1.pos
        norm1 = np.linalg.norm(dir1)
        if norm1 < 1e-6:
            return
        dir1 /= norm1

        ortho = np.array([-dir1[1], dir1[0]])
        target_pos = self.p1.pos + self.l2 * ( np.cos(np.pi - theta) * dir1 + np.sin(np.pi - theta) * ortho )
        
        delta = target_pos - self.p2.pos
        force = self.rigidite * delta

        self.p2.appliquer_force(force)
        self.p1.appliquer_force(-force)
        # print(f"Angle cible = {np.degrees(theta):.1f}°, position cible = {target_pos}, force = {force}")

    def get_angle(self):
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
