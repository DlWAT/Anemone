import numpy as np
import matplotlib.pyplot as plt
from factory import genome_to_creature
from genome_utils import mutate_genome
from evolution import evolve_population
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

# ==== Paramètres de simulation ====
minimal_genome = {
    "points": [[0, 0], [1, 0], [2, 1]],
    "liens": [(0, 1), (1, 2)],
    "muscles": [
        {
            "points": (0, 1, 2),
            "control": {
                "base": 90,
                "amplitudes": [30, 15],
                "frequencies": [0.5, 0.25],
                "phases": [0.0, 1.0]
            }
        }
    ]
}

n = 50                    # Taille de la population
dt = 0.02                 # Pas de temps
steps = 1000              # Nombre d'itérations par créature
generations = 15          # Nombre de générations
keep_fraction = 0.1       # Fraction sélectionnée
mutation_strength = 0.05  # Intensité de mutation


# ==== Simulation d'une créature (pour multiprocessing) ====
def simulate_creature_from_genome(genome):
    creature = genome_to_creature(genome)
    for _ in range(steps):
        creature.step(dt)
    return creature.evaluate(), genome


# ==== Exécution principale ====
if __name__ == "__main__":
    genomes = [mutate_genome(minimal_genome) for _ in range(n)]
    moyennes = []

    for gen in tqdm(range(generations), desc="Générations"):
        # Simulation en parallèle
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(simulate_creature_from_genome, genomes))

        scores = [score for score, _ in results]
        genomes = [genome for _, genome in results]

        # Évolution
        genomes, moyenne = evolve_population(
            creatures=[None]*n,  # non utilisé ici
            genomes=genomes,
            n_new=n,
            keep_fraction=keep_fraction,
            mutation_strength=mutation_strength,
            external_scores=scores
        )

        moyennes.append(moyenne)
        print(f"Génération {gen:02d} - Score moyen : {moyenne:.4f}")

    # Affichage du graphe
    plt.figure()
    plt.plot(moyennes, 'o-', label="Score moyen")
    plt.xlabel("Génération")
    plt.ylabel("Score (distance / énergie)")
    plt.title("Performance moyenne par génération")
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()
