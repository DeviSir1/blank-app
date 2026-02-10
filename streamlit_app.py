import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Eliott Tracker", page_icon="🍼")

st.title("🍼 Suivi d'Eliott")

DATA_FILE = "suivi_eliott.csv"
COLUMNS = ["Date", "Heure", "Type", "Quantité (ml)", "Poids (kg)", "Taille (cm)", "Notes", "Par"]

# --- GESTION DU FICHIER (NETTOYAGE) ---
def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(DATA_FILE, index=False)
        return df
    
    df = pd.read_csv(DATA_FILE)
    
    # Si le fichier est corrompu ou mal colonné (ton cas actuel)
    if list(df.columns) != COLUMNS:
        st.warning("Mise à jour du format des données en cours...")
        # On recrée un dataframe propre avec les anciennes données si possible
        new_df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(DATA_FILE, index=False) # On repart sur du propre
        return new_df
    return df

df_display = load_data()

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

# --- CALCULS ET AFFICHAGE ---
if not df_display.empty:
    # On s'assure que les chiffres sont des chiffres
    df_display['Quantité (ml)'] = pd.to_numeric(df_display['Quantité (ml)'], errors='coerce').fillna(0)
    
    # 1. Total du jour (Mise à jour automatique)
    today = datetime.now().strftime("%d/%m/%Y")
    total_today = df_display[(df_display['Date'] == today) & (df_display['Type'] == "Biberon")]['Quantité (ml)'].sum()
    
    c1, c2 = st.columns(2)
    c1.metric("Total Bib (Auj.)", f"{int(total_today)} ml")
    
    # 2. Dernier Poids
    poids_data = df_display[df_display['Poids (kg)'] > 0]
    if not poids_data.empty:
        c2.metric("Dernier Poids", f"{poids_data.iloc[-1]['Poids (kg)']} kg")

    # 3. Rappel +4h (Sécurisé contre les erreurs de format d'heure)
    bibs = df_display[df_display['Type'] == "Biberon"]
    if not bibs.empty:
        try:
            last_h = str(bibs.iloc[-1]['Heure'])
            if ":" in last_h:
                t_obj = datetime.strptime(last_h, "%H:%M")
                rappel = (t_obj + timedelta(hours=4)).strftime("%H:%M")
                st.info(f"🔔 Prochain bib vers **{rappel}**")
        except:
            st.info("🔔 Enregistrez un nouveau biberon pour activer le rappel.")

    st.subheader("📊 Historique")
    st.dataframe(df_display.tail(10), use_container_width=True)
else:
    st.info("L'historique est vide. Enregistrez le premier biberon d'Eliott !")
