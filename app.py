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
        url = st.secrets["SUPABASE_URL"].strip().rstrip("/")
        key = st.secrets["SUPABASE_KEY"].strip()
        return create_client(url, key)
    except Exception:
        return None

supabase = init_connection()

def procesar_foto(uploaded_file):
    if uploaded_file is not None:
        return "data:image/png;base64," + base64.b64encode(uploaded_file.getvalue()).decode()
    return None

# 2. CARGA DESDE SUPABASE O RESPALDO LOCAL
def cargar_desde_supabase(tabla):
    if supabase:
        try:
            res = supabase.table(tabla).select("*").order("id", desc=False).execute()
            if res.data and len(res.data) > 0:
                registros = []
                for row in res.data:
                    elem = {
                        "ID": row.get("id"),
                        "Nombre": row.get("nombre", "Sin Nombre"),
                        "Edad": row.get("edad", 20),
                        "Club": row.get("club", "N/D"),
                        "Liga": row.get("liga", "N/D"),
                        "Posición": row.get("posicion", "Mediocentro (MC)"),
                        "Foto": row.get("foto")
                    }
                    if "valor" in row: elem["Valor"] = row.get("valor", "N/D")
                    if "nacionalidad" in row: elem["Nacionalidad"] = row.get("nacionalidad", "N/D")
                    if "agencia" in row: elem["Agencia"] = row.get("agencia", "N/D")
                    if "viabilidad" in row: elem["Viabilidad"] = row.get("viabilidad", "🟡 Media")
                    if "overall" in row: elem["Overall"] = row.get("overall", 70)
                    if "status" in row: elem["Status"] = row.get("status", "OBJETIVO 🔵")
                    registros.append(elem)
                return registros
        except Exception:
            pass
    return []

# Sincronización inicial
st.session_state['scouting_db'] = cargar_desde_supabase('scouting_db')
st.session_state['equipo_ignition'] = cargar_desde_supabase('equipo_ignition')

# 3. LISTA RIGUROSA DE POSICIONES
LISTA_POSICIONES = [
    "Portero", 
    "Defensa Central", 
    "Lateral Izquierdo", 
    "Lateral Derecho", 
    "Pivote Defensivo (MCD)", 
    "Mediocentro (MC)", 
    "Medio Centro Ofensivo (MCO)", 
    "Extremo", 
    "Delantero Centro"
]

def obtener_30_metricas(posicion):
    if posicion == "Portero":
        return {
            "Pilar 1: Atajadas y Reflejos (8)": ["Atajadas Totales p/90", "Reflejos a Quemarropa", "xG Evitados", "Desvíos Exitosos", "Atrapes sin Rebote", "1v1 Ganados %", "Atajadas de Penal", "Tiros Lejanos Salvados"],
            "Pilar 2: Distribución y Pies (7)": ["Pases Largos Precisos %", "Efectividad Pase Corto %", "Saques de Meta Exitosos", "Inicios de Contragolpe", "Pases bajo Presión", "Toques de Balón", "Pérdidas en Salida"],
            "Pilar 3: Dominio del Área (8)": ["Salidas por Alto Exitosas", "Despejes de Puños", "Intercepciones fuera de Área", "Duelos Aéreos Ganados %", "Reivindicaciones de Centro", "Tackles Defensivos", "Faltas Recibidas", "Acciones Defensivas Totales"],
            "Pilar 4: Físico y Contexto (7)": ["Minutos Jugados", "Errores Críticos que terminan en Gol", "Tarjetas Amarillas", "Tarjetas Rojas", "Lesiones", "Distancia Recorrida (km)", "Goles Concedidos p/90"]
        }
    elif posicion == "Defensa Central":
        return {
            "Pilar 1: Defensa Pura (8)": ["Duelos Defensivos Ganados %", "Intercepciones p/90", "Tackles Exitosos", "Bloqueos de Tiro", "Despejes Totales", "Recuperaciones de Balón", "Duelos 1v1 Ganados %", "Faltas Cometidas"],
            "Pilar 2: Juego Aéreo (7)": ["Duelos Aéreos Totales", "Duelos Aéreos Ganados %", "Goles de Cabeza", "Despejes de Cabeza", "Aéreos en Área Rival", "Aéreos en Área Propia", "Faltas Recibidas por Alto"],
            "Pilar 3: Salida y Posesión (8)": ["Pases Precisos %", "Pases Progresivos", "Pases Largos Precisos %", "Conducciones Progresivas", "Pases al Tercio Final", "Toques Totales", "Pérdidas de Balón", "Pases bajo Presión"],
            "Pilar 4: Físico y Contexto (7)": ["Minutos Jugados", "Tarjetas Amarillas", "Tarjetas Rojas", "Errores Críticos", "Sprints p/90", "Distancia Recorrida (km)", "Aceleraciones"]
        }
    elif posicion in ["Lateral Izquierdo", "Lateral Derecho"]:
        return {
            "Pilar 1: Cobertura Defensiva (7)": ["Duelos Defensivos Ganados %", "Intercepciones p/90", "Tackles Exitosos", "Bloqueos de Centro", "Recuperaciones tras Pérdida", "Despejes", "Duelos Aéreos Ganados %"],
            "Pilar 2: Progresión y Posesión (8)": ["Pases Progresivos", "Conducciones Progresivas", "Pases al Tercio Final", "Pases al Espacio", "Toques Totales", "Pérdidas en Salida", "Pases Precisos %", "Pases Recibidos"],
            "Pilar 3: Aporte Ofensivo (8)": ["Centros Precisos %", "Asistencias Esperadas (xA)", "Desbordes Exitosos", "Toques en Área Rival", "Asistencias Totales", "Tiros a Puerta", "Pases Clave", "Faltas Recibidas en Ataque"],
            "Pilar 4: Físico y Sprints (7)": ["Minutos Jugados", "Sprints p/90", "Distancia Recorrida (km)", "Velocidad Máxima (km/h)", "Tarjetas Amarillas", "Faltas Cometidas", "Tarjetas Rojas"]
        }
    elif posicion == "Pivote Defensivo (MCD)":
        return {
            "Pilar 1: Destrucción y Cobertura (8)": ["Duelos Defensivos Ganados %", "Intercepciones p/90", "Tackles Exitosos", "Presión Exitosa %", "Recuperaciones Altas", "Faltas Cometidas", "Bloqueos de Pase", "Recuperaciones en Campo Propio"],
            "Pilar 2: Posesión y Salida (8)": ["Pases Precisos %", "Toques Totales", "Pases bajo Presión", "Pérdidas de Balón", "Pases Recibidos", "Conducciones de Balón", "Faltas Recibidas", "Retención de Balón %"],
            "Pilar 3: Distribución y Transición (7)": ["Pases Progresivos", "Pases al Tercio Final", "Cambios de Orientación", "Pases Largos Precisos %", "Pases Clave", "Desbordes Evitados", "Intercepciones en Transición"],
            "Pilar 4: Físico y Despliegue (7)": ["Minutos Jugados", "Distancia Recorrida (km)", "Sprints p/90", "Duelos Aéreos Ganados %", "Tarjetas Amarillas", "Tarjetas Rojas", "Aceleraciones"]
        }
    elif posicion == "Mediocentro (MC)":
        return {
            "Pilar 1: Control y Volumen (8)": ["Pases Precisos %", "Toques Totales", "Pases bajo Presión", "Pérdidas de Balón", "Pases Recibidos", "Retención de Balón %", "Pases Cortos Exitosos", "Orientación de Juego"],
            "Pilar 2: Creación y Progresión (8)": ["Pases Clave p/90", "Pases Progresivos", "Asistencias Esperadas (xA)", "Pases al Tercio Final", "Cambios de Orientación", "Asistencias Directas", "Desbordes Exitosos", "Tiros de Larga Distancia"],
            "Pilar 3: Trabajo Defensivo (7)": ["Duelos Defensivos Ganados %", "Intercepciones", "Tackles Exitosos", "Presión Exitosa", "Recuperaciones de Balón", "Faltas Cometidas", "Bloqueos"],
            "Pilar 4: Finalización y Físico (7)": ["Goles Esperados (xG)", "Tiros a Puerta", "Goles Totales", "Minutos Jugados", "Distancia Recorrida (km)", "Sprints p/90", "Tarjetas Amarillas"]
        }
    elif posicion == "Medio Centro Ofensivo (MCO)":
        return {
            "Pilar 1: Visión y Creación (8)": ["Pases Clave p/90", "Asistencias Esperadas (xA)", "Pases al Área Rival", "Pases Filtro Exitosos", "Asistencias Directas", "Toques en Tercio Final", "Pases Recibidos entre Líneas", "Pases Progresivos"],
            "Pilar 2: Desequilibrio (7)": ["Regates Exitosos %", "Duelos Ofensivos Ganados", "Conducciones al Área", "Faltas Recibidas en Ataque", "Aceleraciones", "Pérdidas de Balón", "Fueras de Lugar"],
            "Pilar 3: Finalización (8)": ["Goles Esperados (xG)", "Tiros Totales p/90", "Tiros a Puerta", "Goles Totales", "Toques en Área Rival", "Tiros de Fuera del Área", "Tiros al Palo", "Conversión de Gol %"],
            "Pilar 4: Presión y Físico (7)": ["Presión Alta Exitosa", "Recuperaciones en Campo Rival", "Minutos Jugados", "Sprints p/90", "Distancia Recorrida (km)", "Velocidad Máxima", "Tarjetas Amarillas"]
        }
    elif posicion == "Extremo":
        return {
            "Pilar 1: Desequilibrio y Regate (8)": ["Regates Exitosos %", "Duelos Ofensivos Ganados", "Desbordes por Banda", "Faltas Recibidas en Ataque", "Aceleraciones p/90", "Conducciones al Área", "Pérdidas de Balón", "Fueras de Lugar"],
            "Pilar 2: Creación y Centros (7)": ["Centros Precisos %", "Pases Clave p/90", "Asistencias Esperadas (xA)", "Asistencias Directas", "Pases al Área Rival", "Toques Totales", "Pases Progresivos Recibidos"],
            "Pilar 3: Finalización (8)": ["Goles Esperados (xG)", "Tiros Totales p/90", "Tiros a Puerta", "Goles Totales", "Toques en Área Rival", "Tiros al Palo", "Conversión de Gol %", "Duelos Aéreos Ganados"],
            "Pilar 4: Físico y Trabajo (7)": ["Presión en Tercio Rival", "Recuperaciones Altas", "Intercepciones", "Minutos Jugados", "Sprints p/90", "Velocidad Máxima (km/h)", "Distancia Recorrida"]
        }
    else: # Delantero Centro
        return {
            "Pilar 1: Finalización Eficaz (8)": ["Goles Totales p/90", "Goles Esperados (xG)", "Tiros a Puerta %", "Tiros Totales p/90", "Conversión de Gol %", "Penales Anotados", "Tiros al Palo", "Fueras de Lugar"],
            "Pilar 2: Presencia en Área (7)": ["Toques en Área Rival", "Duelos Aéreos Ganados %", "Goles de Cabeza", "Faltas Recibidas en Área", "Pases Recibidos en Área", "Anticipaciones Ofensivas", "Rebotes Ganados"],
            "Pilar 3: Asociación y Apoyos (8)": ["Asistencias Directas", "Asistencias Esperadas (xA)", "Pases Clave p/90", "Regates Exitosos", "Duelos Ofensivos Ganados", "Pases Precisos %", "Pérdidas de Balón", "Faltas Cometidas en Ataque"],
            "Pilar 4: Físico y Presión (7)": ["Minutos Jugados", "Presión Exitosa Alta", "Recuperaciones en Campo Rival", "Sprints p/90", "Distancia Recorrida (km)", "Velocidad Máxima", "Tarjetas Amarillas"]
        }

# 4. CONFIGURADOR DEL RADAR DINÁMICO
def obtener_ejes_radar(posicion):
    if posicion == "Portero":
        return ['Reflejos', 'Salidas Aéreas', 'Distribución', '1v1 Ganados', 'Juego de Pies']
    elif posicion == "Defensa Central":
        return ['Defensa Pura', 'Juego Aéreo', 'Salida de Balón', 'Cobertura', 'Físico']
    elif posicion in ["Lateral Izquierdo", "Lateral Derecho"]:
        return ['Defensa', 'Progresión', 'Centros/xA', 'Desborde', 'Despliegue']
    elif posicion == "Pivote Defensivo (MCD)":
        return ['Destrucción', 'Cobertura', 'Recuperación', 'Salida de Balón', 'Físico']
    elif posicion == "Mediocentro (MC)":
        return ['Volumen Pase', 'Creación', 'Presión', 'Transición', 'Llegada']
    elif posicion == "Medio Centro Ofensivo (MCO)":
        return ['Visión/xA', 'Pases Clave', 'Regate', 'Finalización', 'Movilidad']
    elif posicion == "Extremo":
        return ['Desequilibrio', 'Centros', 'Finalización', 'Aceleración', 'Presión Alta']
    else: # Delantero Centro
        return ['Finalización', 'Juego Aéreo', 'Presencia Área', 'Asociación', 'Presión Alta']

def calcular_valores_radar(nombre_jugador, posicion):
    ejes = obtener_ejes_radar(posicion)
    if supabase and nombre_jugador:
        try:
            res = supabase.table('partidos_stats').select("*").eq('jugador', nombre_jugador).execute()
            if res.data and len(res.data) > 0:
                df_p = pd.DataFrame(res.data)
                tot_min = df_p['minutos'].sum()
                if tot_min > 0:
                    goles_p90 = (df_p['goles'].sum() / tot_min) * 90
                    asis_p90 = (df_p['asistencias'].sum() / tot_min) * 90
                    tiros_p90 = (df_p['tiros'].sum() / tot_min) * 90
                    pases_p90 = (df_p['pases_clave'].sum() / tot_min) * 90
                    duelos_p90 = (df_p['duelos_ganados'].sum() / tot_min) * 90
                    inter_p90 = (df_p['intercepciones'].sum() / tot_min) * 90
                    
                    v1 = min(100, int(goles_p90 * 30 + tiros_p90 * 15 + 40))
                    v2 = min(100, int(asis_p90 * 35 + pases_p90 * 15 + 40))
                    v3 = min(100, int(inter_p90 * 20 + duelos_p90 * 5 + 40))
                    v4 = min(100, int(duelos_p90 * 8 + 45))
                    v5 = min(100, int(pases_p90 * 15 + 50))
                    return ejes, [v1, v2, v3, v4, v5]
        except Exception:
            pass
    return ejes, [70, 75, 65, 80, 72]

# 5. DICCIONARIO COMPLETO DE LIGAS Y EQUIPOS 2026/2027
LIGAS_MUNDIALES = [
    "🇲🇽 Liga MX", "🇲🇽 Liga de Expansión", "🇲🇽 Liga MX U-21", "🇲🇽 Liga MX U-19", "🇲🇽 Liga MX U-17", "🇲🇽 Liga MX U-15",
    "🇪🇸 La Liga", "🇪🇸 Liga Hypermotion", "🇪🇸 Primera RFEF", "🇪🇸 Segunda RFEF",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 League One", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 League Two",
    "🇫🇷 Ligue 1", "🇫🇷 Ligue 2", "🇮🇹 Serie A", "🇮🇹 Serie B",
    "🇩🇪 Bundesliga", "🇩🇪 2. Bundesliga", "🇸🇪 Allsvenskan", "🇳🇴 Eliteserien",
    "🇳🇱 Eredivisie", "🇧🇪 Jupiler Pro League", "🇩🇰 Superliga Dinamarca", "🇵🇱 Ekstraklasa",
    "🇧🇬 efbet League Bulgaria", "🇭🇷 SuperSport HNL", "🇨🇿 Chance Liga", "🇷🇸 Superliga Serbia",
    "🇦TV Bundesliga Austria", "🇨🇭 Superliga de Suiza", "🇵🇹 Liga Portugal", "🇵🇹 Liga 2 Portugal",
    "🇸Kb Liga Eslovaquia", "🇸🇮 Liga Eslovenia",
    "🇦🇷 Primera División Argentina", "🇨🇷 Primera División Costa Rica", "🇨🇴 Primera División Colombia", 
    "🇧🇷 Brasileirao", "🇧🇷 Brasileirao Série B", "🇺🇾 Primera División Uruguay", "🇨🇱 Primera División Chile", 
    "🇺🇸 MLS", "🇺🇸 MLS Next Pro", "🇺🇸 USL", "🇯🇵 J-League"
]

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
    "🇺🇸 MLS": ["Atlanta United FC", "Austin FC", "Charlotte FC", "Chicago Fire FC", "FC Cincinnati", "Colorado Rapids", "Columbus Crew", "D.C. United", "FC Dallas", "Houston Dynamo FC", "Inter Miami CF", "LA Galaxy", "LAFC", "Minnesota United FC", "CF Montréal", "Nashville SC", "New England Revolution", "New York City FC", "New York Red Bulls", "Orlando City SC", "Philadelphia Union", "Portland Timbers", "Real Salt Lake", "San Jose Earthquakes", "Seattle Sounders FC", "Sporting Kansas City", "St. Louis City SC", "Toronto FC", "Vancouver Whitecaps FC"],
    "🇦🇷 Primera División Argentina": ["Boca Juniors", "River Plate", "Racing Club", "Independiente", "San Lorenzo", "Vélez Sarsfield", "Estudiantes de La Plata", "Gimnasia La Plata", "Talleres de Córdoba", "Belgrano", "Rosario Central", "Newell's Old Boys", "Argentinos Juniors", "CA Huracán", "CA Lanús", "Godoy Cruz"]
}

# 6. MOSTRAR PERFIL DE JUGADOR CON MANEJO DE ERRORES SEGURO
def mostrar_perfil_jugador(jugador, tabla_origen, idx_origen):
    st.markdown("---")
    st.subheader(f"👤 Perfil Analítico: {jugador['Nombre']}")
    
    col_img, col_info, col_radar = st.columns([1, 2, 2])
    with col_img:
        foto_src = jugador.get('Foto') if jugador.get('Foto') else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
        st.markdown(f"""
            <div class="player-photo-card">
                <img src="{foto_src}" class="player-photo-img" />
            </div>
        """, unsafe_allow_html=True)
        
    with col_info:
        st.markdown(f"**Posición Específica:** {jugador['Posición']}")
        st.markdown(f"**Club:** {jugador['Club']} | **Liga:** {jugador.get('Liga', 'N/D')}")
        st.markdown(f"**Edad:** {jugador['Edad']}")
        
        if 'Nacionalidad' in jugador and jugador['Nacionalidad']:
            st.markdown(f"**Nacionalidad:** {jugador['Nacionalidad']}")
        if 'Valor' in jugador and jugador['Valor']:
            st.markdown(f"**Valor de Mercado:** {jugador['Valor']}")
        if 'Agencia' in jugador and jugador['Agencia']:
            st.markdown(f"**Agencia:** {jugador['Agencia']}")
        if 'Viabilidad' in jugador and jugador['Viabilidad']:
            st.markdown(f"**Viabilidad:** {jugador['Viabilidad']}")
        if 'Status' in jugador: 
            st.markdown(f"**Status:** {jugador['Status']}")
        
    with col_radar:
        ejes_dinamicos, valores_dinamicos = calcular_valores_radar(jugador['Nombre'], jugador['Posición'])
        angulos = [n / 5 * 2 * math.pi for n in range(5)]
        angulos += angulos[:1]
        valores_plot = valores_dinamicos + valores_dinamicos[:1]
        
        fig, ax = plt.subplots(figsize=(2.2, 2.2), subplot_kw=dict(polar=True))
        plt.xticks(angulos[:-1], ejes_dinamicos, color='#1A2B4C', size=7, weight='bold')
        ax.plot(angulos, valores_plot, color='#1A2B4C', linewidth=2)
        ax.fill(angulos, valores_plot, color='#C8A165', alpha=0.45)
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        ax.set_yticklabels([])
        st.pyplot(fig, use_container_width=True)

    st.markdown(f"### Matriz Quirúrgica p/90 ({jugador['Posición']})")
    metricas_q = obtener_30_metricas(jugador['Posición'])
    tabs = st.tabs(list(metricas_q.keys()))
    for i, (pilar, lista_metricas) in enumerate(metricas_q.items()):
        with tabs[i]:
            cols = st.columns(4)
            for j, metrica in enumerate(lista_metricas):
                cols[j % 4].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165; font-weight:bold;'>Acumulado p/90</span></div>", unsafe_allow_html=True)
                
    with st.expander(f"✏️ Editar Perfil y Subir Foto de {jugador['Nombre']}"):
        c_ed1, c_ed2 = st.columns(2)
        nuevo_nom = c_ed1.text_input("Nombre", value=jugador['Nombre'], key=f"nm_{jugador['ID']}")
        nueva_edad = c_ed1.number_input("Edad", 15, 45, value=jugador['Edad'], key=f"ed_{jugador['ID']}")
        
        pos_idx = LISTA_POSICIONES.index(jugador['Posición']) if jugador['Posición'] in LISTA_POSICIONES else 0
        nueva_pos = c_ed1.selectbox("Posición Específica", LISTA_POSICIONES, index=pos_idx, key=f"pos_{jugador['ID']}")
        
        nueva_nac = c_ed1.text_input("Nacionalidad", value=jugador.get('Nacionalidad', ''), key=f"nac_{jugador['ID']}")
        nuevo_val = c_ed2.text_input("Valor de Mercado", value=jugador.get('Valor', ''), key=f"val_{jugador['ID']}")
        nueva_agencia = c_ed2.text_input("Agencia", value=jugador.get('Agencia', ''), key=f"ag_{jugador['ID']}")
        nueva_viab = c_ed2.selectbox("Viabilidad", ["🟢 Alta", "🟡 Media", "🔴 Baja"], index=["🟢 Alta", "🟡 Media", "🔴 Baja"].index(jugador.get('Viabilidad', '🟡 Media')), key=f"via_{jugador['ID']}")
        
        nueva_liga = c_ed2.selectbox("Liga", LIGAS_MUNDIALES, index=LIGAS_MUNDIALES.index(jugador.get('Liga', LIGAS_MUNDIALES[0])) if jugador.get('Liga') in LIGAS_MUNDIALES else 0, key=f"lg_edit_{jugador['ID']}")
        if nueva_liga in EQUIPOS_POR_LIGA:
            nuevo_club = c_ed2.selectbox("Club", EQUIPOS_POR_LIGA[nueva_liga], key=f"cl_edit_{jugador['ID']}")
        else:
            nuevo_club = c_ed2.text_input("Club (Escribir nombre)", value=jugador['Club'], key=f"cl_txt_edit_{jugador['ID']}")
            
        nueva_foto = st.file_uploader("Subir Foto de Perfil (PNG, JPG)", type=['jpg', 'png', 'jpeg'], key=f"ft_{jugador['ID']}")
        
        col_btn1, col_btn2 = st.columns([1, 1])
        if col_btn1.button("💾 Guardar Cambios en Supabase", key=f"sv_{jugador['ID']}"):
            foto_base64 = procesar_foto(nueva_foto) if nueva_foto else jugador.get('Foto')
            payload = {
                "nombre": nuevo_nom, "edad": nueva_edad, "posicion": nueva_pos,
                "liga": nueva_liga, "club": nuevo_club, "foto": foto_base64,
                "valor": nuevo_val, "viabilidad": nueva_viab
            }
            if nueva_nac: payload["nacionalidad"] = nueva_nac
            if nueva_agencia: payload["agencia"] = nueva_agencia

            if supabase and jugador.get('ID'):
                try:
                    supabase.table(tabla_origen).update(payload).eq('id', jugador['ID']).execute()
                    st.success("Guardado en Supabase exitoso.")
                    st.rerun()
                except Exception as e:
                    # Intento alternativo sin campos no soportados
                    try:
                        payload_base = {
                            "nombre": nuevo_nom, "edad": nueva_edad, "posicion": nueva_pos,
                            "liga": nueva_liga, "club": nuevo_club, "foto": foto_base64,
                            "valor": nuevo_val, "viabilidad": nueva_viab
                        }
                        supabase.table(tabla_origen).update(payload_base).eq('id', jugador['ID']).execute()
                        st.success("Guardado en Supabase exitoso.")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error en Supabase: {ex}")
            
        if col_btn2.button("🗑️ Eliminar Perfil", key=f"dl_{jugador['ID']}"):
            if supabase and jugador.get('ID'):
                try: 
                    supabase.table(tabla_origen).delete().eq('id', jugador['ID']).execute()
                    st.success("Jugador eliminado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")

# 7. ESTÉTICA
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA !important; }
    [data-testid="stSidebar"] { background-color: #1A2B4C !important; border-right: 2px solid #C8A165 !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    .player-photo-card {
        width: 150px;
        height: 180px;
        border-radius: 8px;
        border: 2px solid #C8A165;
        overflow: hidden;
        background-color: #111D35;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    .player-photo-img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        object-position: center;
    }
    
    .login-container { max-width: 420px; margin: 50px auto; padding: 40px; background: #FFFFFF; border-radius: 12px; box-shadow: 0 10px 30px rgba(26, 43, 76, 0.12); border-top: 5px solid #C8A165; text-align: center; }
    .metric-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #1A2B4C; padding: 12px; border-radius: 6px; margin-bottom: 10px; color: #1A2B4C; font-size: 13px; }
    .stButton>button { background-color: #C8A165 !important; color: #1A2B4C !important; font-weight: bold !important; border: none !important; border-radius: 6px !important; width: 100% !important; }
    .stButton>button:hover { background-color: #1A2B4C !important; color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

# 8. SESIÓN Y NAVEGACIÓN
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
        
        with st.expander("➕ Crear Nuevo Jugador a Scoutear"):
            c_a, c_b = st.columns(2)
            reg_nom = c_a.text_input("Nombre Completo", key="reg_nom_input")
            reg_edad = c_a.number_input("Edad", 15, 45, 20, key="reg_edad_input")
            reg_pos = c_a.selectbox("Posición Específica", LISTA_POSICIONES, key="reg_pos_input")
            reg_nac = c_a.text_input("Nacionalidad (ej. 🇲🇽 Mexicana)", key="reg_nac_input")
            
            reg_val = c_b.text_input("Valor de Mercado (ej. €1.2M)", key="reg_val_input")
            reg_ag = c_b.text_input("Agencia de Representación", key="reg_ag_input")
            reg_viab = c_b.selectbox("Viabilidad de Fichaje", ["🟢 Alta", "🟡 Media", "🔴 Baja"], key="reg_viab_input")
            
            reg_liga = c_b.selectbox("Liga", LIGAS_MUNDIALES, key="reg_liga_dyn")
            if reg_liga in EQUIPOS_POR_LIGA:
                reg_club = c_b.selectbox("Club", EQUIPOS_POR_LIGA[reg_liga], key="reg_club_dyn")
            else:
                reg_club = c_b.text_input("Club (Escribir)", key="reg_club_txt_dyn")
                
            reg_foto = st.file_uploader("Foto de Perfil (Opcional)", type=['jpg', 'png', 'jpeg'], key="reg_foto_dyn")
            
            if st.button("Guardar Jugador en Nube", key="btn_reg_scouting"):
                if reg_nom and supabase:
                    f_b64 = procesar_foto(reg_foto)
                    payload = {
                        "nombre": reg_nom, "edad": reg_edad, "posicion": reg_pos,
                        "liga": reg_liga, "club": reg_club, "foto": f_b64,
                        "valor": reg_val, "viabilidad": reg_viab, "overall": 70
                    }
                    if reg_nac: payload["nacionalidad"] = reg_nac
                    if reg_ag: payload["agencia"] = reg_ag

                    try:
                        supabase.table('scouting_db').insert(payload).execute()
                        st.success(f"{reg_nom} guardado en la nube.")
                        st.rerun()
                    except Exception as e:
                        # Intento con campos base si las columnas nuevas no están indexadas
                        try:
                            payload_base = {
                                "nombre": reg_nom, "edad": reg_edad, "posicion": reg_pos,
                                "liga": reg_liga, "club": reg_club, "foto": f_b64,
                                "valor": reg_val, "viabilidad": reg_viab, "overall": 70
                            }
                            supabase.table('scouting_db').insert(payload_base).execute()
                            st.success(f"{reg_nom} guardado en la nube.")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error en Supabase: {ex}")

        if len(st.session_state['scouting_db']) > 0:
            df_scouting = pd.DataFrame(st.session_state['scouting_db'])
            seleccion = st.dataframe(df_scouting[["Nombre", "Edad", "Club", "Liga", "Posición", "Viabilidad"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
            
            if len(seleccion.selection.rows) > 0:
                mostrar_perfil_jugador(st.session_state['scouting_db'][seleccion.selection.rows[0]], 'scouting_db', seleccion.selection.rows[0])

    elif opcion == "Equipo Ignition":
        st.title("💼 Equipo Ignition")
        
        with st.expander("➕ Añadir Jugador a Equipo Ignition"):
            c_a, c_b = st.columns(2)
            eq_nom = c_a.text_input("Nombre Completo", key="eq_nom_input")
            eq_edad = c_a.number_input("Edad", 15, 45, 20, key="eq_edad_input")
            eq_pos = c_a.selectbox("Posición Específica", LISTA_POSICIONES, key="eq_pos_input")
            eq_status = c_a.selectbox("Estatus", ["FIRMADO 🟡", "OBJETIVO 🔵", "SEGUIMIENTO INTENSIVO 🟢"], key="eq_status_input")
            
            eq_liga = c_b.selectbox("Liga", LIGAS_MUNDIALES, key="eq_liga_dyn")
            if eq_liga in EQUIPOS_POR_LIGA:
                eq_club = c_b.selectbox("Club", EQUIPOS_POR_LIGA[eq_liga], key="eq_club_dyn")
            else:
                eq_club = c_b.text_input("Club (Escribir)", key="eq_club_txt_dyn")
                
            eq_foto = st.file_uploader("Foto de Perfil (Opcional)", type=['jpg', 'png', 'jpeg'], key="eq_foto_dyn")
            
            if st.button("Guardar en Equipo Ignition", key="btn_reg_equipo"):
                if eq_nom and supabase:
                    f_b64 = procesar_foto(eq_foto)
                    payload = {
                        "nombre": eq_nom, "edad": eq_edad, "posicion": eq_pos,
                        "liga": eq_liga, "club": eq_club, "foto": f_b64, "status": eq_status
                    }
                    try:
                        supabase.table('equipo_ignition').insert(payload).execute()
                        st.success(f"{eq_nom} registrado en Supabase.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error en Supabase: {e}")

        if len(st.session_state['equipo_ignition']) > 0:
            df_equipo = pd.DataFrame(st.session_state['equipo_ignition'])
            seleccion_eq = st.dataframe(df_equipo[["Nombre", "Edad", "Club", "Liga", "Posición", "Status"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
            
            if len(seleccion_eq.selection.rows) > 0:
                mostrar_perfil_jugador(st.session_state['equipo_ignition'][seleccion_eq.selection.rows[0]], 'equipo_ignition', seleccion_eq.selection.rows[0])

    elif opcion == "Ingreso de Data (Partidos)":
        st.title("📥 Registro Manual de Estadísticas")
        
        c1, c2 = st.columns(2)
        n_jugador = c1.text_input("Nombre del Jugador", key="p_nom_input")
        n_posicion = c1.selectbox("📍 Posición Específica", LISTA_POSICIONES, key="p_pos_input")
        
        n_liga = c2.selectbox("🏆 Competición", LIGAS_MUNDIALES, key="p_liga_dyn")
        if n_liga in EQUIPOS_POR_LIGA:
            n_equipo = c2.selectbox("🛡️ Equipo (2026/2027)", EQUIPOS_POR_LIGA[n_liga], key="p_club_dyn")
        else:
            n_equipo = c2.text_input("🛡️ Equipo (Escribir nombre del club)", key="p_club_txt_dyn")
            
        n_jornada = c1.selectbox("Jornada", [f"Jornada {i}" for i in range(1, 39)], key="p_jornada_input")
        
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
                if n_jugador and supabase:
                    stats_partido = {
                        "jugador": n_jugador, "posicion": n_posicion, "liga": n_liga,
                        "equipo": n_equipo, "jornada": n_jornada, "minutos": v_minutos,
                        "goles": v_goles, "asistencias": v_asis, "tiros": v_tiros,
                        "pases_clave": v_pases, "duelos_ganados": v_duelos,
                        "intercepciones": v_intercep, "faltas": v_faltas
                    }
                    try:
                        supabase.table('partidos_stats').insert(stats_partido).execute()
                        st.success(f"Estadísticas guardadas permanentemente para {n_jugador}.")
                    except Exception as e:
                        st.error(f"Error al escribir en Supabase: {e}")
                else:
                    st.error("Ingresa el nombre del jugador.")

    else:
        st.info(f"Módulo '{opcion}' listo para sincronización.")
