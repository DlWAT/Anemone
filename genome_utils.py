import numpy as np
from point import Point
from link import Lien
from muscle import Muscle
from creature import Creature

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
