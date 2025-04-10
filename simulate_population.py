import numpy as np
import matplotlib.pyplot as plt
import json
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

n = 150
dt = 0.002
steps = 1000
generations = 100
keep_fraction = 0.1
mutation_strength = 0.01


def simulate_creature_from_genome(genome):
    creature = genome_to_creature(genome)
    for _ in range(steps):
        creature.step(dt)
    return creature.evaluate(), genome


if __name__ == "__main__":
    genomes = [mutate_genome(minimal_genome) for _ in range(n)]
    moyennes = []

    worst_score = float('inf')
    worst_genome = None
    best_genome_last_gen = None
    best_score_last_gen = -float('inf')

    for gen in tqdm(range(generations), desc="Générations"):
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(simulate_creature_from_genome, genomes))

        scores = [score for score, _ in results]
        genomes = [genome for _, genome in results]

        # Suivi du pire score toutes générations confondues
        gen_worst_score = min(scores)
        if gen_worst_score < worst_score:
            worst_score = gen_worst_score
            worst_genome = genomes[scores.index(gen_worst_score)]

        # Sauvegarde du meilleur de la dernière génération
        if gen == generations - 1:
            best_score_last_gen = max(scores)
            best_genome_last_gen = genomes[scores.index(best_score_last_gen)]

        genomes, moyenne = evolve_population(
            creatures=[None] * n,
            genomes=genomes,
            n_new=n,
            keep_fraction=keep_fraction,
            mutation_strength=mutation_strength,
            external_scores=scores
        )

        moyennes.append(moyenne)
        # print(f"Génération {gen:02d} - Score moyen : {moyenne:.4f}")

    # Affichage du graphe
    plt.figure()
    plt.plot(moyennes, 'o-', label="Score moyen")
    plt.xlabel("Génération")
    plt.ylabel("Score (distance / énergie)")
    plt.title("Performance moyenne par génération")
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.savefig("performance_par_generation.png", dpi=300)
    plt.show()

    # Sauvegarde des génomes en JSON
    with open("worst_genome_all_time.json", "w") as f:
        json.dump(worst_genome, f, indent=2)
    with open("best_genome_last_generation.json", "w") as f:
        json.dump(best_genome_last_gen, f, indent=2)

    print(f"Pire score global : {worst_score:.4f}")
    print(f"Meilleur score dernière génération : {best_score_last_gen:.4f}")
