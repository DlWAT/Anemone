import copy
import numpy as np

def mutate_genome(genome, strength=0.1):
    g = copy.deepcopy(genome)

    mutation_type = np.random.choice(["base", "amplitude", "frequency", "phase"]) # "point",

    if mutation_type == "point":
        i = np.random.randint(len(g["points"]))
        dx, dy = np.random.randn(2) * strength
        g["points"][i][0] += dx
        g["points"][i][1] += dy

    elif mutation_type == "base":
        m = np.random.choice(g["muscles"])
        m["control"]["base"] += np.random.randn() * 2

    elif mutation_type == "amplitude":
        m = np.random.choice(g["muscles"])
        a_idx = np.random.randint(len(m["control"]["amplitudes"]))
        m["control"]["amplitudes"][a_idx] += np.random.randn() * 2

    elif mutation_type == "frequency":
        m = np.random.choice(g["muscles"])
        f_idx = np.random.randint(len(m["control"]["frequencies"]))
        m["control"]["frequencies"][f_idx] = max(0.05, m["control"]["frequencies"][f_idx] + np.random.randn() * 0.1)

    elif mutation_type == "phase":
        m = np.random.choice(g["muscles"])
        p_idx = np.random.randint(len(m["control"]["phases"]))
        m["control"]["phases"][p_idx] += np.random.randn() * 0.2

    return g
