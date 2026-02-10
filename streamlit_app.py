import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# Config
st.set_page_config(page_title="App Eliott", page_icon="🍼")

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect('eliott_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS suivi 
                 (date TEXT, heure TEXT, type TEXT, quantite REAL, poids REAL, taille REAL, note TEXT, auteur TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- ANNIVERSAIRE SAMUEL (DEMAIN !) ---
if datetime.now().strftime("%d/%m") == "11/02":
    st.balloons()
    st.success("🎉 **JOYEUX ANNIVERSAIRE SAMUEL !** 🎂 (4 ans aujourd'hui !)")

st.title("🍼 Suivi d'Eliott")

# --- FORMULAIRE DYNAMIQUE ---
with st.expander("➕ Noter un événement", expanded=True):
    with st.form("form_eliott", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_ev = col1.date_input("Date", datetime.now())
        heure_ev = col2.time_input("Heure", datetime.now())
        
        type_ev = st.selectbox("Type", ["Biberon", "Pipi", "Caca", "Poids/Taille", "Note"])
        
        # Initialisation des valeurs cachées
        q, p, ta = 0.0, 0.0, 0.0
        
        # LOGIQUE D'AFFICHAGE : On ne montre que ce qui est nécessaire
        if type_ev == "Biberon":
            q = st.number_input("Quantité de lait (ml)", min_value=0.0, step=10.0, value=150.0)
        elif type_ev == "Poids/Taille":
            col_p, col_t = st.columns(2)
            p = col_p.number_input("Poids (kg)", min_value=0.0, step=0.01, format="%.2f")
            ta = col_t.number_input("Taille (cm)", min_value=0.0, step=0.5)
            
        note = st.text_input("Commentaire / Détails")
        auteur = st.radio("Qui note ?", ["Papa", "Maman"], horizontal=True)
        
        if st.form_submit_button("Enregistrer"):
            c = conn.cursor()
            c.execute("INSERT INTO suivi VALUES (?,?,?,?,?,?,?,?)", 
                      (date_ev.strftime("%d/%m/%Y"), heure_ev.strftime("%H:%M"), type_ev, q, p, ta, note, auteur))
            conn.commit()
            st.rerun()

# --- AFFICHAGE ---
df = pd.read_sql_query("SELECT * FROM suivi", conn)

if not df.empty:
    today = datetime.now().strftime("%d/%m/%Y")
    df_today = df[df['date'] == today]
    total_today = df_today[df_today['type'] == "Biberon"]['quantite'].sum()
    
    st.subheader(f"📊 État du jour : {int(total_today)} ml")
    st.progress(min(total_today / 900.0, 1.0))
    
    bibs = df[df['type'] == "Biberon"]
    if not bibs.empty:
        last_h = datetime.strptime(bibs.iloc[-1]['heure'], "%H:%M")
        next_h = (last_h + timedelta(hours=4)).strftime("%H:%M")
        st.warning(f"🔔 Prochain bib prévu à : **{next_h}**")

    st.subheader("📝 Historique")
    # On affiche les colonnes proprement (on cache les colonnes à 0 pour la lecture)
    st.dataframe(df.iloc[::-1].head(10)[['date', 'heure', 'type', 'quantite', 'note', 'auteur']], use_container_width=True)
else:
    st.info("Aucune donnée enregistrée.")
