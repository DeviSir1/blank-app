import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# Configuration de la page
st.set_page_config(page_title="Le Petit Carnet d'Eliott", page_icon="🧸")

# --- STYLE PERSONNALISÉ (Atmosphère Douce) ---
st.markdown("""
    <style>
    .main {
        background-color: #fdfbfb;
    }
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #ffcad4;
        background-color: #ffffff;
        color: #f08080;
    }
    .stProgress > div > div > div > div {
        background-color: #bde0fe;
    }
    h1 {
        color: #9a8c98;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('eliott_v4.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS suivi 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, heure TEXT, type TEXT, 
                  quantite REAL, poids REAL, taille REAL, 
                  note TEXT, auteur TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- ACCUEIL BIENVEILLANT ---
st.title("🧸 Le Petit Carnet d'Eliott")

# Message spécial pour demain 11/02
if datetime.now().strftime("%d/%m") == "11/02":
    st.balloons()
    st.markdown("### ✨ Journée Spéciale ! ✨")
    st.success("🎉 **Joyeux 4 ans à Samuel !** Profitez bien de cette belle fête en famille. 🎂")
else:
    st.markdown(f"✨ Bonjour ! Nous sommes le **{datetime.now().strftime('%d/%m')}**. Prêts pour une belle journée avec Eliott ?")

# --- SAISIE DOUCE ---
with st.expander("📝 Noter un petit moment", expanded=True):
    type_ev = st.selectbox("C'est pour...", ["🍼 Biberon", "💦 Pipi", "💩 Caca", "⚖️ Poids/Taille", "📝 Petite note"], key="type")
    
    with st.form("form_douceur", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_ev = col1.date_input("Date", datetime.now())
        heure_ev = col2.time_input("Heure", datetime.now())
        
        q, p, ta = 0.0, 0.0, 0.0
        
        # Interface adaptative
        if "Biberon" in type_ev:
            q = st.number_input("Quantité de lait (ml)", min_value=0.0, step=10.0, value=150.0)
        elif "Poids" in type_ev:
            cp, ct = st.columns(2)
            p = cp.number_input("Poids (kg)", min_value=0.0, step=0.01, format="%.2f")
            ta = ct.number_input("Taille (cm)", min_value=0.0, step=0.5)
            
        note = st.text_input("Un petit mot ? (facultatif)")
        auteur = st.radio("C'est qui ?", ["👨‍🦱 Papa", "👩‍🦰 Maman"], horizontal=True)
        
        if st.form_submit_button("Enregistrer avec tendresse"):
            c = conn.cursor()
            c.execute("INSERT INTO suivi (date, heure, type, quantite, poids, taille, note, auteur) VALUES (?,?,?,?,?,?,?,?)", 
                      (date_ev.strftime("%d/%m/%Y"), heure_ev.strftime("%H:%M"), type_ev, q, p, ta, note, auteur))
            conn.commit()
            st.rerun()

# --- VUE D'ENSEMBLE ---
df = pd.read_sql_query("SELECT * FROM suivi", conn)

if not df.empty:
    today = datetime.now().strftime("%d/%m/%Y")
    total_today = df[(df['date'] == today) & (df['type'].str.contains("Biberon"))]['quantite'].sum()
    
    st.markdown(f"### ☁️ Aujourd'hui, Eliott a bu **{int(total_today)} ml**")
    st.progress(min(total_today / 900.0, 1.0))
    
    # Rappel prochain bib
    bibs = df[df['type'].str.contains("Biberon")]
    if not bibs.empty:
        try:
            last_h = datetime.strptime(str(bibs.iloc[-1]['heure']), "%H:%M")
            next_h = (last_h + timedelta(hours=4)).strftime("%H:%M")
            st.warning(f"⏰ Prochain rendez-vous douceur vers **{next_h}**")
        except: pass

    st.write("---")
    st.subheader("📖 Les derniers souvenirs")
    st.dataframe(df.iloc[::-1].head(10)[['date', 'heure', 'type', 'quantite', 'note', 'auteur']], use_container_width=True)

    # --- MODIF / SUPPR ---
    with st.expander("🛠️ Modifier une étourderie"):
        df_edit = df.copy()
        df_edit['label'] = df_edit['date'] + " " + df_edit['heure'] + " - " + df_edit['type']
        choice = st.selectbox("Ligne à corriger", options=df_edit['id'].tolist(), 
                              format_func=lambda x: df_edit[df_edit['id'] == x]['label'].values[0])
        
        row = df[df['id'] == choice].iloc[0]
        with st.form("edit_douceur"):
            new_n = st.text_input("Nouvelle note", value=row['note'])
            new_q = st.number_input("Corriger Quantité", value=float(row['quantite'])) if "Biberon" in row['type'] else row['quantite']
            
            c1, c2 = st.columns(2)
            if c1.form_submit_button("✅ Valider"):
                c = conn.cursor()
                c.execute("UPDATE suivi SET note=?, quantite=? WHERE id=?", (new_n, new_q, choice))
                conn.commit()
                st.rerun()
            if c2.form_submit_button("🗑️ Supprimer"):
                c = conn.cursor()
                c.execute("DELETE FROM suivi WHERE id=?", (choice,))
                conn.commit()
                st.rerun()
else:
    st.info("Le carnet est tout neuf. Bienvenue !")
