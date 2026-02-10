import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# Configuration de la page
st.set_page_config(page_title="Eliott App", page_icon="🍼")

# --- INITIALISATION DE LA BASE (VERSION PROPRE) ---
def init_db():
    conn = sqlite3.connect('eliott_data.db', check_same_thread=False)
    c = conn.cursor()
    # Création de la table avec toutes les colonnes nécessaires dès le départ
    c.execute('''CREATE TABLE IF NOT EXISTS suivi 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, heure TEXT, type TEXT, 
                  quantite REAL, poids REAL, taille REAL, 
                  note TEXT, auteur TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- MESSAGE ANNIVERSAIRE SAMUEL (POUR DEMAIN !) ---
if datetime.now().strftime("%d/%m") == "11/02":
    st.balloons()
    st.success("🎉 **JOYEUX ANNIVERSAIRE SAMUEL !** 🎂 (4 ans aujourd'hui !)")

st.title("🍼 Suivi d'Eliott")

# --- FORMULAIRE DYNAMIQUE ---
with st.expander("➕ Noter un événement", expanded=True):
    # Choix du type en dehors du formulaire pour la réactivité
    type_ev = st.selectbox("Type d'événement", ["Biberon", "Pipi", "Caca", "Poids/Taille", "Note"])
    
    with st.form("form_saisie", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_ev = col1.date_input("Date", datetime.now())
        heure_ev = col2.time_input("Heure", datetime.now())
        
        q, p, ta = 0.0, 0.0, 0.0
        
        # Les champs n'apparaissent QUE si nécessaire
        if type_ev == "Biberon":
            q = st.number_input("Quantité de lait (ml)", min_value=0.0, step=10.0, value=150.0)
        elif type_ev == "Poids/Taille":
            cp, ct = st.columns(2)
            p = cp.number_input("Poids (kg)", min_value=0.0, step=0.01, format="%.2f")
            ta = ct.number_input("Taille (cm)", min_value=0.0, step=0.5)
            
        note = st.text_input("Commentaire / Détails")
        auteur = st.radio("Qui note ?", ["Papa", "Maman"], horizontal=True)
        
        if st.form_submit_button("Enregistrer"):
            c = conn.cursor()
            c.execute("INSERT INTO suivi (date, heure, type, quantite, poids, taille, note, auteur) VALUES (?,?,?,?,?,?,?,?)", 
                      (date_ev.strftime("%d/%m/%Y"), heure_ev.strftime("%H:%M"), type_ev, q, p, ta, note, auteur))
            conn.commit()
            st.rerun()

# --- RÉCUPÉRATION ET AFFICHAGE ---
df = pd.read_sql_query("SELECT * FROM suivi", conn)

if not df.empty:
    today = datetime.now().strftime("%d/%m/%Y")
    total_today = df[(df['date'] == today) & (df['type'] == "Biberon")]['quantite'].sum()
    
    # État du jour
    st.subheader(f"📊 État du jour : {int(total_today)} ml")
    st.progress(min(total_today / 900.0, 1.0))
    
    # Rappel +4h sécurisé
    bibs = df[df['type'] == "Biberon"]
    if not bibs.empty:
        try:
            last_h = datetime.strptime(str(bibs.iloc[-1]['heure']), "%H:%M")
            next_h = (last_h + timedelta(hours=4)).strftime("%H:%M")
            st.warning(f"🔔 Prochain bib prévu à : **{next_h}**")
        except: pass

    st.subheader("📝 Historique")
    st.dataframe(df.iloc[::-1].head(10)[['date', 'heure', 'type', 'quantite', 'note', 'auteur']], use_container_width=True)

    # --- MODIFICATION / SUPPRESSION ---
    with st.expander("✏️ Modifier ou Supprimer une ligne"):
        df_edit = df.copy()
        df_edit['label'] = df_edit['date'] + " " + df_edit['heure'] + " - " + df_edit['type']
        
        choice = st.selectbox("Ligne à modifier", options=df_edit['id'].tolist(), 
                              format_func=lambda x: df_edit[df_edit['id'] == x]['label'].values[0])
        
        row = df[df['id'] == choice].iloc[0]
        
        with st.form("edit_form"):
            edit_note = st.text_input("Note", value=row['note'])
            edit_q = row['quantite']
            if row['type'] == "Biberon":
                edit_q = st.number_input("Quantité (ml)", value=float(row['quantite']), step=10.0)
            
            c1, c2 = st.columns(2)
            if c1.form_submit_button("✅ Valider"):
                c = conn.cursor()
                c.execute("UPDATE suivi SET note = ?, quantite = ? WHERE id = ?", (edit_note, edit_q, choice))
                conn.commit()
                st.rerun()
                
            if c2.form_submit_button("🗑️ Supprimer"):
                c = conn.cursor()
                c.execute("DELETE FROM suivi WHERE id = ?", (choice,))
                conn.commit()
                st.rerun()
else:
    st.info("Aucune donnée enregistrée pour le moment.")
