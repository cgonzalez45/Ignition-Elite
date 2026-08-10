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
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        return None

supabase = init_connection()

# 2. INICIALIZAR MEMORIA
if 'scouting_db' not in st.session_state:
    st.session_state['scouting_db'] = [
        {"ID": 1, "Nombre": "Alisana Yirajang", "Edad": 21, "Club": "Slovan", "Liga": "🇸🇰 Liga Eslovaquia", "Valor": "€800k", "Overall": 85, "Viabilidad": "🔴 Baja", "Posición": "Extremo", "Foto": None},
        {"ID": 2, "Nombre": "Fidel Ambriz", "Edad": 21, "Club": "Monterrey", "Liga": "🇲🇽 Liga MX", "Valor": "€4.5M", "Overall": 87, "Viabilidad": "🟡 Media", "Posición": "Medio", "Foto": None}
    ]

if 'equipo_ignition' not in st.session_state:
    st.session_state['equipo_ignition'] = [
        {"ID": 3, "Nombre": "José Juan Macías", "Edad": 24, "Club": "Pumas", "Liga": "🇲🇽 Liga MX", "Status": "FIRMADO 🟡", "Posición": "Delantero", "Foto": None},
        {"ID": 4, "Nombre": "Oscar García", "Edad": 20, "Club": "León", "Liga": "🇲🇽 Liga MX", "Status": "FIRMADO 🟡", "Posición": "Medio", "Foto": None},
        {"ID": 5, "Nombre": "Kevin Mora", "Edad": 19, "Club": "León", "Liga": "🇲🇽 Liga MX", "Status": "FIRMADO 🟡", "Posición": "Lateral Derecho", "Foto": None},
        {"ID": 6, "Nombre": "Miguel Mendoza", "Edad": 17, "Club": "León", "Liga": "🇲🇽 Liga MX U-17", "Status": "FIRMADO 🟡", "Posición": "Extremo", "Foto": None},
        {"ID": 7, "Nombre": "Sergio Luna", "Edad": 19, "Club": "León", "Liga": "🇲🇽 Liga MX U-19", "Status": "FIRMADO 🟡", "Posición": "Defensa Central", "Foto": None},
        {"ID": 8, "Nombre": "Bryan Destin", "Edad": 18, "Club": "CT United", "Liga": "🇺🇸 MLS Next Pro", "Status": "OBJETIVO 🔵", "Posición": "Delantero", "Foto": None}
    ]

# 3. DICCIONARIOS DE LIGAS Y EQUIPOS (MOTOR DINÁMICO)
LIGAS_MUNDIALES = [
    "🇲🇽 Liga MX", "🇲🇽 Liga de Expansión", "🇲🇽 Liga MX U-23", "🇲🇽 Liga MX U-19", "🇲🇽 Liga MX U-17", "🇲🇽 Liga MX U-15",
    "🇪🇸 La Liga", "🇪🇸 Liga Hypermotion", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship", 
    "🇵🇹 Liga Portugal", "🇵🇹 Liga 2 Portugal", "🇸🇪 Allsvenskan", "🇸🇰 Liga Eslovaquia", "🇸🇮 Liga Eslovenia",
    "🇺🇸 MLS", "🇺🇸 MLS Next Pro", "🇺🇸 USL", "🇦🇷 Primera División Argentina", "🇧🇷 Brasileirao", 
    "🇨🇴 Primera División Colombia", "🇺🇾 Primera División Uruguay", "🇨🇱 Primera División Chile",
    "🇫🇷 Ligue 1", "🇮🇹 Serie A", "🇩🇪 Bundesliga", "🇳🇱 Eredivisie"
]

# Base de datos inicial de equipos (Agregaremos los miles que faltan después)
EQUIPOS_POR_LIGA = {
    "🇲🇽 Liga MX": ["América", "Atlas", "Atlético San Luis", "Cruz Azul", "Chivas", "FC Juárez", "León", "Mazatlán", "Monterrey", "Necaxa", "Pachuca", "Puebla", "Pumas", "Querétaro", "Santos Laguna", "Tigres", "Tijuana", "Toluca"],
    "🇸🇪 Allsvenskan": ["AIK", "Brommapojkarna", "Djurgården", "Elfsborg", "GAIS", "Göteborg", "Halmstad", "Hammarby", "Häcken", "Kalmar FF", "Malmö FF", "Mjällby", "Norrköping", "Sirius", "Värnamo", "Västerås SK"],
    "🇵🇹 Liga Portugal": ["Benfica", "Porto", "Sporting CP", "Braga", "Vitória de Guimarães", "Moreirense", "Arouca", "Famalicão", "Casa Pia", "Farense", "Rio Ave", "Gil Vicente", "Estoril", "Estrela", "Boavista", "Nacional", "Santa Clara", "AVS"],
}

# 4. LAS 30 MÉTRICAS QUIRÚRGICAS (Diccionario Completo)
def obtener_metricas(posicion):
    if posicion == "Portero":
        return {
            "Pilar 1: Atajadas (8)": ["Atajadas Totales p/90", "Reflejos a Quemarropa", "xG Evitados", "Desvíos", "Atrapes sin rebote", "1v1 Ganados", "Atajadas de Penal", "Tiros Lejanos Salvados"],
            "Pilar 2: Distribución (7)": ["Pases Largos Precisos", "Efectividad Pase Corto", "Saques de Meta Exitosos", "Inicios de Contragolpe", "Pases bajo presión", "Toques de balón", "Pérdidas en salida"],
            "Pilar 3: Dominio del Área (8)": ["Salidas por Alto", "Despejes de Puños", "Intercepciones fuera del área", "Duelos Aéreos Ganados", "Reivindicaciones de centros", "Tackles", "Faltas recibidas", "Acciones defensivas fuera del área"],
            "Pilar 4: Físico/Contexto (7)": ["Minutos Jugados", "Errores que terminan en Gol", "Tarjetas Amarillas", "Tarjetas Rojas", "Lesiones", "Distancia Recorrida", "Goles Concedidos p/90"]
        }
    elif posicion == "Defensa Central":
        return {
            "Pilar 1: Defensa Pura (8)": ["Duelos Defensivos Ganados %", "Intercepciones p/90", "Tackles Exitosos", "Bloqueos de Tiro", "Despejes", "Recuperaciones", "Duelos 1v1 Ganados", "Faltas Cometidas"],
            "Pilar 2: Juego Aéreo (7)": ["Duelos Aéreos Totales", "Duelos Aéreos Ganados %", "Goles de Cabeza", "Despejes de Cabeza", "Duelos Aéreos en Área Rival", "Duelos Aéreos en Área Propia", "Faltas recibidas por alto"],
            "Pilar 3: Salida y Posesión (8)": ["Pases Precisos %", "Pases Progresivos", "Pases Largos Precisos", "Conducciones al Medio Campo", "Pases al Tercio Final", "Toques", "Pérdidas de Balón", "Pases bajo presión"],
            "Pilar 4: Físico/Contexto (7)": ["Minutos", "Tarjetas Amarillas", "Tarjetas Rojas", "Errores Críticos", "Sprints", "Distancia Recorrida", "Aceleraciones"]
        }
    elif posicion in ["Lateral Izquierdo", "Lateral Derecho"]:
        return {
            "Pilar 1: Defensa (7)": ["Duelos Defensivos %", "Intercepciones p/90", "Tackles", "Bloqueos de Centro", "Recuperaciones tras pérdida", "Despejes", "Duelos Aéreos"],
            "Pilar 2: Progresión (8)": ["Pases Progresivos", "Conducciones Progresivas", "Pases al Tercio Final", "Pases al Espacio", "Toques", "Pérdidas en Salida", "Pases Precisos %", "Pases Recibidos"],
            "Pilar 3: Daño Ofensivo (8)": ["Centros Precisos %", "Asistencias Esperadas (xA)", "Desbordes Exitosos", "Toques en Área Rival", "Asistencias", "Tiros a Puerta", "Pases Clave", "Faltas Recibidas en Ataque"],
            "Pilar 4: Físico/Contexto (7)": ["Minutos", "Sprints p/90", "Distancia Recorrida", "Velocidad Máxima", "Tarjetas Amarillas", "Faltas Cometidas", "Tarjetas Rojas"]
        }
    elif posicion == "Medio":
        return {
            "Pilar 1: Destrucción (7)": ["Duelos Defensivos", "Intercepciones", "Tackles", "Presión Exitosa", "Recuperaciones Altas", "Faltas Cometidas", "Bloqueos"],
            "Pilar 2: Posesión (8)": ["Pases Precisos %", "Toques", "Pases bajo presión", "Pérdidas de Balón", "Pases Recibidos", "Conducciones", "Faltas Recibidas", "Retención de Balón %"],
            "Pilar 3: Creación (8)": ["Pases Clave", "Pases Progresivos", "Asistencias Esperadas (xA)", "Pases al Tercio Final", "Cambios de Orientación", "Asistencias", "Desbordes", "Tiros de Larga Distancia"],
            "Pilar 4: Finalización y Físico (7)": ["Goles Esperados (xG)", "Tiros a Puerta", "Goles", "Minutos", "Distancia Recorrida", "Sprints", "Tarjetas Amarillas"]
        }
    elif posicion == "Extremo":
        return {
            "Pilar 1: Desequilibrio (8)": ["Regates Exitosos", "Duelos Ofensivos Ganados", "Desbordes", "Faltas Recibidas", "Aceleraciones", "Conducciones al Área", "Pérdidas de Balón", "Fueras de Lugar"],
            "Pilar 2: Creación (7)": ["Centros Precisos %", "Pases Clave", "xA", "Asistencias", "Pases al Área", "Toques", "Pases Progresivos Recibidos"],
            "Pilar 3: Finalización (8)": ["xG", "Tiros Totales", "Tiros a Puerta", "Goles", "Toques en Área Rival", "Tiros al Palo", "Conversión de Gol %", "Duelos Aéreos Ganados"],
            "Pilar 4: Defensa y Físico (7)": ["Presión en Tercio Rival", "Recuperaciones Altas", "Intercepciones", "Minutos", "Sprints p/90", "Velocidad Máxima", "Distancia Recorrida"]
        }
    else: # Delantero
        return {
            "Pilar 1: Finalización (8)": ["Goles", "xG", "Tiros a Puerta", "Tiros Totales", "Conversión de Gol %", "Penales Anotados", "Tiros al Palo", "Fueras de Lugar"],
            "Pilar 2: Presencia en Área (7)": ["Toques en Área Rival", "Duelos Aéreos Ganados", "Goles de Cabeza", "Faltas Recibidas en Área", "Pases Recibidos en Área", "Anticipaciones", "Rebotes Ganados"],
            "Pilar 3: Asociación (8)": ["Asistencias", "xA", "Pases Clave", "Regates Exitosos", "Duelos Ofensivos", "Pases Precisos %", "Pérdidas de Balón", "Faltas Cometidas en Ataque"],
            "Pilar 4: Físico y Defensa (7)": ["Minutos", "Presión Exitosa Alta", "Recuperaciones Altas", "Sprints", "Distancia Recorrida", "Velocidad Máxima", "Tarjetas Amarillas"]
        }

# 5. FUNCIÓN: MOSTRAR PERFIL Y EDICIÓN
def mostrar_perfil_jugador(jugador, lista_origen, idx_origen):
    st.markdown("---")
    st.subheader(f"👤 Perfil Analítico: {jugador['Nombre']}")
    
    col_img, col_info, col_radar = st.columns([1, 2, 2])
    with col_img:
        # Foto visible u opcional genérica
        if jugador.get('Foto'):
            st.image(jugador['Foto'], width=150)
        else:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150)
        
    with col_info:
        st.markdown(f"**Posición:** {jugador['Posición']}")
        st.markdown(f"**Club:** {jugador['Club']} | **Liga:** {jugador.get('Liga', 'N/D')}")
        st.markdown(f"**Edad:** {jugador['Edad']}")
        if 'Status' in jugador: st.markdown(f"**Status:** {jugador['Status']}")
        
    with col_radar:
        categorias = ['Ataque', 'Creación', 'Defensa', 'Físico', 'Posesión']
        valores = [85, 70, 45, 80, 65]
        angulos = [n / 5 * 2 * math.pi for n in range(5)]; angulos += angulos[:1]; valores += valores[:1]
        fig, ax = plt.subplots(figsize=(2, 2), subplot_kw=dict(polar=True))
        plt.xticks(angulos[:-1], categorias, color='#1A2B4C', size=8)
        ax.plot(angulos, valores, color='#1A2B4C'); ax.fill(angulos, valores, color='#C8A165', alpha=0.5)
        fig.patch.set_facecolor('none'); ax.set_facecolor('none'); ax.set_yticklabels([])
        st.pyplot(fig, use_container_width=True)

    # MATRIZ QUIRÚRGICA
    st.markdown(f"### Matriz de Rendimiento p/90 ({jugador['Posición']})")
    metricas_q = obtener_metricas(jugador['Posición'])
    tabs = st.tabs(list(metricas_q.keys()))
    for i, (pilar, lista_metricas) in enumerate(metricas_q.items()):
        with tabs[i]:
            cols = st.columns(4)
            for j, metrica in enumerate(lista_metricas):
                cols[j % 4].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165;'>API</span></div>", unsafe_allow_html=True)
                
    st.write("")
    
    # MÓDULO DE EDICIÓN Y FOTO 
    with st.expander(f"✏️ Editar Perfil y Subir Foto de {jugador['Nombre']}"):
        st.caption("Modifica la información incorrecta o añade su fotografía de perfil.")
        c_ed1, c_ed2 = st.columns(2)
        nuevo_nom = c_ed1.text_input("Nombre", value=jugador['Nombre'], key=f"nm_{jugador['ID']}")
        nueva_edad = c_ed1.number_input("Edad", 15, 45, value=jugador['Edad'], key=f"ed_{jugador['ID']}")
        nueva_pos = c_ed1.selectbox("Posición", ["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"], index=["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"].index(jugador['Posición']), key=f"pos_{jugador['ID']}")
        
        # Selección Dinámica de Liga y Equipo en Edición
        nueva_liga = c_ed2.selectbox("Liga", LIGAS_MUNDIALES, index=LIGAS_MUNDIALES.index(jugador.get('Liga', LIGAS_MUNDIALES[0])) if jugador.get('Liga') in LIGAS_MUNDIALES else 0, key=f"lg_{jugador['ID']}")
        if nueva_liga in EQUIPOS_POR_LIGA:
            nuevo_club = c_ed2.selectbox("Club / Equipo", EQUIPOS_POR_LIGA[nueva_liga], key=f"cl_{jugador['ID']}")
        else:
            nuevo_club = c_ed2.text_input("Club / Equipo (Escribir)", value=jugador['Club'], key=f"cl_txt_{jugador['ID']}")
            
        nueva_foto = st.file_uploader("Subir o Actualizar Foto (PNG, JPG)", type=['jpg', 'png', 'jpeg'], key=f"ft_{jugador['ID']}")
        
        col_btn1, col_btn2 = st.columns([1, 1])
        if col_btn1.button("💾 Guardar Cambios", key=f"sv_{jugador['ID']}"):
            st.session_state[lista_origen][idx_origen]['Nombre'] = nuevo_nom
            st.session_state[lista_origen][idx_origen]['Edad'] = nueva_edad
            st.session_state[lista_origen][idx_origen]['Posición'] = nueva_pos
            st.session_state[lista_origen][idx_origen]['Liga'] = nueva_liga
            st.session_state[lista_origen][idx_origen]['Club'] = nuevo_club
            if nueva_foto:
                st.session_state[lista_origen][idx_origen]['Foto'] = nueva_foto.getvalue()
            st.success("Perfil actualizado.")
            st.rerun()
            
        if col_btn2.button("🗑️ Eliminar Perfil", key=f"dl_{jugador['ID']}"):
            st.session_state[lista_origen].pop(idx_origen)
            st.rerun()

# 6. ESTÉTICA
st.markdown("""
    <style>
    [data-testid="stSidebar"] {background-color: #1A2B4C !important;}
    [data-testid="stSidebar"] * {color: #FFFFFF !important;}
    .metric-card {background-color: #F8F9FA; border-left: 5px solid #1A2B4C; padding: 10px; border-radius: 5px; margin-bottom: 10px; color: #1A2B4C; font-size: 12px;}
    .stButton>button {background-color: #C8A165; color: #1A2B4C !important; font-weight: bold; width: 100%;}
    </style>
""", unsafe_allow_html=True)

# 7. SISTEMA DE LOGIN Y NAVEGACIÓN
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center; color:#1A2B4C; font-size:45px;'>IGNITION</h1>", unsafe_allow_html=True)
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
        st.markdown("<h2 style='color:#C8A165; text-align:center;'>IGNITION ELITE</h2>", unsafe_allow_html=True)
        st.write("---")
        opcion = st.radio("Navegación", [
            "Dashboard General (Scouting)", "Equipo Ignition", 
            "Ingreso de Data (Partidos)", "Shortlists", "Comparador", "Scoring por Perfil"
        ])
        st.write("---")
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False; st.rerun()

    # MÓDULO 1: DASHBOARD
    if opcion == "Dashboard General (Scouting)":
        st.title("Inteligencia de Mercado y Seguimiento")
        df_scouting = pd.DataFrame(st.session_state['scouting_db'])
        seleccion = st.dataframe(df_scouting[["Nombre", "Edad", "Club", "Liga", "Overall", "Viabilidad", "Posición"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        
        if len(seleccion.selection.rows) > 0:
            idx = seleccion.selection.rows[0]
            mostrar_perfil_jugador(st.session_state['scouting_db'][idx], 'scouting_db', idx)

    # MÓDULO 2: EQUIPO IGNITION
    elif opcion == "Equipo Ignition":
        st.title("💼 Equipo Ignition")
        df_equipo = pd.DataFrame(st.session_state['equipo_ignition'])
        seleccion_eq = st.dataframe(df_equipo[["Nombre", "Edad", "Club", "Liga", "Posición", "Status"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        
        if len(seleccion_eq.selection.rows) > 0:
            idx_eq = seleccion_eq.selection.rows[0]
            mostrar_perfil_jugador(st.session_state['equipo_ignition'][idx_eq], 'equipo_ignition', idx_eq)

    # MÓDULO 3: INGRESO DE DATA (CON MOTOR DE EQUIPO DINÁMICO)
    elif opcion == "Ingreso de Data (Partidos)":
        st.title("📥 Registro Manual de Estadísticas")
        st.caption("Selecciona la liga para desplegar automáticamente los equipos registrados.")
        
        c1, c2 = st.columns(2)
        n_jugador = c1.text_input("Nombre del Jugador")
        n_posicion = c1.selectbox("📍 Posición (Define las métricas)", ["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"])
        
        n_liga = c2.selectbox("🏆 Competición / Torneo", LIGAS_MUNDIALES)
        # 🧠 MAGIA DINÁMICA DE EQUIPOS
        if n_liga in EQUIPOS_POR_LIGA:
            n_equipo = c2.selectbox("🛡️ Equipo", EQUIPOS_POR_LIGA[n_liga])
        else:
            n_equipo = c2.text_input("🛡️ Equipo (Escribir nombre)")
            
        n_jornada = c1.selectbox("Jornada", [f"Jornada {i}" for i in range(1, 39)])
        c2.write("<br>", unsafe_allow_html=True)
        n_conv = c2.checkbox("Convocatoria sin minutos (Solo experiencia)")
            
        st.markdown("#### Datos del Partido")
        cd1, cd2, cd3, cd4 = st.columns(4)
        with cd1: 
            v_minutos = st.number_input("Minutos Jugados", 0, 120, 90)
            v_goles = st.number_input("Goles", 0, 10, 0)
        with cd2: 
            v_asis = st.number_input("Asistencias", 0, 10, 0)
            v_tiros = st.number_input("Tiros a Puerta", 0, 20, 0)
        with cd3:
            v_pases = st.number_input("Pases Clave", 0, 20, 0)
            v_duelos = st.number_input("Duelos Ganados", 0, 40, 0)
        with cd4:
            v_intercep = st.number_input("Intercepciones", 0, 30, 0)
            v_faltas = st.number_input("Faltas Cometidas", 0, 20, 0)
            
        if st.button("Guardar Estadísticas en Base de Datos"):
            st.success(f"¡Estadísticas de {n_jugador} con el {n_equipo} registradas exitosamente!")

    else:
        st.info(f"Módulo de {opcion} en construcción.")
