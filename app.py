import streamlit as st
import numpy as np
import pandas as pd
from agent_tester import AgentTester
from agent_proiectant import AgentProiectant
from model_matematic import functia_de_joc, valori_nominale

st.set_page_config(page_title="Optimizare Tolerante", page_icon="⚙️", layout="wide")

# ---------- Dictionar traduceri ----------
LANG = {
    'ro': {
        'tab1': "🏠 Acasa", 'tab2': "📊 Optimizare", 'tab3': "📈 Grafice",
        'tab4': "📖 Despre", 'tab5': "📐 Matematica",
        'params': "⚡ Parametri",
        'alpha': "Alpha (memorie fractionara)",
        'alpha_help': "0.1 = memorie lunga | 1.0 = memorie scurta",
        'delta': "Delta (pas ajustare)",
        'delta_help': "Cat de mult se modifica tolerantele la fiecare pas",
        'tol': "Toleranta initiala (mm)",
        'tol_help': "Toate cele 6 cote pornesc cu aceasta valoare",
        'run': "▶️ Ruleaza optimizarea",
        'wait': "Configureaza parametrii in panoul din stanga si apasa **Ruleaza optimizarea**.",
        'defect': "🔴 DEFECT la cota",
        'ok': "🟢 OK",
        'conv': "✅ CONVERGENTA atinsa in",
        'iterations': "Iteratii totale",
        'cost_opt': "Cost optim",
        'cost_init': "Cost initial",
        'tol_header': "Tolerante optime",
        'mc_header': "🎲 Simulare Monte Carlo",
        'mc_samples': "Esantioane",
        'mc_defects': "Defecte gasite",
        'mc_prob': "Probabilitate de defect",
        'mc_dist': "Distributie",
        'comp_header': "📊 Comparatie cu metodele clasice",
        'export': "📥 Exporta rezultatele (CSV)",
        'grafice_warn': "⚠️ Ruleaza mai intai optimizarea din tab-ul Optimizare.",
        'history': "📋 Istoricul complet al iteratiilor",
        'chart_cost': "Evolutia costului",
        'chart_beta': "Dinamica Beta",
        'chart_joc': "Evolutia jocului minim",
        'cap_cost': "Costul creste pe masura ce tolerantele sunt stranse. Un cost mai mic = fabricatie mai ieftina.",
        'cap_beta': "Beta reflecta starea neuronului fractionar. ~0.85 = sistem alert (strange agresiv). ~0.15 = sistem stabil (ajustari fine).",
        'cap_joc': "Jocul minim evolueaza de la negativ (interferenta) spre zero. Pozitiv = ansamblul functioneaza.",
        'joc_label': "Joc =",
        'cote': ['Diametru stift', 'Diametru gaura', 'DistX baza', 'DistY baza', 'DistX capac', 'DistY capac'],
    },
    'en': {
        'tab1': "🏠 Home", 'tab2': "📊 Optimization", 'tab3': "📈 Charts",
        'tab4': "📖 About", 'tab5': "📐 Mathematics",
        'params': "⚡ Parameters",
        'alpha': "Alpha (fractional memory)",
        'alpha_help': "0.1 = long memory | 1.0 = short memory",
        'delta': "Delta (adjustment step)",
        'delta_help': "How much tolerances change at each step",
        'tol': "Initial tolerance (mm)",
        'tol_help': "All 6 dimensions start with this value",
        'run': "▶️ Run Optimization",
        'wait': "Set parameters in the left panel and press **Run Optimization**.",
        'defect': "🔴 DEFECT at dimension",
        'ok': "🟢 OK",
        'conv': "✅ CONVERGENCE reached in",
        'iterations': "Total Iterations",
        'cost_opt': "Optimal Cost",
        'cost_init': "Initial Cost",
        'tol_header': "Optimal Tolerances",
        'mc_header': "🎲 Monte Carlo Simulation",
        'mc_samples': "Samples",
        'mc_defects': "Defects Found",
        'mc_prob': "Defect Probability",
        'mc_dist': "Distribution",
        'comp_header': "📊 Comparison with Classical Methods",
        'export': "📥 Export Results (CSV)",
        'grafice_warn': "⚠️ Run the optimization first from the Optimization tab.",
        'history': "📋 Complete Iteration History",
        'chart_cost': "Cost Evolution",
        'chart_beta': "Beta Dynamics",
        'chart_joc': "Gap Evolution",
        'cap_cost': "Cost increases as tolerances are tightened. Lower = cheaper manufacturing.",
        'cap_beta': "Beta reflects the fractional neuron state. ~0.85 = alert (tightens aggressively). ~0.15 = stable (fine adjustments).",
        'cap_joc': "Gap evolves from negative (interference) towards zero. Positive = assembly works.",
        'joc_label': "Gap =",
        'cote': ['Pin Diameter', 'Hole Diameter', 'DistX base', 'DistY base', 'DistX cover', 'DistY cover'],
    }
}

# ---------- Initializare ----------
if 'lang' not in st.session_state:
    st.session_state.lang = 'ro'
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

t = LANG[st.session_state.lang]

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("""
    <style>
        div[data-testid="stHorizontalBlock"] button {
            padding: 2px 8px !important;
            font-size: 12px !important;
            min-height: 0px !important;
            height: auto !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("RO", use_container_width=True, key="btn_ro"):
            st.session_state.lang = 'ro'
    with col2:
        if st.button("EN", use_container_width=True, key="btn_en"):
            st.session_state.lang = 'en'
    with col3:
        theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
        if st.button(theme_icon, use_container_width=True, key="btn_theme"):
            st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
    
    st.divider()
    st.header(t['params'])
    
    alpha = st.slider(t['alpha'], 0.10, 1.00, 0.70, 0.05, help=t['alpha_help'])
    delta = st.slider(t['delta'], 0.01, 0.50, 0.20, 0.01, help=t['delta_help'])
    tol_init = st.slider(t['tol'], 0.010, 1.000, 0.500, 0.005, help=t['tol_help'])
    
    st.divider()
    run = st.button(t['run'], type="primary", use_container_width=True)

# ---------- Dark theme ----------
if st.session_state.theme == 'dark':
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117 !important; color: #fafafa !important; }
        div[style*="background: #f8f9fa"] { background-color: #1a1c23 !important; border-color: #2d3139 !important; }
        div[style*="background: #f0f4ff"] { background-color: #1a1c23 !important; border-color: #2d3139 !important; }
        div[style*="background: linear-gradient"] { opacity: 0.9; }
        .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
        .stMarkdown li, .stMarkdown strong { color: #e0e0e0 !important; }
        div[style*="background: linear-gradient"] p,
        div[style*="background: linear-gradient"] strong { color: white !important; }
        div[data-testid="stMetric"] { background-color: #1a1c23 !important; }
        div[data-testid="stMetric"] label { color: #999 !important; }
        div[data-testid="stMetric"] div { color: #fafafa !important; }
        blockquote { background-color: #1a1c23 !important; border-left: 4px solid #667eea !important; color: #e0e0e0 !important; }
        .stDataFrame > div > div { background-color: #1a1c23 !important; }
        div[data-testid="stAlert"] { background-color: #1a1c23 !important; }
        .stTabs [data-baseweb="tab-list"] { background-color: #1a1c23 !important; }
        .stTabs [aria-selected="true"] { background-color: #2d3139 !important; color: #fafafa !important; }
    </style>
    """, unsafe_allow_html=True)

# ---------- CSS tab-uri ----------
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 6px; background-color: #f0f2f6; border-radius: 10px; padding: 6px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 6px 18px; font-size: 15px; font-weight: 500; }
    .stTabs [aria-selected="true"] { background-color: #ffffff; box-shadow: 0 1px 6px rgba(0,0,0,0.08); }
</style>
""", unsafe_allow_html=True)

# ---------- Tab-uri ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([t['tab1'], t['tab2'], t['tab3'], t['tab4'], t['tab5']])

# ================================================================
# TAB 1: ACASA
# ================================================================
with tab1:
    if st.session_state.lang == 'ro':
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="font-size: 2.2rem; margin-bottom: 0.5rem;">⚙️ Sistem Multi-Agent cu Neuron Fractionar</h1>
            <p style="font-size: 1.1rem; color: #666;">Optimizarea tolerantelor pentru ansambluri mecanice</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="display: flex; justify-content: center;">
            <img src="https://raw.githubusercontent.com/adumitrescu1212/optimizare-tolerante/main/ansamblu.gif" width="700">
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 20px; color: white; margin: 20px 0;">
            <p style="font-size: 0.95rem; line-height: 1.6; margin: 0; text-align: center;">
            Acest proiect propune o <strong>metoda noua</strong> de optimizare a tolerantelor,
            bazata pe o <strong>arhitectura multi-agent adversiala</strong> cu <strong>neuron fractionar</strong>.
            Doi agenti software interactioneaza iterativ pentru a gasi
            <strong>cel mai ieftin set de tolerante</strong> care garanteaza functionalitatea.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="font-size: 2.2rem; margin-bottom: 0.5rem;">⚙️ Multi-Agent System with Fractional Neuron</h1>
            <p style="font-size: 1.1rem; color: #666;">Tolerance Optimization for Mechanical Assemblies</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="display: flex; justify-content: center;">
            <img src="https://raw.githubusercontent.com/adumitrescu1212/optimizare-tolerante/main/ansamblu.gif" width="700">
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 20px; color: white; margin: 20px 0;">
            <p style="font-size: 0.95rem; line-height: 1.6; margin: 0; text-align: center;">
            This project proposes a <strong>novel method</strong> for dimensional tolerance optimization,
            based on an <strong>adversarial multi-agent architecture</strong> with a <strong>fractional neuron</strong>.
            Two software agents interact iteratively to find the
            <strong>cheapest tolerance set</strong> that guarantees assembly functionality.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #e0e0e0;">
            <h2 style="margin: 0; color: #667eea;">2</h2>
            <p style="margin: 5px 0 0 0; color: #555;">Agenti software autonomi</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #e0e0e0;">
            <h2 style="margin: 0; color: #764ba2;">64</h2>
            <p style="margin: 5px 0 0 0; color: #555;">Colturi verificate exhaustiv</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #e0e0e0;">
            <h2 style="margin: 0; color: #e74c3c;">< 1s</h2>
            <p style="margin: 5px 0 0 0; color: #555;">Timp de executie</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 🔴 Problema
            In fabricatia mecanica, **tolerantele dimensionale** reprezinta un compromis fundamental:
            - **Tolerante stranse** garanteaza asamblarea, dar costa foarte mult
            - **Tolerante largi** sunt economice, dar risca rebuturi
            Metodele traditionale trateaza optimizarea si analiza ca procese separate.
            """)
        else:
            st.markdown("""
            ### 🔴 The Problem
            In mechanical manufacturing, **dimensional tolerances** represent a fundamental trade-off:
            - **Tight tolerances** guarantee assembly but are very expensive
            - **Wide tolerances** are economical but risk defects
            Traditional methods treat optimization and analysis as separate processes.
            """)
    with col2:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 🟢 Solutia noastra
            Un **sistem multi-agent** cu doi roboti software care invata unul de la celalalt:
            - **🔵 Proiectantul** vrea tolerante cat mai largi (cost minim)
            - **🔴 Testerul** ataca fiecare propunere, cautand vulnerabilitati
            - **🧠 Neuronul fractionar** controleaza adaptiv agresivitatea
            """)
        else:
            st.markdown("""
            ### 🟢 Our Solution
            A **multi-agent system** with two software robots that learn from each other:
            - **🔵 The Designer** wants tolerances as wide as possible
            - **🔴 The Tester** attacks each proposal, searching for vulnerabilities
            - **🧠 The Fractional Neuron** adaptively controls aggressiveness
            """)
    
    st.divider()
    
    if st.session_state.lang == 'ro':
        st.markdown("### 🔬 Domenii de cercetare implicate")
    else:
        st.markdown("### 🔬 Research Areas Involved")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown("**🤖 Inteligenta artificiala**\nSisteme multi-agent")
    with col2: st.markdown("**📐 Calcul fractionar**\nDerivata Grunwald-Letnikov")
    with col3: st.markdown("**⚡ Optimizare**\nCercetari operationale")
    with col4: st.markdown("**🔧 Inginerie mecanica**\nSolidWorks CAD")
    
    st.divider()
    
    if st.session_state.lang == 'ro':
        st.markdown("""
        <div style="background: rgba(128, 128, 128, 0.08); border-radius: 8px; padding: 20px 25px; margin-top: 10px;">
            <p style="font-size: 1.05rem; margin: 0 0 10px 0;"><strong>Procedura de utilizare a sistemului</strong></p>
            <p style="margin: 4px 0; font-size: 0.95rem;">1. Configurati parametrii <strong>Alpha</strong>, <strong>Delta</strong> si <strong>Toleranta initiala</strong> in panoul lateral.</p>
            <p style="margin: 4px 0; font-size: 0.95rem;">2. Accesati tab-ul <strong>Optimizare</strong> si actionati butonul <strong>Ruleaza optimizarea</strong>.</p>
            <p style="margin: 4px 0; font-size: 0.95rem;">3. Analizati rezultatele: tolerante optime, simulare Monte Carlo, comparatii cu metodele clasice.</p>
            <p style="margin: 4px 0; font-size: 0.95rem;">4. Consultati tab-ul <strong>Matematica</strong> pentru fundamentarea teoretica a fiecarui modul.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(128, 128, 128, 0.08); border-radius: 8px; padding: 20px 25px; margin-top: 10px;">
            <p style="font-size: 1.05rem; margin: 0 0 10px 0;"><strong>System Usage Procedure</strong></p>
            <p style="margin: 4px 0; font-size: 0.95rem;">1. Configure parameters <strong>Alpha</strong>, <strong>Delta</strong>, and <strong>Initial Tolerance</strong> in the side panel.</p>
            <p style="margin: 4px 0; font-size: 0.95rem;">2. Go to the <strong>Optimization</strong> tab and press <strong>Run Optimization</strong>.</p>
            <p style="margin: 4px 0; font-size: 0.95rem;">3. Analyze the results: optimal tolerances, Monte Carlo simulation, comparisons with classical methods.</p>
            <p style="margin: 4px 0; font-size: 0.95rem;">4. Consult the <strong>Mathematics</strong> tab for the theoretical foundation of each module.</p>
        </div>
        """, unsafe_allow_html=True)


# ================================================================
# TAB 2: OPTIMIZARE
# ================================================================
with tab2:
    st.title(t['tab2'])
    
    if run:
        tolerante_init = np.full(6, tol_init)
                # ---------- Combinatia critica INITIALA ----------
        st.divider()
        st.header("🔍 " + ("Combinatia critica INAINTE de optimizare (tolerante initiale)" if st.session_state.lang == 'ro' else "Critical Combination BEFORE optimization (initial tolerances)"))
        
        tester_init = AgentTester(alpha=alpha, max_iteratii=500)
        rez_init, X_init, cota_init = tester_init.ataca(np.full(6, tol_init))
        joc_init, _, _ = functia_de_joc(X_init)
        
        df_critic_init = pd.DataFrame({
            ('Cota' if st.session_state.lang == 'ro' else 'Dimension'): t['cote'],
            ('Valoare nominala' if st.session_state.lang == 'ro' else 'Nominal Value'): valori_nominale,
            ('Valoare critica' if st.session_state.lang == 'ro' else 'Critical Value'): np.round(X_init, 5),
            ('Abatere' if st.session_state.lang == 'ro' else 'Deviation'): np.round(X_init - valori_nominale, 5),
            ('Directie' if st.session_state.lang == 'ro' else 'Direction'): [
                'Maxim' if X_init[i] > valori_nominale[i] else 'Minim' for i in range(6)
            ]
        })
        st.dataframe(df_critic_init, use_container_width=True, hide_index=True)
        
        if st.session_state.lang == 'ro':
            st.markdown(
                "> **Pentru validare CAD:** Acestea sunt valorile care trebuie introduse in SolidWorks "
                f"pentru a reproduce interferenta. Jocul cu aceste valori este **{joc_init:.4f} mm** "
                "(puternic negativ → interferenta vizibila)."
            )
        else:
            st.markdown(
                "> **For CAD validation:** These are the values to enter in SolidWorks "
                f"to reproduce the interference. The gap with these values is **{joc_init:.4f} mm** "
                "(strongly negative → visible interference)."
            )
        
        st.divider()
        st.header("⏳ " + ("Optimizare in curs..." if st.session_state.lang == 'ro' else "Optimization in progress..."))
        proiectant = AgentProiectant(valori_nominale, tolerante_init, delta=delta)
        tester = AgentTester(alpha=alpha, max_iteratii=500)
        
        status = st.empty()
        c1, c2, c3 = st.columns(3)
        m_iter = c1.empty()
        m_cost = c2.empty()
        m_beta = c3.empty()
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
                'Iterație': iteratii, 'Rezultat': rezultat, 'Beta': round(beta, 3),
                'Cost': round(cost, 2), 'Joc (mm)': round(joc, 4),
                'Cotă vinovată': cota + 1 if cota is not None else '-'
            })
            
            m_iter.metric(t['iterations'], f"{iteratii}")
            m_cost.metric(t['cost_opt'], f"{cost:.2f}")
            m_beta.metric("Beta", f"{beta:.3f}")
            
            if rezultat == "DEFECT":
                fara_defect = 0
                proiectant.primeste_raport(True, cota, beta)
                status.warning(f"{t['defect']} {cota+1} | {t['joc_label']} {joc:.4f} mm")
            else:
                fara_defect += 1
                status.success(f"{t['ok']} | {t['joc_label']} {joc:.4f} mm")
                if fara_defect >= 2:
                    status.info(f"{t['conv']} {iteratii}!")
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
        st.session_state['iteratii'] = iteratii
        
        st.divider()
        st.header("📊 " + ("Rezultate finale" if st.session_state.lang == 'ro' else "Final Results"))
        
        c1, c2, c3 = st.columns(3)
        c1.metric(t['iterations'], f"{iteratii}")
        c2.metric(t['cost_opt'], f"{proiectant.calculeaza_cost():.2f}")
        c3.metric(t['cost_init'], f"{np.sum(1.0/(tolerante_init + 1e-9)):.2f}")
        
        if st.session_state.lang == 'ro':
            st.markdown(f"> **Interpretare:** Sistemul a convergit in **{iteratii} iteratii**. Costul a crescut de la **{np.sum(1.0/(tolerante_init + 1e-9)):.2f}** la **{proiectant.calculeaza_cost():.2f}**. Aceasta este frontiera de fezabilitate.")
        else:
            st.markdown(f"> **Interpretation:** Converged in **{iteratii} iterations**. Cost increased from **{np.sum(1.0/(tolerante_init + 1e-9)):.2f}** to **{proiectant.calculeaza_cost():.2f}**.")
        
        st.subheader(t['tol_header'])
        df_tol = pd.DataFrame({
            ('Cotă' if st.session_state.lang == 'ro' else 'Dimension'): t['cote'],
            ('Val. nominală (mm)' if st.session_state.lang == 'ro' else 'Nominal (mm)'): valori_nominale,
            ('Toleranță optimă (±mm)' if st.session_state.lang == 'ro' else 'Optimal (±mm)'): np.round(proiectant.propune_tolerante(), 5),
        })
        st.dataframe(df_tol, use_container_width=True, hide_index=True)
        
        st.divider()
        st.header(t['mc_header'])
        tol_opt = proiectant.propune_tolerante()
        n_mc, defecte_mc = 5000, 0
        for _ in range(n_mc):
            X_mc = np.random.normal(loc=valori_nominale, scale=tol_opt/3)
            X_mc = np.clip(X_mc, valori_nominale - tol_opt, valori_nominale + tol_opt)
            if functia_de_joc(X_mc)[0] <= 0:
                defecte_mc += 1
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t['mc_samples'], f"{n_mc:,}")
        c2.metric(t['mc_defects'], f"{defecte_mc}")
        c3.metric(t['mc_prob'], f"{100*defecte_mc/n_mc:.3f}%")
        c4.metric(t['mc_dist'], "Normală (3σ)")
        
        st.divider()
        st.header(t['comp_header'])
        df_comp = pd.DataFrame({
            ('Metoda' if st.session_state.lang == 'ro' else 'Method'): ['Sistem Multi-Agent', 'Worst-Case', 'Monte Carlo'],
            'Cost': [f"{proiectant.calculeaza_cost():.2f}", "∞", "~180"],
            ('Evaluări' if st.session_state.lang == 'ro' else 'Evaluations'): [f"~{iteratii * 64:,}", "1", "10,000+"],
            ('Garanție' if st.session_state.lang == 'ro' else 'Guarantee'): ['Absolută', 'Absolută', 'Statistică'],
        })
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
        
         # ---------- Combinația critică ----------
        st.divider()
        st.header("🔍 " + ("Combinația critică (cel mai rău caz)" if st.session_state.lang == 'ro' else "Critical Combination (Worst Case)"))
        
        tester2 = AgentTester(alpha=alpha, max_iteratii=500)
        rezultat_crit, X_crit, cota_crit = tester2.ataca(proiectant.propune_tolerante())
        joc_crit, j1, j2 = functia_de_joc(X_crit)
        
        df_critic = pd.DataFrame({
            ('Cotă' if st.session_state.lang == 'ro' else 'Dimension'): t['cote'],
            ('Valoare nominală' if st.session_state.lang == 'ro' else 'Nominal Value'): valori_nominale,
            ('Valoare critică' if st.session_state.lang == 'ro' else 'Critical Value'): np.round(X_crit, 5),
            ('Abatere' if st.session_state.lang == 'ro' else 'Deviation'): np.round(X_crit - valori_nominale, 5),
            ('Direcție' if st.session_state.lang == 'ro' else 'Direction'): [
                'Maxim' if X_crit[i] > valori_nominale[i] else 'Minim' for i in range(6)
            ]
        })
        st.dataframe(df_critic, use_container_width=True, hide_index=True)
        
        # Extragem cota într-o variabilă sigură pentru afișare
        cota_afisata = cota_crit + 1 if cota_crit is not None else "-"
        
        if st.session_state.lang == 'ro':
            st.markdown(
                "> **Interpretare:** Tabelul arata combinatia exacta de dimensiuni care produce cel mai mic joc "
                f"(joc = **{joc_crit:.4f} mm**). Aceste valori trebuie introduse in SolidWorks pentru validarea "
                "experimentala. Coloana *Directie* indica daca dimensiunea trebuie setata la maximul sau minimul "
                f"tolerantei. Cota **{cota_afisata}** este cea mai solicitată în această configurație."
            )
        else:
            st.markdown(
                "> **Interpretation:** The table shows the exact dimension combination producing the smallest gap "
                f"(gap = **{joc_crit:.4f} mm**). These values should be entered in SolidWorks for experimental "
                "validation. The *Direction* column indicates whether the dimension is at maximum or minimum "
                f"tolerance. Dimension **{cota_afisata}** is the most stressed in this configuration."
            )
        csv = pd.DataFrame(istoric).to_csv(index=False).encode('utf-8')
        st.download_button(t['export'], csv, 'istoric_optimizare.csv', 'text/csv')
        st.success("👈 " + ("Mergi la tab-ul Grafice." if st.session_state.lang == 'ro' else "Go to Charts tab."))
    else:
        st.info(t['wait'])

# ================================================================
# TAB 3: GRAFICE
# ================================================================
with tab3:
    st.title("📈 " + ("Grafice" if st.session_state.lang == 'ro' else "Charts"))
    if 'istoric' not in st.session_state or st.session_state['istoric'] is None:
        st.warning(t['grafice_warn'])
    else:
        df = pd.DataFrame(st.session_state['istoric'])
        st.subheader(t['history'])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.divider()
        tg1, tg2, tg3 = st.tabs([t['chart_cost'], t['chart_beta'], t['chart_joc']])
        with tg1:
            st.line_chart(df, x='Iterație', y='Cost', height=400)
            st.caption(t['cap_cost'])
        with tg2:
            st.line_chart(df, x='Iterație', y='Beta', height=400)
            st.caption(t['cap_beta'])
        with tg3:
            st.line_chart(df, x='Iterație', y='Joc (mm)', height=400)
            st.caption(t['cap_joc'])

# ================================================================
# TAB 4: DESPRE
# ================================================================
with tab4:
    st.title("📖 " + ("Despre proiect" if st.session_state.lang == 'ro' else "About the Project"))
    if st.session_state.lang == 'ro':
        st.markdown("""
        ### 🎯 Ce este acest proiect?
        Un **sistem inteligent de optimizare a toleranțelor** pentru ansambluri mecanice, dezvoltat
        la intersecția dintre **inteligența artificială**, **ingineria mecanică** și **calculul fracționar**.
        
        ---
        ### 🔥 Ce ne-a motivat?
        Toleranțarea este o provocare fundamentală: toleranțe strânse = calitate + cost mare,
        toleranțe largi = economic + risc. Metodele tradiționale tratează optimizarea și analiza separat.
        Am vrut un sistem care să le integreze dinamic.
        
        ---
        ### ✨ Elemente de originalitate
        1. **Abordare adversială pentru toleranțe** — premieră în domeniu
        2. **Neuron fracționar ca manager de risc** — contribuție originală
        3. **Garanție matematică absolută** — teorema colțurilor (64 verificări)
        4. **Flux complet pe resurse minime** — Python + SolidWorks Student
        
        ---
        ### 🏗️ Cum funcționează
        **🔵 Agentul Proiectant** ajustează toleranțele. **🔴 Agentul Tester** verifică 64 de colțuri.
        **🧠 Neuronul fracționar** controlează agresivitatea cu memorie lungă.
        """)
    else:
        st.markdown("""
        ### 🎯 What is this project?
        An **intelligent tolerance optimization system** developed at the intersection of
        **artificial intelligence**, **mechanical engineering**, and **fractional calculus**.
        
        ---
        ### 🔥 What motivated us?
        Tolerancing is a fundamental challenge. We wanted a system that dynamically integrates
        optimization and analysis.
        
        ---
        ### ✨ Original Contributions
        1. **Adversarial approach for tolerances** — novel in the field
        2. **Fractional neuron as risk manager** — original contribution
        3. **Absolute mathematical guarantee** — corner theorem (64 checks)
        4. **Complete low-cost workflow** — Python + SolidWorks Student
        
        ---
        ### 🏗️ How It Works
        **🔵 Designer Agent** adjusts tolerances. **🔴 Tester Agent** checks 64 corners.
        **🧠 Fractional Neuron** controls aggressiveness with long memory.
        """)

# ================================================================
# TAB 5: MATEMATICA
# ================================================================
# TAB 5: MATEMATICA
# ================================================================
with tab5:
    st.title("📐 " + ("Breviat teoretic" if st.session_state.lang == 'ro' else "Theoretical Brief"))
    
    if st.session_state.lang == 'ro':
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 20px; color: white; margin-bottom: 25px;">
            <p style="font-size: 1rem; line-height: 1.6; margin: 0;">
            Acest breviar contine <strong>fundamentele matematice</strong> pe care se bazeaza intregul sistem.
            Fiecare sectiune prezinta <strong>conceptul teoretic</strong>, <strong>formulele corespunzatoare</strong>
            si <strong>modulul Python</strong> in care este implementat.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 20px; color: white; margin-bottom: 25px;">
            <p style="font-size: 1rem; line-height: 1.6; margin: 0;">
            This brief contains the <strong>mathematical foundations</strong> underlying the entire system.
            Each section presents the <strong>theoretical concept</strong>, <strong>corresponding formulas</strong>,
            and the <strong>Python module</strong> where it is implemented.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    tm1, tm2, tm3, tm4, tm5, tm6, tm7, tm8, tm9 = st.tabs([
        "1. " + ("Functia de joc" if st.session_state.lang == 'ro' else "Gap Function"),
        "2. " + ("Gradientul analitic" if st.session_state.lang == 'ro' else "Analytical Gradient"),
        "3. " + ("Subgradientul" if st.session_state.lang == 'ro' else "Subgradient"),
        "4. " + ("Teorema colturilor" if st.session_state.lang == 'ro' else "Corner Theorem"),
        "5. " + ("Neuronul fractionar" if st.session_state.lang == 'ro' else "Fractional Neuron"),
        "6. " + ("Cuantificarea incertitudinii" if st.session_state.lang == 'ro' else "Uncertainty Quantification"),
        "7. " + ("Functia de cost" if st.session_state.lang == 'ro' else "Cost Function"),
        "8. " + ("Convergenta" if st.session_state.lang == 'ro' else "Convergence"),
        "9. " + ("Limitari" if st.session_state.lang == 'ro' else "Limitations"),
    ])
    
    # ---------- TAB 5.1 ----------
    with tm1:
        st.markdown("### 1. " + ("Functia de joc" if st.session_state.lang == 'ro' else "The Gap Function"))
        if st.session_state.lang == 'ro':
            st.markdown("""
            <div style="background: rgba(128,128,128,0.06); border-radius: 10px; padding: 20px; margin: 15px 0;">
                <p style="font-size: 1rem; line-height: 1.7;">
                <strong>Obiectiv:</strong> Determinarea matematica a conditiei de asamblare corecta pentru o pereche stift-gaura.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("**Definitie.** Pentru o pereche stift-gaura, fie $R_s$ raza stiftului, $R_g$ raza gaurii si $d = \\|S - G\\|$ distanta euclidiana dintre centrele lor. **Jocul** este:")
            st.latex(r"J = R_g - R_s - d")
            st.markdown("**Demonstratie.** Doua cercuri sunt disjuncte daca $d > R_s + R_g$ sau $d < |R_s - R_g|$. Pentru asamblare, stiftul trebuie sa fie **complet interior** gaurii ($R_g > R_s$). Conditia: $d + R_s < R_g$, adica $R_g - R_s - d > 0$.")
            st.markdown("**Functia globala de joc:**")
            st.latex(r"f(X) = \min(J_1(X), J_2(X))")
            st.markdown("**Criteriul de asamblare:** Ansamblul functioneaza *daca si numai daca* $f(X) > 0$.")
            st.markdown("**Exprimare explicita:**")
            st.latex(r"f(X) = \frac{x_2 - x_1}{2} - \sqrt{(x_3 - x_5)^2 + (x_4 - x_6)^2}")
            st.markdown("""
            <div style="background: rgba(102,126,234,0.1); border-left: 3px solid #667eea; border-radius: 0 8px 8px 0; padding: 10px 15px; margin-top: 15px;">
                <strong>💻 Implementare:</strong> <code>model_matematic.py</code> → functia <code>functia_de_joc(X)</code>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: rgba(128,128,128,0.06); border-radius: 10px; padding: 20px; margin: 15px 0;">
                <p style="font-size: 1rem; line-height: 1.7;">
                <strong>Objective:</strong> Mathematical determination of the correct assembly condition for a pin-hole pair.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.latex(r"J = R_g - R_s - d")
            st.latex(r"f(X) = \min(J_1(X), J_2(X))")
            st.latex(r"f(X) = \frac{x_2 - x_1}{2} - \sqrt{(x_3 - x_5)^2 + (x_4 - x_6)^2}")
            st.markdown("""
            <div style="background: rgba(102,126,234,0.1); border-left: 3px solid #667eea; border-radius: 0 8px 8px 0; padding: 10px 15px; margin-top: 15px;">
                <strong>💻 Implementation:</strong> <code>model_matematic.py</code> → function <code>functia_de_joc(X)</code>
            </div>
            """, unsafe_allow_html=True)
    
    # ---------- TAB 5.2 ----------
    with tm2:
        st.markdown("### 2. " + ("Gradientul analitic" if st.session_state.lang == 'ro' else "Analytical Gradient"))
        if st.session_state.lang == 'ro':
            st.markdown("""
            <div style="background: rgba(128,128,128,0.06); border-radius: 10px; padding: 20px; margin: 15px 0;">
                <p style="font-size: 1rem; line-height: 1.7;">
                <strong>Obiectiv:</strong> Identificarea cotelor cu cel mai mare impact asupra jocului.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.latex(r"\nabla f(X) = \begin{bmatrix} -\frac{1}{2} & +\frac{1}{2} & -\frac{x_3-x_5}{d} & -\frac{x_4-x_6}{d} & +\frac{x_3-x_5}{d} & +\frac{x_4-x_6}{d} \end{bmatrix}^T")
            st.markdown("$-1/2$ pentru stift → mai gros = joc mai mic. $+1/2$ pentru gaura → mai mare = joc mai mare.")
        else:
            st.markdown("""
            <div style="background: rgba(128,128,128,0.06); border-radius: 10px; padding: 20px; margin: 15px 0;">
                <p style="font-size: 1rem; line-height: 1.7;">
                <strong>Objective:</strong> Identifying dimensions with greatest impact on the gap.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.latex(r"\nabla f(X) = \begin{bmatrix} -\frac{1}{2} & +\frac{1}{2} & -\frac{x_3-x_5}{d} & -\frac{x_4-x_6}{d} & +\frac{x_3-x_5}{d} & +\frac{x_4-x_6}{d} \end{bmatrix}^T")
        st.markdown("""
        <div style="background: rgba(102,126,234,0.1); border-left: 3px solid #667eea; border-radius: 0 8px 8px 0; padding: 10px 15px; margin-top: 15px;">
            <strong>💻 Implementare:</strong> <code>model_matematic.py</code> → <code>calculeaza_subgradient(X)</code>
        </div>
        """, unsafe_allow_html=True)
    
    # ---------- TAB 5.3 ----------
    with tm3:
        st.markdown("### 3. " + ("Subgradientul" if st.session_state.lang == 'ro' else "Subgradient"))
        if st.session_state.lang == 'ro':
            st.markdown("""
            <div style="background: rgba(128,128,128,0.06); border-radius: 10px; padding: 20px; margin: 15px 0;">
                <p style="font-size: 1rem; line-height: 1.7;">
                <strong>Obiectiv:</strong> Tratarea punctelor in care $f(X) = \\min(J_1, J_2)$ nu este diferentiabila.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.latex(r"\partial f(X) = \text{conv}\{\nabla J_i(X) : i \in \mathcal{A}(X)\}")
            st.markdown("**Cazul 1:** Un singur $J_i$ activ → gradientul sau. **Cazul 2:** $J_1 = J_2$ → orice combinatie convexa. Cand $d=0$: regularizare.")
        else:
            st.markdown("""
            <div style="background: rgba(128,128,128,0.06); border-radius: 10px; padding: 20px; margin: 15px 0;">
                <p style="font-size: 1rem; line-height: 1.7;">
                <strong>Objective:</strong> Handling non-differentiable points of $f(X) = \\min(J_1, J_2)$.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.latex(r"\partial f(X) = \text{conv}\{\nabla J_i(X) : i \in \mathcal{A}(X)\}")
        st.markdown("""
        <div style="background: rgba(102,126,234,0.1); border-left: 3px solid #667eea; border-radius: 0 8px 8px 0; padding: 10px 15px; margin-top: 15px;">
            <strong>💻 Implementare:</strong> <code>model_matematic.py</code> → <code>calculeaza_subgradient(X)</code>
        </div>
        """, unsafe_allow_html=True)
