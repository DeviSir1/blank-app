import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Eliott App", page_icon="🍼")

# Connexion au Google Sheet (la base de données de l'app)
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🍼 Eliott Tracker")

# Lecture des données existantes
df = conn.read(ttl=0) # ttl=0 pour forcer la mise à jour immédiate

# --- FORMULAIRE D'ENREGISTREMENT ---
with st.expander("➕ Noter un événement", expanded=True):
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        date_ev = c1.date_input("Date", datetime.now())
        heure_ev = c2.time_input("Heure", datetime.now())
        
        type_ev = st.selectbox("Type", ["Biberon", "Pipi", "Caca", "Poids/Taille"])
        
        valeur = 0
        if type_ev == "Biberon":
            valeur = st.number_input("Quantité (ml)", step=10, value=150)
        elif type_ev == "Poids/Taille":
            valeur = st.number_input("Poids (kg)", step=0.01, format="%.2f")

        note = st.text_input("Note particulière")
        auteur = st.radio("Qui ?", ["Papa", "Maman"], horizontal=True)
        
        if st.form_submit_button("Valider"):
            # Préparation de la nouvelle ligne
            new_row = pd.DataFrame([{
                "Date": date_ev.strftime("%d/%m/%Y"),
                "Heure": heure_ev.strftime("%H:%M"),
                "Type": type_ev,
                "Quantite": valeur,
                "Notes": note,
                "Par": auteur
            }])
            
            # Ajout au tableau existant et mise à jour du Cloud
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("C'est enregistré !")
            st.rerun()

# --- AFFICHAGE DES SCORES ---
if not df.empty:
    today = datetime.now().strftime("%d/%m/%Y")
    # Calcul du total bu AUJOURD'HUI
    total_lait = df[(df['Date'] == today) & (df['Type'] == "Biberon")]['Quantite'].astype(float).sum()
    
    col_a, col_b = st.columns(2)
    col_a.metric("Bu aujourd'hui", f"{int(total_lait)} ml")
    
    # Rappel +4h
    bibs = df[df['Type'] == "Biberon"]
    if not bibs.empty:
        last_h = datetime.strptime(bibs.iloc[-1]['Heure'], "%H:%M")
        next_h = (last_h + timedelta(hours=4)).strftime("%H:%M")
        st.info(f"🔔 Prochain bib à prévoir vers **{next_h}**")

    st.subheader("📊 Historique partagé")
    st.dataframe(df.tail(10), use_container_width=True)
