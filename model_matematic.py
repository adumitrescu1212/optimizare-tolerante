import numpy as np

# =============================================
# DATELE ANSAMBLULUI (valori nominale)
# =============================================
# Ordinea cotelor în vectorul X:
# [D_stift, D_gaura, DistX_baza, DistY_baza, DistX_capac, DistY_capac]

valori_nominale = np.array([10.0, 10.2, 50.0, 40.0, 50.0, 40.0])

# Toleranțe inițiale (folosite doar la test)
tolerante_test = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5])


def functia_de_joc(X):
    """
    Calculează jocul minim pentru un vector de cote X.
    
    X = [D_stift, D_gaura, DistX_baza, DistY_baza, DistX_capac, DistY_capac]
    
    Pentru simplificare, considerăm 2 știfturi cu pozițiile:
      Știft 1: (DistX_baza - 25, DistY_baza - 20)
      Știft 2: (DistX_baza + 25, DistY_baza + 20)
    
    Găurile sunt la pozițiile:
      Gaura 1: (DistX_capac - 25, DistY_capac - 20)
      Gaura 2: (DistX_capac + 25, DistY_capac + 20)
    
    Abaterea de poziție ΔPoz = distanța euclidiană între centrul știftului
    și centrul găurii.
    """
    D_stift, D_gaura = X[0], X[1]
    R_stift = D_stift / 2.0
    R_gaura = D_gaura / 2.0
    
    # Pozițiile știfturilor
    stift1_x = X[2] - 25.0
    stift1_y = X[3] - 20.0
    stift2_x = X[2] + 25.0
    stift2_y = X[3] + 20.0
    
    # Pozițiile găurilor
    gaura1_x = X[4] - 25.0
    gaura1_y = X[5] - 20.0
    gaura2_x = X[4] + 25.0
    gaura2_y = X[5] + 20.0
    
    # Abateri de poziție
    delta1 = np.sqrt((stift1_x - gaura1_x)**2 + (stift1_y - gaura1_y)**2)
    delta2 = np.sqrt((stift2_x - gaura2_x)**2 + (stift2_y - gaura2_y)**2)
    
    # Jocuri
    joc1 = R_gaura - R_stift - delta1
    joc2 = R_gaura - R_stift - delta2
    
    # Jocul global = minimul
    return min(joc1, joc2), joc1, joc2


def calculeaza_subgradient(X, epsilon=1e-8):
    """
    Calculează subgradientul funcției de joc în punctul X.
    Folosește expresia analitică exactă a gradientului.
    """
    x1, x2, x3, x4, x5, x6 = X
    
    # Distanța euclidiană dintre centre
    dx = x3 - x5
    dy = x4 - x6
    d = np.sqrt(dx**2 + dy**2)
    
    # Regularizare: dacă centrele coincid, folosim o direcție implicită
    if d < epsilon:
        # Când centrele coincid, orice direcție de separare e validă
        # Folosim un vector unitar arbitrar pentru termenii de poziție
        d_inv = 0.0
    else:
        d_inv = 1.0 / d
    
    # Gradientul analitic (conform Teoremei 3.3)
    grad = np.array([
        -0.5,           # ∂f/∂x1 = -1/2
         0.5,           # ∂f/∂x2 = +1/2
        -dx * d_inv,    # ∂f/∂x3 = -(x3-x5)/d
        -dy * d_inv,    # ∂f/∂x4 = -(x4-x6)/d
         dx * d_inv,    # ∂f/∂x5 = +(x3-x5)/d
         dy * d_inv     # ∂f/∂x6 = +(x4-x6)/d
    ])
    
    return grad

# =============================================
# TEST
# =============================================
if __name__ == "__main__":
    # Test 1: Valori nominale (ar trebui să fie OK)
    print("=== TEST 1: Valori nominale ===")
    joc, j1, j2 = functia_de_joc(valori_nominale)
    print(f"  Joc 1 = {j1:.4f} mm")
    print(f"  Joc 2 = {j2:.4f} mm")
    print(f"  Joc global = {joc:.4f} mm")
    print(f"  Asamblare: {'OK' if joc > 0 else 'DEFECT'}")
    
    # Test 2: Caz critic (știft maxim, gaură minimă, poziții decalate)
    print("\n=== TEST 2: Caz critic ===")
    X_critic = np.array([10.5, 9.7, 50.0, 40.0, 50.5, 40.5])
    joc, j1, j2 = functia_de_joc(X_critic)
    print(f"  Joc 1 = {j1:.4f} mm")
    print(f"  Joc 2 = {j2:.4f} mm")
    print(f"  Joc global = {joc:.4f} mm")
    print(f"  Asamblare: {'OK' if joc > 0 else 'DEFECT'}")
    
    # Test 3: Subgradientul la valorile nominale
    print("\n=== TEST 3: Subgradientul ===")
    grad = calculeaza_subgradient(valori_nominale)
    print(f"  Subgradient: {grad}")
    print(f"  Direcția de scădere maximă: {-grad}")
    