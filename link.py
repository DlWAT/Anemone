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
        if distance < 1e-8 or not np.isfinite(distance):
            return
        direction = delta / distance
        correction = (distance - self.longueur_repos) * direction * 0.5 * self.intensite
        if not np.all(np.isfinite(correction)):
            return
        self.p1.pos += correction
        self.p2.pos -= correction

    def resistance_fluide(self):
        delta = self.p2.pos - self.p1.pos
        distance = np.linalg.norm(delta)
        if distance < 1e-8 or not np.isfinite(distance):
            return

        direction = delta / distance
        v_moy = 0.5 * (self.p1.vitesse + self.p2.vitesse)

        # Composantes parallèle et perpendiculaire
        v_para = np.dot(v_moy, direction) * direction
        v_perp = -(v_moy - v_para)

        # Coefficients de résistance de base
        k_para = 0.01
        k_perp = 0.5

        # Freinage asymétrique si recul
        if np.dot(v_para, direction) < 0:
            k_para *= 3

        # Ajustement du k_perp en fonction de l’alignement global (forme profilée)
        norm_vg = np.linalg.norm(v_moy)
        if norm_vg > 1e-6:
            v_dir = v_moy / norm_vg
            alignement = abs(np.dot(v_dir, direction))  # proche de 1 si bien aligné
            k_perp_eff = k_perp * (1 - 0.7 * alignement**2)

            # Asymétrie directionnelle
            ortho = np.array([-direction[1], direction[0]])  # vecteur perpendiculaire
            if np.dot(v_moy, ortho) > 0:
                k_perp_eff *= 1.2
            else:
                k_perp_eff *= 0.8
        else:
            k_perp_eff = k_perp

        # Force de fluide
        f_fluide = -k_para * v_para - k_perp_eff * v_perp

        # Application de la force
        self.p1.appliquer_force(f_fluide * 0.5)
        self.p2.appliquer_force(f_fluide * 0.5)

        # Calcul du moment de rotation autour du centre du lien (à titre informatif)
        center = 0.5 * (self.p1.pos + self.p2.pos)
        r1 = self.p1.pos - center
        r2 = self.p2.pos - center
        moment = np.cross(r1, f_fluide * 0.5) + np.cross(r2, -f_fluide * 0.5)

        # --- PROPULSION ACTIVE ASYMÉTRIQUE ---

        # Vitesse relative entre les deux extrémités
        v_rel = self.p2.vitesse - self.p1.vitesse

        # Direction perpendiculaire (rame) dans le plan 2D
        ortho = np.array([-direction[1], direction[0]])

        # Composante perpendiculaire de la vitesse relative (effet de rame)
        v_proj = np.dot(v_rel, ortho)

        # Force de propulsion : asymétrique selon le sens de poussée
        k_propulsion = 0.2  # à ajuster selon ton échelle de vitesses
        if v_proj > 0:
            f_prop = -ortho * v_proj * k_propulsion  # poussée dans un sens
        else:
            f_prop = -ortho * v_proj * k_propulsion * 0.5  # moins efficace dans l’autre

        # Appliquer la poussée aux deux extrémités
        self.p1.appliquer_force(+0.5 * f_prop)
        self.p2.appliquer_force(-0.5 * f_prop)

        # DEBUG (optionnel)
        # print(f"Propulsion ({self.i}, {self.j}) : {f_prop}")
