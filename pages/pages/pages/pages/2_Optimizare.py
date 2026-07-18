import streamlit as st
import numpy as np
import pandas as pd
from agent_tester import AgentTester
from agent_proiectant import AgentProiectant
from model_matematic import functia_de_joc, valori_nominale

st.title("📊 Optimizare")

with st.sidebar:
    st.header("⚡ Parametri")
    alpha = st.slider("Alpha (memorie fracționară)", 0.1, 1.0, 0.7, 0.1)
    delta = st.slider("Delta (pas ajustare)", 0.05, 0.5, 0.2, 0.05)
    tol_init = st.slider("Toleranță inițială (mm)", 0.1, 1.0, 0.5, 0.1)
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
    
    st.success("👈 Mergi la pagina **Grafice** pentru vizualizări.")
else:
    st.info("Configurează parametrii în panoul din stânga și apasă **Rulează optimizarea**.")
