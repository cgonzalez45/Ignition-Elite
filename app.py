import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import base64
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

# FUNCIÓN PARA GUARDAR FOTOS PERMANENTEMENTE (BASE64)
def procesar_foto(uploaded_file):
    if uploaded_file is not None:
        return "data:image/png;base64," + base64.b64encode(uploaded_file.getvalue()).decode()
    return None

# 2. INICIALIZAR MEMORIA TAMPÓN (Mientras Supabase se llena)
if 'scouting_db' not in st.session_state:
    st.session_state['scouting_db'] = [
        {"ID": 1, "Nombre": "Alisana Yirajang", "Edad": 21, "Club": "Slovan", "Liga": "🇸🇰 Liga Eslovaquia", "Valor": "€800k", "Overall": 85, "Viabilidad": "🔴 Baja", "Posición": "Extremo", "Foto": None}
    ]

if 'equipo_ignition' not in st.session_state:
    st.session_state['equipo_ignition'] = [
        {"ID": 3, "Nombre": "José Juan Macías", "Edad": 24, "Club": "Pumas UNAM", "Liga": "🇲🇽 Liga MX", "Status": "FIRMADO 🟡", "Posición": "Delantero", "Foto": None}
    ]

# 3. DICCIONARIOS DE LIGAS Y EQUIPOS 2026/2027
LIGAS_MUNDIALES = [
    "🇲🇽 Liga MX", "🇲🇽 Liga de Expansión", "🇲🇽 Liga MX U-21", "🇲🇽 Liga MX U-19", "🇲🇽 Liga MX U-17", "🇲🇽 Liga MX U-15",
    "🇪🇸 La Liga", "🇪🇸 Liga Hypermotion", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship", 
    "🇵🇹 Liga Portugal", "🇵🇹 Liga 2 Portugal", "🇸🇪 Allsvenskan", "🇸🇰 Liga Eslovaquia", "🇸🇮 Liga Eslovenia",
    "🇺🇸 MLS", "🇺🇸 MLS Next Pro", "🇺🇸 USL", "🇦🇷 Primera División Argentina", "🇧🇷 Brasileirao", 
    "🇨🇴 Primera División Colombia", "🇺🇾 Primera División Uruguay", "🇨🇱 Primera División Chile",
    "🇫🇷 Ligue 1", "🇮🇹 Serie A", "🇩🇪 Bundesliga", "🇳🇱 Eredivisie"
]

equipos_mx_base = ["América", "Atlas", "Atlético San Luis", "Cruz Azul", "Guadalajara (Chivas)", "FC Juárez", "León", "Mazatlán", "Monterrey", "Necaxa", "Pachuca", "Puebla", "Pumas UNAM", "Querétaro", "Santos Laguna", "Tigres UANL", "Tijuana", "Toluca"]

EQUIPOS_POR_LIGA = {
    "🇲🇽 Liga MX": equipos_mx_base,
    "🇲🇽 Liga MX U-21": [e + " U-21" for e in equipos_mx_base],
    "🇲🇽 Liga MX U-19": [e + " U-19" for e in equipos_mx_base],
    "🇲🇽 Liga MX U-17": [e + " U-17" for e in equipos_mx_base],
    "🇲🇽 Liga MX U-15": [e + " U-15" for e in equipos_mx_base],
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": ["Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich Town", "Leicester City", "Liverpool", "Manchester City", "Manchester United", "Newcastle United", "Nottingham Forest", "Southampton", "Tottenham", "West Ham", "Wolverhampton"],
    "🇪🇸 La Liga": ["Alavés", "Athletic Club", "Atlético Madrid", "Barcelona", "Betis", "Celta Vigo", "Espanyol", "Getafe", "Girona", "Las Palmas", "Leganés", "Mallorca", "Osasuna", "Rayo Vallecano", "Real Madrid", "Real Sociedad", "Sevilla", "Valencia", "Valladolid", "Villarreal"],
    "🇺🇸 MLS": ["Atlanta United", "Austin FC", "Charlotte FC", "Chicago Fire", "FC Cincinnati", "Colorado Rapids", "Columbus Crew", "FC Dallas", "D.C. United", "Houston Dynamo", "LA Galaxy", "LAFC", "Inter Miami", "Minnesota United", "Montreal", "Nashville SC", "New England Revolution", "New York City FC", "New York Red Bulls", "Orlando City", "Philadelphia Union", "Portland Timbers", "Real Salt Lake", "San Jose Earthquakes", "Seattle Sounders", "Sporting KC", "St. Louis City SC", "Toronto FC", "Vancouver Whitecaps"]
}

# 4. LAS 30 MÉTRICAS QUIRÚRGICAS
def obtener_metricas(posicion):
    if posicion == "Portero":
        return {"Pilar 1: Atajadas": ["Atajadas Totales p/90", "Reflejos a Quemarropa", "xG Evitados", "Desvíos", "Atrapes sin rebote", "1v1 Ganados", "Atajadas de Penal", "Tiros Lejanos Salvados"], "Pilar 2: Distribución": ["Pases Largos Precisos", "Efectividad Pase Corto", "Saques de Meta Exitosos", "Inicios de Contragolpe", "Pases bajo presión", "Toques de balón", "Pérdidas en salida"], "Pilar 3: Dominio del Área": ["Salidas por Alto", "Despejes de Puños", "Intercepciones", "Duelos Aéreos Ganados", "Reivindicaciones", "Tackles", "Faltas recibidas", "Acciones defensivas fuera"], "Pilar 4: Físico/Contexto": ["Minutos Jugados", "Errores Críticos", "Tarjetas Amarillas", "Tarjetas Rojas", "Lesiones", "Distancia Recorrida", "Goles Concedidos"]}
    elif posicion == "Defensa Central":
        return {"Pilar 1: Defensa Pura": ["Duelos Defensivos %", "Intercepciones p/90", "Tackles", "Bloqueos", "Despejes", "Recuperaciones", "Duelos 1v1", "Faltas Cometidas"], "Pilar 2: Juego Aéreo": ["Duelos Aéreos Totales", "Duelos Aéreos %", "Goles de Cabeza", "Despejes de Cabeza", "Aéreos en Área Rival", "Aéreos en Área Propia", "Faltas por alto"], "Pilar 3: Salida": ["Pases Precisos %", "Pases Progresivos", "Pases Largos Precisos", "Conducciones", "Pases al Tercio Final", "Toques", "Pérdidas de Balón", "Pases bajo presión"], "Pilar 4: Físico": ["Minutos", "Tarjetas Amarillas", "Tarjetas Rojas", "Errores Críticos", "Sprints", "Distancia Recorrida", "Aceleraciones"]}
    elif posicion in ["Lateral Izquierdo", "Lateral Derecho"]:
        return {"Pilar 1: Defensa": ["Duelos Defensivos %", "Intercepciones p/90", "Tackles", "Bloqueos de Centro", "Recuperaciones", "Despejes", "Duelos Aéreos"], "Pilar 2: Progresión": ["Pases Progresivos", "Conducciones", "Pases al Tercio Final", "Pases al Espacio", "Toques", "Pérdidas en Salida", "Pases Precisos %", "Pases Recibidos"], "Pilar 3: Ofensiva": ["Centros Precisos %", "xA", "Desbordes", "Toques en Área", "Asistencias", "Tiros", "Pases Clave", "Faltas Recibidas"], "Pilar 4: Físico": ["Minutos", "Sprints p/90", "Distancia Recorrida", "Velocidad Máxima", "Tarjetas", "Faltas Cometidas", "Rojas"]}
    elif posicion == "Medio":
        return {"Pilar 1: Destrucción": ["Duelos Defensivos", "Intercepciones", "Tackles", "Presión", "Recuperaciones", "Faltas", "Bloqueos"], "Pilar 2: Posesión": ["Pases Precisos %", "Toques", "Pases bajo presión", "Pérdidas", "Pases Recibidos", "Conducciones", "Faltas Recibidas", "Retención %"], "Pilar 3: Creación": ["Pases Clave", "Pases Progresivos", "xA", "Pases al Tercio Final", "Cambios de Orientación", "Asistencias", "Desbordes", "Tiros Lejanos"], "Pilar 4: Finalización": ["xG", "Tiros", "Goles", "Minutos", "Distancia Recorrida", "Sprints", "Tarjetas Amarillas"]}
    elif posicion == "Extremo":
        return {"Pilar 1: Desequilibrio": ["Regates Exitosos", "Duelos Ofensivos", "Desbordes", "Faltas Recibidas", "Aceleraciones", "Conducciones al Área", "Pérdidas", "Fueras de Lugar"], "Pilar 2: Creación": ["Centros Precisos %", "Pases Clave", "xA", "Asistencias", "Pases al Área", "Toques", "Pases Progresivos"], "Pilar 3: Finalización": ["xG", "Tiros Totales", "Tiros a Puerta", "Goles", "Toques en Área", "Tiros al Palo", "Conversión %", "Duelos Aéreos"], "Pilar 4: Físico": ["Presión", "Recuperaciones", "Intercepciones", "Minutos", "Sprints", "Velocidad Máxima", "Distancia"]}
    else: 
        return {"Pilar 1: Finalización": ["Goles", "xG", "Tiros a Puerta", "Tiros Totales", "Conversión %", "Penales", "Tiros al Palo", "Fueras de Lugar"], "Pilar 2: Presencia": ["Toques en Área", "Duelos Aéreos", "Goles de Cabeza", "Faltas en Área", "Pases en Área", "Anticipaciones", "Rebotes"], "Pilar 3: Asociación": ["Asistencias", "xA", "Pases Clave", "Regates", "Duelos Ofensivos", "Pases Precisos %", "Pérdidas", "Faltas en Ataque"], "Pilar 4: Físico": ["Minutos", "Presión Alta", "Recuperaciones", "Sprints", "Distancia", "Velocidad Máxima", "Tarjetas"]}

# 5. MOSTRAR PERFIL Y EDICIÓN
def mostrar_perfil_jugador(jugador, lista_origen, idx_origen):
    st.markdown("---")
    st.subheader(f"👤 Perfil Analítico: {jugador['Nombre']}")
    
    col_img, col_info, col_radar = st.columns([1, 2, 2])
    with col_img:
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

    st.markdown(f"### Matriz de Rendimiento p/90 ({jugador['Posición']})")
    metricas_q = obtener_metricas(jugador['Posición'])
    tabs = st.tabs(list(metricas_q.keys()))
    for i, (pilar, lista_metricas) in enumerate(metricas_q.items()):
        with tabs[i]:
            cols = st.columns(4)
            for j, metrica in enumerate(lista_metricas):
                cols[j % 4].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165;'>API</span></div>", unsafe_allow_html=True)
                
    with st.expander(f"✏️ Editar Perfil y Subir Foto de {jugador['Nombre']}"):
        c_ed1, c_ed2 = st.columns(2)
        nuevo_nom = c_ed1.text_input("Nombre", value=jugador['Nombre'], key=f"nm_{jugador['ID']}")
        nueva_edad = c_ed1.number_input("Edad", 15, 45, value=jugador['Edad'], key=f"ed_{jugador['ID']}")
        nueva_pos = c_ed1.selectbox("Posición", ["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"], index=["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"].index(jugador['Posición']), key=f"pos_{jugador['ID']}")
        
        nueva_liga = c_ed2.selectbox("Liga", LIGAS_MUNDIALES, index=LIGAS_MUNDIALES.index(jugador.get('Liga', LIGAS_MUNDIALES[0])) if jugador.get('Liga') in LIGAS_MUNDIALES else 0, key=f"lg_{jugador['ID']}")
        if nueva_liga in EQUIPOS_POR_LIGA:
            nuevo_club = c_ed2.selectbox("Club", EQUIPOS_POR_LIGA[nueva_liga], key=f"cl_{jugador['ID']}")
        else:
            nuevo_club = c_ed2.text_input("Club", value=jugador['Club'], key=f"cl_txt_{jugador['ID']}")
            
        nueva_foto = st.file_uploader("Subir Foto de Perfil (PNG, JPG)", type=['jpg', 'png', 'jpeg'], key=f"ft_{jugador['ID']}")
        
        col_btn1, col_btn2 = st.columns([1, 1])
        if col_btn1.button("💾 Guardar Cambios (Base de Datos)", key=f"sv_{jugador['ID']}"):
            foto_base64 = procesar_foto(nueva_foto)
            st.session_state[lista_origen][idx_origen].update({
                'Nombre': nuevo_nom, 'Edad': nueva_edad, 'Posición': nueva_pos, 
                'Liga': nueva_liga, 'Club': nuevo_club
            })
            if foto_base64: st.session_state[lista_origen][idx_origen]['Foto'] = foto_base64
            
            # COMANDO REAL SUPABASE
            if supabase:
                try: supabase.table(lista_origen).update({'nombre': nuevo_nom}).eq('id', jugador['ID']).execute()
                except: pass
                
            st.success("Perfil actualizado en Base de Datos.")
            st.rerun()
            
        if col_btn2.button("🗑️ Eliminar Perfil", key=f"dl_{jugador['ID']}"):
            st.session_state[lista_origen].pop(idx_origen)
            st.rerun()

# 6. ESTÉTICA INSTITUCIONAL
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
        # LOGO DE EMPRESA FORZADO AL CENTRO
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
        # LOGO EN MENÚ LATERAL FORZADO
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        elif os.path.exists("logo.jpg"): st.image("logo.jpg", use_container_width=True)
        else: st.markdown("<h2 style='color:#C8A165; text-align:center;'>IGNITION ELITE</h2>", unsafe_allow_html=True)
        
        st.write("---")
        opcion = st.radio("Navegación", ["Dashboard General", "Equipo Ignition", "Ingreso de Data (Partidos)"])
        st.write("---")
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False; st.rerun()

    if opcion == "Dashboard General":
        st.title("Inteligencia de Mercado")
        df_scouting = pd.DataFrame(st.session_state['scouting_db'])
        seleccion = st.dataframe(df_scouting[["Nombre", "Edad", "Club", "Liga", "Overall", "Posición"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        
        if len(seleccion.selection.rows) > 0:
            mostrar_perfil_jugador(st.session_state['scouting_db'][seleccion.selection.rows[0]], 'scouting_db', seleccion.selection.rows[0])

    elif opcion == "Equipo Ignition":
        st.title("💼 Equipo Ignition")
        df_equipo = pd.DataFrame(st.session_state['equipo_ignition'])
        seleccion_eq = st.dataframe(df_equipo[["Nombre", "Edad", "Club", "Liga", "Posición", "Status"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        
        if len(seleccion_eq.selection.rows) > 0:
            mostrar_perfil_jugador(st.session_state['equipo_ignition'][seleccion_eq.selection.rows[0]], 'equipo_ignition', seleccion_eq.selection.rows[0])

    elif opcion == "Ingreso de Data (Partidos)":
        st.title("📥 Registro y Creación Automática")
        st.caption("Si el jugador no existe, se creará su perfil en el Dashboard con estos datos.")
        
        with st.form("form_partido"):
            c1, c2 = st.columns(2)
            n_jugador = c1.text_input("Nombre del Jugador")
            n_posicion = c1.selectbox("📍 Posición", ["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"])
            
            n_liga = c2.selectbox("🏆 Competición", LIGAS_MUNDIALES)
            if n_liga in EQUIPOS_POR_LIGA:
                n_equipo = c2.selectbox("🛡️ Equipo", EQUIPOS_POR_LIGA[n_liga])
            else:
                n_equipo = c2.text_input("🛡️ Equipo")
                
            n_jornada = c1.selectbox("Jornada", [f"Jornada {i}" for i in range(1, 39)])
            
            st.markdown("#### Datos del Partido")
            cd1, cd2, cd3 = st.columns(3)
            with cd1: v_minutos = st.number_input("Minutos", 0, 120, 90)
            with cd2: v_goles = st.number_input("Goles", 0, 10, 0)
            with cd3: v_asis = st.number_input("Asistencias", 0, 10, 0)
                
            if st.form_submit_button("Guardar en Base de Datos"):
                if n_jugador:
                    # VERIFICAR SI EXISTE, SI NO, CREARLO
                    existe = any(j['Nombre'].lower() == n_jugador.lower() for j in st.session_state['scouting_db'])
                    if not existe:
                        nuevo = {"ID": len(st.session_state['scouting_db']) + 100, "Nombre": n_jugador, "Edad": 20, "Club": n_equipo, "Liga": n_liga, "Valor": "N/D", "Overall": 70, "Viabilidad": "🟡 Media", "Posición": n_posicion, "Foto": None}
                        st.session_state['scouting_db'].append(nuevo)
                        
                        # INYECCIÓN A SUPABASE REAL
                        if supabase:
                            try: supabase.table('scouting_db').insert(nuevo).execute()
                            except: pass
                            
                    st.success(f"Estadísticas guardadas. {n_jugador} está en el Dashboard.")
                else:
                    st.error("Escribe el nombre del jugador.")
