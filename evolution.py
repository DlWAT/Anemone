import numpy as np
from genome_utils import mutate_genome
import copy

def evolve_population(creatures, genomes, n_new, keep_fraction=0.1, mutation_strength=0.05, external_scores=None):
    """
    Fait évoluer une population avec conservation stricte de certains individus :
    - garde les meilleurs inchangés (élitisme)
    - génère les autres via mutation
    """

    if external_scores is not None:
        scores = np.array(external_scores)
    else:
        scores = np.array([c.evaluate() for c in creatures])

    n_parents = max(1, int(len(genomes) * keep_fraction))
    best_indices = np.argsort(scores)[-n_parents:]

    new_genomes = []

    # === Étape 1 : Ajouter les parents tels quels (non mutés)
    for idx in best_indices:
        new_genomes.append(copy.deepcopy(genomes[idx]))  # clone exact

    # === Étape 2 : Ajouter des mutants
    while len(new_genomes) < n_new:
        parent_idx = np.random.choice(best_indices)
        parent_genome = genomes[parent_idx]
        child_genome = mutate_genome(parent_genome, mutation_strength=mutation_strength)
        new_genomes.append(child_genome)

    moyenne = np.max(scores)
    return new_genomes, moyenne
