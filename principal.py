import numpy as np
from agent_tester import AgentTester
from agent_proiectant import AgentProiectant
from model_matematic import functia_de_joc, valori_nominale


def ruleaza_sistem(tolerante_init, alpha=0.7, max_iteratii=200):
    proiectant = AgentProiectant(valori_nominale, tolerante_init, delta=0.2)
    tester = AgentTester(alpha=alpha, max_iteratii=500)
    
    fara_defect_consecutiv = 0
    
    print(f"{'Iter':<6} {'Rezultat':<8} {'Beta':<8} {'Cost':<10} {'Joc min':<10}")
    print("-" * 50)
    
    for it in range(max_iteratii):
        tolerante = proiectant.propune_tolerante()
        cost = proiectant.calculeaza_cost()
        
        rezultat, X_worst, cota_vinovata = tester.ataca(tolerante)
        beta = tester.get_beta()
        joc, _, _ = functia_de_joc(X_worst)
        
        if it % 3 == 0 or rezultat == "OK":
            print(f"{it+1:<6} {rezultat:<8} {beta:<8.3f} {cost:<10.2f} {joc:<10.4f}")
        
        if rezultat == "DEFECT":
            fara_defect_consecutiv = 0
            proiectant.primeste_raport(defect_gasit=True, cota_vinovata=cota_vinovata, beta=beta)
        else:
            fara_defect_consecutiv += 1
            
            if fara_defect_consecutiv >= 2:
                print(f"\n>>> CONVERGENTA <<<")
                break
            
            cota_modificata = proiectant.primeste_raport(defect_gasit=False, beta=beta)
            
            if cota_modificata is False:
                continue
            
            tolerante_noi = proiectant.propune_tolerante()
            rezultat2, _, _ = tester.ataca(tolerante_noi)
            
            if rezultat2 == "DEFECT":
                proiectant.confirma_esec(cota_modificata)
                fara_defect_consecutiv = 0
    
    print("\n=== REZULTATE FINALE ===")
    print(f"Tolerante optime: {np.round(proiectant.propune_tolerante(), 4)}")
    print(f"Cost optim: {proiectant.calculeaza_cost():.2f}")
    
    return proiectant.propune_tolerante(), proiectant.calculeaza_cost()


if __name__ == "__main__":
    tolerante_init = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
    
    print("=" * 50)
    print("SISTEM MULTI-AGENT CU NEURON FRACTIONAR")
    print("=" * 50)
    print(f"Alpha = 0.7\n")
    
    ruleaza_sistem(tolerante_init, alpha=0.7)