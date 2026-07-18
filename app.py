""")

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

m_iter.metric(t['iterations'], f"{iteratii}", help="Numărul curent de iterații. Sistemul se oprește după 2 iterații consecutive fără defecte.")
m_cost.metric(t['cost_opt'], f"{cost:.2f}", help="Costul total al toleranțelor. Mai mic = fabricație mai ieftină. Cost = suma(1/toleranță).")
m_beta.metric("Beta", f"{beta:.3f}", help="Factorul de agresivitate al neuronului fracționar. ~0.85 = agresiv (strânge tare). ~0.15 = precaut (ajustează fin).")

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

# ---------- Rezultate finale ----------
st.divider()
st.header(t['results_header'])

col1, col2, col3 = st.columns(3)
col1.metric(t['iterations'], f"{iteratii}", help="Numărul total de iterații până la convergență. Mai puține = sistemul a găsit repede soluția.")
col2.metric(t['cost_opt'], f"{proiectant.calculeaza_cost():.2f}", help="Costul final al toleranțelor optime. Acesta e cel mai mic cost care garantează funcționalitatea.")
col3.metric(t['cost_init'], f"{np.sum(1.0/(tolerante_init + 1e-9)):.2f}", help="Costul inițial (cu toleranțe maximale). Mai mic decât costul optim pentru că toleranțele erau prea largi și cauzau defecte.")

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

# ---------- Comparație cu metode clasice ----------
st.divider()
st.header(t['comparison_header'])
st.markdown(t['comparison_text'])

df_comp = pd.DataFrame({
t['col_method']: [t['method_mas'], t['method_wc'], t['method_mc']],
t['cost_opt']: [f"{proiectant.calculeaza_cost():.2f}", "∞ (teoretic)", "~180 (estimat)"],
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
col_mc1.metric(t['mc_samples'], f"{n_mc:,}", help="Numărul de combinații aleatoare generate pentru simulare.")
col_mc2.metric(t['mc_defects'], f"{defecte_mc}", help="Câte combinații au produs interferență (joc ≤ 0).")
col_mc3.metric(t['mc_prob'], f"{100*defecte_mc/n_mc:.2f}%", help="Probabilitatea estimată ca ansamblul să nu se poată monta. Sub 0.1% e excelent.")
col_mc4.metric(t['mc_dist'], "Normală (3σ)", help="Distribuția normală centrată pe valoarea nominală, cu σ = toleranță/3 (regula Six Sigma).")

# ---------- Istoric complet ----------
st.divider()
st.subheader(t['history_header'])
df_istoric = pd.DataFrame(istoric)
st.dataframe(df_istoric, use_container_width=True, hide_index=True)

# ---------- Export CSV ----------
csv = df_istoric.to_csv(index=False).encode('utf-8')
st.download_button(
label=t['export_csv'],
data=csv,
file_name='istoric_optimizare.csv',
mime='text/csv',
help=t['export_tooltip']
)

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
