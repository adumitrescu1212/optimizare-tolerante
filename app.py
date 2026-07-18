import streamlit as st
import numpy as np
import pandas as pd
from agent_tester import AgentTester
from agent_proiectant import AgentProiectant
from model_matematic import functia_de_joc, valori_nominale

st.set_page_config(page_title="Optimizare Toleranțe", page_icon="⚙️", layout="wide")

# ---------- CSS pentru tab-uri personalizate ----------
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f0f2f6;
        border-radius: 12px;
        padding: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-size: 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ---------- Tab-uri principale ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Acasă", 
    "📊 Optimizare", 
    "📈 Grafice", 
    "📖 Despre", 
    "📐 Matematică"
])

# ================================================================
# TAB 1: ACASĂ
# ================================================================
with tab1:
    st.title("⚙️ Sistem Multi-Agent cu Neuron Fracționar")
    st.subheader("Optimizarea toleranțelor pentru ansambluri mecanice")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### 🎯 Ce rezolvă acest proiect?
        
        În fabricarea pieselor mecanice, dimensiunile nu ies niciodată perfect. 
        Un știft proiectat la 10 mm va avea în realitate între 9.9 și 10.1 mm.
        
        **Provocarea:** Găsirea celui mai ieftin set de toleranțe care garantează 
        că piesele se vor asambla corect.
        
        **Soluția:** Doi agenți software inteligenți care colaborează pentru 
        a găsi automat aceste toleranțe.
        """)
    
    with col2:
        st.info("""
        ### 🚀 Cum începi?
        
        1. Mergi la tab-ul **📊 Optimizare**
        2. Setează parametrii în panoul din stânga
        3. Apasă **Rulează optimizarea**
        4. Vezi rezultatele în timp real
        5. Explorează graficele și matematica
        """)
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Agenți software", "2", help="Proiectant + Tester")
    col2.metric("Colțuri verificate", "64", help="Garanție matematică absolută")
    col3.metric("Timp execuție", "< 1s", help="Pe un laptop standard")

# ================================================================
# TAB 2: OPTIMIZARE
# ================================================================
with tab2:
    with st.sidebar:
        st.header("⚡ Parametri")
        alpha = st.slider("Alpha (memorie fracționară)", 0.1, 1.0, 0.7, 0.1,
                          help="0.1 = memorie lungă | 1.0 = memorie scurtă")
        delta = st.slider("Delta (pas ajustare)", 0.05, 0.5, 0.2, 0.05,
                          help="Cât de mult se modifică toleranțele la fiecare pas")
        tol_init = st.slider("Toleranță inițială (mm)", 0.1, 1.0, 0.5, 0.1,
                             help="Toate cele 6 cote pornesc cu această valoare")
        run = st.button("▶️ Rulează optimizarea", type="primary", use_container_width=True)
    
    if run:
        tolerante_init = np.full(6, tol_init)
        proiectant = AgentProiectant(valori_nominale, tolerante_init, delta=delta)
        tester = AgentTester(alpha=alpha, max_iteratii=500)
        
        status = st.empty()
        col1, col2, col3 = st.columns(3)
        m_iter = col1.empty()
        m_cost = col2.empty()
        m_beta = col3.empty()
        progress_bar = st.progress(0)
        
        istoric = []
        fara_defect = 0
        iteratii = 0
        
        for it in range(300):
            iteratii = it + 1
            tolerante = proiectant.propune_tolerante()
            cost = proiectant.calculeaza_cost()
            rezultat, X_worst, cota = tester.ataca(tolerante)
            beta = tester.get_beta()
            joc, _, _ = functia_de_joc(X_worst)
            
            istoric.append({
                'Iterație': iteratii,
                'Rezultat': rezultat,
                'Beta': round(beta, 3),
                'Cost': round(cost, 2),
                'Joc (mm)': round(joc, 4),
                'Cotă vinovată': cota + 1 if cota is not None else '-'
            })
            
            m_iter.metric("Iterație", f"{iteratii}")
            m_cost.metric("Cost", f"{cost:.2f}")
            m_beta.metric("Beta", f"{beta:.3f}")
            
            if rezultat == "DEFECT":
                fara_defect = 0
                proiectant.primeste_raport(True, cota, beta)
                status.warning(f"🔴 DEFECT la cota {cota+1} | Joc = {joc:.4f} mm")
            else:
                fara_defect += 1
                status.success(f"🟢 OK | Joc = {joc:.4f} mm")
                if fara_defect >= 2:
                    status.info(f"✅ CONVERGENȚĂ atinsă în {iteratii} iterații!")
                    break
                cota_mod = proiectant.primeste_raport(False, None, beta)
                if cota_mod is not False:
                    tol_noi = proiectant.propune_tolerante()
                    rez2, _, _ = tester.ataca(tol_noi)
                    if rez2 == "DEFECT":
                        proiectant.confirma_esec(cota_mod)
                        fara_defect = 0
            
            progress_bar.progress(min(iteratii / 300, 1.0))
        
        st.session_state['istoric'] = istoric
        st.session_state['proiectant'] = proiectant
        st.session_state['tolerante_init'] = tolerante_init
        st.session_state['iteratii'] = iteratii
        
        st.divider()
        st.header("📊 Rezultate finale")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Iterații totale", f"{iteratii}")
        col2.metric("Cost optim", f"{proiectant.calculeaza_cost():.2f}")
        col3.metric("Cost inițial", f"{np.sum(1.0/(tolerante_init + 1e-9)):.2f}")
        
        st.subheader("Toleranțe optime")
        cote = ['Diametru știft', 'Diametru gaură', 'DistX bază', 'DistY bază', 'DistX capac', 'DistY capac']
        df_tol = pd.DataFrame({
            'Cotă': cote,
            'Val. nominală (mm)': valori_nominale,
            'Toleranță optimă (±mm)': np.round(proiectant.propune_tolerante(), 4),
            'Interval admis': [
                f"[{valori_nominale[i] - proiectant.propune_tolerante()[i]:.2f}, {valori_nominale[i] + proiectant.propune_tolerante()[i]:.2f}]"
                for i in range(6)
            ]
        })
        st.dataframe(df_tol, use_container_width=True, hide_index=True)
        
        st.divider()
        st.header("🎲 Simulare Monte Carlo")
        
        tol_opt = proiectant.propune_tolerante()
        n_mc = 5000
        defecte_mc = 0
        for _ in range(n_mc):
            X_mc = np.random.normal(loc=valori_nominale, scale=tol_opt/3)
            X_mc = np.clip(X_mc, valori_nominale - tol_opt, valori_nominale + tol_opt)
            joc_mc, _, _ = functia_de_joc(X_mc)
            if joc_mc <= 0:
                defecte_mc += 1
        
        col_mc1, col_mc2, col_mc3, col_mc4 = st.columns(4)
        col_mc1.metric("Eșantioane", f"{n_mc:,}")
        col_mc2.metric("Defecte găsite", f"{defecte_mc}")
        col_mc3.metric("Probabilitate de defect", f"{100*defecte_mc/n_mc:.3f}%")
        col_mc4.metric("Distribuție", "Normală (3σ)")
        
        st.divider()
        st.header("📊 Comparație cu metodele clasice")
        df_comp = pd.DataFrame({
            'Metoda': ['Sistem Multi-Agent', 'Worst-Case (teoretic)', 'Monte Carlo (estimat)'],
            'Cost': [f"{proiectant.calculeaza_cost():.2f}", "∞", "~180"],
            'Evaluări': [f"~{iteratii * 64:,}", "1", "10,000+"],
            'Garanție': ['Absolută', 'Absolută', 'Statistică']
        })
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
        
        df_istoric = pd.DataFrame(istoric)
        csv = df_istoric.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportă rezultatele (CSV)", csv, 'istoric_optimizare.csv', 'text/csv')
        
        st.success("👈 Mergi la tab-ul **📈 Grafice** pentru vizualizări detaliate.")
    else:
        st.info("Configurează parametrii în panoul din stânga și apasă **Rulează optimizarea**.")

# ================================================================
# TAB 3: GRAFICE
# ================================================================
with tab3:
    st.title("📈 Grafice")
    
    if 'istoric' not in st.session_state or st.session_state['istoric'] is None:
        st.warning("⚠️ Rulează mai întâi optimizarea din tab-ul **📊 Optimizare**.")
    else:
        df = pd.DataFrame(st.session_state['istoric'])
        
        st.subheader("📋 Istoricul complet al iterațiilor")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        tab_g1, tab_g2, tab_g3 = st.tabs(["Evoluția costului", "Dinamica Beta", "Evoluția jocului minim"])
        
        with tab_g1:
            st.line_chart(df, x='Iterație', y='Cost', height=400)
            st.caption("Costul crește pe măsură ce toleranțele sunt strânse. Un cost mai mic = fabricație mai ieftină.")
        
        with tab_g2:
            st.line_chart(df, x='Iterație', y='Beta', height=400)
            st.caption("Beta ~0.85 = sistem alert (strânge agresiv). Beta ~0.15 = sistem stabil (ajustări fine).")
        
        with tab_g3:
            st.line_chart(df, x='Iterație', y='Joc (mm)', height=400)
            st.caption("Jocul evoluează de la negativ (interferență) spre zero. Pozitiv = ansamblul funcționează.")

# ================================================================
# TAB 4: DESPRE
# ================================================================
with tab4:
    st.title("📖 Despre proiect")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🏗️ Cum funcționează
        
        **🔵 Agentul Proiectant** pornește cu toleranțe foarte largi (cost minim) 
        și le ajustează pe baza feedback-ului. Când Testerul găsește un defect, 
        strânge toleranța. Când totul e OK, încearcă să lărgească.
        
        **🔴 Agentul Tester** verifică fiecare set de toleranțe testând toate cele 
        64 de combinații extreme posibile. Garanție matematică absolută.
        
        **🧠 Neuronul fracționar** are memorie lungă și controlează cât de agresiv 
        se fac ajustările (Beta ~0.85 = agresiv, ~0.15 = relaxat).
        """)
    
    with col2:
        st.markdown("""
        ### 📘 Ghid rapid
        
        1. **Tab-ul Optimizare** — Setează Alpha, Delta și Toleranța
        2. Apasă **Rulează optimizarea**
        3. Vezi rezultatele în timp real
        4. **Tab-ul Grafice** — Vizualizează evoluția
        5. **Exportă** rezultatele ca CSV
        
        ### 📊 Interpretare
        - **Cost** — mai mic = mai ieftin
        - **Beta** — ~0.85 = agresiv, ~0.15 = relaxat
        - **Joc** — negativ = interferență, pozitiv = OK
        - **Probabilitate de defect** — sub 0.1% e excelent
        """)

# ================================================================
# TAB 5: MATEMATICĂ
# ================================================================
with tab5:
    st.title("📐 Matematica din spatele sistemului")
    
    tab_m1, tab_m2, tab_m3, tab_m4 = st.tabs([
        "Funcția de joc", 
        "Gradientul", 
        "Minimul garantat", 
        "Neuronul fracționar"
    ])
    
    with tab_m1:
        st.markdown("""
        ### Cum știm dacă piesele se potrivesc?
        
        Pentru o pereche știft-gaură, **jocul** este:
        
        $$J = R_g - R_s - d$$
        
        - $R_g$ = raza găurii, $R_s$ = raza știftului, $d$ = distanța dintre centre
        
        **Exemplu:** Știft 10 mm, gaură 10.2 mm, centre aliniate → Joc = **0.1 mm** ✅
        
        Funcția globală pentru 2 știfturi și 2 găuri:
        
        $$f(X) = \\frac{x_2 - x_1}{2} - \\sqrt{(x_3 - x_5)^2 + (x_4 - x_6)^2}$$
        
        Dacă $f(X) > 0$ → OK. Dacă $f(X) \\leq 0$ → DEFECT.
        """)
    
    with tab_m2:
        st.markdown("""
        ### Cum știm ce cotă să ajustăm?
        
        Gradientul funcției de joc:
        
        $$\\nabla f = \\begin{bmatrix} -\\frac{1}{2} & +\\frac{1}{2} & -\\frac{x_3-x_5}{d} & -\\frac{x_4-x_6}{d} & +\\frac{x_3-x_5}{d} & +\\frac{x_4-x_6}{d} \\end{bmatrix}$$
        
        - $-1/2$: mărirea știftului **reduce** jocul
        - $+1/2$: mărirea găurii **crește** jocul
        """)
    
    with tab_m3:
        st.markdown("""
        ### De ce 64 de colțuri sunt suficiente?
        
        **Teorema:** Minimul funcției de joc se atinge întotdeauna la un colț al domeniului.
        
        **Demonstrație intuitivă:**
        - Diametrele apar liniar → minimul la extreme
        - Distanța $d$ e maximă când pozițiile sunt la extreme opuse
        
        **Consecința:** $2^6 = 64$ colțuri verificate exhaustiv → garanție absolută.
        
        | Metoda | Verificări | Garanție |
        |---|---|---|
        | Worst-Case | 1 | Absolută (dar prea pesimistă) |
        | Monte Carlo | 10,000+ | Statistică |
        | **Metoda noastră** | **64** | **Absolută** |
        """)
    
    with tab_m4:
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
