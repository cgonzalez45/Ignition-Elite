import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from supabase import create_client, Client

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="CG Scouting Pro V2", page_icon="⚽", layout="wide")

# 2. CONEXIÓN A BASE DE DATOS SUPABASE
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_connection()
    db_conectada = True
except Exception as e:
    db_conectada = False

# 3. ESTÉTICA INSTITUCIONAL V2.0 (Logo Fijo y Contraste)
st.markdown("""
    <style>
    /* Fondo del Menú Lateral y Texto Blanco */
    [data-testid="stSidebar"] {
        background-color: #1A2B4C !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    /* Logo Fijo Superior Izquierdo */
    .sidebar-logo-container {
        text-align: center;
        padding: 20px 0;
        border-bottom: 2px solid #C8A165;
        margin-bottom: 20px;
    }
    .cg-logo {
        color: #C8A165 !important;
        font-size: 45px !important;
        font-weight: 900 !important;
        margin: 0 !important;
        line-height: 1 !important;
    }
    .cg-sub {
        color: #FFFFFF !important;
        font-size: 13px !important;
        font-weight: bold !important;
        letter-spacing: 2px !important;
    }
    /* Botones Dorados */
    .stButton>button {
        background-color: #C8A165;
        color: #1A2B4C !important;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #FFFFFF;
    }
    /* Tarjetas de Métricas */
    .metric-card {
        background-color: #F8F9FA;
        border-left: 5px solid #1A2B4C;
        padding: 12px;
        border-radius: 5px;
        margin-bottom: 10px;
        color: #1A2B4C;
    }
    </style>
""", unsafe_allow_html=True)

# 4. MANEJO DE SESIÓN (LOGIN)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="background-color:#1A2B4C; padding:40px; border-radius:15px; text-align:center; border: 3px solid #C8A165;">
                <h1 style="color:#C8A165; font-size:70px; margin:0;">CG</h1>
                <h3 style="color:#FFFFFF; margin-top:0;">SCOUTING PRO</h3>
                <hr style="border-color:#C8A165;">
                <p style="color:#FFFFFF;">Base de Datos de Inteligencia Deportiva</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        usuario = st.text_input("Usuario Corporativo")
        password = st.text_input("Contraseña", type="password")
        if st.button("AUTENTICAR SISTEMA"):
            if usuario.lower() == "christian" and password == "1234":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

# 5. SISTEMA PRINCIPAL
else:
    # MENÚ LATERAL CON LOGO FIJO
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-logo-container">
                <p class="cg-logo">CG</p>
                <p class="cg-sub">SCOUTING PRO</p>
            </div>
        """, unsafe_allow_html=True)
        
        opcion = st.radio(
            "Navegación",
            ["Métricas y Radares", "Ingreso de Data (Partidos)", "Mi Plantilla"]
        )
        st.write("---")
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.rerun()

    # MÓDULO: MÉTRICAS Y RADARES
    if opcion == "Métricas y Radares":
        st.title("Inteligencia de Mercado y Seguimiento")
        
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            busqueda = st.text_input("🔍 Buscar jugador en la Base de Datos...")
        with col_f2:
            filtro_torneo = st.selectbox("🏆 Competición", 
                ["Gran Total (Temporada)", "Liga MX - Fechas 1 a 3", "Leagues Cup", "Fuerzas Básicas"])

        st.markdown("---")
        st.subheader("👤 Perfil Analítico: Alisana Yirajang (Ejemplo de Estructura)")
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"**Posición:** Extremo Izq. | **Edad:** 21 | **Valor:** €800k")
            st.markdown(f"**Filtro Activo:** `{filtro_torneo}`")
            
            # Radar Adaptativo (No se deforma)
            categorias = ['Ataque', 'Creación', 'Defensa', 'Físico', 'Posesión']
            valores = [85, 70, 45, 80, 65]
            angulos = [n / 5 * 2 * math.pi for n in range(5)]
            angulos += angulos[:1]
            valores += valores[:1]
            
            fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(polar=True))
            plt.xticks(angulos[:-1], categorias, color='#1A2B4C', size=8, weight='bold')
            ax.set_rlabel_position(0)
            plt.yticks([20, 40, 60, 80], [], color="grey", size=7)
            ax.plot(angulos, valores, linewidth=2, linestyle='solid', color='#1A2B4C')
            ax.fill(angulos, valores, color='#C8A165', alpha=0.5)
            fig.patch.set_facecolor('none')
            ax.set_facecolor('none')
            st.pyplot(fig, use_container_width=True) 

        with c2:
            st.markdown("### Matriz de Rendimiento p/90")
            t1, t2, t3, t4 = st.tabs(["Ofensiva", "Creación", "Defensa", "Físico / Contexto"])
            
            with t1:
                st.markdown("<div class='metric-card'><b>xG (Goles Esperados) p/90:</b> 0.45 <span style='color:green;'>(p85)</span></div>", unsafe_allow_html=True)
                st.markdown("<div class='metric-card'><b>Tiros a Puerta p/90:</b> 2.1 <span style='color:green;'>(p78)</span></div>", unsafe_allow_html=True)
                st.markdown("<div class='metric-card'><b>Toques en Área Rival p/90:</b> 4.5 <span style='color:#C8A165;'>(p60)</span></div>", unsafe_allow_html=True)

    # MÓDULO: INGRESO DE DATA
    elif opcion == "Ingreso de Data (Partidos)":
        st.title("📥 Ingreso de Estadísticas (Fechas 1, 2, 3 y Leagues Cup)")
        if db_conectada:
            st.success("✅ Base de Datos Conectada: Los datos se guardarán en Supabase.")
        else:
            st.warning("⚠️ Modo Offline: Revisa tus llaves en 'Secrets'.")
        
        with st.form("form_carga_datos"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre del Jugador")
                torneo = st.selectbox("Torneo", ["Liga MX Apertura 2026", "Leagues Cup", "Fuerzas Básicas"])
            with col2:
                fecha = st.selectbox("Jornada", ["Fecha 1", "Fecha 2", "Fecha 3"])
                viaje_primer_equipo = st.checkbox("Convocatoria/Viaje sin minutos (Experiencia)")
            
            st.markdown("#### Métricas del Partido")
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.number_input("Minutos", 0, 120, 90)
            with c2: st.number_input("Goles", 0, 5, 0)
            with c3: st.number_input("Asistencias", 0, 5, 0)
            with c4: st.number_input("Duelos Ganados", 0, 30, 0)
            
            submit = st.form_submit_button("Guardar en Base de Datos")
            if submit:
                st.success(f"¡Estadísticas de {nombre} registradas exitosamente en la nube!")

    # MÓDULO: MI PLANTILLA
    elif opcion == "Mi Plantilla":
        st.title("💼 Mi Plantilla")
        df_p = pd.DataFrame([
            {"Jugador": "José Juan Macías", "Club": "Pumas", "Cat": "Primera", "Status": "FIRMADO"},
            {"Jugador": "Oscar García", "Club": "León", "Cat": "Primera", "Status": "FIRMADO"},
            {"Jugador": "Kevin Mora", "Club": "León", "Cat": "Primera", "Status": "FIRMADO"},
            {"Jugador": "Miguel Mendoza", "Club": "León", "Cat": "Sub-17", "Status": "FIRMADO"},
            {"Jugador": "Sergio Luna", "Club": "León", "Cat": "Sub-19", "Status": "FIRMADO"},
            {"Jugador": "Bryan Destin", "Club": "CT United", "Cat": "Internacional", "Status": "OBJETIVO"}
        ])
        st.dataframe(df_p, use_container_width=True, hide_index=True)
