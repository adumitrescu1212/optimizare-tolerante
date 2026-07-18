import numpy as np
from neuron_fractionar import NeuronFractionar
from model_matematic import functia_de_joc, valori_nominale


class AgentTester:
    def __init__(self, alpha=0.7, max_iteratii=500):
        self.neuron = NeuronFractionar(alpha=alpha, memorie_max=20)
        self.max_iteratii = max_iteratii
        self.ultimul_beta = 0.5  # valoare implicită
    
    def ataca(self, tolerante):
        f_best = float('inf')
        X_best = None
        
        # Enumerează toate cele 2^6 = 64 de vârfuri
        for masca in range(64):
            X = valori_nominale.copy()
            for i in range(6):
                if (masca >> i) & 1:
                    X[i] = valori_nominale[i] + tolerante[i]
                else:
                    X[i] = valori_nominale[i] - tolerante[i]
            
            joc, _, _ = functia_de_joc(X)
            if joc < f_best:
                f_best = joc
                X_best = X.copy()
        
        # Puncte interioare aleatoare pentru siguranță
        limite_inf = valori_nominale - tolerante
        limite_sup = valori_nominale + tolerante
        for _ in range(100):
            X = np.random.uniform(limite_inf, limite_sup)
            joc, _, _ = functia_de_joc(X)
            if joc < f_best:
                f_best = joc
                X_best = X.copy()
        
        if f_best < -0.01:
            cota_vinovata = self._identifica_cota_vinovata(X_best, tolerante)
            self.ultimul_beta = self.neuron.calculeaza_agresivitate(+1)
            return "DEFECT", X_best, cota_vinovata
        else:
            self.ultimul_beta = self.neuron.calculeaza_agresivitate(-1)
            return "OK", X_best, None
    
    def get_beta(self):
        """Întoarce ultimul factor de agresivitate calculat."""
        return self.ultimul_beta
    
    def _identifica_cota_vinovata(self, X, tolerante):
        abateri = np.abs(X - valori_nominale) / (tolerante + 1e-9)
        return np.argmax(abateri)