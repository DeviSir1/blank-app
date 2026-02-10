import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Eliott Tracker", page_icon="🍼")

st.title("🍼 Suivi d'Eliott")

DATA_FILE = "suivi_eliott.csv"
COLUMNS = ["Date", "Heure", "Type", "Quantité (ml)", "Poids (kg)", "Taille (cm)", "Notes", "Par"]

# Initialisation ou mise à jour du fichier CSV
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=COLUMNS)
    df.to_csv(DATA_FILE, index=False)
else:
    # Vérification que toutes les colonnes existent (sécurité anti-crash)
    df_check = pd.read_csv(DATA_FILE)
    for col in COLUMNS:
        if col not in df_check.columns:
            df_check[col] = 0
    df_check.to_csv(DATA_FILE, index=False)

# --- FORMULAIRE DE SAISIE ---
with st.expander("➕ Enregistrer un événement", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_ev = st.date_input("Date", datetime.now())
        with col2:
            heure_ev = st.time_input("Heure", datetime.now())
        
        type_event = st.selectbox("Type", ["Biberon", "Pipi", "Caca", "Poids/Taille", "Note"])
        
        quantite, poids, taille = 0, 0.0, 0.0
        
        if type_event == "Biberon":
            quantite = st.number_input("Quantité (ml)", min_value=0, step=10, value=150)
        elif type_event == "Poids/Taille":
            poids = st.number_input("Poids (kg)", min_value=0.0, step=0.01, format="%.2f")
            taille = st.number_input("Taille (cm)", min_value=0.0, step=0.5)
        
        note = st.text_input("Commentaire / Note")
        auteur = st.radio("Qui note ?", ["Papa", "Maman"], horizontal=True)
        
        if st.form_submit_button("Enregistrer"):
            new_entry = [date_ev.strftime("%d/%m/%Y"), heure_ev.strftime("%H:%M"), type_event, quantite, poids, taille, note, auteur]
            new_df = pd.DataFrame([new_entry], columns=COLUMNS)
            new_df.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.rerun() # Force le rafraîchissement des calculs

# --- AFFICHAGE ET CALCULS ---
df_display = pd.read_csv(DATA_FILE)

# On s'assure que les types sont corrects pour les calculs
df_display['Quantité (ml)'] = pd.to_numeric(df_display['Quantité (ml)'], errors='coerce').fillna(0)
df_display['Poids (kg)'] = pd.to_numeric(df_display['Poids (kg)'], errors='coerce').fillna(0)

# Métriques
today_str = datetime.now().strftime("%d/%m/%Y")
total_bib_today = df_display[(df_display['Date'] == today_str) & (df_display['Type'] == "Biberon")]['Quantité (ml)'].sum()

c1, c2 = st.columns(2)
c1.metric("Total Bib (Auj.)", f"{int(total_bib_today)} ml")

# Récupérer le dernier poids non nul
weights = df_display[df_display['Poids (kg)'] > 0]
if not weights.empty:
    c2.metric("Dernier Poids", f"{weights.iloc[-1]['Poids (kg)']} kg")

# Rappel +4h
bibs = df_display[df_display['Type'] == "Biberon"]
if not bibs.empty:
    last_time = datetime.strptime(bibs.iloc[-1]['Heure'], "%H:%M")
    next_bib = (last_time + timedelta(hours=4)).strftime("%H:%M")
    st.info(f"🔔 Prochain bib vers **{next_bib}**")

st.subheader("📊 Historique")
st.dataframe(df_display.tail(15), use_container_width=True)
