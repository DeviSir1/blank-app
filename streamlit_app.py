import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# Configuration de l'application
st.set_page_config(page_title="App Eliott", page_icon="🍼", layout="centered")

# --- INITIALISATION DE LA BASE DE DONNÉES INTERNE ---
def init_db():
    conn = sqlite3.connect('eliott_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS suivi 
                 (date TEXT, heure TEXT, type TEXT, quantite REAL, poids REAL, taille REAL, note TEXT, auteur TEXT)''')
    conn.commit()
    return conn

conn = init_db()

def add_data(d, h, t, q, p, ta, n, a):
    c = conn.cursor()
    c.execute("INSERT INTO suivi VALUES (?,?,?,?,?,?,?,?)", (d, h, t, q, p, ta, n, a))
    conn.commit()

def get_data():
    return pd.read_sql_query("SELECT * FROM suivi", conn)

# --- INTERFACE ---
st.title("🍼 Suivi d'Eliott")

# Formulaire d'ajout
with st.expander("➕ Ajouter un enregistrement", expanded=True):
    with st.form("form_eliott", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_ev = col1.date_input("Date", datetime.now())
        heure_ev = col2.time_input("Heure", datetime.now())
        
        type_ev = st.selectbox("Type", ["Biberon", "Pipi", "Caca", "Poids/Taille", "Note"])
        
        q, p, ta = 0.0, 0.0, 0.0
        if type_ev == "Biberon":
            q = st.number_input("Quantité (ml)", step=10.0, value=150.0)
        elif type_ev == "Poids/Taille":
            p = st.number_input("Poids (kg)", step=0.01, format="%.2f")
            ta = st.number_input("Taille (cm)", step=0.5)
            
        note = st.text_input("Note / Commentaire")
        auteur = st.radio("Qui note ?", ["Papa", "Maman"], horizontal=True)
        
        if st.form_submit_button("Enregistrer"):
            add_data(date_ev.strftime("%d/%m/%Y"), heure_ev.strftime("%H:%M"), type_ev, q, p, ta, note, auteur)
            st.success("Enregistré !")
            st.rerun()

# --- RÉCUPÉRATION ET CALCULS ---
df = get_data()

if not df.empty:
    # 1. Calcul du total bu aujourd'hui
    today = datetime.now().strftime("%d/%m/%Y")
    total_today = df[(df['date'] == today) & (df['type'] == "Biberon")]['quantite'].sum()
    
    # 2. Rappel +4h
    bibs = df[df['type'] == "Biberon"]
    
    # Affichage des métriques en haut
    c1, c2 = st.columns(2)
    c1.metric("Bu aujourd'hui", f"{int(total_today)} ml")
    
    if not bibs.empty:
        last_h = datetime.strptime(bibs.iloc[-1]['heure'], "%H:%M")
        next_h = (last_h + timedelta(hours=4)).strftime("%H:%M")
        st.info(f"🔔 Prochain biberon conseillé : **{next_h}**")

    # 3. Historique
    st.subheader("📊 Dernières notes")
    # Inverser pour voir le plus récent en haut
    st.dataframe(df.iloc[::-1].head(10), use_container_width=True)
    
    # Bouton de sécurité pour effacer (si besoin)
    if st.button("Supprimer la dernière ligne"):
        c = conn.cursor()
        c.execute("DELETE FROM suivi WHERE rowid = (SELECT MAX(rowid) FROM suivi)")
        conn.commit()
        st.rerun()
else:
    st.info("L'historique est vide. Commencez à noter !")
