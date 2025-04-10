import numpy as np
from genome_utils import mutate_genome

def evolve_population(creatures, genomes, n_new, keep_fraction=0.1, mutation_strength=0.05, external_scores=None):
    """
    Fait évoluer une population de créatures :
    - sélectionne un sous-ensemble biaisé vers les meilleures
    - applique une mutation légère aux génomes sélectionnés
    - génère une nouvelle génération de n_new individus

    Args:
        creatures: liste d'objets Creature simulés (non utilisé si external_scores est fourni)
        genomes: liste de génomes correspondants
        n_new: nombre de nouveaux génomes à générer
        keep_fraction: proportion d'individus à garder comme parents
        mutation_strength: intensité de la mutation appliquée
        external_scores: scores pré-calculés à utiliser (sinon scores = c.evaluate())

    Returns:
        new_genomes: liste de nouveaux génomes
        moyenne: score moyen de la génération actuelle
    """
    if external_scores is not None:
        scores = np.array(external_scores)
    else:
        scores = np.array([c.evaluate() for c in creatures])

    scores = scores - np.min(scores) + 1e-6  # éviter les 0
    probs = scores / np.sum(scores)

    n_parents = max(1, int(len(genomes) * keep_fraction))
    selected_indices = np.random.choice(len(genomes), size=n_parents, p=probs, replace=False)

    new_genomes = []
    for _ in range(n_new):
        parent_idx = np.random.choice(selected_indices)
        parent_genome = genomes[parent_idx]
        child_genome = mutate_genome(parent_genome, strength=mutation_strength)
        new_genomes.append(child_genome)

    return new_genomes, scores.mean()
