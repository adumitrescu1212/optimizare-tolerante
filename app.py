import streamlit as st
import numpy as np
import pandas as pd

from agent_tester import AgentTester
from agent_proiectant import AgentProiectant
from model_matematic import functia_de_joc, valori_nominale

# ---------- Configurare pagină ----------
st.set_page_config(page_title="Tolerance Optimization", page_icon="⚙️", layout="wide")

# ---------- Dicționare pentru traduceri ----------
LANG = {
    'ro': {
        'title': "⚙️ Sistem Multi-Agent cu Neuron Fracționar",
        'subtitle': "Optimizarea toleranțelor pentru ansambluri mecanice",
        'guide_header': "📖 Ghid de utilizare",
        'guide_expander': "📘 Cum funcționează?",
        'guide_text': """
        **Ce face acest program?**
        
        Găsește automat cele mai bune toleranțe pentru un ansamblu mecanic 
        (o bază cu știfturi + un capac cu găuri).
        
        **Cei doi agenți:**
        - 🟢 **Proiectantul** vrea toleranțe cât mai largi (cost mic)
        - 🔴 **Testerul** caută combinația de dimensiuni care strică ansamblul
        
        **Neuronul fracționar (Beta):**
        - Memoria lungă ajută sistemul să fie agresiv când găsește defecte 
          și precaut când totul e în regulă
        - Beta ~ 0.85 = agresiv | Beta ~ 0.15 = precaut
        
        **Ce vezi după rulare:**
        - Tabel cu toleranțele optime găsite
        - Istoricul complet al iterațiilor
        - Grafice cu evoluția costului și Beta
        """,
        'params_header': "⚡ Parametri",
        'alpha_label': "Alpha",
        'alpha_help': "0.1 = memorie foarte lungă | 1.0 = memorie scurtă (neuron clasic)",
        'delta_label': "Delta (pas ajustare)",
        'delta_help': "Valori mici = ajustări fine | Valori mari = ajustări rapide",
        'tol_label': "Toleranță inițială (mm)",
        'tol_help': "Valori mari = cost inițial mic, dar multe defecte de corectat",
        'run_button': "▶️ Rulează optimizarea",
        'status_defect': "🔴 DEFECT la cota",
        'status_ok': "🟢 OK",
        'status_convergence': "✅ CONVERGENȚĂ atinsă în",
        'results_header': "📊 Rezultate finale",
        'iterations': "Iterații totale",
        'cost_opt': "Cost optim",
        'cost_init': "Cost inițial",
        'tol_header': "Toleranțe optime",
        'col_cota': "Cotă",
        'col_val': "Val. nominală (mm)",
        'col_tol': "Toleranță optimă (±mm)",
        'col_interval': "Interval admis",
        'cote': ['Diametru știft', 'Diametru gaură', 'DistX bază', 'DistY bază', 'DistX capac', 'DistY capac'],
        'history_header': "📋 Istoricul complet al iterațiilor",
        'charts_header': "📈 Grafice",
        'tab_cost': "Evoluția costului",
        'tab_beta': "Dinamica Beta",
        'caption_cost': "Costul crește pe măsură ce toleranțele sunt strânse pentru a elimina defectele.",
        'caption_beta': "Beta scade când sistemul se stabilizează (faza OK), permițând ajustări fine.",
        'col_iter': "Iterație",
        'col_result': "Rezultat",
        'col_beta': "Beta",
        'col_cost': "Cost",
        'col_joc': "Joc (mm)",
        'col_cota_vin': "Cotă vinovată",
        'about_title': "📖 Despre acest proiect",
        'about_text': """
        Acest sistem folosește o arhitectură **multi-agent** cu doi roboței software care 
        interacționează pentru a găsi cele mai bune toleranțe pentru un ansamblu mecanic:
        
        - **Agentul Proiectant** încearcă să lărgească toleranțele (reducând costul de fabricație)
        - **Agentul Tester** verifică fiecare propunere, căutând combinația de dimensiuni care 
          ar putea cauza defecte de asamblare
        
        Un **neuron fracționar** cu memorie lungă (bazat pe derivata Grünwald-Letnikov) 
        controlează adaptiv cât de agresiv se fac ajustările.
        
        ### 🎯 Rezultatul
        
        La final, obții **toleranțele optime** — cel mai ieftin set de toleranțe care 
        garantează că piesele se vor asambla corect, indiferent de variațiile de fabricație.
        """,
        'wait_text': "👈 Configurează parametrii în panoul din stânga și apasă **Rulează optimizarea** pentru a începe.",
        'joc_label': "Joc ="
    },
    'en': {
        'title': "⚙️ Multi-Agent System with Fractional Neuron",
        'subtitle': "Tolerance optimization for mechanical assemblies",
        'guide_header': "📖 User Guide",
        'guide_expander': "📘 How does it work?",
        'guide_text': """
        **What does this program do?**
        
        Automatically finds the best tolerances for a mechanical assembly 
        (a base with pins + a cover with holes).
        
        **The two agents:**
        - 🟢 **The Designer** wants tolerances as wide as possible (low cost)
        - 🔴 **The Tester** searches for the dimension combination that breaks the assembly
        
        **The fractional neuron (Beta):**
        - Long memory helps the system be aggressive when finding defects 
          and cautious when everything is fine
        - Beta ~ 0.85 = aggressive | Beta ~ 0.15 = cautious
        
        **What you see after running:**
        - Table with the optimal tolerances found
        - Complete iteration history
        - Charts with cost and Beta evolution
        """,
        'params_header': "⚡ Parameters",
        'alpha_label': "Alpha",
        'alpha_help': "0.1 = very long memory | 1.0 = short memory (classical neuron)",
        'delta_label': "Delta (adjustment step)",
        'delta_help': "Small values = fine adjustments | Large values = fast adjustments",
        'tol_label': "Initial tolerance (mm)",
        'tol_help': "Large values = low initial cost, but many defects to fix",
        'run_button': "▶️ Run Optimization",
        'status_defect': "🔴 DEFECT at dimension",
        'status_ok': "🟢 OK",
        'status_convergence': "✅ CONVERGENCE reached in",
        'results_header': "📊 Final Results",
        'iterations': "Total Iterations",
        'cost_opt': "Optimal Cost",
        'cost_init': "Initial Cost",
        'tol_header': "Optimal Tolerances",
        'col_cota': "Dimension",
        'col_val': "Nominal Value (mm)",
        'col_tol': "Optimal Tolerance (±mm)",
        'col_interval': "Allowed Range",
        'cote': ['Pin Diameter', 'Hole Diameter', 'DistX base', 'DistY base', 'DistX cover', 'DistY cover'],
        'history_header': "📋 Complete Iteration History",
        'charts_header': "📈 Charts",
        'tab_cost': "Cost Evolution",
        'tab_beta': "Beta Dynamics",
        'caption_cost': "Cost increases as tolerances are tightened to eliminate defects.",
        'caption_beta': "Beta drops when the system stabilizes (OK phase), allowing fine adjustments.",
        'col_iter': "Iteration",
        'col_result': "Result",
        'col_beta': "Beta",
        'col_cost': "Cost",
        'col_joc': "Gap (mm)",
        'col_cota_vin': "Faulty Dim.",
        'about_title': "📖 About This Project",
        'about_text': """
        This system uses a **multi-agent** architecture with two software robots that 
        interact to find the best tolerances for a mechanical assembly:
        
        - **The Designer Agent** tries to widen tolerances (reducing manufacturing cost)
        - **The Tester Agent** checks each proposal, searching for dimension combinations 
          that could cause assembly defects
        
        A **fractional neuron** with long memory (based on the Grünwald-Letnikov derivative) 
        adaptively controls how aggressive the adjustments are.
        
        ### 🎯 The Result
        
        At the end, you get the **optimal tolerances** — the cheapest tolerance set that 
        guarantees the parts will assemble correctly, regardless of manufacturing variations.
        """,
        'wait_text': "👈 Configure the parameters in the sidebar and press **Run Optimization** to start.",
        'joc_label': "Gap ="
    }
}

# ---------- Selector limbă ----------
if 'lang' not in st.session_state:
    st.session_state.lang = 'ro'

with st.sidebar:
    col_lang1, col_lang2 = st.columns(2)
    if col_lang1.button("🇷🇴 RO", use_container_width=True):
        st.session_state.lang = 'ro'
    if col_lang2.button("🇬🇧 EN", use_container_width=True):
        st.session_state.lang = 'en'

t = LANG[st.session_state.lang]

# ---------- Titlu ----------
st.title(t['title'])
st.subheader(t['subtitle'])

# ---------- Panou lateral ----------
with st.sidebar:
    st.header(t['guide_header'])
    with st.expander(t['guide_expander'], expanded=False):
        st.markdown(t['guide_text'])
    
    st.divider()
    st.header(t['params_header'])
    
    st.markdown(f"**{t['alpha_label']}**")
    alpha = st.slider(t['alpha_label'], 0.1, 1.0, 0.7, 0.1, help=t['alpha_help'])
    
    st.markdown(f"**{t['delta_label']}**")
    delta = st.slider(t['delta_label'], 0.05, 0.5, 0.2, 0.05, help=t['delta_help'])
    
    st.markdown(f"**{t['tol_label']}**")
    tol_init = st.slider(t['tol_label'], 0.1, 1.0, 0.5, 0.1, help=t['tol_help'])
    
    st.divider()
    run = st.button(t['run_button'], type="primary", use_container_width=True)

# ---------- Zona principală ----------
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
            t['col_iter']: iteratii,
            t['col_result']: rezultat,
            t['col_beta']: round(beta, 3),
            t['col_cost']: round(cost, 2),
            t['col_joc']: round(joc, 4),
            t['col_cota_vin']: cota + 1 if cota is not None else '-'
        })
        
        m_iter.metric(t['iterations'], f"{iteratii}")
        m_cost.metric(t['cost_opt'], f"{cost:.2f}")
        m_beta.metric("Beta", f"{beta:.3f}")
        
        if rezultat == "DEFECT":
            fara_defect = 0
            proiectant.primeste_raport(True, cota, beta)
            status.warning(f"{t['status_defect']} {cota+1} | {t['joc_label']} {joc:.4f} mm")
        else:
            fara_defect += 1
            status.success(f"{t['status_ok']} | {t['joc_label']} {joc:.4f} mm")
            if fara_defect >= 2:
                status.info(f"{t['status_convergence']} {iteratii}!")
                break
            cota_mod = proiectant.primeste_raport(False, None, beta)
            if cota_mod is not False:
                tol_noi = proiectant.propune_tolerante()
                rez2, _, _ = tester.ataca(tol_noi)
                if rez2 == "DEFECT":
                    proiectant.confirma_esec(cota_mod)
                    fara_defect = 0
        
        progress_bar.progress(min(iteratii / 300, 1.0))
    
    st.divider()
    st.header(t['results_header'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric(t['iterations'], f"{iteratii}")
    col2.metric(t['cost_opt'], f"{proiectant.calculeaza_cost():.2f}")
    col3.metric(t['cost_init'], f"{np.sum(1.0/(tolerante_init + 1e-9)):.2f}")
    
    st.subheader(t['tol_header'])
    df_tol = pd.DataFrame({
        t['col_cota']: t['cote'],
        t['col_val']: valori_nominale,
        t['col_tol']: np.round(proiectant.propune_tolerante(), 4),
        t['col_interval']: [
            f"[{valori_nominale[i] - proiectant.propune_tolerante()[i]:.2f}, {valori_nominale[i] + proiectant.propune_tolerante()[i]:.2f}]"
            for i in range(6)
        ]
    })
    st.dataframe(df_tol, use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader(t['history_header'])
    df_istoric = pd.DataFrame(istoric)
    st.dataframe(df_istoric, use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader(t['charts_header'])
    
    tab1, tab2 = st.tabs([t['tab_cost'], t['tab_beta']])
    
    with tab1:
        st.line_chart(df_istoric, x=t['col_iter'], y=t['col_cost'], height=300)
        st.caption(t['caption_cost'])
    
    with tab2:
        st.line_chart(df_istoric, x=t['col_iter'], y=t['col_beta'], height=300)
        st.caption(t['caption_beta'])

else:
    st.info(t['wait_text'])
    st.markdown(t['about_text'])
