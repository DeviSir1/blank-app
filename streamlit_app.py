import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# --- CONFIGURATION & DESIGN DOUX ---
st.set_page_config(page_title="Le Petit Carnet d'Eliott", page_icon="🧸")

st.markdown("""
    <style>
    .stApp { background-color: #FDFBFA; }
    .main-title { color: #8E9AAF; font-family: 'Segoe UI', sans-serif; text-align: center; font-weight: 300; font-size: 2.5rem; }
    .metric-card { background-color: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); text-align: center; border: 1px solid #F1F1F1; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 10px; padding: 10px 20px; color: #8E9AAF; }
    .stTabs [aria-selected="true"] { background-color: #BDE0FE !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES (VERSION FINALE) ---
def init_db():
    conn = sqlite3.connect('eliott_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS suivi 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, heure TEXT, type TEXT, 
                  quantite REAL, poids REAL, taille REAL, note TEXT, auteur TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- ENTÊTE ---
st.markdown('<h1 class="main-title">🧸 Le Petit Carnet d\'Eliott</h1>', unsafe_allow_html=True)

# Message spécial pour Samuel (demain 11/02)
if datetime.now().strftime("%d/%m") == "11/02":
    st.balloons()
    st.success("🎉 **JOYEUX ANNIVERSAIRE SAMUEL !** 🎂 (4 ans aujourd'hui !)")

# --- FORMULAIRE D'AJOUT ---
with st.expander("✨ Ajouter un nouveau souvenir", expanded=True):
    type_ev = st.selectbox("C'est pour...", ["🍼 Biberon", "💦 Pipi", "💩 Caca", "⚖️ Poids/Taille", "📝 Note"])
    
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
            
        note = st.text_input("Un petit commentaire ?")
        qui = st.radio("Qui note ?", ["👨‍🦱 Papa", "👩‍🦰 Maman"], horizontal=True)
        
        if st.form_submit_button("Enregistrer avec tendresse"):
            c = conn.cursor()
            c.execute("INSERT INTO suivi (date, heure, type, quantite, poids, taille, note, auteur) VALUES (?,?,?,?,?,?,?,?)", 
                      (d_ev.strftime("%d/%m/%Y"), h_ev.strftime("%H:%M"), type_ev, q, p, ta, note, qui))
            conn.commit()
            st.rerun()

# --- RÉCUPÉRATION ET AFFICHAGE ---
df = pd.read_sql_query("SELECT * FROM suivi", conn)

if not df.empty:
    today = datetime.now().strftime("%d/%m/%Y")
    total_today = df[(df['date'] == today) & (df['type'].str.contains("Biberon"))]['quantite'].sum()
    
    # Cartes de stats
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f'<div class="metric-card"><p style="color: #A2ADBC; font-size:0.9rem;">Bu aujourd\'hui</p><h2 style="color: #BDE0FE; margin:0;">{int(total_today)} ml</h2></div>', unsafe_allow_html=True)
    with col_b:
        bibs = df[df['type'].str.contains("Biberon")]
        next_h = "--:--"
        if not bibs.empty:
            last_h = datetime.strptime(str(bibs.iloc[-1]['heure']), "%H:%M")
            next_h = (last_h + timedelta(hours=4)).strftime("%H:%M")
        st.markdown(f'<div class="metric-card"><p style="color: #A2ADBC; font-size:0.9rem;">Prochain Bib</p><h2 style="color: #FFCAD4; margin:0;">{next_h}</h2></div>', unsafe_allow_html=True)

    # --- ONGLETS ---
    st.write("---")
    tab_journal, tab_croissance = st.tabs(["📖 Journal de bord", "📈 Suivi de Croissance"])

    with tab_journal:
        st.subheader("Les derniers moments")
        # On ne montre pas les colonnes poids/taille ici
        journal_df = df[~df['type'].str.contains("Poids")].iloc[::-1]
        st.dataframe(journal_df[['date', 'heure', 'type', 'quantite', 'note', 'auteur']], use_container_width=True)

    with tab_croissance:
        croissance_df = df[df['type'].str.contains("Poids")].copy()
        if not croissance_df.empty:
            st.subheader("Tableau de croissance")
            st.dataframe(croissance_df[['date', 'poids', 'taille', 'auteur']].iloc[::-1], use_container_width=True)
            
            if len(croissance_df) >= 2:
                st.subheader("Courbe de poids")
                croissance_df['DateObj'] = pd.to_datetime(croissance_df['date'], format='%d/%m/%Y')
                st.line_chart(croissance_df.set_index('DateObj')['poids'], color="#BDE0FE")
        else:
            st.info("Aucune mesure de croissance enregistrée pour le moment.")

    # --- ÉDITION ---
    with st.expander("🛠️ Corriger une erreur"):
        df_edit = df.copy()
        df_edit['label'] = df_edit['date'] + " " + df_edit['heure'] + " - " + df_edit['type']
        choice = st.selectbox("Choisir la ligne", options=df_edit['id'].tolist(), format_func=lambda x: df_edit[df_edit['id'] == x]['label'].values[0])
        if st.button("🗑️ Supprimer cette ligne"):
            c = conn.cursor()
            c.execute("DELETE FROM suivi WHERE id=?", (choice,))
            conn.commit()
            st.rerun()
else:
    st.info("Le carnet est prêt pour accueillir les premiers souvenirs d'Eliott.")
