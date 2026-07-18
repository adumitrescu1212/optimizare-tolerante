import numpy as np
import time
from agent_tester import AgentTester
from agent_proiectant import AgentProiectant
from model_matematic import functia_de_joc, valori_nominale


def ruleaza_si_masoara(tolerante_init, alpha):
    proiectant = AgentProiectant(valori_nominale, tolerante_init, delta=0.2)
    tester = AgentTester(alpha=alpha, max_iteratii=500)
    
    fara_defect_consecutiv = 0
    iteratii = 0
    
    start = time.time()
    
    for it in range(300):
        iteratii = it + 1
        tolerante = proiectant.propune_tolerante()
        
        rezultat, X_worst, cota_vinovata = tester.ataca(tolerante)
        beta = tester.get_beta()
        
        if rezultat == "DEFECT":
            fara_defect_consecutiv = 0
            proiectant.primeste_raport(defect_gasit=True, cota_vinovata=cota_vinovata, beta=beta)
        else:
            fara_defect_consecutiv += 1
            
            if fara_defect_consecutiv >= 2:
                break
            
            cota_modificata = proiectant.primeste_raport(defect_gasit=False, beta=beta)
            
            if cota_modificata is False:
                continue
            
            tolerante_noi = proiectant.propune_tolerante()
            rezultat2, _, _ = tester.ataca(tolerante_noi)
            
            if rezultat2 == "DEFECT":
                proiectant.confirma_esec(cota_modificata)
                fara_defect_consecutiv = 0
    
    timp = time.time() - start
    cost = proiectant.calculeaza_cost()
    tolerante = proiectant.propune_tolerante()
    
    return iteratii, cost, timp, tolerante


if __name__ == "__main__":
    tolerante_init = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
    alpha_values = [0.2, 0.4, 0.6, 0.8, 1.0]
    
    print("=" * 65)
    print("EXPERIMENT: Influenta lui alpha asupra performantei")
    print("=" * 65)
    print(f"{'Alpha':<8} {'Iteratii':<10} {'Cost final':<12} {'Timp (s)':<10}")
    print("-" * 45)
    
    rezultate = []
    
    for alpha in alpha_values:
        it, cost, timp, tol = ruleaza_si_masoara(tolerante_init, alpha)
        rezultate.append((alpha, it, cost, timp, tol))
        print(f"{alpha:<8} {it:<10} {cost:<12.2f} {timp:<10.3f}")
    
    print("\n=== ANALIZA ===")
    best_it = min(rezultate, key=lambda x: x[1])
    best_cost = min(rezultate, key=lambda x: x[2])
    print(f"Cea mai rapida convergenta: alpha = {best_it[0]} ({best_it[1]} iteratii)")
    print(f"Cel mai bun cost: alpha = {best_cost[0]} (cost = {best_cost[2]:.2f})")