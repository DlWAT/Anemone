import numpy as np

def random_angle_function(n_terms=2, base=90):
    # Génère une fonction angle(t) = base + Σ amp_i * sin(2π * freq_i * t + phase_i)
    amplitudes = np.random.uniform(5, 30, size=n_terms)
    frequencies = np.random.uniform(0.1, 1.5, size=n_terms)
    phases = np.random.uniform(0, 2 * np.pi, size=n_terms)

    def angle_func(t):
        total = base
        for amp, freq, phase in zip(amplitudes, frequencies, phases):
            total += amp * np.sin(2 * np.pi * freq * t + phase)
        return np.radians(np.clip(total, 10, 170))  # Toujours entre 10° et 170°
    
    return angle_func
