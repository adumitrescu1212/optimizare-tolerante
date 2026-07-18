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
        'wait': "Configurează parametrii și apasă **Rulează optimizarea**.",
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
        'cap_cost': "Costul crește pe măsură ce toleranțele sunt strânse. Mai mic = mai ieftin.",
        'cap_beta': "Beta ~0.85 = sistem alert. Beta ~0.15 = sistem stabil.",
        'cap_joc': "Jocul evoluează de la negativ (interferență) spre zero. Pozitiv = OK.",
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
        'wait': "Set parameters and press **Run Optimization**.",
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
        'cap_cost': "Cost increases as tolerances are tightened. Lower = cheaper.",
        'cap_beta': "Beta ~0.85 = system alert. Beta ~0.15 = system stable.",
        'cap_joc': "Gap evolves from negative (interference) towards zero. Positive = OK.",
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
    col1, col2, col3 = st.columns(3)
    if col1.button("RO", use_container_width=True):
        st.session_state.lang = 'ro'
    if col2.button("EN", use_container_width=True):
        st.session_state.lang = 'en'
    theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
    if col3.button(theme_icon, use_container_width=True):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
    
    st.divider()
    st.header(t['params'])
    
    alpha = st.slider(t['alpha'], 0.1, 1.0, 0.7, 0.1, help=t['alpha_help'])
    delta = st.slider(t['delta'], 0.05, 0.5, 0.2, 0.05, help=t['delta_help'])
    tol_init = st.slider(t['tol'], 0.1, 1.0, 0.5, 0.1, help=t['tol_help'])
    
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
    st.title("⚙️ " + ("Sistem Multi-Agent cu Neuron Fracționar" if st.session_state.lang == 'ro' else "Multi-Agent System with Fractional Neuron"))
    st.subheader("Optimizarea toleranțelor pentru ansambluri mecanice" if st.session_state.lang == 'ro' else "Tolerance optimization for mechanical assemblies")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🎯 " + ("Ce rezolvă acest proiect?" if st.session_state.lang == 'ro' else "What does this project solve?"))
        st.markdown("În fabricarea pieselor mecanice, dimensiunile nu ies niciodată perfect. Un știft proiectat la 10 mm va avea în realitate între 9.9 și 10.1 mm." if st.session_state.lang == 'ro' else "In manufacturing, dimensions are never perfect. A pin designed at 10 mm will actually be between 9.9 and 10.1 mm.")
        st.markdown("**" + ("Provocarea:" if st.session_state.lang == 'ro' else "The challenge:") + "** " + ("Găsirea celui mai ieftin set de toleranțe care garantează asamblarea corectă." if st.session_state.lang == 'ro' else "Finding the cheapest tolerance set that guarantees correct assembly."))
    with col2:
        st.info(("🚀 Mergi la tab-ul **📊 Optimizare**, setează parametrii și apasă **Rulează optimizarea**." if st.session_state.lang == 'ro' else "🚀 Go to the **📊 Optimization** tab, set parameters and press **Run Optimization**."))
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric(("Agenți software" if st.session_state.lang == 'ro' else "Software Agents"), "2")
    c2.metric(("Colțuri verificate" if st.session_state.lang == 'ro' else "Corners Checked"), "64")
    c3.metric(("Timp execuție" if st.session_state.lang == 'ro' else "Runtime"), "< 1s")

# ================================================================
# TAB 2: OPTIMIZARE
# ================================================================
with tab2:
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
        
        st.subheader(t['tol_header'])
        df_tol = pd.DataFrame({
            'Cotă' if st.session_state.lang == 'ro' else 'Dimension': t['cote'],
            'Val. nominală (mm)' if st.session_state.lang == 'ro' else 'Nominal (mm)': valori_nominale,
            'Toleranță optimă (±mm)' if st.session_state.lang == 'ro' else 'Optimal tol. (±mm)': np.round(proiectant.propune_tolerante(), 4),
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
            'Metoda' if st.session_state.lang == 'ro' else 'Method': ['Sistem Multi-Agent', 'Worst-Case', 'Monte Carlo'],
            'Cost': [f"{proiectant.calculeaza_cost():.2f}", "∞", "~180"],
            'Evaluări' if st.session_state.lang == 'ro' else 'Evaluations': [f"~{iteratii * 64:,}", "1", "10,000+"],
            'Garanție' if st.session_state.lang == 'ro' else 'Guarantee': ['Absolută', 'Absolută', 'Statistică'],
        })
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
        
        csv = pd.DataFrame(istoric).to_csv(index=False).encode('utf-8')
        st.download_button(t['export'], csv, 'istoric_optimizare.csv', 'text/csv')
        st.success(("👈 Mergi la tab-ul Grafice pentru vizualizări." if st.session_state.lang == 'ro' else "👈 Go to the Charts tab for visualizations."))
    else:
        st.info(t['wait'])

# ================================================================
# TAB 3: GRAFICE
# ================================================================
with tab3:
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
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(("### 🏗️ Cum funcționează" if st.session_state.lang == 'ro' else "### 🏗️ How it Works"))
        st.markdown(("**🔵 Agentul Proiectant** pornește cu toleranțe largi și le ajustează. **🔴 Agentul Tester** verifică 64 de colțuri. **🧠 Neuronul fracționar** controlează agresivitatea." if st.session_state.lang == 'ro' else "**🔵 Designer Agent** starts wide and adjusts. **🔴 Tester Agent** checks 64 corners. **🧠 Fractional Neuron** controls aggressiveness."))
    with c2:
        st.markdown(("### 📘 Ghid rapid" if st.session_state.lang == 'ro' else "### 📘 Quick Guide"))
        st.markdown(("1. Tab-ul Optimizare → setează parametrii\n2. Apasă Rulează\n3. Vezi rezultatele\n4. Tab-ul Grafice → vizualizări\n5. Exportă CSV" if st.session_state.lang == 'ro' else "1. Optimization tab → set parameters\n2. Press Run\n3. See results\n4. Charts tab → visualizations\n5. Export CSV"))

# ================================================================
# TAB 5: MATEMATICĂ
# ================================================================
with tab5:
    st.title("📐 " + ("Matematica" if st.session_state.lang == 'ro' else "Mathematics"))
    tm1, tm2, tm3, tm4 = st.tabs([
        ("Funcția de joc" if st.session_state.lang == 'ro' else "Gap Function"),
        ("Gradientul" if st.session_state.lang == 'ro' else "Gradient"),
        ("Minimul garantat" if st.session_state.lang == 'ro' else "Guaranteed Minimum"),
        ("Neuronul fracționar" if st.session_state.lang == 'ro' else "Fractional Neuron"),
    ])
    with tm1:
        st.markdown(("$$J = R_g - R_s - d$$\n\n$R_g$ = raza găurii, $R_s$ = raza știftului, $d$ = distanța dintre centre.\n\nExemplu: știft 10 mm, gaură 10.2 mm, centre aliniate → Joc = **0.1 mm** ✅" if st.session_state.lang == 'ro' else "$$J = R_g - R_s - d$$\n\n$R_g$ = hole radius, $R_s$ = pin radius, $d$ = center distance.\n\nExample: pin 10 mm, hole 10.2 mm, aligned → Gap = **0.1 mm** ✅"))
    with tm2:
        st.markdown(("Gradientul indică ce cotă influențează cel mai mult jocul. $-1/2$ = mărirea știftului reduce jocul. $+1/2$ = mărirea găurii crește jocul." if st.session_state.lang == 'ro' else "The gradient shows which dimension most affects the gap. $-1/2$ = larger pin reduces gap. $+1/2$ = larger hole increases gap."))
    with tm3:
        st.markdown(("Minimul funcției de joc se atinge întotdeauna la un colț al domeniului. Verificăm $2^6 = 64$ colțuri → garanție absolută." if st.session_state.lang == 'ro' else "The gap function minimum is always at a corner. We check $2^6 = 64$ corners → absolute guarantee."))
    with tm4:
        st.markdown(("Neuronul folosește derivata Grünwald-Letnikov pentru memorie lungă. $\\beta \\to 1$ = agresiv, $\\beta \\to 0$ = relaxat." if st.session_state.lang == 'ro' else "The neuron uses Grünwald-Letnikov derivative for long memory. $\\beta \\to 1$ = aggressive, $\\beta \\to 0$ = relaxed."))
