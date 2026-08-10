import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import base64
from supabase import create_client, Client

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Ignition Elite Scouting", page_icon="⚽", layout="wide")

@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        return None

supabase = init_connection()

def procesar_foto(uploaded_file):
    if uploaded_file is not None:
        return "data:image/png;base64," + base64.b64encode(uploaded_file.getvalue()).decode()
    return None

# 2. FUNCIONES DE LECTURA Y ESCRITURA CON SUPABASE (PERSISTENCIA REAL)
def cargar_desde_supabase(tabla):
    if supabase:
        try:
            res = supabase.table(tabla).select("*").order("id", desc=False).execute()
            if res.data is not None:
                registros = []
                for row in res.data:
                    elem = {
                        "ID": row.get("id"),
                        "Nombre": row.get("nombre", "Sin Nombre"),
                        "Edad": row.get("edad", 20),
                        "Club": row.get("club", "N/D"),
                        "Liga": row.get("liga", "N/D"),
                        "Posición": row.get("posicion", "Medio"),
                        "Foto": row.get("foto")
                    }
                    if "valor" in row: elem["Valor"] = row.get("valor", "N/D")
                    if "overall" in row: elem["Overall"] = row.get("overall", 70)
                    if "viabilidad" in row: elem["Viabilidad"] = row.get("viabilidad", "🟡 Media")
                    if "status" in row: elem["Status"] = row.get("status", "OBJETIVO 🔵")
                    registros.append(elem)
                return registros
        except Exception as e:
            st.error(f"Error consultando la tabla {tabla} en Supabase: {e}")
    return []

# Inicializar sesiones desde Supabase directamente
st.session_state['scouting_db'] = cargar_desde_supabase('scouting_db')
st.session_state['equipo_ignition'] = cargar_desde_supabase('equipo_ignition')

# 3. LIGAS MUNDIALES Y EQUIPOS VERIFICADOS (TEMPORADA 2026/2027)
LIGAS_MUNDIALES = [
    "🇲🇽 Liga MX", "🇲🇽 Liga de Expansión", "🇲🇽 Liga MX U-21", "🇲🇽 Liga MX U-19", "🇲🇽 Liga MX U-17", "🇲🇽 Liga MX U-15",
    "🇪🇸 La Liga", "🇪🇸 Liga Hypermotion", "🇪🇸 Primera RFEF", "🇪🇸 Segunda RFEF",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 League One", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 League Two",
    "🇫🇷 Ligue 1", "🇫🇷 Ligue 2", "🇮🇹 Serie A", "🇮🇹 Serie B",
    "🇩🇪 Bundesliga", "🇩🇪 2. Bundesliga", "🇸🇪 Allsvenskan", "🇳🇴 Eliteserien",
    "🇳🇱 Eredivisie", "🇧🇪 Jupiler Pro League", "🇩🇰 Superliga Dinamarca", "🇵🇱 Ekstraklasa",
    "🇧🇬 efbet League Bulgaria", "🇭🇷 SuperSport HNL", "🇨🇿 Chance Liga", "🇷🇸 Superliga Serbia",
    "🇦🇹 Bundesliga Austria", "🇨🇭 Superliga de Suiza", "🇵🇹 Liga Portugal", "🇵🇹 Liga 2 Portugal",
    "🇸🇰 Liga Eslovaquia", "🇸🇮 Liga Eslovenia",
    "🇦🇷 Primera División Argentina", "🇨🇷 Primera División Costa Rica", "🇨🇴 Primera División Colombia", 
    "🇧🇷 Brasileirao", "🇧🇷 Brasileirao Série B", "🇺🇾 Primera División Uruguay", "🇨🇱 Primera División Chile", 
    "🇺🇸 MLS", "🇺🇸 MLS Next Pro", "🇺🇸 USL", "🇯🇵 J-League"
]

# EQUIPOS CORREGIDOS SEGÚN TRANSFERMARKT 2026/2027 (ATLANTE INCLUIDO)
equipos_mx_2026 = [
    "CF América", "CF Atlante", "Atlas FC", "Club Atlético de San Luis", "Cruz Azul", 
    "CD Guadalajara (Chivas)", "FC Juárez", "Club León", "CF Monterrey", "Club Necaxa", 
    "CF Pachuca", "Club Puebla", "Pumas UNAM", "Querétaro FC", "Club Santos Laguna", 
    "Tigres UANL", "Club Tijuana", "Deportivo Toluca"
]

EQUIPOS_POR_LIGA = {
    "🇲🇽 Liga MX": equipos_mx_2026,
    "🇲🇽 Liga MX U-21": [e + " U-21" for e in equipos_mx_2026],
    "🇲🇽 Liga MX U-19": [e + " U-19" for e in equipos_mx_2026],
    "🇲🇽 Liga MX U-17": [e + " U-17" for e in equipos_mx_2026],
    "🇲🇽 Liga MX U-15": [e + " U-15" for e in equipos_mx_2026],
    "🇪🇸 La Liga": ["Athletic Club", "Club Atlético de Madrid", "CA Osasuna", "CD Leganés", "Deportivo Alavés", "Elche CF", "FC Barcelona", "Getafe CF", "Girona FC", "Levante UD", "RCD Espanyol", "Rayo Vallecano", "Real Betis", "Real Celta Vigo", "Real Madrid", "Real Oviedo", "Real Sociedad", "Sevilla FC", "Valencia CF", "Villarreal CF"],
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": ["Arsenal FC", "Aston Villa FC", "AFC Bournemouth", "Brentford FC", "Brighton & Hove Albion", "Chelsea FC", "Crystal Palace", "Everton FC", "Fulham FC", "Ipswich Town", "Leeds United", "Liverpool FC", "Manchester City", "Manchester United", "Newcastle United", "Nottingham Forest", "Sunderland AFC", "Tottenham Hotspur", "West Ham United", "Wolverhampton Wanderers"],
    "🇸🇪 Allsvenskan": ["AIK", "BK Häcken", "Djurgårdens IF", "GAIS", "Halmstads BK", "Hammarby IF", "IF Brommapojkarna", "IF Elfsborg", "IFK Göteborg", "IFK Norrköping", "IK Sirius", "Kalmar FF", "Malmö FF", "Mjällby AIF", "Västerås SK"],
    "🇵🇹 Liga Portugal": ["Arouca", "AVS", "SL Benfica", "Boavista FC", "SC Braga", "Casa Pia AC", "GD Estoril Praia", "CF Estrela da Amadora", "FC Famalicão", "SC Farense", "Gil Vicente FC", "Moreirense FC", "CD Nacional", "FC Porto", "Rio Ave FC", "CD Santa Clara", "Sporting CP", "Vitória de Guimarães"],
    "🇺🇸 MLS": ["Atlanta United FC", "Austin FC", "Charlotte FC", "Chicago Fire FC", "FC Cincinnati", "Colorado Rapids", "Columbus Crew", "D.C. United", "FC Dallas", "Houston Dynamo FC", "Inter Miami CF", "LA Galaxy", "LAFC", "Minnesota United FC", "CF Montréal", "Nashville SC", "New England Revolution", "New York City FC", "New York Red Bulls", "Orlando City SC", "Philadelphia Union", "Portland Timbers", "Real Salt Lake", "San Jose Earthquakes", "Seattle Sounders FC", "Sporting Kansas City", "St. Louis City SC", "Toronto FC", "Vancouver Whitecaps FC"]
}

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

# 4. MOSTRAR PERFIL DE JUGADOR Y EDICIÓN PERMANENTE
def mostrar_perfil_jugador(jugador, tabla_origen, idx_origen):
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
        valores = [75, 70, 65, 80, 72]
        angulos = [n / 5 * 2 * math.pi for n in range(5)]; angulos += angulos[:1]; valores += valores[:1]
        fig, ax = plt.subplots(figsize=(2.2, 2.2), subplot_kw=dict(polar=True))
        plt.xticks(angulos[:-1], categorias, color='#1A2B4C', size=8, weight='bold')
        ax.plot(angulos, valores, color='#1A2B4C', linewidth=2)
        ax.fill(angulos, valores, color='#C8A165', alpha=0.4)
        fig.patch.set_facecolor('none'); ax.set_facecolor('none'); ax.set_yticklabels([])
        st.pyplot(fig, use_container_width=True)

    st.markdown(f"### Matriz de Rendimiento p/90 ({jugador['Posición']})")
    metricas_q = obtener_metricas(jugador['Posición'])
    tabs = st.tabs(list(metricas_q.keys()))
    for i, (pilar, lista_metricas) in enumerate(metricas_q.items()):
        with tabs[i]:
            cols = st.columns(4)
            for j, metrica in enumerate(lista_metricas):
                cols[j % 4].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165; font-weight:bold;'>Sincronizado</span></div>", unsafe_allow_html=True)
                
    with st.expander(f"✏️ Editar Perfil y Subir Foto de {jugador['Nombre']}"):
        c_ed1, c_ed2 = st.columns(2)
        nuevo_nom = c_ed1.text_input("Nombre", value=jugador['Nombre'], key=f"nm_{jugador['ID']}")
        nueva_edad = c_ed1.number_input("Edad", 15, 45, value=jugador['Edad'], key=f"ed_{jugador['ID']}")
        nueva_pos = c_ed1.selectbox("Posición", ["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"], index=["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"].index(jugador['Posición']), key=f"pos_{jugador['ID']}")
        
        nueva_liga = c_ed2.selectbox("Liga", LIGAS_MUNDIALES, index=LIGAS_MUNDIALES.index(jugador.get('Liga', LIGAS_MUNDIALES[0])) if jugador.get('Liga') in LIGAS_MUNDIALES else 0, key=f"lg_{jugador['ID']}")
        if nueva_liga in EQUIPOS_POR_LIGA:
            nuevo_club = c_ed2.selectbox("Club", EQUIPOS_POR_LIGA[nueva_liga], key=f"cl_{jugador['ID']}")
        else:
            nuevo_club = c_ed2.text_input("Club (Escribir nombre)", value=jugador['Club'], key=f"cl_txt_{jugador['ID']}")
            
        nueva_foto = st.file_uploader("Subir Foto de Perfil (PNG, JPG)", type=['jpg', 'png', 'jpeg'], key=f"ft_{jugador['ID']}")
        
        col_btn1, col_btn2 = st.columns([1, 1])
        if col_btn1.button("💾 Guardar Cambios en Supabase", key=f"sv_{jugador['ID']}"):
            foto_base64 = procesar_foto(nueva_foto) if nueva_foto else jugador.get('Foto')
            
            payload = {
                "nombre": nuevo_nom,
                "edad": nueva_edad,
                "posicion": nueva_pos,
                "liga": nueva_liga,
                "club": nuevo_club,
                "foto": foto_base64
            }
            if supabase:
                try:
                    if jugador.get('ID'):
                        supabase.table(tabla_origen).update(payload).eq('id', jugador['ID']).execute()
                    else:
                        supabase.table(tabla_origen).insert(payload).execute()
                    st.success("Guardado permanente en Supabase exitoso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Fallo al escribir en Supabase: {e}")
            else:
                st.error("Supabase no está conectado.")
            
        if col_btn2.button("🗑️ Eliminar Perfil", key=f"dl_{jugador['ID']}"):
            if supabase and jugador.get('ID'):
                try: 
                    supabase.table(tabla_origen).delete().eq('id', jugador['ID']).execute()
                    st.success("Jugador eliminado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")

# 5. ESTÉTICA
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA !important; }
    [data-testid="stSidebar"] { background-color: #1A2B4C !important; border-right: 2px solid #C8A165 !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .login-container { max-width: 420px; margin: 50px auto; padding: 40px; background: #FFFFFF; border-radius: 12px; box-shadow: 0 10px 30px rgba(26, 43, 76, 0.12); border-top: 5px solid #C8A165; text-align: center; }
    .metric-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #1A2B4C; padding: 12px; border-radius: 6px; margin-bottom: 10px; color: #1A2B4C; font-size: 13px; }
    .stButton>button { background-color: #C8A165 !important; color: #1A2B4C !important; font-weight: bold !important; border: none !important; border-radius: 6px !important; width: 100% !important; }
    .stButton>button:hover { background-color: #1A2B4C !important; color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

# 6. SESIÓN Y NAVEGACIÓN
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        col_img_1, col_img_2, col_img_3 = st.columns([1, 2, 1])
        with col_img_2:
            if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
            elif os.path.exists("logo.jpg"): st.image("logo.jpg", use_container_width=True)
            else: st.markdown("<h1 style='text-align:center; color:#1A2B4C; font-size:36px; margin:0;'>IGNITION</h1>", unsafe_allow_html=True)
        
        st.markdown("""
            <h2 style='color:#1A2B4C; margin-top:15px; margin-bottom:0; font-size:22px; text-align:center;'>SCOUTING PRO</h2>
            <p style='color:#C8A165; font-size:12px; font-weight:bold; letter-spacing:1px; margin-top:4px; text-align:center;'>SCOUTING INTERNACIONAL Y DIRECCIÓN DEPORTIVA</p>
            <hr style='border-color:#E2E8F0; margin: 20px 0;'>
        """, unsafe_allow_html=True)
        
        usuario = st.text_input("Usuario Corporativo")
        password = st.text_input("Contraseña", type="password")
        st.write("")
        if st.button("INGRESAR AL SISTEMA"):
            if usuario.lower() == "christian" and password == "1234":
                st.session_state['logged_in'] = True; st.rerun()
            else:
                st.error("Credenciales incorrectas")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        elif os.path.exists("logo.jpg"): st.image("logo.jpg", use_container_width=True)
        else: st.markdown("<h2 style='color:#C8A165; text-align:center;'>IGNITION ELITE</h2>", unsafe_allow_html=True)
        
        st.write("---")
        opcion = st.radio("Navegación Táctica", [
            "Dashboard General (Scouting)", 
            "Equipo Ignition", 
            "Ingreso de Data (Partidos)",
            "Shortlists",
            "Comparador",
            "Scoring por Perfil"
        ])
        st.write("---")
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False; st.rerun()

    if opcion == "Dashboard General (Scouting)":
        st.title("Inteligencia de Mercado y Seguimiento")
        
        with st.expander("➕ Crear Nuevo Jugador en Base de Datos"):
            with st.form("form_nuevo_scouting"):
                c_a, c_b = st.columns(2)
                reg_nom = c_a.text_input("Nombre Completo")
                reg_edad = c_a.number_input("Edad", 15, 45, 20)
                reg_pos = c_a.selectbox("Posición", ["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"])
                reg_liga = c_b.selectbox("Liga", LIGAS_MUNDIALES)
                if reg_liga in EQUIPOS_POR_LIGA:
                    reg_club = c_b.selectbox("Club", EQUIPOS_POR_LIGA[reg_liga])
                else:
                    reg_club = c_b.text_input("Club (Escribir)")
                reg_foto = st.file_uploader("Foto de Perfil (Opcional)", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("Guardar Jugador en Nube"):
                    if reg_nom and supabase:
                        f_b64 = procesar_foto(reg_foto)
                        payload = {
                            "nombre": reg_nom, "edad": reg_edad, "posicion": reg_pos,
                            "liga": reg_liga, "club": reg_club, "foto": f_b64,
                            "valor": "N/D", "overall": 70, "viabilidad": "🟡 Media"
                        }
                        supabase.table('scouting_db').insert(payload).execute()
                        st.success(f"{reg_nom} creado permanentemente.")
                        st.rerun()

        if len(st.session_state['scouting_db']) > 0:
            df_scouting = pd.DataFrame(st.session_state['scouting_db'])
            seleccion = st.dataframe(df_scouting[["Nombre", "Edad", "Club", "Liga", "Overall", "Posición"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
            
            if len(seleccion.selection.rows) > 0:
                mostrar_perfil_jugador(st.session_state['scouting_db'][seleccion.selection.rows[0]], 'scouting_db', seleccion.selection.rows[0])
        else:
            st.info("No hay jugadores registrados en Supabase. Agrega uno con el botón de arriba.")

    elif opcion == "Equipo Ignition":
        st.title("💼 Equipo Ignition")
        
        with st.expander("➕ Añadir Jugador a Equipo Ignition"):
            with st.form("form_nuevo_equipo"):
                c_a, c_b = st.columns(2)
                eq_nom = c_a.text_input("Nombre Completo")
                eq_edad = c_a.number_input("Edad", 15, 45, 20)
                eq_pos = c_a.selectbox("Posición", ["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"])
                eq_status = c_a.selectbox("Estatus", ["FIRMADO 🟡", "OBJETIVO 🔵", "SEGUIMIENTO INTENSIVO 🟢"])
                eq_liga = c_b.selectbox("Liga", LIGAS_MUNDIALES)
                if eq_liga in EQUIPOS_POR_LIGA:
                    eq_club = c_b.selectbox("Club", EQUIPOS_POR_LIGA[eq_liga])
                else:
                    eq_club = c_b.text_input("Club (Escribir)")
                eq_foto = st.file_uploader("Foto de Perfil (Opcional)", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("Guardar en Equipo Ignition"):
                    if eq_nom and supabase:
                        f_b64 = procesar_foto(eq_foto)
                        payload = {
                            "nombre": eq_nom, "edad": eq_edad, "posicion": eq_pos,
                            "liga": eq_liga, "club": eq_club, "foto": f_b64, "status": eq_status
                        }
                        supabase.table('equipo_ignition').insert(payload).execute()
                        st.success(f"{eq_nom} registrado en el equipo.")
                        st.rerun()

        if len(st.session_state['equipo_ignition']) > 0:
            df_equipo = pd.DataFrame(st.session_state['equipo_ignition'])
            seleccion_eq = st.dataframe(df_equipo[["Nombre", "Edad", "Club", "Liga", "Posición", "Status"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
            
            if len(seleccion_eq.selection.rows) > 0:
                mostrar_perfil_jugador(st.session_state['equipo_ignition'][seleccion_eq.selection.rows[0]], 'equipo_ignition', seleccion_eq.selection.rows[0])
        else:
            st.info("No hay jugadores en tu plantilla de Ignition.")

    elif opcion == "Ingreso de Data (Partidos)":
        st.title("📥 Registro Manual de Estadísticas")
        
        c1, c2 = st.columns(2)
        n_jugador = c1.text_input("Nombre del Jugador")
        n_posicion = c1.selectbox("📍 Posición (Métricas)", ["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"])
        
        n_liga = c2.selectbox("🏆 Competición", LIGAS_MUNDIALES)
        if n_liga in EQUIPOS_POR_LIGA:
            n_equipo = c2.selectbox("🛡️ Equipo (2026/2027)", EQUIPOS_POR_LIGA[n_liga])
        else:
            n_equipo = c2.text_input("🛡️ Equipo (Escribir nombre del club)")
            
        n_jornada = c1.selectbox("Jornada", [f"Jornada {i}" for i in range(1, 39)])
        
        with st.form("form_stats_partido"):
            st.markdown("#### Datos Manuales del Partido")
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
                
            if st.form_submit_button("Guardar Estadísticas en Supabase"):
                if n_jugador:
                    stats_partido = {
                        "jugador": n_jugador, "posicion": n_posicion, "liga": n_liga,
                        "equipo": n_equipo, "jornada": n_jornada, "minutos": v_minutos,
                        "goles": v_goles, "asistencias": v_asis, "tiros": v_tiros,
                        "pases_clave": v_pases, "duelos_ganados": v_duelos,
                        "intercepciones": v_intercep, "faltas": v_faltas
                    }
                    if supabase:
                        try:
                            supabase.table('partidos_stats').insert(stats_partido).execute()
                            st.success(f"Estadísticas guardadas permanentemente para {n_jugador}.")
                        except Exception as e:
                            st.error(f"Error al escribir en Supabase: {e}")
                else:
                    st.error("Ingresa el nombre del jugador.")

    else:
        st.info(f"Módulo '{opcion}' listo para sincronización con Supabase.")
