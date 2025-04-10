import numpy as np

class Lien:
    def __init__(self, p1, p2, i=None, j=None, longueur_repos=None, intensite=2.0):
        """
        Lien entre deux points avec option de stockage des indices (i, j)
        :param p1: premier point
        :param p2: deuxième point
        :param i: index du point p1 dans la liste des points (optionnel)
        :param j: index du point p2 dans la liste des points (optionnel)
        :param longueur_repos: longueur au repos du lien
        :param intensite: raideur du lien
        """
        self.p1 = p1
        self.p2 = p2
        self.i = i
        self.j = j
        self.longueur_repos = longueur_repos or np.linalg.norm(p2.pos - p1.pos)
        self.intensite = intensite

    def corriger(self):
        delta = self.p2.pos - self.p1.pos
        distance = np.linalg.norm(delta)
        if distance < 1e-8:
            return
        direction = delta / distance
        correction = (distance - self.longueur_repos) * direction * 0.5 * self.intensite
        self.p1.pos += correction
        self.p2.pos -= correction

    def resistance_fluide(self):
        delta = self.p2.pos - self.p1.pos
        distance = np.linalg.norm(delta)
        if distance < 1e-8:
            return
        direction = delta / distance
        v_moy = 0.5 * (self.p1.vitesse + self.p2.vitesse)
        v_para = np.dot(v_moy, direction) * direction
        v_perp = -(v_moy - v_para)

        k_para = 0.01
        k_perp = 0.5
        if np.dot(v_para, direction) < 0:
            k_para *= 3  # freinage asymétrique

        v_global = 0.5 * (self.p1.vitesse + self.p2.vitesse)
        norm_vg = np.linalg.norm(v_global)

        if norm_vg > 1e-6:
            v_dir = v_global / norm_vg
            alignement = abs(np.dot(v_dir, direction))  # proche de 1 si bien aligné
            k_perp_eff = k_perp * (1 - 0.7 * alignement**2)  # moins de résistance si bien profilé
        else:
            k_perp_eff = k_perp

        f_fluide = -k_para * v_para - k_perp_eff * v_perp
        self.p1.appliquer_force(f_fluide * 0.5)
        self.p2.appliquer_force(f_fluide * 0.5)