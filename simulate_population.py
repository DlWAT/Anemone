from genome_utils import genome_to_creature

def evaluate_genome(genome, steps=1000, dt=0.01):
    creature = genome_to_creature(genome)
    for _ in range(steps):
        creature.step(dt)
    return creature.evaluate()

def evaluate_population(population):
    scores = []
    for genome in population:
        score = evaluate_genome(genome)
        scores.append(score)
    return scores
