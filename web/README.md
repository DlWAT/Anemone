# Evolve — version navigateur

Simulateur de soft-body évolutif tournant entièrement dans un navigateur moderne.
Aucune dépendance, aucun build : un simple serveur HTTP statique suffit.

## Lancer

Depuis le dossier `web/` :

```bash
# Recommandé (MIME JS forcé pour modules ES, robuste sur Windows)
python dev_server.py --port 8000

# Alternative (peut casser selon la config MIME de la machine)
# python -m http.server 8000
```

Puis ouvrir `http://localhost:8000/` dans Chrome / Firefox / Edge récents.

> Pourquoi un serveur ? Le code utilise les modules ES (`import`) et un Web Worker
> de type module : les navigateurs refusent de charger ces ressources depuis
> `file://` pour des raisons de sécurité. Sur certaines machines Windows,
> `python -m http.server` peut aussi servir `.js` avec un mauvais MIME type,
> d'où `dev_server.py`.

## Architecture

| Fichier | Rôle |
|---|---|
| `index.html` | structure de la page |
| `style.css`  | mise en page sombre |
| `physics.js` | moteur physique (Verlet + PBD + drag anisotrope) |
| `genome.js`  | génération aléatoire et mutation |
| `renderer.js`| rendu Canvas 2D (créature, grille, courbe) |
| `editor.js`  | édition manuelle au clic |
| `worker.js`  | algorithme génétique en arrière-plan |
| `main.js`    | orchestration UI |

## Modèle physique

Chaque créature est un treillis 2D de points masses reliés par des **liens
inextensibles** (PBD) avec des **muscles triangulaires** qui imposent un angle
oscillant (somme de sinusoïdes).

Le milieu fluide est modélisé par segment :

```
F = − C_⊥ · |v·n| · (v·n) · L · n   − C_∥ · |v·t| · (v·t) · L · t
```

avec `C_⊥ ≫ C_∥` (ici 1.8 vs 0.08, soit un rapport ~22), ce qui reproduit
l'asymétrie de drag d'une nageoire dans un fluide visqueux. Une **masse ajoutée**
constante est aussi appliquée (le fluide entraîné autour de chaque point), ce
qui stabilise l'intégration et rend le mouvement plus crédible.

Intégrateur : **Verlet positionnel**, avec contraintes de distance résolues par
**4 itérations PBD** par pas. Stable même à `dt = 0.02 s`.

## Évaluation

```
fitness = distance² / (1 + énergie cinétique cumulée)
```

Favorise les créatures qui se déplacent loin pour peu d'énergie dépensée
(nageurs efficaces).
