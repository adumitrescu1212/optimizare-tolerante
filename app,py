import streamlit as st
import numpy as np
import pandas as pd

from agent_tester import AgentTester
from agent_proiectant import AgentProiectant
from model_matematic import functia_de_joc, valori_nominale

st.set_page_config(page_title="Optimizare Toleranțe", page_icon="⚙️", layout="wide")
st.title("⚙️ Sistem Multi-Agent cu Neuron Fracționar")
st.subheader("Optimizarea toleranțelor pentru ansambluri mecanice")

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
    
    fara_defect = 0
    iteratii = 0
    
    for it in range(300):
        iteratii = it + 1
        tolerante = proiectant.propune_tolerante()
        cost = proiectant.calculeaza_cost()
        rezultat, X_worst, cota = tester.ataca(tolerante)
        beta = tester.get_beta()
        joc, _, _ = functia_de_joc(X_worst)
        
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
                status.info("✅ CONVERGENȚĂ atinsă!")
                break
            cota_mod = proiectant.primeste_raport(False, None, beta)
            if cota_mod is not False:
                tol_noi = proiectant.propune_tolerante()
                rez2, _, _ = tester.ataca(tol_noi)
                if rez2 == "DEFECT":
                    proiectant.confirma_esec(cota_mod)
                    fara_defect = 0
    
    st.divider()
    st.header("📊 Rezultate finale")
    c1, c2, c3 = st.columns(3)
    c1.metric("Iterații totale", f"{iteratii}")
    c2.metric("Cost optim", f"{proiectant.calculeaza_cost():.2f}")
    c3.metric("Cost inițial", f"{np.sum(1.0/(tolerante_init + 1e-9)):.2f}")
    
    st.subheader("Toleranțe optime")
    df = pd.DataFrame({
        'Cotă': ['Diametru știft', 'Diametru gaură', 'DistX bază', 'DistY bază', 'DistX capac', 'DistY capac'],
        'Valoare nominală': valori_nominale,
        'Toleranță optimă (±mm)': np.round(proiectant.propune_tolerante(), 4)
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.info("👈 Configurează parametrii și apasă **Rulează optimizarea**.")
