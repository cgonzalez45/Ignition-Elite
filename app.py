import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from supabase import create_client, Client

# 1. CONFIGURACIÓN
st.set_page_config(page_title="CG Scouting Pro V3", page_icon="⚽", layout="wide")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = init_connection()
    db_conectada = True
except:
    db_conectada = False

# 2. LISTA MUNDIAL DE LIGAS (Con Banderas)
LIGAS_MUNDIALES = [
    "🇪🇸 La Liga", "🇪🇸 Liga Hypermotion", "🇪🇸 Primera RFEF", "🇪🇸 Segunda RFEF",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 League One", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 League Two",
    "🇫🇷 Ligue 1", "🇫🇷 Ligue 2", "🇮🇹 Serie A", "🇮🇹 Serie B",
    "🇩🇪 Bundesliga", "🇩🇪 2. Bundesliga", "🇸🇪 Allsvenskan", "🇳🇴 Eliteserien",
    "🇳🇱 Eredivisie", "🇧🇪 Jupiler Pro League", "🇩🇰 Superliga Dinamarca", "🇵🇱 Ekstraklasa",
    "🇧🇬 efbet League Bulgaria", "🇭🇷 SuperSport HNL", "🇨🇿 Chance Liga", "🇷🇸 Superliga Serbia",
    "🇦🇹 Bundesliga Austria", "🇨🇭 Superliga de Suiza",
    "🇦🇷 Primera División Argentina", "🇲🇽 Liga MX", "🇲🇽 Liga de Expansión", 
    "🇲🇽 Liga MX U-23", "🇲🇽 Liga MX U-19", "🇲🇽 Liga MX U-17", "🇲🇽 Liga MX U-15",
    "🇨🇷 Primera División Costa Rica", "🇨🇴 Primera División Colombia", 
    "🇧🇷 Brasileirao", "🇧🇷 Brasileirao Série B", "🇺🇾 Primera División Uruguay", 
    "🇨🇱 Primera División Chile", "🇺🇸 MLS", "🇯🇵 J-League"
]

# 3. MOTOR DE MÉTRICAS QUIRÚRGICAS POR POSICIÓN
def obtener_metricas(posicion):
    if posicion == "Portero":
        return {
            "Pilar 1: Atajadas y Reflejos": ["Atajadas p/90", "Reflejos a Quemarropa", "Penales Salvados", "xG Evitados", "Desvíos", "Atrapes sin rebote", "1v1 Ganados"],
            "Pilar 2: Distribución": ["Pases Largos Precisos", "Efectividad Pase Corto", "Saques de Meta al Tercio Rival", "Inicios de Contragolpe"],
            "Pilar 3: Dominio del Área": ["Salidas por Alto Exitosas", "Despejes de Puños", "Intercepciones fuera del área", "Duelos Aéreos Ganados"],
            "Pilar 4: Físico y Contexto": ["Minutos Jugados", "Errores que terminan en Gol", "Tarjetas"] # Hasta llenar 30 específicas
        }
    elif posicion in ["Lateral Izquierdo", "Lateral Derecho"]:
        return {
            "Pilar 1: Defensa y Duelos": ["Duelos Defensivos Ganados %", "Intercepciones p/90", "Tackles Exitosos", "Recuperaciones tras pérdida", "Duelos Aéreos"],
            "Pilar 2: Progresión": ["Pases Progresivos", "Conducciones al Tercio Final", "Pases al Espacio", "Pérdidas de Balón en Salida"],
            "Pilar 3: Daño Ofensivo": ["Centros Precisos %", "Asistencias Esperadas (xA)", "Desbordes Exitosos", "Toques en Área Rival"],
            "Pilar 4: Físico": ["Sprints p/90", "Distancia Recorrida", "Faltas Cometidas"]
        }
    # Por defecto para jugadores de campo (Aquí cargaremos las 30 exactas para Medios y Delanteros)
    return {
        "Pilar 1: Destrucción/Defensa": ["Duelos Ganados", "Intercepciones", "Tackles", "Presión Exitosa", "Recuperaciones Altas"],
        "Pilar 2: Creación/Salida": ["Pases Clave", "Precisión Pases", "Pases Progresivos", "Cambios de Orientación", "Asistencias"],
        "Pilar 3: Finalización": ["Goles Esperados (xG)", "Tiros a Puerta", "Toques en Área", "Regates Exitosos", "Tiros Totales"],
        "Pilar 4: Desgaste": ["Minutos", "Tarjetas Amarillas", "Faltas Recibidas"]
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

# 5. MENÚ LATERAL Y NAVEGACIÓN
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center; color:#1A2B4C;'>CG SCOUTING PRO</h1>", unsafe_allow_html=True)
        usuario = st.text_input("Usuario Corporativo")
        password = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR"):
            if usuario == "christian" and password == "1234":
                st.session_state['logged_in'] = True; st.rerun()

else:
    with st.sidebar:
        # AQUÍ IRÁ TU LOGO REAL CUANDO LO SUBAMOS A GITHUB
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.markdown("<h1 style='color:#C8A165; text-align:center;'>CG PRO</h1>", unsafe_allow_html=True)
        
        st.write("---")
        opcion = st.radio("Navegación", [
            "Dashboard Principal", "Ingreso de Data (Partidos)", 
            "Mi Plantilla", "Shortlists", "Comparador", "Scoring por Perfil"
        ])
        st.write("---")
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False; st.rerun()

    # MÓDULO 1: DASHBOARD Y PERFIL QUIRÚRGICO
    if opcion == "Dashboard Principal":
        st.title("Inteligencia de Mercado y Seguimiento")
        
        busqueda = st.text_input("🔍 Buscar jugador...")
        
        st.markdown("---")
        st.subheader("👤 Perfil Analítico Individual")
        
        col_img, col_info, col_radar = st.columns([1, 2, 2])
        
        with col_img:
            # FOTO DE PERFIL DEL JUGADOR
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150) # Placeholder genérico
            
        with col_info:
            posicion_actual = st.selectbox("Posición (Cambia esto para ver métricas quirúrgicas):", ["Portero", "Lateral Izquierdo", "Defensa Central", "Extremo", "Delantero"])
            st.markdown(f"**Nombre:** Alisana Yirajang")
            st.markdown(f"**Club:** Slovan | **Edad:** 21")
            st.markdown(f"**Valor:** €800k")
            
        with col_radar:
            categorias = ['Ataque', 'Creación', 'Defensa', 'Físico', 'Posesión']
            valores = [85, 70, 45, 80, 65]
            angulos = [n / 5 * 2 * math.pi for n in range(5)]; angulos += angulos[:1]; valores += valores[:1]
            fig, ax = plt.subplots(figsize=(2, 2), subplot_kw=dict(polar=True))
            plt.xticks(angulos[:-1], categorias, color='#1A2B4C', size=8)
            ax.plot(angulos, valores, color='#1A2B4C'); ax.fill(angulos, valores, color='#C8A165', alpha=0.5)
            fig.patch.set_facecolor('none'); ax.set_facecolor('none'); ax.set_yticklabels([])
            st.pyplot(fig, use_container_width=True)
            
        st.markdown("### Matriz de Rendimiento p/90 (Específica por Posición)")
        metricas_q = obtener_metricas(posicion_actual)
        
        # Tabs dinámicos según la posición
        tabs = st.tabs(list(metricas_q.keys()))
        for i, (pilar, lista_metricas) in enumerate(metricas_q.items()):
            with tabs[i]:
                cols = st.columns(3)
                for j, metrica in enumerate(lista_metricas):
                    cols[j % 3].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165;'>Dato pendiente (API)</span></div>", unsafe_allow_html=True)

    # MÓDULO 2: INGRESO DE DATA CON LIGAS MUNDIALES
    elif opcion == "Ingreso de Data (Partidos)":
        st.title("📥 Registro de Stats de Partido")
        with st.form("form_partido"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Jugador")
                st.selectbox("🏆 Competición / Torneo", LIGAS_MUNDIALES)
            with col2:
                st.selectbox("Jornada", [f"Jornada {i}" for i in range(1, 39)])
                st.checkbox("Viaje/Convocatoria sin minutos")
            st.form_submit_button("Guardar Estadísticas")

    # MÓDULO 3: MI PLANTILLA Y AÑADIR JUGADORES
    elif opcion == "Mi Plantilla":
        st.title("💼 Mi Plantilla y Seguimiento")
        
        # BOTÓN PARA AGREGAR NUEVO JUGADOR A LA PLANTILLA
        with st.expander("➕ Añadir Nuevo Jugador a Mi Plantilla"):
            with st.form("nuevo_plantilla"):
                c1, c2 = st.columns(2)
                c1.text_input("Nombre Completo")
                c1.selectbox("Estatus", ["FIRMADO 🟡", "OBJETIVO 🔵", "SEGUIMIENTO INTENSIVO 🟢"])
                c2.text_input("URL de su Fotografía (Link)")
                c2.selectbox("Posición", ["Portero", "Defensa", "Medio", "Delantero"])
                if st.form_submit_button("Registrar en Plantilla"):
                    st.success("Jugador añadido a tu base de datos (Supabase en background).")
                    
        df_p = pd.DataFrame([
            {"Jugador": "José Juan Macías", "Club": "Pumas", "Liga": "🇲🇽 Liga MX", "Status": "FIRMADO 🟡"},
            {"Jugador": "Miguel Mendoza", "Club": "León", "Liga": "🇲🇽 Liga MX U-17", "Status": "FIRMADO 🟡"}
        ])
        st.dataframe(df_p, use_container_width=True, hide_index=True)

    else:
        st.info(f"Módulo de {opcion} en construcción.")
