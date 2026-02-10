import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Eliott Tracker", page_icon="🍼")

# Titre de l'app
st.title("🍼 Suivi d'Eliott")

DATA_FILE = "suivi_eliott.csv"
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Date", "Heure", "Type", "Quantité (ml)", "Notes", "Par"])
    df.to_csv(DATA_FILE, index=False)

# --- FORMULAIRE DE SAISIE ---
with st.expander("➕ Enregistrer un événement", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_ev = st.date_input("Date", datetime.now())
        with col2:
            # Ajout de la possibilité de mettre l'heure précise
            heure_ev = st.time_input("Heure", datetime.now())
        
        type_event = st.selectbox("Type", ["Biberon", "Pipi", "Caca", "Note"])
        
        quantite = 0
        if type_event == "Biberon":
            quantite = st.number_input("Quantité (ml)", min_value=0, step=10, value=150)
            st.info("💡 Un rappel sera programmé 4h après cette heure.")
        
        note = st.text_input("Commentaire / Note")
        auteur = st.radio("Qui note ?", ["Papa", "Maman"], horizontal=True)
        
        submitted = st.form_submit_button("Enregistrer")
        
        if submitted:
            date_str = date_ev.strftime("%d/%m/%Y")
            heure_str = heure_ev.strftime("%H:%M")
            
            new_data = pd.DataFrame([[date_str, heure_str, type_event, quantite, note, auteur]], 
                                    columns=["Date", "Heure", "Type", "Quantité (ml)", "Notes", "Par"])
            new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
            
            st.success(f"Enregistré à {heure_str} !")
            
            # Logique de rappel si c'est un biberon
            if type_event == "Biberon":
                # Calcul de l'heure du rappel (Heure du bib + 4h)
                full_datetime = datetime.combine(date_ev, heure_ev)
                rappel_time = (full_datetime + timedelta(hours=4)).strftime("%H:%M")
                st.warning(f"🔔 Prochain biberon prévu vers {rappel_time}")

# --- HISTORIQUE ---
st.subheader("📊 Derniers événements")
df_display = pd.read_csv(DATA_FILE)
st.dataframe(df_display.tail(10), use_container_width=True)

# --- RÉCAPITULATIF DU JOUR ---
today_str = datetime.now().strftime("%d/%m/%Y")
total_bib = df_display[(df_display['Date'] == today_str) & (df_display['Type'] == "Biberon")]['Quantité (ml)'].sum()
st.metric("Total Biberons aujourd'hui", f"{total_bib} ml")
