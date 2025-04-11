import numpy as np
from point import Point
from link import Lien
from muscle import Muscle
from creature import Creature
import copy
import random


def sinus_sum_func(freqs, amps, phases):
    def omega_func(t):
        return sum(a * np.sin(2 * np.pi * f * t + p) for a, f, p in zip(amps, freqs, phases))
    return omega_func

def genome_to_creature(genome):
    points_data = genome['points']
    links_data = genome['links']
    muscles_data = genome['muscles']

    points = [Point(x, y) for x, y in points_data]

    liens = []
    for i, j in links_data:
        lien = Lien(points[i], points[j], i=i, j=j)
        liens.append(lien)

    muscles = []
    for muscle_def in muscles_data:
        i, j, k = muscle_def['p0'], muscle_def['p1'], muscle_def['p2']
        freqs = muscle_def.get('freqs', [1.0])
        amps = muscle_def.get('amps', [1.0])
        phases = muscle_def.get('phases', [0.0])
        intensite = muscle_def.get('intensite', 10.0)
        omega_func = sinus_sum_func(freqs, amps, phases)
        muscle = Muscle(points[i], points[j], points[k], omega_func, intensite)
        muscles.append(muscle)

    return Creature(points, liens, muscles)

import copy
import random
import numpy as np

def mutate_genome(genome, mutation_strength=0.1):
    new_genome = copy.deepcopy(genome)

    # # === Mutation position points 0 et 2 (autour de p1) ===
    # if "points" in new_genome and len(new_genome["points"]) >= 3:
    #     p1 = np.array(new_genome["points"][1])
    #     l1 = np.linalg.norm(np.array(new_genome["points"][0]) - p1)
    #     l2 = np.linalg.norm(np.array(new_genome["points"][2]) - p1)

    #     theta0 = random.uniform(0, 2 * np.pi)
    #     theta2 = random.uniform(0, 2 * np.pi)

    #     new_genome["points"][0] = (p1 + l1 * np.array([np.cos(theta0), np.sin(theta0)])).tolist()
    #     new_genome["points"][2] = (p1 + l2 * np.array([np.cos(theta2), np.sin(theta2)])).tolist()

    # === Mutation des muscles (au plus UNE mutation par muscle) ===
    for m in new_genome.get("muscles", []):
        actions = []

        if len(m.get("freqs", [])) > 0:
            actions.append("mut_freq")
        if len(m.get("amps", [])) > 0:
            actions.append("mut_amp")
        if len(m.get("phases", [])) > 0:
            actions.append("mut_phase")
        actions.append("mut_intensite")
        if len(m.get("freqs", [])) > 1:
            actions.append("remove")
        if len(m.get("freqs", [])) < 6:
            actions.append("add")

        action = random.choice(actions)

        if action == "mut_freq":
            idx = random.randint(0, len(m["freqs"]) - 1)
            m["freqs"][idx] = max(0.05, m["freqs"][idx] + random.gauss(0, mutation_strength))

        elif action == "mut_amp":
            idx = random.randint(0, len(m["amps"]) - 1)
            m["amps"][idx] = max(0.0, m["amps"][idx] + random.gauss(0, mutation_strength))

        elif action == "mut_phase":
            idx = random.randint(0, len(m["phases"]) - 1)
            m["phases"][idx] = (m["phases"][idx] + random.gauss(0, mutation_strength)) % (2 * np.pi)

        elif action == "mut_intensite":
            m["intensite"] = max(0.1, m.get("intensite", 10.0) + random.gauss(0, mutation_strength * 5))

        elif action == "add":
            m["freqs"].append(random.uniform(0.1, 2.0))
            m["amps"].append(random.uniform(0.1, 2.0))
            m["phases"].append(random.uniform(0, 2 * np.pi))

        elif action == "remove":
            idx = random.randint(0, len(m["freqs"]) - 1)
            m["freqs"].pop(idx)
            m["amps"].pop(idx)
            m["phases"].pop(idx)

    return new_genome

