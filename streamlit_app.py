import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# Configuration de la page
st.set_page_config(page_title="Le Petit Carnet d'Eliott", page_icon="🧸")

# --- LE DESIGN "NUAGE" (CSS FORCÉ) ---
st.markdown("""
    <style>
    /* Fond de page et police */
    .stApp {
        background-color: #F8F9FB;
    }
    
    /* Titre personnalisé */
    .main-title {
        color: #7B8FA1;
        font-family: 'Helvetica Neue', sans-serif;
        text-align: center;
        font-weight: 300;
        font-size: 2.5rem;
        padding-bottom: 20px;
    }

    /* Cartes de statistiques */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #EAEAEA;
    }

    /* Boutons arrondis */
    .stButton>button {
        border-radius: 25px !important;
        background-color: #BDE0FE !important;
        color: #565E64 !important;
        border: none !important;
        padding: 10px 25px !important;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #A2D2FF !important;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('eliott_v5.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS suivi 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, heure TEXT, type TEXT, 
                  quantite REAL, poids REAL, taille REAL, 
                  note TEXT, auteur TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- ENTÊTE ---
st.markdown('<h1 class="main-title">🧸 Le Carnet d\'Eliott</h1>', unsafe_allow_html=True)

# Message Anniversaire Samuel (Demain !)
if datetime.now().strftime("%d/%m") == "11/02":
    st.balloons()
    st.markdown("""
        <div style="background-color: #FFCAD4; padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <h2>🎉 Joyeux 4 ans Samuel ! 🎂</h2>
            <p>Une journée magique pour un grand garçon !</p>
        </div>
        <br>
    """, unsafe_allow_html=True)

# --- RÉCAPITULATIF VISUEL ---
df = pd.read_sql_query("SELECT * FROM suivi", conn)

if not df.empty:
    today = datetime.now().strftime("%d/%m/%Y")
    total_today = df[(df['date'] == today) & (df['type'].str.contains("Biberon"))]['quantite'].sum()
    
    # Affichage en colonnes "Cartes"
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
            <div class="metric-card">
                <p style="color: #9A8C98; margin: 0;">Bu aujourd'hui</p>
                <h2 style="color: #BDE0FE; margin: 0;">{int(total_today)} ml</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        bibs = df[df['type'].str.contains("Biberon")]
        next_h = "--:--"
        if not bibs.empty:
            last_h = datetime.strptime(str(bibs.iloc[-1]['heure']), "%H:%M")
            next_h = (last_h + timedelta(hours=4)).strftime("%H:%M")
        
        st.markdown(f"""
            <div class="metric-card">
                <p style="color: #9A8C98; margin: 0;">Prochain Bib</p>
                <h2 style="color: #FFCAD4; margin: 0;">{next_h}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.progress(min(total_today / 900.0, 1.0))

# --- FORMULAIRE ---
with st.expander("📝 Noter un nouveau moment", expanded=True):
    type_ev = st.selectbox("Type", ["🍼 Biberon", "💦 Pipi", "💩 Caca", "⚖️ Poids/Taille", "✨ Note"], key="type_v5")
    
    with st.form("form_v5", clear_on_submit=True):
        c1, c2 = st.columns(2)
        d_ev = c1.date_input("Date", datetime.now())
        h_ev = c2.time_input("Heure", datetime.now())
        
        q, p, ta = 0.0, 0.0, 0.0
        if "Biberon" in type_ev:
            q = st.number_input("Quantité (ml)", min_value=0.0, step=10.0, value=150.0)
        elif "Poids" in type_ev:
            p = st.number_input("Poids (kg)", step=0.01, format="%.2f")
            ta = st.number_input("Taille (cm)", step=0.5)
            
        note = st.text_input("Commentaire")
        qui = st.radio("Par qui ?", ["👨‍🦱 Papa", "👩‍🦰 Maman"], horizontal=True)
        
        if st.form_submit_button("Enregistrer avec tendresse"):
            c = conn.cursor()
            c.execute("INSERT INTO suivi (date, heure, type, quantite, poids, taille, note, auteur) VALUES (?,?,?,?,?,?,?,?)", 
                      (d_ev.strftime("%d/%m/%Y"), h_ev.strftime("%H:%M"), type_ev, q, p, ta, note, qui))
            conn.commit()
            st.rerun()

# --- HISTORIQUE ---
if not df.empty:
    st.markdown("### 📖 Derniers souvenirs")
    st.dataframe(df.iloc[::-1].head(10)[['date', 'heure', 'type', 'quantite', 'note', 'auteur']], use_container_width=True)
    
    with st.expander("🛠️ Modifier ou Supprimer"):
        df_edit = df.copy()
        df_edit['label'] = df_edit['date'] + " " + df_edit['heure'] + " - " + df_edit['type']
        choice = st.selectbox("Ligne", options=df_edit['id'].tolist(), 
                              format_func=lambda x: df_edit[df_edit['id'] == x]['label'].values[0])
        
        c1, c2 = st.columns(2)
        if c1.button("🗑️ Supprimer définitivement"):
            c = conn.cursor()
            c.execute("DELETE FROM suivi WHERE id=?", (choice,))
            conn.commit()
            st.rerun()
