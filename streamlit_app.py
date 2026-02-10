import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# Configuration
st.set_page_config(page_title="Eliott App", page_icon="🍼")

# --- BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('eliott_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS suivi 
                 (date TEXT, heure TEXT, type TEXT, quantite REAL, poids REAL, taille REAL, note TEXT, auteur TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- CADEAU POUR DEMAIN (11 FÉVRIER) ---
if datetime.now().strftime("%d/%m") == "11/02":
    st.balloons()
    st.success("🎉 **JOYEUX ANNIVERSAIRE SAMUEL !** 🎂 (4 ans aujourd'hui !)")

st.title("🍼 Suivi d'Eliott")

# --- FORMULAIRE DYNAMIQUE ---
# On sort le selectbox du formulaire pour que l'app réagisse instantanément au choix
with st.expander("➕ Noter un événement", expanded=True):
    type_ev = st.selectbox("Type d'événement", ["Biberon", "Pipi", "Caca", "Poids/Taille", "Note"])
    
    with st.form("form_saisie", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_ev = col1.date_input("Date", datetime.now())
        heure_ev = col2.time_input("Heure", datetime.now())
        
        q, p, ta = 0.0, 0.0, 0.0
        
        # ICI LA MAGIE : Les champs ne s'affichent QUE si nécessaire
        if type_ev == "Biberon":
            q = st.number_input("Quantité de lait (ml)", min_value=0.0, step=10.0, value=150.0)
        elif type_ev == "Poids/Taille":
            c_p, c_t = st.columns(2)
            p = c_p.number_input("Poids (kg)", min_value=0.0, step=0.01, format="%.2f")
            ta = c_t.number_input("Taille (cm)", min_value=0.0, step=0.5)
            
        note = st.text_input("Commentaire / Détails")
        auteur = st.radio("Qui note ?", ["Papa", "Maman"], horizontal=True)
        
        if st.form_submit_button("Enregistrer"):
            c = conn.cursor()
            c.execute("INSERT INTO suivi VALUES (?,?,?,?,?,?,?,?)", 
                      (date_ev.strftime("%d/%m/%Y"), heure_ev.strftime("%H:%M"), type_ev, q, p, ta, note, auteur))
            conn.commit()
            st.rerun()

# --- VISUELS ET CALCULS ---
df = pd.read_sql_query("SELECT * FROM suivi", conn)

if not df.empty:
    today = datetime.now().strftime("%d/%m/%Y")
    total_today = df[(df['date'] == today) & (df['type'] == "Biberon")]['quantite'].sum()
    
    # Barre de progression
    st.subheader(f"📊 État du jour : {int(total_today)} ml")
    st.progress(min(total_today / 900.0, 1.0))
    
    # Rappel +4h
    bibs = df[df['type'] == "Biberon"]
    if not bibs.empty:
        try:
            last_h = datetime.strptime(str(bibs.iloc[-1]['heure']), "%H:%M")
            next_h = (last_h + timedelta(hours=4)).strftime("%H:%M")
            st.warning(f"🔔 Prochain bib prévu à : **{next_h}**")
        except: pass

    st.subheader("📝 Historique")
    # Affichage propre (on cache les colonnes techniques)
    st.dataframe(df.iloc[::-1].head(10)[['date', 'heure', 'type', 'quantite', 'note', 'auteur']], use_container_width=True)
    
    # BOUTON DE SUPPRESSION (en cas d'erreur)
    if st.button("❌ Supprimer le dernier enregistrement"):
        c = conn.cursor()
        c.execute("DELETE FROM suivi WHERE rowid = (SELECT MAX(rowid) FROM suivi)")
        conn.commit()
        st.error("Dernière ligne supprimée.")
        st.rerun()
else:
    st.info("Aucune donnée. Prêt pour le premier bib !")

# Sidebar pour le mode nuit
st.sidebar.info("🌙 **Mode Nuit :** Settings > Theme > Dark")
