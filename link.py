import numpy as np

class Lien:
    def __init__(self, p1, p2, i=None, j=None, longueur_repos=None):
        self.p1 = p1
        self.p2 = p2
        self.i = i
        self.j = j
        self.longueur_repos = longueur_repos or np.linalg.norm(p2.pos - p1.pos)

    def appliquer_forces(self):
        self.appliquer_frottement_oriente()
        self.appliquer_contrainte_distance()

    def appliquer_frottement_oriente(self, k_para=0.02, k_perp=0.2):
        delta = self.p2.pos - self.p1.pos
        dist = np.linalg.norm(delta)
        if dist < 1e-8:
            return

        u = delta / dist
        u_perp = np.array([-u[1], u[0]])
        v_moy = 0.5 * (self.p1.v + self.p2.v)
        v_norm = np.linalg.norm(v_moy)
        if v_norm < 1e-8:
            return

        v_dir = v_moy / v_norm
        cos_theta = np.dot(u, v_dir)
        sin_theta = np.dot(u_perp, v_dir)

        f = -v_norm * (k_para * cos_theta * u + k_perp * sin_theta * u_perp)

        self.p1.v += (f / self.p1.masse) * 0.5
        self.p2.v += (f / self.p2.masse) * 0.5

    def appliquer_contrainte_distance(self):
        delta = self.p2.pos - self.p1.pos
        dist = np.linalg.norm(delta)
        if dist == 0:
            return
        direction = delta / dist
        erreur = dist - self.longueur_repos
        correction = 0.5 * erreur * direction
        self.p1.pos += correction
        self.p2.pos -= correction

        v_rel = self.p2.v - self.p1.v
        radial = np.dot(v_rel, direction)
        self.p1.v += 0.5 * radial * direction
        self.p2.v -= 0.5 * radial * direction
