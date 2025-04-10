import numpy as np
from point import Point
from link import Lien
from muscle import Muscle
from creature import Creature

def make_angle_func(control):
    base = control["base"]
    amps = control["amplitudes"]
    freqs = control["frequencies"]
    phases = control["phases"]

    def angle_func(t):
        total = base
        for a, f, p in zip(amps, freqs, phases):
            total += a * np.sin(2 * np.pi * f * t + p)
        return np.radians(np.clip(total, 10, 170))

    return angle_func

def genome_to_creature(genome):
    points = [Point(x, y) for x, y in genome["points"]]
    liens = [Lien(points[i], points[j], i=i, j=j) for i, j in genome["liens"]]  # <-- CORRIGÉ ICI

    muscles = []
    for m in genome["muscles"]:
        i, j, k = m["points"]
        angle_func = make_angle_func(m["control"])
        muscles.append(Muscle(points[i], points[j], points[k], angle_func, rigidite=50, amortissement=10))

    return Creature(points, liens, muscles)
