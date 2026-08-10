import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import os
from supabase import create_client, Client

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Ignition Elite Scouting", page_icon="⚽", layout="wide")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = init_connection()
    db_conectada = True
except:
    db_conectada = False

# 2. INICIALIZAR MEMORIA
if 'equipo_ignition' not in st.session_state:
    st.session_state['equipo_ignition'] = [
        {"Jugador": "José Juan Macías", "Club": "Pumas", "Liga": "🇲🇽 Liga MX", "Status": "FIRMADO 🟡"},
        {"Jugador": "Oscar García", "Club": "León", "Liga": "🇲🇽 Liga MX", "Status": "FIRMADO 🟡"},
        {"Jugador": "Kevin Mora", "Club": "León", "Liga": "🇲🇽 Liga MX", "Status": "FIRMADO 🟡"},
        {"Jugador": "Miguel Mendoza", "Club": "León", "Liga": "🇲🇽 Liga MX U-17", "Status": "FIRMADO 🟡"},
        {"Jugador": "Sergio Luna", "Club": "León", "Liga": "🇲🇽 Liga MX U-19", "Status": "FIRMADO 🟡"},
        {"Jugador": "Bryan Destin", "Club": "CT United", "Liga": "🇺🇸 MLS", "Status": "OBJETIVO 🔵"}
    ]

# 3. LISTAS Y MÉTRICAS DUALES
LIGAS_MUNDIALES = [
    "🇪🇸 La Liga", "🇪🇸 Liga Hypermotion", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship", 
    "🇫🇷 Ligue 1", "🇮🇹 Serie A", "🇩🇪 Bundesliga", "🇳🇱 Eredivisie", 
    "🇦🇷 Primera División Argentina", "🇲🇽 Liga MX", "🇲🇽 Liga de Expansión", 
    "🇲🇽 Liga MX U-23", "🇲🇽 Liga MX U-19", "🇲🇽 Liga MX U-17", "🇲🇽 Liga MX U-15",
    "🇨🇴 Primera División Colombia", "🇧🇷 Brasileirao", "🇺🇾 Primera División Uruguay", 
    "🇨🇱 Primera División Chile", "🇺🇸 MLS" 
]

def obtener_metricas(posicion):
    if posicion == "Portero":
        return {
            "Pilar 1: Atajadas y Reflejos": ["Atajadas p/90", "Reflejos a Quemarropa", "xG Evitados", "Desvíos"],
            "Pilar 2: Distribución": ["Pases Largos Precisos", "Efectividad Pase Corto"],
            "Pilar 3: Dominio del Área": ["Salidas por Alto", "Despejes de Puños"],
            "Pilar 4: Físico/Contexto": ["Minutos Jugados", "Errores Críticos"]
        }
    elif posicion in ["Lateral Izquierdo", "Lateral Derecho"]:
        return {
            "Pilar 1: Defensa": ["Duelos Defensivos %", "Intercepciones p/90", "Tackles Exitosos"],
            "Pilar 2: Progresión": ["Pases Progresivos", "Conducciones al Tercio Final"],
            "Pilar 3: Daño Ofensivo": ["Centros Precisos %", "Desbordes Exitosos"],
            "Pilar 4: Físico/Contexto": ["Sprints p/90", "Faltas Cometidas"]
        }
    return {
        "Pilar 1: Destrucción": ["Duelos Ganados", "Intercepciones", "Tackles"],
        "Pilar 2: Creación": ["Pases Clave", "Precisión Pases", "Pases Progresivos"],
        "Pilar 3: Finalización": ["xG", "Tiros a Puerta", "Regates Exitosos"],
        "Pilar 4: Desgaste": ["Minutos", "Tarjetas"]
    }

# 4. ESTÉTICA
st.markdown("""
    <style>
    [data-testid="stSidebar"] {background-color: #1A2B4C !important;}
    [data-testid="stSidebar"] * {color: #FFFFFF !important;}
    .metric-card {background-color: #F8F9FA; border-left: 5px solid #1A2B4C; padding: 12px; border-radius: 5px; margin-bottom: 10px; color: #1A2B4C;}
    .stButton>button {background-color: #C8A165; color: #1A2B4C !important; font-weight: bold; width: 100%;}
    </style>
""", unsafe_allow_html=True)

# 5. NAVEGACIÓN Y SISTEMA DE LOGIN
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # LOGO EN INICIO DE SESIÓN
        col_img_1, col_img_2, col_img_3 = st.columns([1, 2, 1])
        with col_img_2:
            if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
            elif os.path.exists("logo.jpg"): st.image("logo.jpg", use_container_width=True)
            elif os.path.exists("logo.jpeg"): st.image("logo.jpeg", use_container_width=True)
            else: st.markdown("<h1 style='text-align:center; color:#1A2B4C; font-size:45px;'>IGNITION</h1>", unsafe_allow_html=True)
        
        # TEXTO INSTITUCIONAL RESTAURADO
        st.markdown("""
            <div style="text-align:center;">
                <h3 style="color:#1A2B4C; margin-top:5px; margin-bottom:0;">SCOUTING PRO</h3>
                <p style="color:#C8A165; font-size:16px; font-weight:bold; margin-top:5px;">Scouting Internacional y Dirección Deportiva</p>
                <hr style="border-color:#C8A165; margin: 20px 0;">
            </div>
        """, unsafe_allow_html=True)
        
        usuario = st.text_input("Usuario Corporativo")
        password = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR AL SISTEMA"):
            if usuario == "christian" and password == "1234":
                st.session_state['logged_in'] = True; st.rerun()

else:
    with st.sidebar:
        # LOGO EN EL MENÚ LATERAL
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        elif os.path.exists("logo.jpg"): st.image("logo.jpg", use_container_width=True)
        elif os.path.exists("logo.jpeg"): st.image("logo.jpeg", use_container_width=True)
        else: st.markdown("<h2 style='color:#C8A165; text-align:center;'>IGNITION ELITE</h2>", unsafe_allow_html=True)
        
        st.write("---")
        opcion = st.radio("Navegación", [
            "Dashboard Principal", "Ingreso de Data (Partidos)", 
            "Equipo Ignition", "Shortlists", "Comparador", "Scoring por Perfil"
        ])
        st.write("---")
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False; st.rerun()

    # MÓDULO 1: DASHBOARD
    if opcion == "Dashboard Principal":
        st.title("Inteligencia de Mercado y Seguimiento")
        st.markdown("---")
        
        col_img, col_info, col_radar = st.columns([1, 2, 2])
        with col_img:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150)
            
        with col_info:
            posicion_actual = st.selectbox("Posición (Métricas Quirúrgicas):", ["Portero", "Lateral Izquierdo", "Defensa Central", "Extremo", "Delantero"])
            st.markdown(f"**Nombre:** Alisana Yirajang")
            st.markdown(f"**Club:** Slovan | **Edad:** 21")
            
        with col_radar:
            categorias = ['Ataque', 'Creación', 'Defensa', 'Físico', 'Posesión']
            valores = [85, 70, 45, 80, 65]
            angulos = [n / 5 * 2 * math.pi for n in range(5)]; angulos += angulos[:1]; valores += valores[:1]
            fig, ax = plt.subplots(figsize=(2, 2), subplot_kw=dict(polar=True))
            plt.xticks(angulos[:-1], categorias, color='#1A2B4C', size=8)
            ax.plot(angulos, valores, color='#1A2B4C'); ax.fill(angulos, valores, color='#C8A165', alpha=0.5)
            fig.patch.set_facecolor('none'); ax.set_facecolor('none'); ax.set_yticklabels([])
            st.pyplot(fig, use_container_width=True)
            
        st.markdown("### Matriz de Rendimiento p/90")
        metricas_q = obtener_metricas(posicion_actual)
        tabs = st.tabs(list(metricas_q.keys()))
        for i, (pilar, lista_metricas) in enumerate(metricas_q.items()):
            with tabs[i]:
                cols = st.columns(3)
                for j, metrica in enumerate(lista_metricas):
                    cols[j % 3].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165;'>Dato pendiente (API)</span></div>", unsafe_allow_html=True)

    # MÓDULO 2: INGRESO DE DATA
    elif opcion == "Ingreso de Data (Partidos)":
        st.title("📥 Registro de Stats de Partido")
        with st.form("form_partido"):
            st.selectbox("🏆 Competición", LIGAS_MUNDIALES)
            st.form_submit_button("Guardar Estadísticas")

    # MÓDULO 3: EQUIPO IGNITION
    elif opcion == "Equipo Ignition":
        st.title("💼 Equipo Ignition (Gestión de Agencia)")
        
        with st.expander("➕ Añadir Nuevo Jugador a Equipo Ignition"):
            with st.form("nuevo_plantilla"):
                c1, c2 = st.columns(2)
                nuevo_nombre = c1.text_input("Nombre Completo")
                nuevo_status = c1.selectbox("Estatus", ["FIRMADO 🟡", "OBJETIVO 🔵", "SEGUIMIENTO INTENSIVO 🟢"])
                nueva_liga = c2.selectbox("Liga", LIGAS_MUNDIALES)
                nuevo_club = c2.text_input("Club Actual")
                
                if st.form_submit_button("Registrar en Equipo Ignition"):
                    if nuevo_nombre:
                        st.session_state['equipo_ignition'].append({
                            "Jugador": nuevo_nombre, 
                            "Club": nuevo_club, 
                            "Liga": nueva_liga, 
                            "Status": nuevo_status
                        })
                        st.success(f"¡{nuevo_nombre} añadido al equipo!")
                        st.rerun() 
                    else:
                        st.error("Por favor ingresa al menos el nombre.")
                    
        df_p = pd.DataFrame(st.session_state['equipo_ignition'])
        st.dataframe(df_p, use_container_width=True, hide_index=True)

    else:
        st.info(f"Módulo de {opcion} en construcción.")
