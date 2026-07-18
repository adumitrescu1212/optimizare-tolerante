import numpy as np

class AgentProiectant:
    def __init__(self, valori_nominale, tolerante_init, delta=0.2):
        self.valori_nom = np.array(valori_nominale)
        self.tolerante = np.array(tolerante_init, dtype=float)
        self.delta = delta
        self.n = len(tolerante_init)
        self.incercari_esuate = set()
        self.toleranta_minima = 0.01  # prag minim realist de fabricație (10 microni)
    
    def calculeaza_cost(self):
        return np.sum(1.0 / (self.tolerante + 1e-9))
    
    def propune_tolerante(self):
        return self.tolerante.copy()
    
    def primeste_raport(self, defect_gasit, cota_vinovata=None, beta=0.5):
        # delta efectiv = delta de bază modulat de beta
        delta_efectiv = self.delta * beta
        
        if defect_gasit and cota_vinovata is not None:
            # Strânge toleranța la cota vinovată
            self.tolerante[cota_vinovata] = self.tolerante[cota_vinovata] / (1 + delta_efectiv)
            # Limită inferioară: toleranța nu poate scădea sub pragul minim
            self.tolerante[cota_vinovata] = max(self.tolerante[cota_vinovata], self.toleranta_minima)
            return True
        else:
            # Încearcă să lărgească cea mai strânsă toleranță
            costuri = 1.0 / (self.tolerante + 1e-9)
            ordine = np.argsort(costuri)[::-1]  # descrescător după cost
            for idx in ordine:
                if idx not in self.incercari_esuate:
                    self.tolerante[idx] = self.tolerante[idx] * (1 + delta_efectiv)
                    return True
            return False
    
    def confirma_esec(self, cota):
        # Revino la valoarea anterioară și marchează ca eșuat
        self.tolerante[cota] = self.tolerante[cota] / (1 + self.delta * 0.5)
        self.incercari_esuate.add(cota)
    
    def a_convergenta(self):
        return len(self.incercari_esuate) >= self.n