import numpy as np
from genome_utils import mutate_genome
import copy

def evolve_population(creatures, genomes, n_new, keep_fraction=0.1, mutation_strength=0.05, external_scores=None):
    """
    Fait évoluer une population de créatures avec clonage des meilleurs :
    - sélectionne les meilleurs individus selon leur score
    - les garde inchangés
    - génère n_new individus via mutation des parents

    Args:
        creatures: liste d'objets Creature simulés (non utilisé si external_scores est fourni)
        genomes: liste de génomes correspondants
        n_new: nombre total d'individus dans la nouvelle génération
        keep_fraction: proportion d'individus à garder comme parents
        mutation_strength: intensité de la mutation appliquée
        external_scores: scores pré-calculés à utiliser (sinon scores = c.evaluate())

    Returns:
        new_genomes: liste de nouveaux génomes (parents + mutants)
        moyenne: score moyen de la génération actuelle
    """
    if external_scores is not None:
        scores = np.array(external_scores)
    else:
        scores = np.array([c.evaluate() for c in creatures])

    n_parents = max(1, int(len(genomes) * keep_fraction))
    best_indices = np.argsort(scores)[-n_parents:]  # Garde les meilleurs individus (score max)

    new_genomes = []

    # Ajouter les parents inchangés
    for idx in best_indices:
        new_genomes.append(copy.deepcopy(genomes[idx]))

    # Créer les mutants (n_mutants par parent)
    n_mutants_per_parent = (n_new - n_parents) // n_parents

    for idx in best_indices:
        parent_genome = genomes[idx]
        for _ in range(n_mutants_per_parent):
            child_genome = mutate_genome(parent_genome, strength=mutation_strength)
            new_genomes.append(child_genome)

    # Compléter si besoin (si n_new n'est pas exactement multiple)
    while len(new_genomes) < n_new:
        parent_idx = np.random.choice(best_indices)
        parent_genome = genomes[parent_idx]
        child_genome = mutate_genome(parent_genome, strength=mutation_strength)
        new_genomes.append(child_genome)

    return new_genomes, scores.max()
