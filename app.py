import streamlit as st
import numpy as np
import pandas as pd
from agent_tester import AgentTester
from agent_proiectant import AgentProiectant
from model_matematic import functia_de_joc, valori_nominale

st.set_page_config(page_title="Tolerance Optimization", page_icon="⚙️", layout="wide")

LANG = {
    'ro': {
        'title': "⚙️ Sistem Multi-Agent cu Neuron Fracționar",
        'subtitle': "Optimizarea toleranțelor pentru ansambluri mecanice",
        'guide_header': "📖 Ghid de utilizare",
        'guide_expander': "📘 Cum funcționează?",
        'guide_text': "**Ce face acest program?**\n\nGăsește automat cele mai bune toleranțe pentru un ansamblu mecanic (o bază cu știfturi + un capac cu găuri).\n\n**Cei doi agenți:**\n- Proiectantul vrea toleranțe cât mai largi (cost mic)\n- Testerul caută combinația de dimensiuni care strică ansamblul\n\n**Neuronul fracționar (Beta):**\n- Memoria lungă ajută sistemul să fie agresiv când găsește defecte și precaut când totul e în regulă\n- Beta ~ 0.85 = agresiv | Beta ~ 0.15 = precaut",
        'params_header': "⚡ Parametri",
        'alpha_label': "Alpha (memorie fracționară)",
        'alpha_help': "0.1 = memorie lungă | 1.0 = memorie scurtă (neuron clasic)",
        'delta_label': "Delta (pas ajustare)",
        'delta_help': "Cât de mult se modifică toleranțele la fiecare pas.",
        'tol_label': "Toleranță inițială (mm)",
        'tol_help': "Toate cele 6 cote pornesc cu această toleranță.",
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
        'tab_joc': "Evoluția jocului minim",
        'caption_cost': "Costul crește pe măsură ce toleranțele sunt strânse. Un cost mai mic = fabricație mai ieftină.",
        'caption_beta': "Beta ~0.85 = sistem alert (strânge agresiv). Beta ~0.15 = sistem stabil (ajustări fine).",
        'caption_joc': "Jocul evoluează de la negativ (interferență) spre zero. Pozitiv = ansamblul funcționează.",
        'col_iter': "Iterație",
        'col_result': "Rezultat",
        'col_beta': "Beta",
        'col_cost': "Cost",
        'col_joc': "Joc (mm)",
        'col_cota_vin': "Cotă vinovată",
        'about_title': "📖 Despre acest proiect",
        'about_text': "Acest sistem folosește o arhitectură multi-agent cu doi agenți software care interacționează pentru a găsi cele mai bune toleranțe. Un neuron fracționar cu memorie lungă controlează adaptiv cât de agresiv se fac ajustările.",
        'wait_text': "👈 Configurează parametrii și apasă Rulează optimizarea.",
        'joc_label': "Joc =",
        'export_csv': "📥 Exportă rezultatele (CSV)",
        'export_tooltip': "Descarcă un fișier CSV cu istoricul complet.",
        'comparison_header': "📊 Comparație cu metodele clasice",
        'comparison_text': "Comparație între sistemul multi-agent și metodele tradiționale.",
        'col_method': "Metoda",
        'col_eval': "Evaluări",
        'col_guarantee': "Garanție",
        'method_mas': "Sistem Multi-Agent",
        'method_wc': "Worst-Case (teoretic)",
        'method_mc': "Monte Carlo (estimat)",
        'guarantee_abs': "Absolută",
        'guarantee_stat': "Statistică",
        'mc_header': "🎲 Simulare Monte Carlo",
        'mc_text': "Estimarea probabilității de defect cu toleranțele optime:",
        'mc_samples': "Eșantioane",
        'mc_defects': "Defecte găsite",
        'mc_prob': "Probabilitate de defect",
        'mc_dist': "Distribuție",
        'how_header': "🏗️ Cum funcționează sistemul",
        'how_text': """
        Sistemul este format din două componente software care colaborează pentru a găsi toleranțele optime:
        
        **🔵 Agentul Proiectant** pornește cu toleranțe foarte largi (cost minim) și le ajustează pe baza feedback-ului primit. Când Testerul găsește un defect, Proiectantul strânge toleranța la cota respectivă. Când totul e în regulă, încearcă să lărgească toleranțele pentru a reduce costul.
        
        **🔴 Agentul Tester** verifică fiecare set de toleranțe propus. Folosește o metodă matematică exactă: testează toate cele 64 de combinații extreme posibile (fiecare cotă la minim sau maxim). Dacă găsește o combinație care produce interferență, raportează DEFECT și indică exact care cotă e vinovată.
        
        **🧠 Neuronul fracționar** acționează ca un manager de risc. Are memorie lungă — își amintește ce s-a întâmplat în iterațiile trecute. Când Testerul găsește multe defecte consecutiv, neuronul devine "stresat" (Beta ~0.85) și Proiectantul strânge toleranțele agresiv. Când sistemul se stabilizează, neuronul se relaxează (Beta ~0.15) și ajustările devin fine și precise.
        
        **📐 Modelul matematic** calculează jocul dintre știfturi și găuri pe baza geometriei reale a ansamblului proiectat în SolidWorks.
        """
    },
    'en': {
        'title': "⚙️ Multi-Agent System with Fractional Neuron",
        'subtitle': "Tolerance optimization for mechanical assemblies",
        'guide_header': "📖 User Guide",
        'guide_expander': "📘 How does it work?",
        'guide_text': "**What does this program do?**\n\nAutomatically finds the best tolerances for a mechanical assembly (a base with pins + a cover with holes).\n\n**The two agents:**\n- The Designer wants tolerances as wide as possible (low cost)\n- The Tester searches for the dimension combination that breaks the assembly\n\n**The fractional neuron (Beta):**\n- Long memory helps the system be aggressive when finding defects and cautious when everything is fine\n- Beta ~ 0.85 = aggressive | Beta ~ 0.15 = cautious",
        'params_header': "⚡ Parameters",
        'alpha_label': "Alpha (fractional memory)",
        'alpha_help': "0.1 = long memory | 1.0 = short memory (classical neuron)",
        'delta_label': "Delta (adjustment step)",
        'delta_help': "How much tolerances change at each step.",
        'tol_label': "Initial tolerance (mm)",
        'tol_help': "All 6 dimensions start with this tolerance.",
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
        'tab_joc': "Gap Evolution",
        'caption_cost': "Cost increases as tolerances are tightened. Lower cost = cheaper manufacturing.",
        'caption_beta': "Beta ~0.85 = system alert (tightens aggressively). Beta ~0.15 = system stable (fine adjustments).",
        'caption_joc': "Gap evolves from negative (interference) towards zero. Positive = assembly works.",
        'col_iter': "Iteration",
        'col_result': "Result",
        'col_beta': "Beta",
        'col_cost': "Cost",
        'col_joc': "Gap (mm)",
        'col_cota_vin': "Faulty Dim.",
        'about_title': "📖 About This Project",
        'about_text': "This system uses a multi-agent architecture with two software agents that interact to find the best tolerances. A fractional neuron with long memory adaptively controls how aggressive the adjustments are.",
        'wait_text': "👈 Configure the parameters and press Run Optimization.",
        'joc_label': "Gap =",
        'export_csv': "📥 Export Results (CSV)",
        'export_tooltip': "Download a CSV file with the complete history.",
        'comparison_header': "📊 Comparison with Classical Methods",
        'comparison_text': "Comparison between the multi-agent system and traditional methods.",
        'col_method': "Method",
        'col_eval': "Evaluations",
        'col_guarantee': "Guarantee",
        'method_mas': "Multi-Agent System",
        'method_wc': "Worst-Case (theoretical)",
        'method_mc': "Monte Carlo (estimated)",
        'guarantee_abs': "Absolute",
        'guarantee_stat': "Statistical",
        'mc_header': "🎲 Monte Carlo Simulation",
        'mc_text': "Estimating defect probability with optimal tolerances:",
        'mc_samples': "Samples",
        'mc_defects': "Defects Found",
        'mc_prob': "Defect Probability",
        'mc_dist': "Distribution",
        'how_header': "🏗️ How the System Works",
        'how_text': """
        The system consists of two software components that collaborate to find the optimal tolerances:
        
        **🔵 The Designer Agent** starts with very wide tolerances (minimum cost) and adjusts them based on feedback. When the Tester finds a defect, the Designer tightens the tolerance for that dimension. When everything is fine, it tries to widen tolerances to reduce cost.
        
        **🔴 The Tester Agent** checks each proposed tolerance set. It uses an exact mathematical method: testing all 64 possible extreme combinations (each dimension at minimum or maximum). If it finds a combination that causes interference, it reports DEFECT and indicates exactly which dimension is at fault.
        
        **🧠 The Fractional Neuron** acts as a risk manager. It has long memory — it remembers what happened in past iterations. When the Tester finds many consecutive defects, the neuron becomes "stressed" (Beta ~0.85) and the Designer tightens aggressively. When the system stabilizes, the neuron relaxes (Beta ~0.15) and adjustments become fine and precise.
        
        **📐 The Mathematical Model** calculates the gap between pins and holes based on the real geometry of the assembly designed in SolidWorks.
        """
    }
}

# ---------- Inițializare sesiune ----------
if 'lang' not in st.session_state:
    st.session_state.lang = 'ro'
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

t = LANG[st.session_state.lang]

# ---------- Sidebar ----------
with st.sidebar:
    col_lang1, col_lang2, col_theme = st.columns(3)
    if col_lang1.button("RO", use_container_width=True):
        st.session_state.lang = 'ro'
    if col_lang2.button("EN", use_container_width=True):
        st.session_state.lang = 'en'
    theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
    if col_theme.button(theme_icon, use_container_width=True):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
    
    st.header(t['guide_header'])
    with st.expander(t['guide_expander'], expanded=False):
        st.markdown(t['guide_text'])
    
    st.divider()
    st.header(t['params_header'])
    
    alpha = st.slider(t['alpha_label'], 0.1, 1.0, 0.7, 0.1, help=t['alpha_help'])
    delta = st.slider(t['delta_label'], 0.05, 0.5, 0.2, 0.05, help=t['delta_help'])
    tol_init = st.slider(t['tol_label'], 0.1, 1.0, 0.5, 0.1, help=t['tol_help'])
    
    st.divider()
    run = st.button(t['run_button'], type="primary", use_container_width=True)

# ---------- Temă dark ----------
if st.session_state.theme == 'dark':
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #fafafa; }
    </style>
    """, unsafe_allow_html=True)

# ---------- Titlu ----------
st.title(t['title'])
st.subheader(t['subtitle'])

# ---------- Cum funcționează (doar înainte de rulare) ----------
if not run:
    st.header(t['how_header'])
    st.markdown(t['how_text'])

# ---------- Optimizare ----------
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
        
        m_iter.metric(t['iterations'], f"{iteratii}", help="Numărul curent de iterații.")
        m_cost.metric(t['cost_opt'], f"{cost:.2f}", help="Cost = suma(1/toleranță). Mai mic = mai ieftin.")
        m_beta.metric("Beta", f"{beta:.3f}", help="~0.85 = agresiv | ~0.15 = precaut")
        
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
    
    # ---------- Rezultate ----------
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
    
    # ---------- Comparație ----------
    st.divider()
    st.header(t['comparison_header'])
    st.markdown(t['comparison_text'])
    df_comp = pd.DataFrame({
        t['col_method']: [t['method_mas'], t['method_wc'], t['method_mc']],
        t['cost_opt']: [f"{proiectant.calculeaza_cost():.2f}", "∞", "~180"],
        t['col_eval']: [f"~{iteratii * 64:,}", "1", "10,000+"],
        t['col_guarantee']: [t['guarantee_abs'], t['guarantee_abs'], t['guarantee_stat']]
    })
    st.dataframe(df_comp, use_container_width=True, hide_index=True)
    
    # ---------- Monte Carlo ----------
    st.divider()
    st.header(t['mc_header'])
    st.markdown(t['mc_text'])
    
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
    col_mc1.metric(t['mc_samples'], f"{n_mc:,}")
    col_mc2.metric(t['mc_defects'], f"{defecte_mc}")
    col_mc3.metric(t['mc_prob'], f"{100*defecte_mc/n_mc:.3f}%")
    col_mc4.metric(t['mc_dist'], "Normală (3σ)")
    
    # ---------- Istoric ----------
    st.divider()
    st.subheader(t['history_header'])
    df_istoric = pd.DataFrame(istoric)
    st.dataframe(df_istoric, use_container_width=True, hide_index=True)
    
    csv = df_istoric.to_csv(index=False).encode('utf-8')
    st.download_button(t['export_csv'], csv, 'istoric_optimizare.csv', 'text/csv', help=t['export_tooltip'])
    
    # ---------- Grafice ----------
    st.divider()
    st.subheader(t['charts_header'])
    
    tab1, tab2, tab3 = st.tabs([t['tab_cost'], t['tab_beta'], t['tab_joc']])
    
    with tab1:
        st.line_chart(df_istoric, x=t['col_iter'], y=t['col_cost'], height=300)
        st.caption(t['caption_cost'])
    with tab2:
        st.line_chart(df_istoric, x=t['col_iter'], y=t['col_beta'], height=300)
        st.caption(t['caption_beta'])
    with tab3:
        st.line_chart(df_istoric, x=t['col_iter'], y=t['col_joc'], height=300)
        st.caption(t['caption_joc'])

else:
    st.info(t['wait_text'])
    st.markdown(t['about_text'])
