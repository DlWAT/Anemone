import numpy as np
from genome_utils import mutate_genome
import copy

def evolve_population(creatures, genomes, n_new, keep_fraction=0.1, mutation_strength=0.05, external_scores=None):
    """
    Fait évoluer une population de génomes :
    - sélectionne les meilleurs selon leur score
    - garde certains parents inchangés
    - génère des enfants par mutation

    Args:
        creatures: liste de créatures (non utilisé si external_scores est fourni)
        genomes: liste de génomes
        n_new: taille cible de la nouvelle population
        keep_fraction: proportion de parents à garder
        mutation_strength: intensité des mutations
        external_scores: tableau de scores (si fourni)

    Returns:
        (nouvelle_liste_genomes, score_moyen)
    """
    if external_scores is not None:
        scores = np.array(external_scores)
    else:
        scores = np.array([c.evaluate() for c in creatures])

    n_parents = max(1, int(len(genomes) * keep_fraction))
    best_indices = np.argsort(scores)[-n_parents:]  # meilleurs scores = meilleurs individus

    new_genomes = []

    # === Étape 1 : garder les meilleurs inchangés ===
    for idx in best_indices:
        new_genomes.append(copy.deepcopy(genomes[idx]))

    # === Étape 2 : produire des mutants ===
    while len(new_genomes) < n_new:
        parent_idx = np.random.choice(best_indices)
        parent_genome = genomes[parent_idx]
        child_genome = mutate_genome(parent_genome, mutation_strength=mutation_strength)
        new_genomes.append(child_genome)

    moyenne = np.mean(scores)
    return new_genomes, moyenne
