import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Eliott Tracker", page_icon="🍼")

st.title("🍼 Suivi d'Eliott")

DATA_FILE = "suivi_eliott.csv"
COLUMNS = ["Date", "Heure", "Type", "Quantité (ml)", "Poids (kg)", "Taille (cm)", "Notes", "Par"]

# 1. Initialisation robuste du fichier
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=COLUMNS)
    df.to_csv(DATA_FILE, index=False)
else:
    df_fix = pd.read_csv(DATA_FILE)
    # Si on a changé de version, on ajoute les colonnes manquantes
    for col in COLUMNS:
        if col not in df_fix.columns:
            df_fix[col] = 0.0
    df_fix.to_csv(DATA_FILE, index=False)

# --- FORMULAIRE ---
with st.expander("➕ Enregistrer un événement", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_ev = col1.date_input("Date", datetime.now())
        heure_ev = col2.time_input("Heure", datetime.now())
        
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
            pd.DataFrame([new_entry], columns=COLUMNS).to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.rerun()

# --- LECTURE ET AFFICHAGE ---
df_display = pd.read_csv(DATA_FILE)

if not df_display.empty:
    # Nettoyage des données pour éviter les erreurs de calcul
    df_display['Quantité (ml)'] = pd.to_numeric(df_display['Quantité (ml)'], errors='coerce').fillna(0)
    df_display['Poids (kg)'] = pd.to_numeric(df_display['Poids (kg)'], errors='coerce').fillna(0)

    # Métriques
    today = datetime.now().strftime("%d/%m/%Y")
    total_today = df_display[(df_display['Date'] == today) & (df_display['Type'] == "Biberon")]['Quantité (ml)'].sum()
    
    c1, c2 = st.columns(2)
    c1.metric("Total Bib (Auj.)", f"{int(total_today)} ml")
    
    # Dernier poids (sécurisé)
    weights = df_display[df_display['Poids (kg)'] > 0]
    if not weights.empty:
        c2.metric("Dernier Poids", f"{weights.iloc[-1]['Poids (kg)']} kg")

    # Rappel +4h (sécurisé)
    bibs = df_display[df_display['Type'] == "Biberon"]
    if not bibs.empty:
        try:
            last_time_str = str(bibs.iloc[-1]['Heure'])
            last_time = datetime.strptime(last_time_str, "%H:%M")
            next_bib = (last_time + timedelta(hours=4)).strftime("%H:%M")
            st.info(f"🔔 Prochain bib prévu vers **{next_bib}**")
        except:
            st.info("🔔 Prochain bib : Heure non valide")
            
    st.subheader("📊 Historique")
    st.dataframe(df_display.tail(10), use_container_width=True)
else:
    st.write("Aucune donnée enregistrée pour le moment.")
