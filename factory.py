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
    points = [Point(x, y) for x, y in genome["points"]]
    liens = [Lien(points[i], points[j], i=i, j=j) for i, j in genome["links"]]

    muscles = []
    for m in genome["muscles"]:
        i, j, k = m["p0"], m["p1"], m["p2"]
        freqs = m.get("freqs", [1.0])
        amps = m.get("amps", [1.0])
        phases = m.get("phases", [0.0])
        omega_func = sinus_sum_func(freqs, amps, phases)
        muscles.append(Muscle(points[i], points[j], points[k], omega_func, intensite=10.0))

    return Creature(points, liens, muscles)
