import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

# Config page
st.set_page_config(page_title="Eliott App", page_icon="🍼")

st.title("🍼 Eliott Tracker")

# Connexion stable au Google Sheet
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
except:
    st.error("Connexion au Google Sheet impossible. Vérifie tes 'Secrets' dans Streamlit Cloud.")
    st.stop()

# --- FORMULAIRE ---
with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    d = col1.date_input("Jour", datetime.now())
    t = col2.time_input("Heure", datetime.now())
    
    cat = st.selectbox("Quoi ?", ["Biberon", "Pipi", "Caca", "Poids", "Taille"])
    val = st.number_input("Valeur (ml ou kg)", value=0.0, step=0.1)
    txt = st.text_input("Note (ex: a tout bu)")
    qui = st.radio("Qui ?", ["Papa", "Maman"], horizontal=True)
    
    if st.form_submit_button("Enregistrer"):
        new_row = pd.DataFrame([{
            "Date": d.strftime("%d/%m/%Y"),
            "Heure": t.strftime("%H:%M"),
            "Type": cat,
            "Valeur": val,
            "Note": txt,
            "Par": qui
        }])
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(data=updated_df)
        st.success("C'est noté !")
        st.rerun()

# --- AFFICHAGE ---
if not df.empty:
    # Calcul du total lait aujourd'hui
    today = datetime.now().strftime("%d/%m/%Y")
    total_lait = df[(df['Date'] == today) & (df['Type'] == "Biberon")]['Valeur'].sum()
    
    st.metric("Lait aujourd'hui", f"{int(total_lait)} ml")
    
    # Historique
    st.write("### Historique")
    st.dataframe(df.tail(10), use_container_width=True)
