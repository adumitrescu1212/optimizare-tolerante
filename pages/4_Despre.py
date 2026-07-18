import streamlit as st

st.title("📖 Despre proiect")

tab1, tab2 = st.tabs(["🏗️ Cum funcționează", "📘 Ghid de utilizare"])

with tab1:
    st.markdown("""
    ### 🏗️ Cum funcționează sistemul

    **🔵 Agentul Proiectant** pornește cu toleranțe foarte largi (cost minim) și le ajustează pe baza feedback-ului. Când Testerul găsește un defect, strânge toleranța la cota respectivă. Când totul e în regulă, încearcă să lărgească toleranțele.

    **🔴 Agentul Tester** verifică fiecare set de toleranțe. Folosește o metodă matematică exactă: testează toate cele 64 de combinații extreme posibile. Dacă găsește interferență, raportează DEFECT și indică cota vinovată.

    **🧠 Neuronul fracționar** are memorie lungă. Când sunt multe defecte, e "stresat" (Beta ~0.85) și ajustările sunt agresive. Când sistemul se stabilizează, se relaxează (Beta ~0.15) și ajustările devin fine.

    **📐 Modelul matematic** calculează jocul pe baza geometriei reale a ansamblului proiectat în SolidWorks.
    """)

with tab2:
    st.markdown("""
    ### 📘 Ghid de utilizare

    1. **Pagina Optimizare** — Setează parametrii:
        - **Alpha** — memoria neuronului (0.1 = lungă, 1.0 = scurtă)
        - **Delta** — cât de mult se modifică toleranțele la fiecare pas
        - **Toleranță inițială** — valoarea de pornire
    2. Apasă **Rulează optimizarea**
    3. Vezi rezultatele: toleranțe optime, Monte Carlo, comparații
    4. **Pagina Grafice** — Vizualizează evoluția costului, Beta și jocului
    5. **Exportă** rezultatele ca CSV
    
    **Interpretare:**
    - **Cost** — mai mic = fabricație mai ieftină
    - **Beta** — ~0.85 = agresiv, ~0.15 = relaxat
    - **Joc** — negativ = interferență, pozitiv = OK
    - **Probabilitate de defect** — sub 0.1% e excelent
    """)
