import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# Configuration
st.set_page_config(page_title="Le Carnet d'Eliott", page_icon="🧸")

# --- DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FB; }
    .main-title { color: #7B8FA1; font-family: sans-serif; text-align: center; font-weight: 300; font-size: 2.5rem; }
    .metric-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border: 1px solid #EAEAEA; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('eliott_v7.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS suivi 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, heure TEXT, type TEXT, 
                  quantite REAL, poids REAL, taille REAL, note TEXT, auteur TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- ENTÊTE ---
st.markdown('<h1 class="main-title">🧸 Le Carnet d\'Eliott</h1>', unsafe_allow_html=True)

# Message pour Samuel (demain 11/02)
if datetime.now().strftime("%d/%m") == "11/02":
    st.balloons()
    st.success("🎉 **JOYEUX ANNIVERSAIRE SAMUEL !** 🎂 (4 ans aujourd'hui !)")

# --- FORMULAIRE D'AJOUT ---
with st.expander("➕ Noter un événement", expanded=True):
    type_ev = st.selectbox("Type", ["🍼 Biberon", "💦 Pipi", "💩 Caca", "⚖️ Poids/Taille", "📝 Note"])
    with st.form("form_eliott", clear_on_submit=True):
        c1, c2 = st.columns(2)
        d_ev = c1.date_input("Date", datetime.now())
        h_ev = c2.time_input("Heure", datetime.now())
        
        q, p, ta = 0.0, 0.0, 0.0
        if "Biberon" in type_ev:
            q = st.number_input("Quantité (ml)", min_value=0.0, step=10.0, value=150.0)
        elif "Poids" in type_ev:
            colp, colt = st.columns(2)
            p = colp.number_input("Poids (kg)", min_value=0.0, step=0.01, format="%.2f")
            ta = colt.number_input("Taille (cm)", min_value=0.0, step=0.5)
            
        note = st.text_input("Commentaire")
        qui = st.radio("Qui ?", ["👨‍🦱 Papa", "👩‍🦰 Maman"], horizontal=True)
        
        if st.form_submit_button("Enregistrer"):
            c = conn.cursor()
            c.execute("INSERT INTO suivi (date, heure, type, quantite, poids, taille, note, auteur) VALUES (?,?,?,?,?,?,?,?)", 
                      (d_ev.strftime("%d/%m/%Y"), h_ev.strftime("%H:%M"), type_ev, q, p, ta, note, qui))
            conn.commit()
            st.rerun()

# --- RÉCUPÉRATION DES DONNÉES ---
df = pd.read_sql_query("SELECT * FROM suivi", conn)

if not df.empty:
    # Métriques du haut
    today = datetime.now().strftime("%d/%m/%Y")
    total_today = df[(df['date'] == today) & (df['type'].str.contains("Biberon"))]['quantite'].sum()
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f'<div class="metric-card"><p style="color: #9A8C98; margin: 0;">Bu aujourd\'hui</p><h2 style="color: #BDE0FE; margin: 0;">{int(total_today)} ml</h2></div>', unsafe_allow_html=True)
    with col_b:
        bibs = df[df['type'].str.contains("Biberon")]
        next_h = "--:--"
        if not bibs.empty:
            last_h = datetime.strptime(str(bibs.iloc[-1]['heure']), "%H:%M")
            next_h = (last_h + timedelta(hours=4)).strftime("%H:%M")
        st.markdown(f'<div class="metric-card"><p style="color: #9A8C98; margin: 0;">Prochain Bib</p><h2 style="color: #FFCAD4; margin: 0;">{next_h}</h2></div>', unsafe_allow_html=True)

    # --- AFFICHAGE PAR ONGLETS ---
    st.write("---")
    tab1, tab2 = st.tabs(["📖 Journal de bord", "📈 Croissance (Poids/Taille)"])

    with tab1:
        st.subheader("Derniers événements")
        # On cache les colonnes Poids/Taille ici pour la clarté
        journal = df[~df['type'].str.contains("Poids")].iloc[::-1]
        st.dataframe(journal[['date', 'heure', 'type', 'quantite', 'note', 'auteur']], use_container_width=True)

    with tab2:
        croissance = df[df['type'].str.contains("Poids")].copy()
        if not croissance.empty:
            st.subheader("Tableau de croissance")
            st.dataframe(croissance[['date', 'poids', 'taille', 'auteur']].iloc[::-1], use_container_width=True)
            
            if len(croissance) >= 2:
                st.subheader("Courbe de poids")
                croissance['DateObj'] = pd.to_datetime(croissance['date'], format='%d/%m/%Y')
                st.line_chart(croissance.set_index('DateObj')['poids'], color="#BDE0FE")
        else:
            st.info("Aucune mesure de poids/taille enregistrée.")

    # --- MODIF / SUPPR ---
    with st.expander("🛠️ Modifier ou Supprimer une ligne"):
        df_edit = df.copy()
        df_edit['label'] = df_edit['date'] + " " + df_edit['heure'] + " - " + df_edit['type']
        choice = st.selectbox("Ligne à gérer", options=df_edit['id'].tolist(), 
                              format_func=lambda x: df_edit[df_edit['id'] == x]['label'].values[0])
        if st.button("🗑️ Supprimer cette ligne"):
            c = conn.cursor()
            c.execute("DELETE FROM suivi WHERE id=?", (choice,))
            conn.commit()
            st.rerun()
else:
    st.info("Prêt pour le premier souvenir d'Eliott !")
