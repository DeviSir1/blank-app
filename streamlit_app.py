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
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, heure TEXT, type TEXT, quantite REAL, poids REAL, taille REAL, note TEXT, auteur TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- CADEAU POUR DEMAIN (11 FÉVRIER) ---
if datetime.now().strftime("%d/%m") == "11/02":
    st.balloons()
    st.success("🎉 **JOYEUX ANNIVERSAIRE SAMUEL !** 🎂 (4 ans aujourd'hui !)")

st.title("🍼 Suivi d'Eliott")

# --- FORMULAIRE D'AJOUT ---
with st.expander("➕ Noter un nouvel événement", expanded=True):
    type_ev = st.selectbox("Type d'événement", ["Biberon", "Pipi", "Caca", "Poids/Taille", "Note"])
    
    with st.form("form_saisie", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_ev = col1.date_input("Date", datetime.now())
        heure_ev = col2.time_input("Heure", datetime.now())
        
        q, p, ta = 0.0, 0.0, 0.0
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
            c.execute("INSERT INTO suivi (date, heure, type, quantite, poids, taille, note, auteur) VALUES (?,?,?,?,?,?,?,?)", 
                      (date_ev.strftime("%d/%m/%Y"), heure_ev.strftime("%H:%M"), type_ev, q, p, ta, note, auteur))
            conn.commit()
            st.rerun()

# --- RÉCUPÉRATION DES DONNÉES ---
df = pd.read_sql_query("SELECT * FROM suivi", conn)

if not df.empty:
    today = datetime.now().strftime("%d/%m/%Y")
    total_today = df[(df['date'] == today) & (df['type'] == "Biberon")]['quantite'].sum()
    
    st.subheader(f"📊 État du jour : {int(total_today)} ml")
    st.progress(min(total_today / 900.0, 1.0))
    
    # Historique
    st.subheader("📝 Historique")
    st.dataframe(df.iloc[::-1].head(10)[['date', 'heure', 'type', 'quantite', 'note', 'auteur']], use_container_width=True)

    # --- SECTION MODIFICATION ---
    with st.expander("✏️ Modifier ou Supprimer une ligne"):
        # On crée une liste d'options lisibles pour le sélecteur
        df_edit = df.iloc[::-1].copy()
        df_edit['label'] = df_edit['date'] + " " + df_edit['heure'] + " - " + df_edit['type']
        
        option = st.selectbox("Choisir la ligne à modifier", options=df_edit['id'].tolist(), 
                              format_func=lambda x: df_edit[df_edit['id'] == x]['label'].values[0])
        
        row_to_edit = df[df['id'] == option].iloc[0]
        
        with st.form("form_edit"):
            new_note = st.text_input("Nouvelle note", value=row_to_edit['note'])
            new_q = row_to_edit['quantite']
            
            if row_to_edit['type'] == "Biberon":
                new_q = st.number_input("Corriger Quantité (ml)", value=float(row_to_edit['quantite']), step=10.0)
            
            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.form_submit_button("✅ Valider les modifs"):
                c = conn.cursor()
                c.execute("UPDATE suivi SET note = ?, quantite = ? WHERE id = ?", (new_note, new_q, option))
                conn.commit()
                st.success("Modifié !")
                st.rerun()
                
            if col_btn2.form_submit_button("🗑️ Supprimer cette ligne"):
                c = conn.cursor()
                c.execute("DELETE FROM suivi WHERE id = ?", (option,))
                conn.commit()
                st.warning("Supprimé !")
                st.rerun()
else:
    st.info("Aucune donnée enregistrée.")
