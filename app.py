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

# 2. INICIALIZAR MEMORIA (Para simular la base de datos mientras creamos las tablas en Supabase)
if 'scouting_db' not in st.session_state:
    st.session_state['scouting_db'] = [
        {"Nombre": "Alisana Yirajang", "Edad": 21, "Club": "Slovan", "Valor": "€800k", "Overall": 85, "Viabilidad": "🔴 Baja", "Posición": "Extremo", "Foto": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"},
        {"Nombre": "Fidel Ambriz", "Edad": 21, "Club": "Monterrey", "Valor": "€4.5M", "Overall": 87, "Viabilidad": "🟡 Media", "Posición": "Medio", "Foto": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"}
    ]

if 'equipo_ignition' not in st.session_state:
    st.session_state['equipo_ignition'] = [
        {"Nombre": "José Juan Macías", "Edad": 24, "Club": "Pumas", "Liga": "🇲🇽 Liga MX", "Status": "FIRMADO 🟡", "Posición": "Delantero", "Foto": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"}
    ]

# 3. LISTAS Y MÉTRICAS DUALES
LIGAS_MUNDIALES = [
    "🇪🇸 La Liga", "🇪🇸 Liga Hypermotion", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship", 
    "🇫🇷 Ligue 1", "🇮🇹 Serie A", "🇩🇪 Bundesliga", "🇳🇱 Eredivisie", 
    "🇦🇷 Primera División Argentina", "🇲🇽 Liga MX", "🇲🇽 Liga de Expansión", 
    "🇨🇴 Primera División Colombia", "🇧🇷 Brasileirao", "🇺🇾 Primera División Uruguay", 
    "🇺🇸 MLS" 
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

def mostrar_perfil_jugador(jugador):
    st.markdown("---")
    st.subheader(f"👤 Perfil Analítico: {jugador['Nombre']}")
    
    col_img, col_info, col_radar = st.columns([1, 2, 2])
    with col_img:
        st.image(jugador.get('Foto', "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"), width=150)
        
    with col_info:
        st.markdown(f"**Posición Asignada:** {jugador['Posición']}")
        st.markdown(f"**Club:** {jugador['Club']} | **Edad:** {jugador['Edad']}")
        st.markdown(f"**Valor de Mercado:** {jugador.get('Valor', 'N/D')}")
        
    with col_radar:
        categorias = ['Ataque', 'Creación', 'Defensa', 'Físico', 'Posesión']
        valores = [85, 70, 45, 80, 65]
        angulos = [n / 5 * 2 * math.pi for n in range(5)]; angulos += angulos[:1]; valores += valores[:1]
        fig, ax = plt.subplots(figsize=(2, 2), subplot_kw=dict(polar=True))
        plt.xticks(angulos[:-1], categorias, color='#1A2B4C', size=8)
        ax.plot(angulos, valores, color='#1A2B4C'); ax.fill(angulos, valores, color='#C8A165', alpha=0.5)
        fig.patch.set_facecolor('none'); ax.set_facecolor('none'); ax.set_yticklabels([])
        st.pyplot(fig, use_container_width=True)
        
    st.markdown(f"### Matriz de Rendimiento p/90 ({jugador['Posición']})")
    metricas_q = obtener_metricas(jugador['Posición'])
    tabs = st.tabs(list(metricas_q.keys()))
    for i, (pilar, lista_metricas) in enumerate(metricas_q.items()):
        with tabs[i]:
            cols = st.columns(3)
            for j, metrica in enumerate(lista_metricas):
                cols[j % 3].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165;'>API</span></div>", unsafe_allow_html=True)

# 4. ESTÉTICA
st.markdown("""
    <style>
    [data-testid="stSidebar"] {background-color: #1A2B4C !important;}
    [data-testid="stSidebar"] * {color: #FFFFFF !important;}
    .metric-card {background-color: #F8F9FA; border-left: 5px solid #1A2B4C; padding: 12px; border-radius: 5px; margin-bottom: 10px; color: #1A2B4C;}
    .stButton>button {background-color: #C8A165; color: #1A2B4C !important; font-weight: bold; width: 100%;}
    </style>
""", unsafe_allow_html=True)

# 5. NAVEGACIÓN Y LOGIN
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_img_1, col_img_2, col_img_3 = st.columns([1, 2, 1])
        with col_img_2:
            if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
            elif os.path.exists("logo.jpg"): st.image("logo.jpg", use_container_width=True)
            else: st.markdown("<h1 style='text-align:center; color:#1A2B4C; font-size:45px;'>IGNITION</h1>", unsafe_allow_html=True)
        
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
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        elif os.path.exists("logo.jpg"): st.image("logo.jpg", use_container_width=True)
        else: st.markdown("<h2 style='color:#C8A165; text-align:center;'>IGNITION ELITE</h2>", unsafe_allow_html=True)
        
        st.write("---")
        opcion = st.radio("Navegación", [
            "Dashboard General (Scouting)", "Equipo Ignition", 
            "Ingreso de Data (Partidos)", "Comparador"
        ])
        st.write("---")
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False; st.rerun()

    # MÓDULO 1: DASHBOARD (Tabla Interactiva)
    if opcion == "Dashboard General (Scouting)":
        st.title("Inteligencia de Mercado y Seguimiento")
        st.caption("Haz clic en la fila de un jugador para ver sus estadísticas completas.")
        
        df_scouting = pd.DataFrame(st.session_state['scouting_db'])
        
        # Tabla interactiva
        seleccion = st.dataframe(
            df_scouting[["Nombre", "Edad", "Club", "Valor", "Overall", "Viabilidad"]], 
            use_container_width=True, 
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Lógica de despliegue al hacer clic
        if len(seleccion.selection.rows) > 0:
            idx = seleccion.selection.rows[0]
            jugador_seleccionado = st.session_state['scouting_db'][idx]
            mostrar_perfil_jugador(jugador_seleccionado)
            
        st.markdown("---")
        with st.expander("➕ Añadir Jugador a Base de Scouting"):
            with st.form("nuevo_scouting"):
                c1, c2 = st.columns(2)
                n_nombre = c1.text_input("Nombre")
                n_edad = c1.number_input("Edad", 15, 40, 20)
                n_club = c1.text_input("Club")
                n_posicion = c2.selectbox("Posición (Define sus métricas)", ["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"])
                n_valor = c2.text_input("Valor de Mercado")
                n_foto = st.text_input("URL de su Fotografía (Opcional)", "https://cdn-icons-png.flaticon.com/512/3135/3135715.png")
                
                if st.form_submit_button("Guardar Jugador"):
                    nuevo = {"Nombre": n_nombre, "Edad": n_edad, "Club": n_club, "Valor": n_valor, "Overall": 70, "Viabilidad": "🟡 Media", "Posición": n_posicion, "Foto": n_foto}
                    st.session_state['scouting_db'].append(nuevo)
                    # Aquí irá: supabase.table('scouting').insert(nuevo).execute()
                    st.rerun()

    # MÓDULO 2: EQUIPO IGNITION (Tabla Interactiva)
    elif opcion == "Equipo Ignition":
        st.title("💼 Equipo Ignition")
        st.caption("Haz clic en la fila de un jugador para desplegar su ficha de rendimiento.")
        
        df_equipo = pd.DataFrame(st.session_state['equipo_ignition'])
        
        seleccion_eq = st.dataframe(
            df_equipo[["Nombre", "Edad", "Club", "Liga", "Status"]], 
            use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row"
        )
        
        if len(seleccion_eq.selection.rows) > 0:
            idx_eq = seleccion_eq.selection.rows[0]
            jugador_eq = st.session_state['equipo_ignition'][idx_eq]
            mostrar_perfil_jugador(jugador_eq)

        st.markdown("---")
        with st.expander("➕ Añadir Jugador a Equipo Ignition"):
            with st.form("nuevo_equipo"):
                c1, c2 = st.columns(2)
                e_nombre = c1.text_input("Nombre Completo")
                e_edad = c1.number_input("Edad", 15, 45, 20)
                e_posicion = c1.selectbox("Posición (Define sus métricas)", ["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"])
                e_status = c1.selectbox("Estatus", ["FIRMADO 🟡", "OBJETIVO 🔵", "SEGUIMIENTO INTENSIVO 🟢"])
                e_liga = c2.selectbox("Liga", LIGAS_MUNDIALES)
                e_club = c2.text_input("Club Actual")
                e_foto = st.text_input("URL de su Fotografía", "https://cdn-icons-png.flaticon.com/512/3135/3135715.png")
                
                if st.form_submit_button("Registrar en Equipo Ignition"):
                    nuevo_eq = {"Nombre": e_nombre, "Edad": e_edad, "Posición": e_posicion, "Club": e_club, "Liga": e_liga, "Status": e_status, "Foto": e_foto}
                    st.session_state['equipo_ignition'].append(nuevo_eq)
                    # Aquí irá: supabase.table('equipo').insert(nuevo_eq).execute()
                    st.rerun() 

    # MÓDULO 3: INGRESO DE DATA (Restaurado)
    elif opcion == "Ingreso de Data (Partidos)":
        st.title("📥 Registro Manual de Estadísticas")
        st.caption("Carga los datos partido a partido. El sistema calculará el p/90 automáticamente.")
        
        with st.form("form_partido"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Nombre del Jugador")
                st.selectbox("🏆 Competición / Torneo", LIGAS_MUNDIALES)
            with col2:
                st.selectbox("Jornada", [f"Jornada {i}" for i in range(1, 39)])
                st.checkbox("Convocatoria sin minutos (Solo experiencia)")
                
            st.markdown("#### Datos del Partido")
            c1, c2, c3, c4 = st.columns(4)
            with c1: 
                st.number_input("Minutos Jugados", 0, 120, 90)
                st.number_input("Goles", 0, 10, 0)
            with c2: 
                st.number_input("Asistencias", 0, 10, 0)
                st.number_input("Tiros a Puerta", 0, 20, 0)
            with c3:
                st.number_input("Pases Clave", 0, 20, 0)
                st.number_input("Duelos Ganados", 0, 40, 0)
            with c4:
                st.number_input("Intercepciones", 0, 30, 0)
                st.number_input("Faltas Cometidas", 0, 20, 0)
                
            if st.form_submit_button("Guardar en Base de Datos"):
                st.success("¡Estadísticas registradas exitosamente para este partido!")
                # Aquí irá el comando insert hacia la tabla 'estadisticas' en Supabase

    else:
        st.info(f"Módulo en construcción.")
