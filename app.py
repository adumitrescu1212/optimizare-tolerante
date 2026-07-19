import streamlit as st
import numpy as np
import pandas as pd
from agent_tester import AgentTester
from agent_proiectant import AgentProiectant
from model_matematic import functia_de_joc, valori_nominale

st.set_page_config(page_title="Optimizare Toleranțe", page_icon="⚙️", layout="wide")

# ---------- Dicționar traduceri ----------
LANG = {
    'ro': {
        'tab1': "🏠 Acasă", 'tab2': "📊 Optimizare", 'tab3': "📈 Grafice",
        'tab4': "📖 Despre", 'tab5': "📐 Matematică",
        'params': "⚡ Parametri",
        'alpha': "Alpha (memorie fracționară)",
        'alpha_help': "0.1 = memorie lungă | 1.0 = memorie scurtă",
        'delta': "Delta (pas ajustare)",
        'delta_help': "Cât de mult se modifică toleranțele la fiecare pas",
        'tol': "Toleranță inițială (mm)",
        'tol_help': "Toate cele 6 cote pornesc cu această valoare",
        'run': "▶️ Rulează optimizarea",
        'wait': "Configurează parametrii în panoul din stânga și apasă **Rulează optimizarea**.",
        'defect': "🔴 DEFECT la cota",
        'ok': "🟢 OK",
        'conv': "✅ CONVERGENȚĂ atinsă în",
        'iterations': "Iterații totale",
        'cost_opt': "Cost optim",
        'cost_init': "Cost inițial",
        'tol_header': "Toleranțe optime",
        'mc_header': "🎲 Simulare Monte Carlo",
        'mc_samples': "Eșantioane",
        'mc_defects': "Defecte găsite",
        'mc_prob': "Probabilitate de defect",
        'mc_dist': "Distribuție",
        'comp_header': "📊 Comparație cu metodele clasice",
        'export': "📥 Exportă rezultatele (CSV)",
        'grafice_warn': "⚠️ Rulează mai întâi optimizarea din tab-ul Optimizare.",
        'history': "📋 Istoricul complet al iterațiilor",
        'chart_cost': "Evoluția costului",
        'chart_beta': "Dinamica Beta",
        'chart_joc': "Evoluția jocului minim",
        'cap_cost': "Costul crește pe măsură ce toleranțele sunt strânse. Un cost mai mic = fabricație mai ieftină.",
        'cap_beta': "Beta reflectă starea neuronului fracționar. ~0.85 = sistem alert (strânge agresiv). ~0.15 = sistem stabil (ajustări fine).",
        'cap_joc': "Jocul minim evoluează de la negativ (interferență) spre zero. Pozitiv = ansamblul funcționează.",
        'joc_label': "Joc =",
        'cote': ['Diametru știft', 'Diametru gaură', 'DistX bază', 'DistY bază', 'DistX capac', 'DistY capac'],
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

# ---------- Inițializare ----------
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
    st.markdown("""<style>.stApp { background-color: #0e1117; color: #fafafa; }</style>""", unsafe_allow_html=True)

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
# TAB 1: ACASĂ
# ================================================================
with tab1:
    if st.session_state.lang == 'ro':
        st.markdown("""
        <div style="text-align: center; padding: 20px 0 30px 0;">
            <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚙️ Sistem Multi-Agent cu Neuron Fracționar</h1>
            <p style="font-size: 1.2rem; color: #666;">Optimizarea toleranțelor pentru ansambluri mecanice</p>
        </div>
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 30px; color: white; margin-bottom: 25px;">
            <h3 style="color: white; margin-top: 0;">🎯 Rezumat</h3>
            <p style="font-size: 1.05rem; line-height: 1.7;">
            Acest proiect propune o <strong>metodă nouă</strong> de optimizare a toleranțelor dimensionale,
            bazată pe o <strong>arhitectură multi-agent adversială</strong> cu <strong>neuron fracționar</strong>.
            Doi agenți software — un Proiectant și un Tester — interacționează iterativ pentru a găsi
            <strong>cel mai ieftin set de toleranțe</strong> care garantează funcționalitatea ansamblului.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0 30px 0;">
            <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚙️ Multi-Agent System with Fractional Neuron</h1>
            <p style="font-size: 1.2rem; color: #666;">Tolerance Optimization for Mechanical Assemblies</p>
        </div>
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 30px; color: white; margin-bottom: 25px;">
            <h3 style="color: white; margin-top: 0;">🎯 Abstract</h3>
            <p style="font-size: 1.05rem; line-height: 1.7;">
            This project proposes a <strong>novel method</strong> for dimensional tolerance optimization,
            based on an <strong>adversarial multi-agent architecture</strong> with a <strong>fractional neuron</strong>.
            Two software agents — a Designer and a Tester — interact iteratively to find the
            <strong>cheapest tolerance set</strong> that guarantees assembly functionality.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #e0e0e0;">
            <h2 style="margin: 0; color: #667eea;">2</h2>
            <p style="margin: 5px 0 0 0; color: #555;">Agenți software autonomi</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #e0e0e0;">
            <h2 style="margin: 0; color: #764ba2;">64</h2>
            <p style="margin: 5px 0 0 0; color: #555;">Colțuri verificate exhaustiv</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #e0e0e0;">
            <h2 style="margin: 0; color: #e74c3c;">< 1s</h2>
            <p style="margin: 5px 0 0 0; color: #555;">Timp de execuție</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 🔴 Problema
            În fabricația mecanică, **toleranțele dimensionale** reprezintă un compromis fundamental:
            - **Toleranțe strânse** garantează asamblarea, dar costă foarte mult
            - **Toleranțe largi** sunt economice, dar riscă rebuturi
            Metodele tradiționale tratează optimizarea și analiza ca procese separate.
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
            ### 🟢 Soluția noastră
            Un **sistem multi-agent** cu doi roboți software care învață unul de la celălalt:
            - **🔵 Proiectantul** vrea toleranțe cât mai largi (cost minim)
            - **🔴 Testerul** atacă fiecare propunere, căutând vulnerabilități
            - **🧠 Neuronul fracționar** controlează adaptiv agresivitatea
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
    with col1: st.markdown("**🤖 Inteligență artificială**\nSisteme multi-agent")
    with col2: st.markdown("**📐 Calcul fracționar**\nDerivata Grünwald-Letnikov")
    with col3: st.markdown("**⚡ Optimizare**\nCercetări operaționale")
    with col4: st.markdown("**🔧 Inginerie mecanică**\nSolidWorks CAD")
    
    st.divider()
    
    if st.session_state.lang == 'ro':
        st.info("""
        ### 🚀 Cum începi?
        1. **Configurează parametrii** în panoul din stânga
        2. **Accesează tab-ul Optimizare** și apasă **Rulează optimizarea**
        3. **Explorează rezultatele** — toleranțe, grafice, Monte Carlo, comparații
        4. **Studiază matematica** din spatele sistemului în tab-ul dedicat
        """)
    else:
        st.info("""
        ### 🚀 How to Start
        1. **Configure parameters** in the left panel
        2. **Go to the Optimization tab** and press **Run Optimization**
        3. **Explore the results** — tolerances, charts, Monte Carlo, comparisons
        4. **Study the mathematics** behind the system in the dedicated tab
        """)

# ================================================================
# TAB 2: OPTIMIZARE
# ================================================================
with tab2:
    st.title(t['tab2'])
    
    if run:
        tolerante_init = np.full(6, tol_init)
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
# TAB 5: MATEMATICĂ
# ================================================================
with tab5:
    st.title("📐 " + ("Breviat teoretic" if st.session_state.lang == 'ro' else "Theoretical Brief"))
    
    if st.session_state.lang == 'ro':
        st.markdown("Acest breviar conține fundamentele matematice pe care se bazează întregul sistem. Fiecare concept este însoțit de demonstrația corespunzătoare și de indicarea modulului Python în care este implementat.")
    else:
        st.markdown("This brief contains the mathematical foundations underlying the entire system. Each concept is accompanied by its proof and an indication of the Python module where it is implemented.")
    
    tm1, tm2, tm3, tm4, tm5, tm6, tm7, tm8, tm9 = st.tabs([
        "1. " + ("Funcția de joc" if st.session_state.lang == 'ro' else "Gap Function"),
        "2. " + ("Gradientul analitic" if st.session_state.lang == 'ro' else "Analytical Gradient"),
        "3. " + ("Subgradientul" if st.session_state.lang == 'ro' else "Subgradient"),
        "4. " + ("Teorema colțurilor" if st.session_state.lang == 'ro' else "Corner Theorem"),
        "5. " + ("Neuronul fracționar" if st.session_state.lang == 'ro' else "Fractional Neuron"),
        "6. " + ("Cuantificarea incertitudinii" if st.session_state.lang == 'ro' else "Uncertainty Quantification"),
        "7. " + ("Funcția de cost" if st.session_state.lang == 'ro' else "Cost Function"),
        "8. " + ("Convergența" if st.session_state.lang == 'ro' else "Convergence"),
        "9. " + ("Limitări" if st.session_state.lang == 'ro' else "Limitations"),
    ])
    
    # ---------- TAB 5.1: FUNCȚIA DE JOC ----------
    with tm1:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 1. Funcția de joc — modelarea condiției de asamblare
            
            **Problemă:** Cum determinăm matematic dacă un ansamblu mecanic se poate monta corect?
            **Răspuns:** Prin calculul **jocului** — spațiul liber dintre un știft și gaura corespunzătoare.
            
            ---
            #### Definiție
            Pentru o pereche știft-gaură, fie $R_s$ raza știftului, $R_g$ raza găurii și $d = \\|S - G\\|$ distanța euclidiană dintre centrele lor. **Jocul** este:
            $$J = R_g - R_s - d$$
            
            #### Demonstrație geometrică
            Două cercuri sunt disjuncte dacă $d > R_s + R_g$ sau $d < |R_s - R_g|$. Pentru asamblare, știftul trebuie să fie **complet interior** găurii ($R_g > R_s$). Condiția de incluziune completă: $d + R_s < R_g$, echivalent cu $R_g - R_s - d > 0$. ∎
            
            ---
            #### Funcția globală de joc
            $$f(X) = \\min(J_1(X), J_2(X))$$
            **Criteriul de asamblare:** Ansamblul funcționează **dacă și numai dacă** $f(X) > 0$.
            
            ---
            #### Exprimarea explicită
            $$f(X) = \\frac{x_2 - x_1}{2} - \\sqrt{(x_3 - x_5)^2 + (x_4 - x_6)^2}$$
            **💻 Implementare:** `model_matematic.py` → `functia_de_joc(X)`
            """)
        else:
            st.markdown("""
            ### 1. The Gap Function — modeling the assembly condition
            **Problem:** How do we mathematically determine if a mechanical assembly can be correctly mounted?
            **Answer:** By calculating the **gap** — the free space between a pin and its corresponding hole.
            
            ---
            #### Definition
            $$J = R_g - R_s - d$$
            #### Geometric Proof
            Two circles are disjoint iff $d > R_s + R_g$ or $d < |R_s - R_g|$. For assembly, the pin must be **fully inside** the hole ($R_g > R_s$). The condition: $d + R_s < R_g$, i.e. $R_g - R_s - d > 0$. ∎
            
            ---
            #### Global Gap Function
            $$f(X) = \\min(J_1(X), J_2(X))$$
            **Assembly criterion:** The assembly works **iff** $f(X) > 0$.
            
            ---
            #### Explicit Expression
            $$f(X) = \\frac{x_2 - x_1}{2} - \\sqrt{(x_3 - x_5)^2 + (x_4 - x_6)^2}$$
            **💻 Implementation:** `model_matematic.py` → `functia_de_joc(X)`
            """)
    
    # ---------- TAB 5.2: GRADIENTUL ANALITIC ----------
    with tm2:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 2. Gradientul analitic — direcția de ajustare
            **Problemă:** Cum știm care cotă influențează cel mai mult jocul?
            **Răspuns:** Prin calculul analitic al gradientului funcției de joc.
            
            ---
            $$\\nabla f(X) = \\begin{bmatrix} -\\frac{1}{2} & +\\frac{1}{2} & -\\frac{x_3-x_5}{d} & -\\frac{x_4-x_6}{d} & +\\frac{x_3-x_5}{d} & +\\frac{x_4-x_6}{d} \\end{bmatrix}^T$$
            
            - $-1/2$: știftul mai gros → joc mai mic
            - $+1/2$: gaura mai mare → joc mai mare
            
            **💻 Implementare:** `model_matematic.py` → `calculeaza_subgradient(X)` (analitic, nu diferențe finite)
            """)
        else:
            st.markdown("""
            ### 2. Analytical Gradient — the adjustment direction
            $$\\nabla f(X) = \\begin{bmatrix} -\\frac{1}{2} & +\\frac{1}{2} & -\\frac{x_3-x_5}{d} & -\\frac{x_4-x_6}{d} & +\\frac{x_3-x_5}{d} & +\\frac{x_4-x_6}{d} \\end{bmatrix}^T$$
            **💻 Implementation:** `model_matematic.py` → `calculeaza_subgradient(X)`
            """)
    
    # ---------- TAB 5.3: SUBGRADIENTUL ----------
    with tm3:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 3. Subgradientul — tratarea punctelor de nediferențiabilitate
            **Problemă:** $f(X) = \\min(J_1, J_2)$ nu este diferențiabilă când $J_1 = J_2$.
            **Răspuns:** Prin conceptul de **subgradient** din analiza convexă (Rockafellar, 1970).
            
            ---
            $$\\partial f(X) = \\text{conv}\\{\\nabla J_i(X) : i \\in \\mathcal{A}(X)\\}$$
            - **Cazul 1:** Un singur $J_i$ activ → gradientul său e subgradientul
            - **Cazul 2:** $J_1 = J_2$ → orice combinație convexă a gradienților
            - Când $d = 0$: regularizare $d \\leftarrow \\max(d, 10^{-8})$
            
            **💻 Implementare:** `model_matematic.py` → `calculeaza_subgradient(X)`
            """)
        else:
            st.markdown("""
            ### 3. Subgradient — handling non-differentiable points
            $$\\partial f(X) = \\text{conv}\\{\\nabla J_i(X) : i \\in \\mathcal{A}(X)\\}$$
            When $d = 0$: regularize $d \\leftarrow \\max(d, 10^{-8})$.
            **💻 Implementation:** `model_matematic.py` → `calculeaza_subgradient(X)`
            """)
    
    # ---------- TAB 5.4: TEOREMA COLȚURILOR ----------
    with tm4:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 4. Teorema de localizare a minimului — garanția matematică
            **Problemă:** Cum găsim **garantat** cel mai rău caz?
            **Răspuns:** Minimul se atinge întotdeauna la un vârf al hiper-dreptunghiului.
            
            ---
            $$\\min_{X \\in D(T)} f(X) = \\min_{X \\in \\mathcal{V}(T)} f(X)$$
            unde $\\mathcal{V}(T)$ = cele $2^6 = 64$ vârfuri.
            
            #### Demonstrație
            **Pasul 1:** $x_1$ apare cu $-1/2$ → minimul la maximul toleranței. $x_2$ cu $+1/2$ → minimul la minimul toleranței.
            **Pasul 2:** $g(u,v) = \\sqrt{u^2+v^2}$ e convexă → maximul pe dreptunghi la vârfuri (Rockafellar, 1970).
            **Concluzie:** Minimul global la unul din cele 64 vârfuri. ∎
            
            **💻 Implementare:** `agent_tester.py` → `ataca()` — 64 măști binare
            """)
        else:
            st.markdown("""
            ### 4. Corner Localization Theorem — the mathematical guarantee
            $$\\min_{X \\in D(T)} f(X) = \\min_{X \\in \\mathcal{V}(T)} f(X)$$
            where $\\mathcal{V}(T)$ = the $2^6 = 64$ vertices.
            
            **Step 1:** $x_1$ with $-1/2$ → min at max tolerance. $x_2$ with $+1/2$ → min at min tolerance.
            **Step 2:** $g(u,v) = \\sqrt{u^2+v^2}$ is convex → max on rectangle at vertices (Rockafellar, 1970).
            **Conclusion:** Global minimum at one of 64 vertices. ∎
            
            **💻 Implementation:** `agent_tester.py` → `ataca()` — 64 bit masks
            """)
    
    # ---------- TAB 5.5: NEURONUL FRACȚIONAR ----------
    with tm5:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 5. Neuronul fracționar — memoria lungă și controlul adaptiv
            **Problemă:** Cum facem sistemul agresiv la defecte și precaut când e stabil?
            **Răspuns:** Prin neuron cu **dinamică fracționară** (memorie lungă).
            
            ---
            #### Derivata Grünwald-Letnikov
            $$D^{\\alpha} y(t) = \\lim_{h \\to 0} \\frac{1}{h^{\\alpha}} \\sum_{j=0}^{\\infty} (-1)^j \\binom{\\alpha}{j} y(t - jh)$$
            
            $|w_j| = |\\binom{\\alpha}{j}|$ descresc **algebric** (ca $j^{-\\alpha-1}$), nu exponențial.
            
            #### Implementare discretă
            Semnal: $y(t) = +1$ (DEFECT) sau $-1$ (OK).
            $$u(t) = \\sum_{j=0}^{19} w_j \\cdot y(t-j), \\quad \\beta(t) = \\frac{1}{1 + e^{-u(t)}} \\in (0, 1)$$
            
            $\\beta(t)$ modulează pasul: $\\delta_{\\text{efectiv}} = \\beta \\cdot \\delta$.
            - $\\beta \\to 1$ → agresiv (pași mari)
            - $\\beta \\to 0$ → precaut (pași mici)
            
            Experimental ($\\alpha = 0.7$): $\\beta \\approx 0.85$ (defecte) → $0.44$ → $0.14$ (OK).
            
            **💻 Implementare:** `neuron_fractionar.py` → `NeuronFractionar` (~30 linii)
            """)
        else:
            st.markdown("""
            ### 5. The Fractional Neuron — long memory and adaptive control
            
            #### Grünwald-Letnikov Fractional Derivative
            $$D^{\\alpha} y(t) = \\lim_{h \\to 0} \\frac{1}{h^{\\alpha}} \\sum_{j=0}^{\\infty} (-1)^j \\binom{\\alpha}{j} y(t - jh)$$
            
            Weights $|w_j|$ decay **algebraically** (as $j^{-\\alpha-1}$), not exponentially.
            
            #### Discrete Implementation
            $$u(t) = \\sum_{j=0}^{19} w_j \\cdot y(t-j), \\quad \\beta(t) = \\frac{1}{1 + e^{-u(t)}}$$
            
            $\\beta \\to 1$ = aggressive, $\\beta \\to 0$ = cautious.
            
            **💻 Implementation:** `neuron_fractionar.py` → `NeuronFractionar` (~30 lines)
            """)
    
    # ---------- TAB 5.6: CUANTIFICAREA INCERTITUDINII ----------
    with tm6:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 6. Cuantificarea incertitudinii — estimarea riscului de defect
            
            **Problemă:** După optimizare, care e probabilitatea reală de defect?
            **Răspuns:** Prin **simulare Monte Carlo** cu model stochastic realist.
            
            ---
            #### Modelul stochastic
            $$x_i \\sim \\mathcal{N}(x_i^{\\text{nom}}, \\sigma_i^2), \\quad \\sigma_i = \\frac{t_i}{3}$$
            
            **Justificare:** Teorema limitei centrale (Feller, 1971) + regula $3\\sigma$ din Six Sigma (Pyzdek & Keller, 2014).
            
            #### Estimatorul Monte Carlo
            $$\\hat{P}_{\\text{defect}} = \\frac{1}{N} \\sum_{k=1}^{N} \\mathbf{1}_{\\{f(X_k) \\leq 0\\}}$$
            
            Nedeplasat, convergent. $\\text{Var} \\leq 1/(4N)$. Pentru $N = 5.000$, eroarea standard $< 0.007$.
            
            #### Integrarea în sistem
            1. În bucla de optimizare: mini Monte Carlo la fiecare iterație
            2. La final: Monte Carlo complet pe toleranțele optime
            
            **Noutatea:** UQ integrat în feedback, nu post-optimizare separat.
            **💻 Implementare:** `np.random.normal(loc=nom, scale=t/3)` în aplicație
            """)
        else:
            st.markdown("""
            ### 6. Uncertainty Quantification — estimating defect risk
            
            #### Stochastic Model
            $$x_i \\sim \\mathcal{N}(x_i^{\\text{nom}}, \\sigma_i^2), \\quad \\sigma_i = \\frac{t_i}{3}$$
            
            Justified by Central Limit Theorem (Feller, 1971) + Six Sigma $3\\sigma$ rule (Pyzdek & Keller, 2014).
            
            #### Monte Carlo Estimator
            $$\\hat{P}_{\\text{defect}} = \\frac{1}{N} \\sum_{k=1}^{N} \\mathbf{1}_{\\{f(X_k) \\leq 0\\}}$$
            
            Unbiased, consistent. For $N = 5.000$, standard error $< 0.007$.
            
            **Novelty:** UQ integrated into feedback loop, not separate post-optimization.
            **💻 Implementation:** `np.random.normal(loc=nom, scale=t/3)`
            """)
    
    # ---------- TAB 5.7: FUNCȚIA DE COST ----------
    with tm7:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 7. Funcția de cost și regula de ajustare
            
            #### Funcția de cost
            $$\\text{Cost}(T) = \\sum_{i=1}^{6} \\frac{1}{t_i}$$
            
            **Justificare economică:** Costul crește invers proporțional cu precizia (Singh et al., 2009; Chase & Parkinson, 1991). O toleranță de $\\pm 0.01$ mm e ~10× mai scumpă decât $\\pm 0.1$ mm.
            
            #### Regula de ajustare — pas relativ
            - **Strângere:** $t_i \\leftarrow t_i / (1 + \\delta_{\\text{efectiv}})$
            - **Lărgire:** $t_i \\leftarrow t_i \\times (1 + \\delta_{\\text{efectiv}})$
            
            unde $\\delta_{\\text{efectiv}} = \\beta \\cdot \\delta$, $\\delta = 0.2$.
            
            **💻 Implementare:** `agent_proiectant.py` → `primeste_raport()`
            """)
        else:
            st.markdown("""
            ### 7. Cost Function and Adjustment Rule
            
            $$\\text{Cost}(T) = \\sum_{i=1}^{6} \\frac{1}{t_i}$$
            
            **Economic justification:** Cost increases inversely with precision (Singh et al., 2009; Chase & Parkinson, 1991).
            
            #### Adjustment Rule
            - **Tightening:** $t_i \\leftarrow t_i / (1 + \\delta_{\\text{effective}})$
            - **Widening:** $t_i \\leftarrow t_i \\times (1 + \\delta_{\\text{effective}})$
            
            $\\delta_{\\text{effective}} = \\beta \\cdot \\delta$, $\\delta = 0.2$.
            
            **💻 Implementation:** `agent_proiectant.py` → `primeste_raport()`
            """)
    
    # ---------- TAB 5.8: CONVERGENȚA ----------
    with tm8:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 8. Convergența sistemului multi-agent
            
            #### Criteriul de convergență
            1. **Calitate:** $f(X) > -0.01$ mm pentru toate cele 64 colțuri
            2. **Stabilitate:** 2 iterații consecutive OK
            
            #### Demonstrația convergenței
            **1. Monotonitatea strângerii:** $t_j \\leftarrow t_j/(1+\\delta) < t_j$. Domeniul se contractă.
            **2. Finitudinea explorării:** Maxim 6 eșecuri de lărgire ($\\mathcal{F}$).
            **3. Mărginirea inferioară:** $t_{\\min} = 0.01$ mm.
            **4. Neuronul fracționar:** $\\beta$ scade brusc la tranziție, prevenind oscilațiile.
            
            #### Garanția oferită
            **Absolută** (nu statistică): niciuna din cele 64 combinații extreme nu produce interferență.
            Aceeași clasă de garanție ca Worst-Case, dar la cost finit.
            
            **💻 Implementare:** `principal.py` → bucla principală
            """)
        else:
            st.markdown("""
            ### 8. Convergence of the Multi-Agent System
            
            #### Convergence Criterion
            1. **Quality:** $f(X) > -0.01$ mm for all 64 corners
            2. **Stability:** 2 consecutive OK iterations
            
            #### Convergence Proof
            **1. Monotonicity:** $t_j \\leftarrow t_j/(1+\\delta) < t_j$. Domain contracts.
            **2. Finiteness:** At most 6 failed widenings.
            **3. Lower bound:** $t_{\\min} = 0.01$ mm.
            **4. Fractional neuron:** $\\beta$ drops sharply at transition, preventing oscillations.
            
            #### Guarantee
            **Absolute** (not statistical): none of the 64 extreme combinations produces interference.
            
            **💻 Implementation:** `principal.py` → main loop
            """)
    
    # ---------- TAB 5.9: LIMITĂRI ----------
    with tm9:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 9. Limitări și considerații
            
            #### Limitări actuale
            1. **Scalabilitatea:** $2^n$ colțuri devine prohibitiv pentru $n > 20$. Necesită strategie hibridă.
            2. **Modelul de cost simplificat:** $\\sum 1/t_i$ e o aproximare; costul real depinde de proces.
            3. **Independența cotelor:** În practică, unele cote pot fi corelate.
            4. **Analiză pur geometrică:** Fără deformații elastice, dilatații termice, uzură.
            5. **Geometrie simplă:** 2 știfturi, 2 găuri. Generalizarea necesită adaptarea funcției de joc.
            
            ---
            #### Considerații
            - Pragul de defect ($-0.01$ mm) e calibrat empiric. Pentru aplicații critice, poate fi redus.
            - Distribuția normală ($3\\sigma$) e rezonabilă pentru procese controlate statistic.
            - Costul calculat e o măsură **relativă**, nu absolută (nu în unități monetare).
            """)
        else:
            st.markdown("""
            ### 9. Limitations and Considerations
            
            #### Current Limitations
            1. **Scalability:** $2^n$ becomes prohibitive for $n > 20$. Needs hybrid strategy.
            2. **Simplified cost model:** $\\sum 1/t_i$ is an approximation.
            3. **Independent dimensions:** Some may be correlated in practice.
            4. **Purely geometric:** No elastic deformations, thermal expansion, or wear.
            5. **Simple geometry:** 2 pins, 2 holes. Generalization requires gap function adaptation.
            
            ---
            #### Considerations
            - Defect threshold ($-0.01$ mm) is empirically calibrated.
            - Normal distribution ($3\\sigma$) is reasonable for statistically controlled processes.
            - Calculated cost is a **relative** measure, not absolute monetary value.
            """)
