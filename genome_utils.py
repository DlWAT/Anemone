import copy
import numpy as np

def mutate_genome(genome, p_geom=0.1, p_ctrl=0.3, strength=0.1):
    g = copy.deepcopy(genome)

    # Muter les positions
    for i in range(len(g["points"])):
        if np.random.rand() < p_geom:
            dx, dy = np.random.randn(2) * strength
            g["points"][i][0] += dx
            g["points"][i][1] += dy

    # Muter les contrôles musculaires
    for m in g["muscles"]:
        ctrl = m["control"]
        if np.random.rand() < p_ctrl:
            ctrl["base"] += np.random.randn() * 2
            ctrl["amplitudes"] = [a + np.random.randn() * 2 for a in ctrl["amplitudes"]]
            ctrl["frequencies"] = [max(0.05, f + np.random.randn() * 0.1) for f in ctrl["frequencies"]]
            ctrl["phases"] = [p + np.random.randn() * 0.2 for p in ctrl["phases"]]

    return g
