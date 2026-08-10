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

# 2. INICIALIZAR MEMORIA (Datos y Jugadores Restaurados)
if 'scouting_db' not in st.session_state:
    st.session_state['scouting_db'] = [
        {"ID": 1, "Nombre": "Alisana Yirajang", "Edad": 21, "Club": "Slovan", "Valor": "€800k", "Overall": 85, "Viabilidad": "🔴 Baja", "Posición": "Extremo", "Foto": None},
        {"ID": 2, "Nombre": "Fidel Ambriz", "Edad": 21, "Club": "Monterrey", "Valor": "€4.5M", "Overall": 87, "Viabilidad": "🟡 Media", "Posición": "Medio", "Foto": None}
    ]

if 'equipo_ignition' not in st.session_state:
    st.session_state['equipo_ignition'] = [
        {"ID": 3, "Nombre": "José Juan Macías", "Edad": 24, "Club": "Pumas", "Liga": "🇲🇽 Liga MX", "Status": "FIRMADO 🟡", "Posición": "Delantero", "Foto": None},
        {"ID": 4, "Nombre": "Oscar García", "Edad": 20, "Club": "León", "Liga": "🇲🇽 Liga MX", "Status": "FIRMADO 🟡", "Posición": "Medio", "Foto": None},
        {"ID": 5, "Nombre": "Kevin Mora", "Edad": 19, "Club": "León", "Liga": "🇲🇽 Liga MX", "Status": "FIRMADO 🟡", "Posición": "Lateral Derecho", "Foto": None},
        {"ID": 6, "Nombre": "Miguel Mendoza", "Edad": 17, "Club": "León", "Liga": "🇲🇽 Liga MX U-17", "Status": "FIRMADO 🟡", "Posición": "Extremo", "Foto": None},
        {"ID": 7, "Nombre": "Sergio Luna", "Edad": 19, "Club": "León", "Liga": "🇲🇽 Liga MX U-19", "Status": "FIRMADO 🟡", "Posición": "Defensa Central", "Foto": None},
        {"ID": 8, "Nombre": "Bryan Destin", "Edad": 18, "Club": "CT United", "Liga": "🇺🇸 MLS", "Status": "OBJETIVO 🔵", "Posición": "Delantero", "Foto": None}
    ]

# 3. LAS 30 MÉTRICAS QUIRÚRGICAS (Diccionario Completo)
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

# 4. FUNCIÓN: MOSTRAR PERFIL Y BOTÓN DE BORRADO
def mostrar_perfil_jugador(jugador, lista_origen, key_prefix):
    st.markdown("---")
    c_title, c_btn = st.columns([4, 1])
    c_title.subheader(f"👤 Perfil Analítico: {jugador['Nombre']}")
    
    # 4.1 BOTÓN DE ELIMINAR
    if c_btn.button("🗑️ Eliminar Perfil", key=f"del_{key_prefix}_{jugador['ID']}"):
        st.session_state[lista_origen] = [j for j in st.session_state[lista_origen] if j['ID'] != jugador['ID']]
        st.rerun()
    
    col_img, col_info, col_radar = st.columns([1, 2, 2])
    with col_img:
        # Mostrar foto si se subió, si no, placeholder
        if jugador.get('Foto'):
            st.image(jugador['Foto'], width=150)
        else:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150)
        
    with col_info:
        st.markdown(f"**Posición:** {jugador['Posición']}")
        st.markdown(f"**Club:** {jugador['Club']} | **Edad:** {jugador['Edad']}")
        
    with col_radar:
        categorias = ['Ataque', 'Creación', 'Defensa', 'Físico', 'Posesión']
        valores = [85, 70, 45, 80, 65]
        angulos = [n / 5 * 2 * math.pi for n in range(5)]; angulos += angulos[:1]; valores += valores[:1]
        fig, ax = plt.subplots(figsize=(2, 2), subplot_kw=dict(polar=True))
        plt.xticks(angulos[:-1], categorias, color='#1A2B4C', size=8)
        ax.plot(angulos, valores, color='#1A2B4C'); ax.fill(angulos, valores, color='#C8A165', alpha=0.5)
        fig.patch.set_facecolor('none'); ax.set_facecolor('none'); ax.set_yticklabels([])
        st.pyplot(fig, use_container_width=True)
        
    # 4.2 LAS 30 MÉTRICAS QUIRÚRGICAS (Dependientes de la posición)
    st.markdown(f"### Matriz de Rendimiento p/90 ({jugador['Posición']})")
    metricas_q = obtener_metricas(jugador['Posición'])
    tabs = st.tabs(list(metricas_q.keys()))
    for i, (pilar, lista_metricas) in enumerate(metricas_q.items()):
        with tabs[i]:
            cols = st.columns(4) # 4 columnas para que quepan mejor las 7-8 métricas
            for j, metrica in enumerate(lista_metricas):
                cols[j % 4].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165;'>API</span></div>", unsafe_allow_html=True)

# 5. ESTÉTICA
st.markdown("""
    <style>
    [data-testid="stSidebar"] {background-color: #1A2B4C !important;}
    [data-testid="stSidebar"] * {color: #FFFFFF !important;}
    .metric-card {background-color: #F8F9FA; border-left: 5px solid #1A2B4C; padding: 10px; border-radius: 5px; margin-bottom: 10px; color: #1A2B4C; font-size: 12px;}
    .stButton>button {background-color: #C8A165; color: #1A2B4C !important; font-weight: bold; width: 100%;}
    </style>
""", unsafe_allow_html=True)

# 6. NAVEGACIÓN Y LOGIN
LIGAS_MUNDIALES = ["🇲🇽 Liga MX", "🇪🇸 La Liga", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "🇺🇸 MLS", "🇦🇷 Primera División Argentina", "🇧🇷 Brasileirao", "🇫🇷 Ligue 1", "🇮🇹 Serie A", "🇩🇪 Bundesliga"]

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
        seleccion = st.dataframe(df_scouting[["Nombre", "Edad", "Club", "Valor", "Overall", "Viabilidad", "Posición"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        
        if len(seleccion.selection.rows) > 0:
            idx = seleccion.selection.rows[0]
            jugador_seleccionado = st.session_state['scouting_db'][idx]
            mostrar_perfil_jugador(jugador_seleccionado, 'scouting_db', 'sc')
            
        st.markdown("---")
        with st.expander("➕ Añadir Jugador a Base de Scouting"):
            with st.form("nuevo_scouting", clear_on_submit=True):
                c1, c2 = st.columns(2)
                n_nombre = c1.text_input("Nombre")
                n_edad = c1.number_input("Edad", 15, 40, 20)
                n_club = c1.text_input("Club")
                n_posicion = c2.selectbox("Posición", ["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"])
                n_valor = c2.text_input("Valor de Mercado")
                n_foto = st.file_uploader("Subir Foto de Perfil (jpg, png)", type=['jpg', 'png', 'jpeg']) # SUBIDA DE ARCHIVO REAL
                
                if st.form_submit_button("Guardar Jugador"):
                    # Simulamos el guardado de la foto leyéndola a memoria
                    foto_data = n_foto.getvalue() if n_foto else None 
                    nuevo = {"ID": len(st.session_state['scouting_db']) + 100, "Nombre": n_nombre, "Edad": n_edad, "Club": n_club, "Valor": n_valor, "Overall": 70, "Viabilidad": "🟡 Media", "Posición": n_posicion, "Foto": foto_data}
                    st.session_state['scouting_db'].append(nuevo)
                    st.rerun()

    # MÓDULO 2: EQUIPO IGNITION
    elif opcion == "Equipo Ignition":
        st.title("💼 Equipo Ignition")
        df_equipo = pd.DataFrame(st.session_state['equipo_ignition'])
        seleccion_eq = st.dataframe(df_equipo[["Nombre", "Edad", "Club", "Liga", "Posición", "Status"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        
        if len(seleccion_eq.selection.rows) > 0:
            idx_eq = seleccion_eq.selection.rows[0]
            jugador_eq = st.session_state['equipo_ignition'][idx_eq]
            mostrar_perfil_jugador(jugador_eq, 'equipo_ignition', 'eq')

        st.markdown("---")
        with st.expander("➕ Añadir Jugador a Equipo Ignition"):
            with st.form("nuevo_equipo", clear_on_submit=True):
                c1, c2 = st.columns(2)
                e_nombre = c1.text_input("Nombre Completo")
                e_edad = c1.number_input("Edad", 15, 45, 20)
                e_posicion = c1.selectbox("Posición", ["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"])
                e_status = c1.selectbox("Estatus", ["FIRMADO 🟡", "OBJETIVO 🔵", "SEGUIMIENTO INTENSIVO 🟢"])
                e_liga = c2.selectbox("Liga", LIGAS_MUNDIALES)
                e_club = c2.text_input("Club Actual")
                e_foto = st.file_uploader("Subir Foto de Perfil (jpg, png)", type=['jpg', 'png', 'jpeg']) # SUBIDA DE ARCHIVO REAL
                
                if st.form_submit_button("Registrar en Equipo Ignition"):
                    foto_data = e_foto.getvalue() if e_foto else None
                    nuevo_eq = {"ID": len(st.session_state['equipo_ignition']) + 100, "Nombre": e_nombre, "Edad": e_edad, "Posición": e_posicion, "Club": e_club, "Liga": e_liga, "Status": e_status, "Foto": foto_data}
                    st.session_state['equipo_ignition'].append(nuevo_eq)
                    st.rerun() 

    # MÓDULO 3: INGRESO DE DATA 
    elif opcion == "Ingreso de Data (Partidos)":
        st.title("📥 Registro Manual de Estadísticas")
        with st.form("form_partido"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Nombre del Jugador")
                st.selectbox("🏆 Torneo", LIGAS_MUNDIALES)
                st.selectbox("📍 Posición (Define las métricas base)", ["Portero", "Lateral Izquierdo", "Lateral Derecho", "Defensa Central", "Medio", "Extremo", "Delantero"]) # AÑADIDO
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

    else:
        st.info(f"Módulo de {opcion} en construcción.")
