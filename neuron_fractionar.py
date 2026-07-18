import math
import numpy as np
class NeuronFractionar:
    def __init__(self, alpha=0.7, memorie_max=20):
        self.alpha = alpha
        self.memorie_max = memorie_max
        self.istoric = []
        self.ponderi = self._calculeaza_ponderi()
    
    def _calculeaza_ponderi(self):
        ponderi = [1.0]
        for j in range(1, self.memorie_max):
            coef = ponderi[-1] * (j - 1 - self.alpha) / j
            ponderi.append((-1)**j * coef)
        return ponderi
    
    def calculeaza_agresivitate(self, semnal_nou):
        self.istoric.append(semnal_nou)
        if len(self.istoric) > self.memorie_max:
            self.istoric = self.istoric[-self.memorie_max:]
        
        M = len(self.istoric)
        output_brut = 0.0
        for j in range(M):
            y = self.istoric[-(j+1)]
            output_brut += self.ponderi[j] * y
        
        beta = 1.0 / (1.0 + math.exp(-output_brut))
        return beta


# TEST
if __name__ == "__main__":
    for alpha in [0.4, 0.7, 1.0]:
        neuron = NeuronFractionar(alpha=alpha, memorie_max=20)
        print(f"\n--- alpha = {alpha} ---")
        
        semnale = [+1, +1, -1, +1, -1, -1, +1, +1, +1, -1]
        for t, s in enumerate(semnale):
            beta = neuron.calculeaza_agresivitate(s)
            print(f"  t={t+1}, semnal={s:+d}, beta={beta:.3f}")