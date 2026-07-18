import streamlit as st
import pandas as pd

st.title("📈 Grafice")

if 'istoric' not in st.session_state or st.session_state['istoric'] is None:
    st.warning("⚠️ Rulează mai întâi optimizarea din pagina **Optimizare**.")
else:
    df = pd.DataFrame(st.session_state['istoric'])
    
    st.subheader("📋 Istoricul complet al iterațiilor")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["Evoluția costului", "Dinamica Beta", "Evoluția jocului minim"])
    
    with tab1:
        st.line_chart(df, x='Iterație', y='Cost', height=350)
        st.caption("Costul crește pe măsură ce toleranțele sunt strânse. Un cost mai mic = fabricație mai ieftină.")
    
    with tab2:
        st.line_chart(df, x='Iterație', y='Beta', height=350)
        st.caption("Beta ~0.85 = sistem alert (strânge agresiv). Beta ~0.15 = sistem stabil (ajustări fine).")
    
    with tab3:
        st.line_chart(df, x='Iterație', y='Joc (mm)', height=350)
        st.caption("Jocul evoluează de la negativ (interferență) spre zero. Pozitiv = ansamblul funcționează.")
