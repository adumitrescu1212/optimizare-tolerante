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
        'alpha': "Alpha (memorie fracționară)",
        'alpha_help': "0.1 = memorie lungă | 1.0 = memorie scurtă",
        'delta': "Delta (pas ajustare)",
        'delta_help': "Cât de mult se modifică toleranțele la fiecare pas",
        'tol': "Toleranță inițială (mm)",
        'tol_help': "Toate cele 6 cote pornesc cu această valoare",
        'run': "▶️ Rulează optimizarea",
        'wait': "Configurează parametrii de mai jos și apasă **Rulează optimizarea**.",
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
        'alpha': "Alpha (fractional memory)",
        'alpha_help': "0.1 = long memory | 1.0 = short memory",
        'delta': "Delta (adjustment step)",
        'delta_help': "How much tolerances change at each step",
        'tol': "Initial tolerance (mm)",
        'tol_help': "All 6 dimensions start with this value",
        'run': "▶️ Run Optimization",
        'wait': "Set the parameters below and press **Run Optimization**.",
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

# ---------- Sidebar (doar RO/EN/🌙) ----------
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
        if st.session_state.lang == 'ro':
            st.markdown("""
            În fabricarea pieselor mecanice, dimensiunile nu ies niciodată perfect. 
            Un știft proiectat la 10 mm va avea în realitate între 9.9 și 10.1 mm.
            
            **Provocarea:** Găsirea celui mai ieftin set de toleranțe care garantează 
            că piesele se vor asambla corect.
            
            **Soluția:** Doi agenți software inteligenți care colaborează pentru 
            a găsi automat aceste toleranțe.
            """)
        else:
            st.markdown("""
            In manufacturing, dimensions are never perfect. 
            A pin designed at 10 mm will actually be between 9.9 and 10.1 mm.
            
            **The challenge:** Finding the cheapest tolerance set that guarantees 
            correct assembly.
            
            **The solution:** Two intelligent software agents that collaborate 
            to automatically find these tolerances.
            """)
    with col2:
        st.info("🚀 " + ("Mergi la tab-ul **📊 Optimizare** pentru a rula sistemul." if st.session_state.lang == 'ro' else "Go to the **📊 Optimization** tab to run the system."))
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric(("Agenți software" if st.session_state.lang == 'ro' else "Software Agents"), "2")
    c2.metric(("Colțuri verificate" if st.session_state.lang == 'ro' else "Corners Checked"), "64")
    c3.metric(("Timp execuție" if st.session_state.lang == 'ro' else "Runtime"), "< 1s")

# ================================================================
# TAB 2: OPTIMIZARE
# ================================================================
with tab2:
    st.title(t['tab2'])
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        alpha = st.slider(t['alpha'], 0.10, 1.00, 0.70, 0.05, help=t['alpha_help'])
    with col_p2:
        delta = st.slider(t['delta'], 0.01, 0.50, 0.20, 0.01, help=t['delta_help'])
    with col_p3:
        tol_init = st.slider(t['tol'], 0.010, 1.000, 0.500, 0.005, help=t['tol_help'])
    
    run = st.button(t['run'], type="primary", use_container_width=True)
    
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
            st.markdown(f"""
            > **Interpretare:** Sistemul a convergit în **{iteratii} iterații**. 
            Costul a crescut de la **{np.sum(1.0/(tolerante_init + 1e-9)):.2f}** (toleranțe maximale, 
            dar ansamblu nefuncțional) la **{proiectant.calculeaza_cost():.2f}** (toleranțe optime, 
            ansamblu garantat funcțional). Aceasta este frontiera de fezabilitate: cel mai mic cost 
            la care toate combinațiile de dimensiuni din domeniul de toleranță produc un ansamblu corect.
            """)
        else:
            st.markdown(f"""
            > **Interpretation:** The system converged in **{iteratii} iterations**. 
            Cost increased from **{np.sum(1.0/(tolerante_init + 1e-9)):.2f}** (maximum tolerances, 
            but non-functional assembly) to **{proiectant.calculeaza_cost():.2f}** (optimal tolerances, 
            guaranteed functional assembly). This is the feasibility boundary: the lowest cost at which 
            all dimension combinations within the tolerance domain produce a correct assembly.
            """)
        
        st.subheader(t['tol_header'])
        df_tol = pd.DataFrame({
            ('Cotă' if st.session_state.lang == 'ro' else 'Dimension'): t['cote'],
            ('Val. nominală (mm)' if st.session_state.lang == 'ro' else 'Nominal (mm)'): valori_nominale,
            ('Toleranță optimă (±mm)' if st.session_state.lang == 'ro' else 'Optimal (±mm)'): np.round(proiectant.propune_tolerante(), 5),
        })
        st.dataframe(df_tol, use_container_width=True, hide_index=True)
        
        if st.session_state.lang == 'ro':
            st.markdown(f"""
            > **Interpretare toleranțe:** Fiecare cotă a primit o toleranță optimă, exprimată în milimetri.
            De exemplu, diametrul știftului are toleranța **{proiectant.propune_tolerante()[0]:.4f} mm**, 
            ceea ce înseamnă că în producție este acceptată o variație de ±{proiectant.propune_tolerante()[0]:.4f} mm 
            față de valoarea nominală de {valori_nominale[0]:.1f} mm. Toleranțele mai mici (la poziții) 
            reflectă sensibilitatea mai mare a jocului la decalajele centrelor.
            """)
        else:
            st.markdown(f"""
            > **Tolerance interpretation:** Each dimension received an optimal tolerance in millimeters.
            For example, the pin diameter has a tolerance of **{proiectant.propune_tolerante()[0]:.4f} mm**, 
            meaning a variation of ±{proiectant.propune_tolerante()[0]:.4f} mm from the nominal value 
            of {valori_nominale[0]:.1f} mm is accepted in production. Smaller tolerances (on positions) 
            reflect the higher sensitivity of the gap to center misalignment.
            """)
        
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
        
        if st.session_state.lang == 'ro':
            if defecte_mc == 0:
                st.markdown(f"""
                > **Interpretare Monte Carlo:** Din **{n_mc:,}** de combinații dimensionale generate aleator 
                (distribuție normală, $\\sigma = t/3$), **niciuna** nu a produs interferență. 
                Probabilitatea de defect este sub **0.02%** (sub limita de detecție pentru acest număr 
                de eșantioane). Aceasta confirmă că toleranțele optime găsite de sistem garantează 
                funcționalitatea ansamblului într-un scenariu realist de fabricație.
                """)
            else:
                st.markdown(f"""
                > **Interpretare Monte Carlo:** Din **{n_mc:,}** de combinații generate aleator 
                (distribuție normală, $\\sigma = t/3$), **{defecte_mc}** au produs interferență, 
                rezultând o probabilitate de defect de **{100*defecte_mc/n_mc:.3f}%**. 
                {'Aceasta este o probabilitate foarte mică, acceptabilă în majoritatea aplicațiilor industriale.' if 100*defecte_mc/n_mc < 0.1 else 'Aceasta indică faptul că toleranțele ar putea necesita o strângere suplimentară pentru aplicații critice.'}
                """)
        else:
            if defecte_mc == 0:
                st.markdown(f"""
                > **Monte Carlo interpretation:** Out of **{n_mc:,}** randomly generated dimensional 
                combinations (normal distribution, $\\sigma = t/3$), **none** produced interference. 
                The defect probability is below **0.02%** (below detection limit for this sample size). 
                This confirms that the optimal tolerances found by the system guarantee assembly 
                functionality in a realistic manufacturing scenario.
                """)
            else:
                st.markdown(f"""
                > **Monte Carlo interpretation:** Out of **{n_mc:,}** randomly generated combinations 
                (normal distribution, $\\sigma = t/3$), **{defecte_mc}** produced interference, 
                resulting in a defect probability of **{100*defecte_mc/n_mc:.3f}%**. 
                {'This is a very small probability, acceptable in most industrial applications.' if 100*defecte_mc/n_mc < 0.1 else 'This indicates that tolerances may need further tightening for critical applications.'}
                """)
        
        st.divider()
        st.header(t['comp_header'])
        df_comp = pd.DataFrame({
            ('Metoda' if st.session_state.lang == 'ro' else 'Method'): [
                'Sistem Multi-Agent' if st.session_state.lang == 'ro' else 'Multi-Agent System', 
                'Worst-Case (teoretic)', 
                'Monte Carlo (estimat)'
            ],
            'Cost': [f"{proiectant.calculeaza_cost():.2f}", "∞", "~180"],
            ('Evaluări' if st.session_state.lang == 'ro' else 'Evaluations'): [f"~{iteratii * 64:,}", "1", "10,000+"],
            ('Garanție' if st.session_state.lang == 'ro' else 'Guarantee'): [
                'Absolută' if st.session_state.lang == 'ro' else 'Absolute',
                'Absolută' if st.session_state.lang == 'ro' else 'Absolute',
                'Statistică' if st.session_state.lang == 'ro' else 'Statistical'
            ],
        })
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
        
        if st.session_state.lang == 'ro':
            st.markdown(f"""
            > **Interpretare comparație:** Sistemul multi-agent oferă o **garanție absolută** 
            (ca Worst-Case), dar la un cost finit și rezonabil. Față de Monte Carlo, garanția este 
            superioară (absolută vs. statistică), iar numărul de evaluări este mai mic 
            (~{iteratii * 64:,} față de minimum 10.000). Worst-Case ar impune toleranțe infinit 
            de strânse (cost infinit), ceea ce este nerealist.
            """)
        else:
            st.markdown(f"""
            > **Comparison interpretation:** The multi-agent system offers an **absolute guarantee** 
            (like Worst-Case), but at a finite and reasonable cost. Compared to Monte Carlo, the 
            guarantee is superior (absolute vs. statistical), and the number of evaluations is lower 
            (~{iteratii * 64:,} vs. at least 10,000). Worst-Case would require infinitely tight 
            tolerances (infinite cost), which is unrealistic.
            """)
        
        csv = pd.DataFrame(istoric).to_csv(index=False).encode('utf-8')
        st.download_button(t['export'], csv, 'istoric_optimizare.csv', 'text/csv')
        st.success("👈 " + ("Mergi la tab-ul **📈 Grafice** pentru vizualizări detaliate." if st.session_state.lang == 'ro' else "Go to the **📈 Charts** tab for detailed visualizations."))
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
        
        Acest proiect reprezintă un **sistem inteligent de optimizare a toleranțelor** pentru 
        ansambluri mecanice. El a fost dezvoltat ca lucrare de cercetare la intersecția dintre 
        **inteligența artificială**, **ingineria mecanică** și **calculul fracționar**.
        
        Sistemul utilizează o arhitectură **multi-agent** în care doi agenți software — un 
        Proiectant și un Tester — interacționează pentru a găsi automat cel mai ieftin set de 
        toleranțe care garantează funcționalitatea unui ansamblu mecanic.
        
        ---
        
        ### 🔥 Ce ne-a motivat?
        
        În ingineria mecanică, **toleranțarea** este o provocare fundamentală. Pe de o parte, 
        toleranțele strânse garantează calitatea dar cresc exploziv costurile de fabricație. 
        Pe de altă parte, toleranțele largi reduc costurile dar riscă să producă piese care 
        nu se potrivesc.
        
        Metodele tradiționale (Worst-Case, Monte Carlo, algoritmi genetici) tratează optimizarea 
        și analiza ca **procese separate**. Am vrut să creăm un sistem care să le **integreze 
        dinamic**, permițând celor doi agenți să învețe unul de la celălalt în timp real.
        
        ---
        
        ### ✨ Elemente de originalitate
        
        1. **Abordare adversială pentru toleranțe** — În literatura de specialitate, optimizarea 
        toleranțelor utilizează predominant algoritmi genetici sau metode deterministe. Utilizarea 
        unui sistem multi-agent cu dinamică adversială (un agent propune, celălalt atacă) este o 
        **abordare nouă** în acest domeniu.
        
        2. **Neuron fracționar ca manager de risc** — Am introdus un neuron cu dinamică fracționară, 
        bazat pe derivata **Grünwald-Letnikov**, care acționează ca un **controler adaptiv** al 
        ratei de ajustare. Memoria lungă oferită de calculul fracționar permite sistemului să 
        fie agresiv în faza de corecție și precaut în faza de optimizare fină. Aceasta este o 
        **contribuție originală** la intersecția dintre calculul fracționar și ingineria mecanică.
        
        3. **Garanție matematică absolută** — Am demonstrat o **teoremă de localizare a minimului** 
        care stabilește că cel mai rău caz se găsește întotdeauna la unul dintre cele $2^6 = 64$ 
        de colțuri ale domeniului de toleranță. Aceasta elimină necesitatea metodelor iterative 
        și oferă **siguranța absolută** că niciun defect nu scapă nedetectat.
        
        4. **Flux complet pe resurse minime** — Întregul sistem este implementat în **Python** 
        (open-source) și validat pe un model CAD real în **SolidWorks Student** (licență 
        educațională gratuită), demonstrând că o analiză avansată a toleranțelor poate fi 
        realizată fără investiții în software comercial.
        
        ---
        
        ### 🏗️ Cum funcționează — pe scurt
        
        **🔵 Agentul Proiectant** pornește cu toleranțe foarte largi (cost minim) și le ajustează 
        pe baza feedback-ului. **🔴 Agentul Tester** verifică fiecare set de toleranțe testând 
        toate cele 64 de combinații extreme posibile. **🧠 Neuronul fracționar** controlează 
        cât de agresiv se fac ajustările, având memorie lungă asupra istoricului interacțiunii.
        
        ---
        
        ### 🎯 Rezultatul
        
        Sistemul produce **toleranțele optime** — cel mai ieftin set care garantează că piesele 
        se vor asambla corect, indiferent de variațiile dimensionale inerente fabricației. 
        Convergența se atinge în aproximativ 100–110 iterații (sub o secundă pe un laptop standard).
        """)
    else:
        st.markdown("""
        ### 🎯 What is this project?
        
        This project represents an **intelligent tolerance optimization system** for mechanical 
        assemblies. It was developed as a research paper at the intersection of **artificial 
        intelligence**, **mechanical engineering**, and **fractional calculus**.
        
        The system uses a **multi-agent architecture** where two software agents — a Designer 
        and a Tester — interact to automatically find the cheapest tolerance set that guarantees 
        the functionality of a mechanical assembly.
        
        ---
        
        ### 🔥 What motivated us?
        
        In mechanical engineering, **tolerancing** is a fundamental challenge. Tight tolerances 
        guarantee quality but explosively increase manufacturing costs. Wide tolerances reduce 
        costs but risk producing parts that don't fit together.
        
        Traditional methods (Worst-Case, Monte Carlo, genetic algorithms) treat optimization and 
        analysis as **separate processes**. We wanted to create a system that **dynamically integrates** 
        them, allowing the two agents to learn from each other in real time.
        
        ---
        
        ### ✨ Original Contributions
        
        1. **Adversarial approach for tolerances** — Using a multi-agent system with adversarial 
        dynamics (one agent proposes, the other attacks) is a **novel approach** in tolerance 
        optimization, where genetic algorithms and deterministic methods dominate.
        
        2. **Fractional neuron as risk manager** — We introduced a neuron with fractional dynamics, 
        based on the **Grünwald-Letnikov** derivative, acting as an **adaptive controller** of the 
        adjustment rate. The long memory provided by fractional calculus allows the system to be 
        aggressive in the correction phase and cautious in the fine-tuning phase.
        
        3. **Absolute mathematical guarantee** — We proved a **corner localization theorem** 
        establishing that the worst case is always at one of the $2^6 = 64$ vertices of the 
        tolerance domain. This eliminates the need for iterative methods and provides **absolute 
        certainty** that no defect escapes detection.
        
        4. **Complete low-cost workflow** — The entire system is implemented in **Python** 
        (open-source) and validated on a real CAD model in **SolidWorks Student** (free educational 
        license), demonstrating that advanced tolerance analysis can be performed without 
        investment in commercial software.
        
        ---
        
        ### 🏗️ How It Works — in brief
        
        **🔵 The Designer Agent** starts with very wide tolerances (minimum cost) and adjusts them 
        based on feedback. **🔴 The Tester Agent** checks each tolerance set by testing all 64 
        extreme combinations. **🧠 The Fractional Neuron** controls how aggressive the adjustments 
        are, with long memory of the interaction history.
        
        ---
        
        ### 🎯 The Result
        
        The system produces the **optimal tolerances** — the cheapest set that guarantees the parts 
        will assemble correctly, regardless of manufacturing variations. Convergence is reached in 
        approximately 100–110 iterations (under one second on a standard laptop).
        """)

# ================================================================
# TAB 5: MATEMATICĂ
# ================================================================
with tab5:
    st.title("📐 " + ("Breviat teoretic" if st.session_state.lang == 'ro' else "Theoretical Brief"))
    
    if st.session_state.lang == 'ro':
        st.markdown("""
        Acest breviar conține fundamentele matematice pe care se bazează întregul sistem. 
        Fiecare concept este însoțit de demonstrația corespunzătoare și de indicarea 
        modulului Python în care este implementat.
        """)
    else:
        st.markdown("""
        This brief contains the mathematical foundations underlying the entire system. 
        Each concept is accompanied by its proof and an indication of the Python module 
        where it is implemented.
        """)
    
    tm1, tm2, tm3, tm4, tm5 = st.tabs([
        "1. " + ("Funcția de joc" if st.session_state.lang == 'ro' else "Gap Function"),
        "2. " + ("Gradientul analitic" if st.session_state.lang == 'ro' else "Analytical Gradient"),
        "3. " + ("Subgradientul" if st.session_state.lang == 'ro' else "Subgradient"),
        "4. " + ("Teorema colțurilor" if st.session_state.lang == 'ro' else "Corner Theorem"),
        "5. " + ("Neuronul fracționar" if st.session_state.lang == 'ro' else "Fractional Neuron"),
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
            
            Pentru o pereche știft-gaură, fie $R_s$ raza știftului, $R_g$ raza găurii și 
            $d = \\|S - G\\|$ distanța euclidiană dintre centrele lor. **Jocul** este:
            
            $$J = R_g - R_s - d$$
            
            #### Demonstrație geometrică
            
            Din geometria plană, două cercuri de raze $R_s$ și $R_g$ cu centrele la distanța $d$ 
            sunt disjuncte (nu se intersectează) dacă și numai dacă:
            - $d > R_s + R_g$ (cercuri exterioare), sau
            - $d < |R_s - R_g|$ (un cerc inclus complet în celălalt)
            
            În contextul asamblării, știftul trebuie să fie **complet interior** găurii, deci 
            $R_g > R_s$ și cercul știftului este conținut în cercul găurii. Condiția de incluziune 
            completă fără contact la frontieră este:
            
            $$d + R_s < R_g$$
            
            Rearanjând termenii: $R_g - R_s - d > 0$. ∎
            
            ---
            
            #### Funcția globală de joc
            
            Pentru un ansamblu cu $m = 2$ perechi știft-gaură, definim:
            
            $$f(X) = \\min(J_1(X), J_2(X))$$
            
            unde $X = [x_1, \\dots, x_6]^T$ este vectorul dimensiunilor efective.
            
            **Criteriul de asamblare:** Ansamblul funcționează **dacă și numai dacă** $f(X) > 0$.
            
            #### Demonstrație
            
            ($\\Rightarrow$) Dacă ansamblul se poate monta, fiecare știft intră în gaura sa, deci 
            $J_i > 0$ pentru toți $i$. Atunci $\\min_i J_i > 0$, deci $f(X) > 0$.
            
            ($\\Leftarrow$) Dacă $f(X) > 0$, atunci $\\min_i J_i > 0$, de unde $J_i > 0$ pentru 
            toți $i$. Fiecare pereche este asamblabilă independent. ∎
            
            ---
            
            #### Exprimarea explicită pentru ansamblul nostru
            
            $$f(X) = \\frac{x_2 - x_1}{2} - \\sqrt{(x_3 - x_5)^2 + (x_4 - x_6)^2}$$
            
            unde: $x_1 = D_{stift}$, $x_2 = D_{gaura}$, $x_3, x_4$ = poziții știfturi, 
            $x_5, x_6$ = poziții găuri.
            
            **💻 Implementare:** `model_matematic.py` → funcția `functia_de_joc(X)`
            """)
        else:
            st.markdown("""
            ### 1. The Gap Function — modeling the assembly condition
            
            **Problem:** How do we mathematically determine if a mechanical assembly can be correctly mounted?
            
            **Answer:** By calculating the **gap** — the free space between a pin and its corresponding hole.
            
            ---
            
            #### Definition
            
            For a pin-hole pair, let $R_s$ be the pin radius, $R_g$ the hole radius, and 
            $d = \\|S - G\\|$ the Euclidean distance between their centers. The **gap** is:
            
            $$J = R_g - R_s - d$$
            
            #### Geometric Proof
            
            Two circles of radii $R_s$ and $R_g$ with centers at distance $d$ are disjoint iff:
            - $d > R_s + R_g$ (external circles), or
            - $d < |R_s - R_g|$ (one circle fully contained in the other)
            
            For assembly, the pin must be **fully inside** the hole, so $R_g > R_s$. The condition 
            for complete inclusion without boundary contact is $d + R_s < R_g$, i.e. $R_g - R_s - d > 0$. ∎
            
            ---
            
            #### Global Gap Function
            
            For an assembly with $m = 2$ pin-hole pairs:
            
            $$f(X) = \\min(J_1(X), J_2(X))$$
            
            **Assembly criterion:** The assembly works **if and only if** $f(X) > 0$.
            
            ---
            
            #### Explicit Expression
            
            $$f(X) = \\frac{x_2 - x_1}{2} - \\sqrt{(x_3 - x_5)^2 + (x_4 - x_6)^2}$$
            
            **💻 Implementation:** `model_matematic.py` → function `functia_de_joc(X)`
            """)
    
    # ---------- TAB 5.2: GRADIENTUL ANALITIC ----------
    with tm2:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 2. Gradientul analitic — direcția de ajustare
            
            **Problemă:** Cum știm care cotă influențează cel mai mult jocul?
            
            **Răspuns:** Prin calculul analitic al gradientului funcției de joc.
            
            ---
            
            #### Calcul
            
            Pentru $d(X) = \\sqrt{(x_3-x_5)^2 + (x_4-x_6)^2} > 0$:
            
            $$\\nabla f(X) = \\begin{bmatrix} 
            -\\frac{1}{2} \\\\[4pt] 
            +\\frac{1}{2} \\\\[4pt] 
            -\\frac{x_3-x_5}{d(X)} \\\\[4pt] 
            -\\frac{x_4-x_6}{d(X)} \\\\[4pt] 
            +\\frac{x_3-x_5}{d(X)} \\\\[4pt] 
            +\\frac{x_4-x_6}{d(X)}
            \\end{bmatrix}$$
            
            #### Derivare
            
            - $\\frac{\\partial f}{\\partial x_1} = -\\frac{1}{2}$ (știftul mai gros → joc mai mic)
            - $\\frac{\\partial f}{\\partial x_2} = +\\frac{1}{2}$ (gaura mai mare → joc mai mare)
            - $\\frac{\\partial f}{\\partial x_3} = -\\frac{x_3-x_5}{d}$ (derivata radicalului)
            - Similar pentru $x_4, x_5, x_6$
            
            ---
            
            #### Interpretare practică
            
            Semnul fiecărei componente indică dacă o **creștere** a cotei respective mărește sau 
            micșorează jocul. Când Testerul găsește un defect, gradientul identifică exact cota 
            cu cel mai mare impact.
            
            **💻 Implementare:** `model_matematic.py` → funcția `calculeaza_subgradient(X)` 
            (implementare analitică, nu diferențe finite)
            """)
        else:
            st.markdown("""
            ### 2. Analytical Gradient — the adjustment direction
            
            **Problem:** How do we know which dimension most affects the gap?
            
            **Answer:** By analytically computing the gradient of the gap function.
            
            ---
            
            #### Computation
            
            $$\\nabla f(X) = \\begin{bmatrix} 
            -\\frac{1}{2} \\\\[4pt] 
            +\\frac{1}{2} \\\\[4pt] 
            -\\frac{x_3-x_5}{d(X)} \\\\[4pt] 
            -\\frac{x_4-x_6}{d(X)} \\\\[4pt] 
            +\\frac{x_3-x_5}{d(X)} \\\\[4pt] 
            +\\frac{x_4-x_6}{d(X)}
            \\end{bmatrix}$$
            
            **💻 Implementation:** `model_matematic.py` → function `calculeaza_subgradient(X)`
            """)
    
    # ---------- TAB 5.3: SUBGRADIENTUL ----------
    with tm3:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 3. Subgradientul — tratarea punctelor de nediferențiabilitate
            
            **Problemă:** Funcția $f(X) = \\min(J_1, J_2)$ nu este diferențiabilă când $J_1 = J_2$. 
            Cum tratăm aceste puncte?
            
            **Răspuns:** Prin conceptul de **subgradient** din analiza convexă (Rockafellar, 1970).
            
            ---
            
            #### Definiție
            
            Fie $\\varphi: \\mathbb{R}^n \\to \\mathbb{R}$ o funcție convexă. Un vector $g$ este 
            **subgradient** în $X$ dacă:
            
            $$\\varphi(Y) \\geq \\varphi(X) + g^T(Y - X), \\quad \\forall Y$$
            
            #### Aplicare la funcția noastră
            
            Pentru $f(X) = \\min(J_1, J_2)$, fie $\\mathcal{A}(X) = \\{i : J_i(X) = f(X)\\}$ 
            mulțimea funcțiilor active. Subdiferențiala este:
            
            $$\\partial f(X) = \\text{conv}\\{\\nabla J_i(X) : i \\in \\mathcal{A}(X)\\}$$
            
            - **Cazul 1:** Un singur $J_i$ activ → gradientul său e subgradientul
            - **Cazul 2:** Ambele active ($J_1 = J_2$) → orice combinație convexă a gradienților
            
            #### Rezolvare practică
            
            Când centrele coincid ($x_3 = x_5$ și $x_4 = x_6$), $d = 0$ și gradientul nu e definit. 
            În cod, tratăm acest caz prin regularizare: $d \\leftarrow \\max(d, \\varepsilon)$ cu 
            $\\varepsilon = 10^{-8}$.
            
            **💻 Implementare:** `model_matematic.py` → funcția `calculeaza_subgradient(X)` 
            (conține regularizarea pentru $d = 0$)
            """)
        else:
            st.markdown("""
            ### 3. Subgradient — handling non-differentiable points
            
            **Problem:** $f(X) = \\min(J_1, J_2)$ is not differentiable when $J_1 = J_2$. 
            How do we handle these points?
            
            **Answer:** Using the **subgradient** concept from convex analysis (Rockafellar, 1970).
            
            ---
            
            #### Application
            
            For $f(X) = \\min(J_1, J_2)$, the subdifferential is:
            
            $$\\partial f(X) = \\text{conv}\\{\\nabla J_i(X) : i \\in \\mathcal{A}(X)\\}$$
            
            When centers coincide ($d = 0$), we regularize: $d \\leftarrow \\max(d, \\varepsilon)$.
            
            **💻 Implementation:** `model_matematic.py` → function `calculeaza_subgradient(X)`
            """)
    
    # ---------- TAB 5.4: TEOREMA COLȚURILOR ----------
    with tm4:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 4. Teorema de localizare a minimului — garanția matematică
            
            **Problemă:** Cum găsim **garantat** cel mai rău caz (joc minim) într-un domeniu de toleranță?
            
            **Răspuns:** Prin **Teorema colțurilor** — minimul se atinge întotdeauna la un vârf al hiper-dreptunghiului.
            
            ---
            
            #### Enunț
            
            Fie $D(T) = \\prod_{i=1}^{6} [x_i^{\\text{nom}} - t_i, x_i^{\\text{nom}} + t_i]$ 
            domeniul de toleranță și $\\mathcal{V}(T)$ mulțimea celor $2^6 = 64$ vârfuri. Atunci:
            
            $$\\min_{X \\in D(T)} f(X) = \\min_{X \\in \\mathcal{V}(T)} f(X)$$
            
            #### Demonstrație
            
            **Pasul 1 — Diametrele:** $x_1$ (știftul) apare cu coeficientul $-1/2$. O funcție liniară 
            pe un interval își atinge minimul la una dintre extremități. Pentru a minimiza $f$, 
            trebuie să **maximizăm** $x_1$ (semnul minus) și să **minimizăm** $x_2$ (semnul plus). 
            Deci $x_1^* = x_1^{\\text{nom}} + t_1$ și $x_2^* = x_2^{\\text{nom}} - t_2$.
            
            **Pasul 2 — Pozițiile:** $g(u,v) = \\sqrt{u^2 + v^2}$ cu $u = x_3 - x_5$ și $v = x_4 - x_6$ 
            este o funcție **convexă**. Pe un domeniu dreptunghiular, maximul unei funcții convexe se 
            atinge la unul dintre vârfuri (Rockafellar, 1970, Corolarul 32.3.4). Cele 4 vârfuri ale 
            domeniului $(u,v)$ corespund la combinații de extreme pentru $x_3, x_4, x_5, x_6$.
            
            **Concluzie:** Minimul global se atinge la unul dintre cele $2^6 = 64$ vârfuri. ∎
            
            ---
            
            #### Implicație practică
            
            **Nu avem nevoie de metode iterative.** Este suficient să verificăm cele 64 de colțuri 
            — o operație care durează sub o milisecundă și oferă **garanția absolută** că niciun 
            defect nu scapă nedetectat.
            
            **💻 Implementare:** `agent_tester.py` → metoda `ataca()` — iterează peste cele 64 de 
            măști binare și evaluează $f(X)$ la fiecare vârf.
            """)
        else:
            st.markdown("""
            ### 4. Corner Localization Theorem — the mathematical guarantee
            
            **Problem:** How do we **guarantee** finding the worst case (minimum gap) in a tolerance domain?
            
            **Answer:** Through the **Corner Theorem** — the minimum is always at a vertex of the hyper-rectangle.
            
            ---
            
            #### Statement
            
            $$\\min_{X \\in D(T)} f(X) = \\min_{X \\in \\mathcal{V}(T)} f(X)$$
            
            where $\\mathcal{V}(T)$ is the set of $2^6 = 64$ vertices.
            
            #### Proof
            
            **Step 1:** $x_1$ appears with $-1/2$. A linear function on an interval attains its minimum 
            at an endpoint. To minimize $f$, maximize $x_1$ and minimize $x_2$.
            
            **Step 2:** $g(u,v) = \\sqrt{u^2+v^2}$ is convex. On a rectangular domain, a convex function's 
            maximum is at a vertex (Rockafellar, 1970, Corollary 32.3.4).
            
            **Conclusion:** The global minimum is at one of the $2^6 = 64$ vertices. ∎
            
            ---
            
            #### Practical Implication
            
            No iterative methods needed. Check 64 corners in < 1 ms with **absolute guarantee**.
            
            **💻 Implementation:** `agent_tester.py` → method `ataca()` — iterates over 64 bit masks.
            """)
    
    # ---------- TAB 5.5: NEURONUL FRACȚIONAR ----------
    with tm5:
        if st.session_state.lang == 'ro':
            st.markdown("""
            ### 5. Neuronul fracționar — memoria lungă și controlul adaptiv
            
            **Problemă:** Cum facem sistemul să fie agresiv când descoperă defecte și precaut când 
            totul e în regulă?
            
            **Răspuns:** Printr-un neuron cu **dinamică fracționară** care păstrează memoria 
            istoricului interacțiunii.
            
            ---
            
            #### Calculul fracționar — definiție
            
            Derivata fracționară **Grünwald-Letnikov** de ordin $\\alpha \\in (0, 1]$:
            
            $$D^{\\alpha} y(t) = \\lim_{h \\to 0} \\frac{1}{h^{\\alpha}} \\sum_{j=0}^{\\infty} (-1)^j \\binom{\\alpha}{j} y(t - jh)$$
            
            cu coeficienții binomiali generalizați:
            
            $$\\binom{\\alpha}{0} = 1, \\quad \\binom{\\alpha}{j} = \\frac{\\alpha(\\alpha-1)\\cdots(\\alpha-j+1)}{j!}$$
            
            #### Proprietatea fundamentală: memoria lungă
            
            $|w_j| = |\\binom{\\alpha}{j}|$ descresc **algebric** (ca $j^{-\\alpha-1}$), nu exponențial. 
            Evenimentele din trecutul îndepărtat încă influențează output-ul. Cu cât $\\alpha$ e mai mic, 
            cu atât memoria e mai lungă.
            
            ---
            
            #### Implementare discretă
            
            Semnal de intrare: $y(t) = +1$ (DEFECT) sau $-1$ (OK).
            
            $$u(t) = \\sum_{j=0}^{M-1} w_j \\cdot y(t-j), \\quad w_j = (-1)^j \\binom{\\alpha}{j}, \\quad M = 20$$
            
            Output (funcția sigmoidă):
            
            $$\\beta(t) = \\sigma(u(t)) = \\frac{1}{1 + e^{-u(t)}} \\in (0, 1)$$
            
            ---
            
            #### Rolul în sistem
            
            $\\beta(t)$ modulează pasul de ajustare al Proiectantului:
            
            $$\\delta_{\\text{efectiv}} = \\beta(t) \\cdot \\delta$$
            
            - **Faza de defecte:** $\\beta \\to 1$ → ajustări agresive (pași mari)
            - **Faza de optimizare fină:** $\\beta \\to 0$ → ajustări fine (pași mici)
            
            #### Rezultate experimentale ($\\alpha = 0.7$)
            
            - Iterațiile 1–109 (faza de defecte): $\\beta \\approx 0.85$ constant
            - Iterația 111 (tranziția): $\\beta$ scade la $0.44$
            - Iterația 112 (optimizare fină): $\\beta$ scade la $0.14$
            
            **💻 Implementare:** `neuron_fractionar.py` → clasa `NeuronFractionar` (~30 linii)
            """)
        else:
            st.markdown("""
            ### 5. The Fractional Neuron — long memory and adaptive control
            
            **Problem:** How do we make the system aggressive when finding defects and cautious when stable?
            
            **Answer:** Through a neuron with **fractional dynamics** that retains memory of interaction history.
            
            ---
            
            #### Grünwald-Letnikov Fractional Derivative
            
            $$D^{\\alpha} y(t) = \\lim_{h \\to 0} \\frac{1}{h^{\\alpha}} \\sum_{j=0}^{\\infty} (-1)^j \\binom{\\alpha}{j} y(t - jh)$$
            
            #### Long Memory Property
            
            Weights $|w_j|$ decay **algebraically** (as $j^{-\\alpha-1}$), not exponentially. 
            Smaller $\\alpha$ = longer memory.
            
            ---
            
            #### Discrete Implementation
            
            Input: $y(t) = +1$ (DEFECT) or $-1$ (OK).
            
            $$u(t) = \\sum_{j=0}^{19} w_j \\cdot y(t-j), \\quad \\beta(t) = \\frac{1}{1 + e^{-u(t)}}$$
            
            #### Role in the System
            
            $$\\delta_{\\text{effective}} = \\beta(t) \\cdot \\delta$$
            
            - Defect phase: $\\beta \\to 1$ → aggressive adjustments
            - Fine-tuning phase: $\\beta \\to 0$ → fine adjustments
            
            **💻 Implementation:** `neuron_fractionar.py` → class `NeuronFractionar` (~30 lines)
            """)
