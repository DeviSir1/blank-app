import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Eliott Tracker", page_icon="🍼")

st.title("🍼 Suivi d'Eliott")

DATA_FILE = "suivi_eliott.csv"

# Initialisation du fichier avec les nouvelles colonnes Poids et Taille
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Date", "Heure", "Type", "Quantité (ml)", "Poids (kg)", "Taille (cm)", "Notes", "Par"])
    df.to_csv(DATA_FILE, index=False)

# --- FORMULAIRE DE SAISIE ---
with st.expander("➕ Enregistrer une mesure ou un événement", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_ev = st.date_input("Date", datetime.now())
        with col2:
            heure_ev = st.time_input("Heure", datetime.now())
        
        type_event = st.selectbox("Type", ["Biberon", "Pipi", "Caca", "Poids/Taille", "Note"])
        
        quantite = 0
        poids = 0.0
        taille = 0.0
        
        if type_event == "Biberon":
            quantite = st.number_input("Quantité (ml)", min_value=0, step=10, value=150)
        elif type_event == "Poids/Taille":
            poids = st.number_input("Poids (kg)", min_value=0.0, step=0.01, format="%.2f")
            taille = st.number_input("Taille (cm)", min_value=0.0, step=0.5)
        
        note = st.text_input("Commentaire / Note")
        auteur = st.radio("Qui note ?", ["Papa", "Maman"], horizontal=True)
        
        submitted = st.form_submit_button("Enregistrer")
        
        if submitted:
            date_str = date_ev.strftime("%d/%m/%Y")
            heure_str = heure_ev.strftime("%H:%M")
            
            new_data = pd.DataFrame([[date_str, heure_str, type_event, quantite, poids, taille, note, auteur]], 
                                    columns=["Date", "Heure", "Type", "Quantité (ml)", "Poids (kg)", "Taille (cm)", "Notes", "Par"])
            new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success(f"Données enregistrées !")

# --- CALCUL DU TOTAL (Correction de la mise à jour) ---
# On recharge les données à chaque passage pour garantir la mise à jour
df_display = pd.read_csv(DATA_FILE)

# Calcul dynamique pour aujourd'hui
today_str = datetime.now().strftime("%d/%m/%Y")
total_bib_today = df_display[(df_display['Date'] == today_str) & (df_display['Type'] == "Biberon")]['Quantité (ml)'].sum()

# --- AFFICHAGE DES MÉTRIQUES ---
c1, c2 = st.columns(2)
with c1:
    st.metric("Total Biberons (Auj.)", f"{total_bib_today} ml")
with c2:
    # Affiche le dernier poids enregistré
    last_weight = df_display[df_display['Poids (kg)'] > 0]['Poids (kg)'].last_valid_index()
    if last_weight is not None:
        st.metric("Dernier Poids", f"{df_display.loc[last_weight, 'Poids (kg)']} kg")

# Rappel automatique affiché à l'écran
last_bib = df_display[df_display['Type'] == "Biberon"].tail(1)
if not last_bib.empty:
    h_bib = datetime.strptime(last_bib['Heure'].values[0], "%H:%M")
    rappel = (h_bib + timedelta(hours=4)).strftime("%H:%M")
    st.info(f"🔔 Prochain biberon conseillé vers : **{rappel}**")

st.subheader("📊 Historique")
st.dataframe(df_display.tail(10), use_container_width=True)
