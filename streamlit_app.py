import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuration de la page pour mobile
st.set_page_config(page_title="Eliott Tracker", page_icon="🍼")

st.title("🍼 Suivi d'Eliott")

# Fichier de stockage des données (local ou base de données)
DATA_FILE = "suivi_eliott.csv"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Date", "Type", "Quantité (ml)", "Notes", "Par"])
    df.to_csv(DATA_FILE, index=False)

# --- FORMULAIRE DE SAISIE ---
with st.expander("➕ Enregistrer un événement", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        type_event = st.selectbox("Type", ["Biberon", "Pipi", "Caca", "Note"])
        
        quantite = 0
        if type_event == "Biberon":
            quantite = st.number_input("Quantité (ml)", min_value=0, step=10, value=150)
        
        note = st.text_input("Commentaire / Note")
        auteur = st.radio("Qui note ?", ["Papa", "Maman"], horizontal=True)
        
        submitted = st.form_submit_button("Enregistrer")
        
        if submitted:
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            new_data = pd.DataFrame([[now, type_event, quantite, note, auteur]], 
                                    columns=["Date", "Type", "Quantité (ml)", "Notes", "Par"])
            new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success("Enregistré !")

# --- HISTORIQUE ---
st.subheader("📊 Derniers événements")
df_display = pd.read_csv(DATA_FILE)
st.dataframe(df_display.tail(10), use_container_width=True)

# --- RÉCAPITULATIF DU JOUR ---
today = datetime.now().strftime("%d/%m/%Y")
total_bib = df_display[(df_display['Date'].str.contains(today)) & (df_display['Type'] == "Biberon")]['Quantité (ml)'].sum()

st.metric("Total Biberons aujourd'hui", f"{total_bib} ml")
