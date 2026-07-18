import streamlit as st

st.title("📐 Matematica din spatele sistemului")

tab1, tab2, tab3, tab4 = st.tabs(["Funcția de joc", "Gradientul", "Minimul garantat", "Neuronul fracționar"])

with tab1:
    st.markdown("""
    ### Cum știm dacă piesele se potrivesc?
    
    Pentru o pereche știft-gaură, **jocul** este:
    
    $$J = R_g - R_s - d$$
    
    - $R_g$ = raza găurii, $R_s$ = raza știftului, $d$ = distanța dintre centre
    
    **Exemplu:** Știft 10 mm, gaură 10.2 mm, centre aliniate → Joc = 5.1 - 5 - 0 = **0.1 mm** ✅
    
    Pentru 2 știfturi și 2 găuri, funcția globală:
    
    $$f(X) = \\frac{x_2 - x_1}{2} - \\sqrt{(x_3 - x_5)^2 + (x_4 - x_6)^2}$$
    
    Dacă $f(X) > 0$ → OK. Dacă $f(X) \\leq 0$ → DEFECT.
    """)

with tab2:
    st.markdown("""
    ### Cum știm ce cotă să ajustăm?
    
    Gradientul funcției de joc (formula exactă):
    
    $$\\nabla f = \\begin{bmatrix} -\\frac{1}{2} & +\\frac{1}{2} & -\\frac{x_3-x_5}{d} & -\\frac{x_4-x_6}{d} & +\\frac{x_3-x_5}{d} & +\\frac{x_4-x_6}{d} \\end{bmatrix}$$
    
    - $-1/2$: mărirea știftului **reduce** jocul
    - $+1/2$: mărirea găurii **crește** jocul
    """)

with tab3:
    st.markdown("""
    ### De ce 64 de colțuri sunt suficiente?
    
    **Teorema:** Minimul funcției de joc se atinge întotdeauna la un colț al domeniului de toleranță.
    
    **De ce:** Diametrele apar liniar (minimul la extreme). Distanța $d$ e maximă când pozițiile sunt la extreme opuse.
    
    **Consecința:** Verificăm toate $2^6 = 64$ colțuri → garanție absolută, sub 1 ms.
    
    | Metoda | Verificări | Garanție |
    |---|---|---|
    | Worst-Case | 1 | Absolută (dar prea pesimistă) |
    | Monte Carlo | 10,000+ | Statistică |
    | **Metoda noastră** | **64** | **Absolută** |
    """)

with tab4:
    st.markdown("""
    ### Memoria lungă a neuronului fracționar
    
    Semnal: $+1$ = DEFECT, $-1$ = OK.
    
    Procesare (derivata Grünwald-Letnikov):
    
    $$u(t) = \\sum_{j=0}^{19} (-1)^j \\binom{\\alpha}{j} \\cdot y(t-j)$$
    
    Output (funcția sigmoidă):
    
    $$\\beta(t) = \\frac{1}{1 + e^{-u(t)}}$$
    
    - $\\beta \\to 1$ → ajustări agresive
    - $\\beta \\to 0$ → ajustări fine
    
    $\\alpha = 0.7$ oferă echilibrul optim între memorie și adaptabilitate.
    """)
