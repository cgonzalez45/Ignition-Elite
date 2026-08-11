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
                    if "viabilidad" in row: elem["Viabilidad"] = row.get("viabilidad", "Media")
                    if "overall" in row: elem["Overall"] = row.get("overall", 70)
                    if "status" in row: elem["Status"] = row.get("status", "OBJETIVO")
                    registros.append(elem)
                return registros
        except Exception:
            pass
    return []

# Sincronización inicial
st.session_state['scouting_db'] = cargar_desde_supabase('scouting_db')
st.session_state['equipo_ignition'] = cargar_desde_supabase('equipo_ignition')

# 3. POSICIONES Y LAS 30 MÉTRICAS COMPLETAS POR ROL
LISTA_POSICIONES = [
    "Portero", "Defensa Central", "Lateral Izquierdo", "Lateral Derecho", 
    "Pivote Defensivo (MCD)", "Mediocentro (MC)", "Medio Centro Ofensivo (MCO)", 
    "Extremo", "Delantero Centro"
]

def obtener_30_metricas(posicion):
    if posicion == "Portero":
        return {
            "Pilar 1: Atajadas y Reflejos (8)": ["Atajadas Totales", "Reflejos a Quemarropa", "xG Evitados", "Desvíos Exitosos", "Atrapes sin Rebote", "1v1 Ganados %", "Atajadas de Penal", "Tiros Lejanos Salvados"],
            "Pilar 2: Distribución y Pies (7)": ["Pases Largos Precisos %", "Efectividad Pase Corto %", "Saques de Meta Exitosos", "Inicios de Contragolpe", "Pases bajo Presión", "Toques de Balón", "Pérdidas en Salida"],
            "Pilar 3: Dominio del Área (8)": ["Salidas por Alto Exitosas", "Despejes de Puños", "Intercepciones fuera de Área", "Duelos Aéreos Ganados %", "Reivindicaciones de Centro", "Tackles Defensivos", "Faltas Recibidas", "Acciones Defensivas Totales"],
            "Pilar 4: Físico y Contexto (7)": ["Minutos Jugados", "Errores Críticos", "Tarjetas Amarillas", "Tarjetas Rojas", "Lesiones", "Distancia Recorrida (km)", "Goles Concedidos"]
        }
    elif posicion == "Defensa Central":
        return {
            "Pilar 1: Defensa Pura (8)": ["Duelos Defensivos Ganados %", "Intercepciones", "Tackles Exitosos", "Bloqueos de Tiro", "Despejes Totales", "Recuperaciones de Balón", "Duelos 1v1 Ganados %", "Faltas Cometidas"],
            "Pilar 2: Juego Aéreo (7)": ["Duelos Aéreos Totales", "Duelos Aéreos Ganados %", "Goles de Cabeza", "Despejes de Cabeza", "Aéreos en Área Rival", "Aéreos en Área Propia", "Faltas Recibidas por Alto"],
            "Pilar 3: Salida y Posesión (8)": ["Pases Precisos %", "Pases Progresivos", "Pases Largos Precisos %", "Conducciones Progresivas", "Pases al Tercio Final", "Toques Totales", "Pérdidas de Balón", "Pases bajo Presión"],
            "Pilar 4: Físico y Contexto (7)": ["Minutos Jugados", "Tarjetas Amarillas", "Tarjetas Rojas", "Errores Críticos", "Sprints", "Distancia Recorrida (km)", "Aceleraciones"]
        }
    elif posicion in ["Lateral Izquierdo", "Lateral Derecho"]:
        return {
            "Pilar 1: Cobertura Defensiva (7)": ["Duelos Defensivos Ganados %", "Intercepciones", "Tackles Exitosos", "Bloqueos de Centro", "Recuperaciones tras Pérdida", "Despejes", "Duelos Aéreos Ganados %"],
            "Pilar 2: Progresión y Posesión (8)": ["Pases Progresivos", "Conducciones Progresivas", "Pases al Tercio Final", "Pases al Espacio", "Toques Totales", "Pérdidas en Salida", "Pases Precisos %", "Pases Recibidos"],
            "Pilar 3: Aporte Ofensivo (8)": ["Centros Precisos %", "Asistencias Esperadas (xA)", "Desbordes Exitosos", "Toques en Área Rival", "Asistencias Totales", "Tiros a Puerta", "Pases Clave", "Faltas Recibidas en Ataque"],
            "Pilar 4: Físico y Sprints (7)": ["Minutos Jugados", "Sprints", "Distancia Recorrida (km)", "Velocidad Máxima (km/h)", "Tarjetas Amarillas", "Faltas Cometidas", "Tarjetas Rojas"]
        }
    elif posicion == "Pivote Defensivo (MCD)":
        return {
            "Pilar 1: Destrucción y Cobertura (8)": ["Duelos Defensivos Ganados %", "Intercepciones", "Tackles Exitosos", "Presión Exitosa %", "Recuperaciones Altas", "Faltas Cometidas", "Bloqueos de Pase", "Recuperaciones en Campo Propio"],
            "Pilar 2: Posesión y Salida (8)": ["Pases Precisos %", "Toques Totales", "Pases bajo Presión", "Pérdidas de Balón", "Pases Recibidos", "Conducciones de Balón", "Faltas Recibidas", "Retención de Balón %"],
            "Pilar 3: Distribución y Transición (7)": ["Pases Progresivos", "Pases al Tercio Final", "Cambios de Orientación", "Pases Largos Precisos %", "Pases Clave", "Desbordes Evitados", "Intercepciones en Transición"],
            "Pilar 4: Físico y Despliegue (7)": ["Minutos Jugados", "Distancia Recorrida (km)", "Sprints", "Duelos Aéreos Ganados %", "Tarjetas Amarillas", "Tarjetas Rojas", "Aceleraciones"]
        }
    elif posicion == "Mediocentro (MC)":
        return {
            "Pilar 1: Control y Volumen (8)": ["Pases Precisos %", "Toques Totales", "Pases bajo Presión", "Pérdidas de Balón", "Pases Recibidos", "Retención de Balón %", "Pases Cortos Exitosos", "Orientación de Juego"],
            "Pilar 2: Creación y Progresión (8)": ["Pases Clave", "Pases Progresivos", "Asistencias Esperadas (xA)", "Pases al Tercio Final", "Cambios de Orientación", "Asistencias Directas", "Desbordes Exitosos", "Tiros de Larga Distancia"],
            "Pilar 3: Trabajo Defensivo (7)": ["Duelos Defensivos Ganados %", "Intercepciones", "Tackles Exitosos", "Presión Exitosa", "Recuperaciones de Balón", "Faltas Cometidas", "Bloqueos"],
            "Pilar 4: Finalización y Físico (7)": ["Goles Esperados (xG)", "Tiros a Puerta", "Goles Totales", "Minutos Jugados", "Distancia Recorrida (km)", "Sprints", "Tarjetas Amarillas"]
        }
    elif posicion == "Medio Centro Ofensivo (MCO)":
        return {
            "Pilar 1: Visión y Creación (8)": ["Pases Clave", "Asistencias Esperadas (xA)", "Pases al Área Rival", "Pases Filtro Exitosos", "Asistencias Directas", "Toques en Tercio Final", "Pases Recibidos entre Líneas", "Pases Progresivos"],
            "Pilar 2: Desequilibrio (7)": ["Regates Exitosos %", "Duelos Ofensivos Ganados", "Conducciones al Área", "Faltas Recibidas en Ataque", "Aceleraciones", "Pérdidas de Balón", "Fueras de Lugar"],
            "Pilar 3: Finalización (8)": ["Goles Esperados (xG)", "Tiros Totales", "Tiros a Puerta", "Goles Totales", "Toques en Área Rival", "Tiros de Fuera del Área", "Tiros al Palo", "Conversión de Gol %"],
            "Pilar 4: Presión y Físico (7)": ["Presión Alta Exitosa", "Recuperaciones en Campo Rival", "Minutos Jugados", "Sprints", "Distancia Recorrida (km)", "Velocidad Máxima (km/h)", "Tarjetas Amarillas"]
        }
    elif posicion == "Extremo":
        return {
            "Pilar 1: Desequilibrio y Regate (8)": ["Regates Exitosos %", "Duelos Ofensivos Ganados", "Desbordes por Banda", "Faltas Recibidas en Ataque", "Aceleraciones", "Conducciones al Área", "Pérdidas de Balón", "Fueras de Lugar"],
            "Pilar 2: Creación y Centros (7)": ["Centros Precisos %", "Pases Clave", "Asistencias Esperadas (xA)", "Asistencias Directas", "Pases al Área Rival", "Toques Totales", "Pases Progresivos Recibidos"],
            "Pilar 3: Finalización (8)": ["Goles Esperados (xG)", "Tiros Totales", "Tiros a Puerta", "Goles Totales", "Toques en Área Rival", "Tiros al Palo", "Conversión de Gol %", "Duelos Aéreos Ganados"],
            "Pilar 4: Físico y Trabajo (7)": ["Presión en Tercio Rival", "Recuperaciones Altas", "Intercepciones", "Minutos Jugados", "Sprints", "Velocidad Máxima (km/h)", "Distancia Recorrida (km)"]
        }
    else: # Delantero Centro
        return {
            "Pilar 1: Finalización Eficaz (8)": ["Goles Totales", "Goles Esperados (xG)", "Tiros a Puerta %", "Tiros Totales", "Conversión de Gol %", "Penales Anotados", "Tiros al Palo", "Fueras de Lugar"],
            "Pilar 2: Presencia en Área (7)": ["Toques en Área Rival", "Duelos Aéreos Ganados %", "Goles de Cabeza", "Faltas Recibidas en Área", "Pases Recibidos en Área", "Anticipaciones Ofensivas", "Rebotes Ganados"],
            "Pilar 3: Asociación y Apoyos (8)": ["Asistencias Directas", "Asistencias Esperadas (xA)", "Pases Clave", "Regates Exitosos", "Duelos Ofensivos Ganados", "Pases Precisos %", "Pérdidas de Balón", "Faltas Cometidas en Ataque"],
            "Pilar 4: Físico y Presión (7)": ["Minutos Jugados", "Presión Exitosa Alta", "Recuperaciones en Campo Rival", "Sprints", "Distancia Recorrida (km)", "Velocidad Máxima (km/h)", "Tarjetas Amarillas"]
        }

def obtener_ejes_radar(posicion):
    if posicion == "Portero": return ['Reflejos', 'Salidas Aéreas', 'Distribución', '1v1 Ganados', 'Juego de Pies']
    elif posicion == "Defensa Central": return ['Defensa Pura', 'Juego Aéreo', 'Salida de Balón', 'Cobertura', 'Físico']
    elif posicion in ["Lateral Izquierdo", "Lateral Derecho"]: return ['Defensa', 'Progresión', 'Centros/xA', 'Desborde', 'Despliegue']
    elif posicion == "Pivote Defensivo (MCD)": return ['Destrucción', 'Cobertura', 'Recuperación', 'Salida de Balón', 'Físico']
    elif posicion == "Mediocentro (MC)": return ['Volumen Pase', 'Creación', 'Presión', 'Transición', 'Llegada']
    elif posicion == "Medio Centro Ofensivo (MCO)": return ['Visión/xA', 'Pases Clave', 'Regate', 'Finalización', 'Movilidad']
    elif posicion == "Extremo": return ['Desequilibrio', 'Centros', 'Finalización', 'Aceleración', 'Presión Alta']
    else: return ['Finalización', 'Juego Aéreo', 'Presencia Área', 'Asociación', 'Presión Alta']

@st.cache_data(ttl=3)
def consultar_partidos_jugador(nombre_jugador):
    if supabase and nombre_jugador:
        try:
            res = supabase.table('partidos_stats').select("*").eq('jugador', nombre_jugador).execute()
            if res.data:
                return pd.DataFrame(res.data)
        except Exception:
            pass
    return pd.DataFrame()

def calcular_promedios_df(df_input):
    if df_input.empty:
        return {}, 0, 0
    
    tot_min = df_input['minutos'].sum() if 'minutos' in df_input.columns else 0
    tot_partidos = len(df_input)
    
    if tot_min == 0:
        return {}, tot_partidos, 0
    
    promedios = {}
    sumas = {}
    
    for _, row in df_input.iterrows():
        m_custom = row.get('m_data') if isinstance(row.get('m_data'), dict) else {}
        
        for k, v in m_custom.items():
            try:
                val_f = float(v)
                sumas[k] = sumas.get(k, 0.0) + val_f
            except Exception:
                pass
                
        sumas["Goles Totales"] = sumas.get("Goles Totales", 0.0) + float(row.get('goles', 0) or 0)
        sumas["Asistencias Directas"] = sumas.get("Asistencias Directas", 0.0) + float(row.get('asistencias', 0) or 0)
        sumas["Tiros a Puerta"] = sumas.get("Tiros a Puerta", 0.0) + float(row.get('tiros', 0) or 0)
        sumas["Pases Clave"] = sumas.get("Pases Clave", 0.0) + float(row.get('pases_clave', 0) or 0)
        sumas["Duelos Ganados"] = sumas.get("Duelos Ganados", 0.0) + float(row.get('duelos_ganados', 0) or 0)
        sumas["Intercepciones"] = sumas.get("Intercepciones", 0.0) + float(row.get('intercepciones', 0) or 0)

    for k, total_val in sumas.items():
        if "%" in k:
            promedios[k] = round(total_val / tot_partidos, 1)
        else:
            promedios[k] = round((total_val / tot_min) * 90, 2)
            
    return promedios, tot_partidos, tot_min

# 4. LIGAS MUNDIALES E INTERNACIONALES
LIGAS_MUNDIALES = [
    "Champions League", 
    "Europa League", 
    "Conference League", 
    "Concacaf Champions Cup", 
    "Copa Centroamericana", 
    "Leagues Cup", 
    "Copa Libertadores", 
    "Copa Sudamericana",
    "Copa Doméstica / Otra Competencia (Escribir)",
    
    "Liga Portugal", "Liga MX", "Niké Liga (Eslovaquia)", "Liga de Expansión MX", "Liga MX U-21", "Liga MX U-19", "Liga MX U-17", "Liga MX U-15",
    "La Liga", "Liga Hypermotion", "Primera RFEF", "Segunda RFEF",
    "Premier League", "Championship", "League One", "League Two",
    "Ligue 1", "Ligue 2", "Serie A", "Serie B",
    "Bundesliga", "2. Bundesliga", "Allsvenskan", "Eliteserien",
    "Eredivisie", "Jupiler Pro League", "Superliga Dinamarca", "Ekstraklasa",
    "efbet League Bulgaria", "SuperSport HNL", "Chance Liga", "Superliga Serbia",
    "Bundesliga Austria", "Superliga de Suiza", "Liga 2 Portugal",
    "Liga Eslovenia",
    "Primera División Argentina", "Primera División Costa Rica", "Primera División Colombia", 
    "Brasileirao", "Brasileirao Série B", "Primera División Uruguay", "Primera División Chile", 
    "MLS", "MLS Next Pro", "USL", "J-League"
]

JORNADAS_OPCIONES = [f"Jornada {i}" for i in range(1, 39)] + [
    "Fase de Grupos", 
    "1ra Ronda Previa — Ida", "1ra Ronda Previa — Vuelta",
    "2da Ronda Previa — Ida", "2da Ronda Previa — Vuelta",
    "3ra Ronda Previa — Ida", "3ra Ronda Previa — Vuelta",
    "Playoffs Previa — Ida", "Playoffs Previa — Vuelta",
    "16vos de Final", "Octavos de Final", "Cuartos de Final", "Semifinal", "Final"
]

equipos_mx_2026 = [
    "CF América", "CF Atlante", "Atlas FC", "Club Atlético de San Luis", "Cruz Azul", 
    "CD Guadalajara (Chivas)", "FC Juárez", "Club León", "CF Monterrey", "Club Necaxa", 
    "CF Pachuca", "Club Puebla", "Pumas UNAM", "Querétaro FC", "Club Santos Laguna", 
    "Tigres UANL", "Club Tijuana", "Deportivo Toluca"
]

equipos_mls_2026 = [
    "Atlanta United FC", "Austin FC", "Charlotte FC", "Chicago Fire FC", "FC Cincinnati", "Colorado Rapids", "Columbus Crew", "D.C. United", "FC Dallas", "Houston Dynamo FC", "Inter Miami CF", "LA Galaxy", "LAFC", "Minnesota United FC", "CF Montréal", "Nashville SC", "New England Revolution", "New York City FC", "New York Red Bulls", "Orlando City SC", "Philadelphia Union", "Portland Timbers", "Real Salt Lake", "San Jose Earthquakes", "Seattle Sounders FC", "Sporting Kansas City", "St. Louis City SC", "Toronto FC", "Vancouver Whitecaps FC"
]

equipos_liga_portugal_2026_27 = [
    "Académico de Viseu", "Casa Pia AC", "CD Nacional", "CD Santa Clara", 
    "CF Estrela da Amadora", "CS Marítimo", "FC Alverca", "FC Arouca", 
    "FC Famalicão", "FC Porto", "GD Estoril Praia", "Gil Vicente FC", 
    "Moreirense FC", "Rio Ave FC", "SC Braga", "SL Benfica", 
    "Sporting CP", "Vitória SC"
]

EQUIPOS_POR_LIGA = {
    "Liga Portugal": equipos_liga_portugal_2026_27,
    "Liga MX": equipos_mx_2026,
    "MLS": equipos_mls_2026,
    "Leagues Cup": sorted(equipos_mx_2026 + equipos_mls_2026),
    "Liga de Expansión MX": ["Alebrijes de Oaxaca", "Atlante FC", "Atlético Morelia", "Cancún FC", "Celaya FC", "Correcaminos UAT", "Dorados de Sinaloa", "Leones Negros UdeG", "Mineros de Zacatecas", "Tepatitlán FC", "Tlaxcala FC", "Venados FC", "CD Tapatío"],
    "Liga MX U-21": [e + " U-21" for e in equipos_mx_2026],
    "Liga MX U-19": [e + " U-19" for e in equipos_mx_2026],
    "Liga MX U-17": [e + " U-17" for e in equipos_mx_2026],
    "Liga MX U-15": [e + " U-15" for e in equipos_mx_2026],
    "La Liga": ["Athletic Club", "Club Atlético de Madrid", "CA Osasuna", "CD Leganés", "Deportivo Alavés", "Elche CF", "FC Barcelona", "Getafe CF", "Girona FC", "Levante UD", "RCD Espanyol", "Rayo Vallecano", "Real Betis", "Real Celta Vigo", "Real Madrid", "Real Oviedo", "Real Sociedad", "Sevilla FC", "Valencia CF", "Villarreal CF"],
    "Premier League": ["Arsenal FC", "Aston Villa FC", "AFC Bournemouth", "Brentford FC", "Brighton & Hove Albion", "Chelsea FC", "Crystal Palace", "Everton FC", "Fulham FC", "Ipswich Town", "Leeds United", "Liverpool FC", "Manchester City", "Manchester United", "Newcastle United", "Nottingham Forest", "Sunderland AFC", "Tottenham Hotspur", "West Ham United", "Wolverhampton Wanderers"],
    "Allsvenskan": ["AIK", "BK Häcken", "Djurgårdens IF", "GAIS", "Halmstads BK", "Hammarby IF", "IF Brommapojkarna", "IF Elfsborg", "IFK Göteborg", "IFK Norrköping", "IK Sirius", "Kalmar FF", "Malmö FF", "Mjällby AIF", "Västerås SK"]
}

# 5. MOSTRAR PERFIL
def mostrar_perfil_jugador(jugador, tabla_origen, idx_origen):
    st.markdown("---")
    st.subheader(f"Perfil Analítico: {jugador['Nombre']}")
    
    pestanas_principales = st.tabs(["General & Contrato", "Rendimiento & Data", "Mercado & Viabilidad"] if tabla_origen == 'scouting_db' else ["General & Contrato", "Rendimiento & Data"])
    
    df_partidos = consultar_partidos_jugador(jugador['Nombre'])
    ejes_radar = obtener_ejes_radar(jugador['Posición'])
    
    # TAB 1: GENERAL & CONTRATO
    with pestanas_principales[0]:
        c_img, c_inf1, c_inf2 = st.columns([1, 2, 2])
        with c_img:
            foto_src = jugador.get('Foto') if jugador.get('Foto') else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
            st.markdown(f"""
                <div class="player-photo-card">
                    <img src="{foto_src}" class="player-photo-img" />
                </div>
            """, unsafe_allow_html=True)
            
        with c_inf1:
            st.markdown("##### Datos Personales y Deportivos")
            st.markdown(f"**Nombre:** {jugador['Nombre']}")
            st.markdown(f"**Edad:** {jugador['Edad']} años")
            st.markdown(f"**Posición Específica:** {jugador['Posición']}")
            nac_val = jugador.get('Nacionalidad') or 'N/D'
            st.markdown(f"**Nacionalidad:** {nac_val}")

        with c_inf2:
            st.markdown("##### Situación Contractual")
            st.markdown(f"**Club Actual:** {jugador['Club']}")
            st.markdown(f"**Liga / Competición:** {jugador.get('Liga', 'N/D')}")
            ag_val = jugador.get('Agencia') or 'N/D'
            st.markdown(f"**Agencia / Representante:** {ag_val}")
            if tabla_origen == 'equipo_ignition':
                st.markdown(f"**Estatus:** {jugador.get('Status', 'OBJETIVO')}")

    # TAB 2: RENDIMIENTO & DATA
    with pestanas_principales[1]:
        st.markdown("### Centro de Análisis Estadístico")
        sub_vistas = st.tabs(["Compendio General (p/90)", "Promedio por Torneo", "Ficha de Partido Único"])
        
        with sub_vistas[0]:
            promedios_gen, tot_p, tot_m = calcular_promedios_df(df_partidos)
            c_rad, c_mat = st.columns([1.2, 2.8])
            
            val_radar = [70, 75, 65, 80, 72]
            if tot_m > 0:
                g_p = promedios_gen.get("Goles Totales", 0.0)
                a_p = promedios_gen.get("Asistencias Directas", 0.0)
                t_p = promedios_gen.get("Tiros a Puerta", 0.0)
                p_p = promedios_gen.get("Pases Clave", 0.0)
                d_p = promedios_gen.get("Duelos Ganados", 0.0)
                i_p = promedios_gen.get("Intercepciones", 0.0)
                
                val_radar = [
                    min(100, int(g_p * 30 + t_p * 15 + 35)),
                    min(100, int(a_p * 35 + p_p * 15 + 35)),
                    min(100, int(i_p * 20 + d_p * 5 + 40)),
                    min(100, int(d_p * 8 + 40)),
                    min(100, int(p_p * 15 + 45))
                ]
                
            with c_rad:
                st.caption(f"Acumulado Real: **{tot_p} partidos registrados** | **{tot_m} min**")
                angulos = [n / 5 * 2 * math.pi for n in range(5)]; angulos += angulos[:1]
                valores_plot = val_radar + val_radar[:1]
                fig, ax = plt.subplots(figsize=(2.2, 2.2), subplot_kw=dict(polar=True))
                plt.xticks(angulos[:-1], ejes_radar, color='#1A2B4C', size=7, weight='bold')
                ax.plot(angulos, valores_plot, color='#1A2B4C', linewidth=2)
                ax.fill(angulos, valores_plot, color='#C8A165', alpha=0.45)
                fig.patch.set_facecolor('none'); ax.set_facecolor('none'); ax.set_yticklabels([])
                st.pyplot(fig, use_container_width=True)
                
            with c_mat:
                st.markdown(f"#### Matriz Quirúrgica p/90 (Basada en {tot_p} partidos cargados)")
                metricas_q = obtener_30_metricas(jugador['Posición'])
                m_tabs = st.tabs(list(metricas_q.keys()))
                for i, (pilar, lista_m) in enumerate(metricas_q.items()):
                    with m_tabs[i]:
                        cols = st.columns(4)
                        for j, metrica in enumerate(lista_m):
                            val_calculado = promedios_gen.get(metrica, 0.0)
                            unit = "%" if "%" in metrica else "p/90"
                            cols[j % 4].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165; font-weight:bold;'>{val_calculado} {unit}</span></div>", unsafe_allow_html=True)

        with sub_vistas[1]:
            if not df_partidos.empty and 'liga' in df_partidos.columns:
                torneos_disponibles = df_partidos['liga'].unique().tolist()
                torneo_sel = st.selectbox("Seleccionar Torneo para Evaluar:", torneos_disponibles, key=f"torneo_sel_{jugador['ID']}")
                
                df_torneo = df_partidos[df_partidos['liga'] == torneo_sel]
                promedios_torneo, part_torneo, min_torneo = calcular_promedios_df(df_torneo)
                
                st.info(f"Rendimiento en **{torneo_sel}**: **{part_torneo} partidos registrados** | **{min_torneo} minutos**")
                
                c_rad_t, c_mat_t = st.columns([1.2, 2.8])
                with c_rad_t:
                    val_t = [65, 70, 60, 75, 68]
                    if min_torneo > 0:
                        val_t = [
                            min(100, int(promedios_torneo.get("Goles Totales", 0.0) * 30 + 35)),
                            min(100, int(promedios_torneo.get("Asistencias Directas", 0.0) * 35 + 35)),
                            min(100, int(promedios_torneo.get("Intercepciones", 0.0) * 20 + 40)),
                            min(100, int(promedios_torneo.get("Duelos Ganados", 0.0) * 8 + 40)),
                            min(100, int(promedios_torneo.get("Pases Clave", 0.0) * 15 + 45))
                        ]
                    angulos = [n / 5 * 2 * math.pi for n in range(5)]; angulos += angulos[:1]
                    valores_plot_t = val_t + val_t[:1]
                    fig, ax = plt.subplots(figsize=(2.2, 2.2), subplot_kw=dict(polar=True))
                    plt.xticks(angulos[:-1], ejes_radar, color='#1A2B4C', size=7, weight='bold')
                    ax.plot(angulos, valores_plot_t, color='#1A2B4C', linewidth=2)
                    ax.fill(angulos, valores_plot_t, color='#C8A165', alpha=0.45)
                    fig.patch.set_facecolor('none'); ax.set_facecolor('none'); ax.set_yticklabels([])
                    st.pyplot(fig, use_container_width=True)
                    
                with c_mat_t:
                    st.markdown(f"#### Promedios p/90 en {torneo_sel}")
                    metricas_q = obtener_30_metricas(jugador['Posición'])
                    m_tabs_t = st.tabs(list(metricas_q.keys()))
                    for i, (pilar, lista_m) in enumerate(metricas_q.items()):
                        with m_tabs_t[i]:
                            cols = st.columns(4)
                            for j, metrica in enumerate(lista_m):
                                val_calc_t = promedios_torneo.get(metrica, 0.0)
                                unit_t = "%" if "%" in metrica else "p/90"
                                cols[j % 4].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165; font-weight:bold;'>{val_calc_t} {unit_t}</span></div>", unsafe_allow_html=True)
            else:
                st.info("No hay partidos registrados para filtrar por competición. Registra partidos en 'Ingreso de Data'.")

        with sub_vistas[2]:
            if not df_partidos.empty and 'jornada' in df_partidos.columns:
                c_f1, c_f2 = st.columns(2)
                torneo_f = c_f1.selectbox("Filtrar Torneo:", df_partidos['liga'].unique().tolist(), key=f"tf_{jugador['ID']}")
                
                df_partidos_torneo = df_partidos[df_partidos['liga'] == torneo_f]
                partidos_lista = [f"{row['jornada']} vs. {row['equipo']}" for _, row in df_partidos_torneo.iterrows()]
                
                partido_sel = c_f2.selectbox("Seleccionar Juego Específico:", partidos_lista, key=f"ps_{jugador['ID']}")
                
                idx_p = partidos_lista.index(partido_sel)
                p_data = df_partidos_torneo.iloc[idx_p]
                
                st.success(f"Ficha Táctica: **{p_data['jornada']}** | Rival: **{p_data['equipo']}** | Torneo: **{p_data['liga']}**")
                
                m_custom = p_data.get('m_data') if (isinstance(p_data.get('m_data'), dict)) else {}

                st.markdown("#### Matriz de Acciones Reales del Partido (Conteos Absolutos)")
                metricas_q = obtener_30_metricas(jugador['Posición'])
                m_tabs_p = st.tabs(list(metricas_q.keys()))
                for i, (pilar, lista_m) in enumerate(metricas_q.items()):
                    with m_tabs_p[i]:
                        cols = st.columns(4)
                        for j, metrica in enumerate(lista_m):
                            val_str = "0"
                            if metrica in m_custom:
                                val_str = str(m_custom[metrica])
                            elif "Goles" in metrica: val_str = f"{p_data.get('goles', 0)}"
                            elif "Asistencias" in metrica: val_str = f"{p_data.get('asistencias', 0)}"
                            elif "Tiros" in metrica: val_str = f"{p_data.get('tiros', 0)}"
                            elif "Pases" in metrica: val_str = f"{p_data.get('pases_clave', 0)}"
                            elif "Duelos" in metrica: val_str = f"{p_data.get('duelos_ganados', 0)}"
                            elif "Intercepciones" in metrica: val_str = f"{p_data.get('intercepciones', 0)}"
                            elif "Minutos" in metrica: val_str = f"{p_data.get('minutos', 0)}'"
                            else: val_str = "0"
                            cols[j % 4].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#1A2B4C; font-weight:bold;'>{val_str}</span></div>", unsafe_allow_html=True)
            else:
                st.info("No hay fichas de partidos individuales cargadas para este jugador.")

    # TAB 3: MERCADO & VIABILIDAD
    if tabla_origen == 'scouting_db':
        with pestanas_principales[2]:
            st.markdown("### Ficha Financiera y Viabilidad de Fichaje")
            cm1, cm2, cm3 = st.columns(3)
            
            val_m = jugador.get('Valor', 'N/D')
            via_m = str(jugador.get('Viabilidad', 'Media'))
            
            if "Alta" in via_m: via_m_clean = "Alta"
            elif "Baja" in via_m: via_m_clean = "Baja"
            else: via_m_clean = "Media"
            
            nac_str = str(jugador.get('Nacionalidad') or '')
            es_nacional = "Mexicana" in nac_str or "Mexicano" in nac_str or "🇲🇽" in nac_str
            
            cm1.metric("Valoración Estimada de Mercado", val_m)
            cm2.metric("Semáforo de Viabilidad", via_m_clean)
            cm3.metric("Cupo NMM / Extranjero", "Nacional" if es_nacional else "Aplica Extranjero")

    # MÓDULO DE EDICIÓN
    with st.expander(f"Editar Perfil de {jugador['Nombre']}"):
        c_ed1, c_ed2 = st.columns(2)
        nuevo_nom = c_ed1.text_input("Nombre", value=jugador['Nombre'], key=f"nm_{jugador['ID']}")
        nueva_edad = c_ed1.number_input("Edad", 15, 45, value=jugador['Edad'], key=f"ed_{jugador['ID']}")
        
        pos_idx = LISTA_POSICIONES.index(jugador['Posición']) if jugador['Posición'] in LISTA_POSICIONES else 0
        nueva_pos = c_ed1.selectbox("Posición Específica", LISTA_POSICIONES, index=pos_idx, key=f"pos_{jugador['ID']}")
        
        nueva_nac = c_ed1.text_input("Nacionalidad", value=jugador.get('Nacionalidad', ''), key=f"nac_{jugador['ID']}")
        nueva_agencia = c_ed2.text_input("Agencia", value=jugador.get('Agencia', ''), key=f"ag_{jugador['ID']}")
        
        if tabla_origen == 'scouting_db':
            nuevo_val = c_ed2.text_input("Valor de Mercado", value=jugador.get('Valor', ''), key=f"val_{jugador['ID']}")
            v_raw = str(jugador.get('Viabilidad', 'Media'))
            v_idx = 0 if "Alta" in v_raw else (2 if "Baja" in v_raw else 1)
            nueva_viab = c_ed2.selectbox("Viabilidad", ["Alta", "Media", "Baja"], index=v_idx, key=f"via_{jugador['ID']}")
        else:
            status_opciones = ["FIRMADO", "OBJETIVO", "SEGUIMIENTO INTENSIVO"]
            st_raw = str(jugador.get('Status', 'OBJETIVO'))
            st_idx = status_opciones.index(st_raw) if st_raw in status_opciones else 0
            nuevo_status = c_ed2.selectbox("Estatus", status_opciones, index=st_idx, key=f"st_{jugador['ID']}")

        nueva_liga_sel = c_ed2.selectbox("Liga / Competición Base", LIGAS_MUNDIALES, index=LIGAS_MUNDIALES.index(jugador.get('Liga', LIGAS_MUNDIALES[0])) if jugador.get('Liga') in LIGAS_MUNDIALES else 0, key=f"lg_edit_{jugador['ID']}")
        if "Copa Doméstica" in nueva_liga_sel:
            nueva_liga = c_ed2.text_input("Nombre de la Copa (ej. Copa del Rey, Slovnaft Cup)", value=jugador.get('Liga', ''), key=f"lg_copa_txt_edit_{jugador['ID']}")
        else:
            nueva_liga = nueva_liga_sel

        if nueva_liga in EQUIPOS_POR_LIGA:
            nuevo_club = c_ed2.selectbox("Club", EQUIPOS_POR_LIGA[nueva_liga], key=f"cl_edit_{jugador['ID']}")
        else:
            nuevo_club = c_ed2.text_input("Club (Escribir nombre)", value=jugador['Club'], key=f"cl_txt_edit_{jugador['ID']}")
            
        nueva_foto = st.file_uploader("Subir Foto de Perfil (PNG, JPG)", type=['jpg', 'png', 'jpeg'], key=f"ft_{jugador['ID']}")
        
        col_btn1, col_btn2 = st.columns([1, 1])
        if col_btn1.button("Guardar Cambios en Supabase", key=f"sv_{jugador['ID']}"):
            foto_base64 = procesar_foto(nueva_foto) if nueva_foto else jugador.get('Foto')
            
            payload = {
                "nombre": nuevo_nom, 
                "edad": nueva_edad, 
                "posicion": nueva_pos,
                "liga": nueva_liga, 
                "club": nuevo_club, 
                "foto": foto_base64
            }
            if nueva_nac: payload["nacionalidad"] = nueva_nac
            if nueva_agencia: payload["agencia"] = nueva_agencia

            if tabla_origen == 'scouting_db':
                payload["valor"] = nuevo_val
                payload["viabilidad"] = nueva_viab
            else:
                payload["status"] = nuevo_status

            if supabase and jugador.get('ID'):
                try:
                    supabase.table(tabla_origen).update(payload).eq('id', jugador['ID']).execute()
                    st.success("Guardado en Supabase exitoso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error en Supabase: {e}")
            
        if col_btn2.button("Eliminar Perfil", key=f"dl_{jugador['ID']}"):
            if supabase and jugador.get('ID'):
                try: 
                    supabase.table(tabla_origen).delete().eq('id', jugador['ID']).execute()
                    st.success("Jugador eliminado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")

# 6. ESTÉTICA
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
    
    .login-container { max-width: 440px; margin: 40px auto; padding: 30px; background: #FFFFFF; border-radius: 12px; box-shadow: 0 10px 30px rgba(26, 43, 76, 0.12); border-top: 5px solid #C8A165; text-align: center; }
    .metric-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #1A2B4C; padding: 12px; border-radius: 6px; margin-bottom: 10px; color: #1A2B4C; font-size: 13px; }
    .stButton>button { background-color: #C8A165 !important; color: #1A2B4C !important; font-weight: bold !important; border: none !important; border-radius: 6px !important; width: 100% !important; }
    .stButton>button:hover { background-color: #1A2B4C !important; color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

# 7. SESIÓN Y NAVEGACIÓN (LOGIN REFORMADO)
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        
        # 📸 BÚSQUEDA EXCLUSIVA DE IMAGEN DE PORTADA / HERO PARA LOGIN
        if os.path.exists("login_hero.png"):
            st.image("login_hero.png", use_container_width=True)
        elif os.path.exists("login_hero.jpg"):
            st.image("login_hero.jpg", use_container_width=True)
        elif os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        elif os.path.exists("logo.jpg"):
            st.image("logo.jpg", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align:center; color:#1A2B4C; font-size:36px; margin:0;'>IGNITION</h1>", unsafe_allow_html=True)
        
        st.markdown("""
            <h2 style='color:#1A2B4C; margin-top:15px; margin-bottom:0; font-size:22px; text-align:center;'>SCOUTING PRO</h2>
            <p style='color:#C8A165; font-size:12px; font-weight:bold; letter-spacing:1px; margin-top:4px; text-align:center;'>SCOUTING INTERNACIONAL Y DIRECCIÓN DEPORTIVA</p>
            <hr style='border-color:#E2E8F0; margin: 20px 0;'>
        """, unsafe_allow_html=True)
        
        usuario = st.text_input("Usuario Corporativo", key="login_usr_txt")
        password = st.text_input("Contraseña", type="password", key="login_pwd_txt")
        st.write("")
        if st.button("INGRESAR AL SISTEMA", key="login_btn_submit"):
            if usuario.lower() == "christian" and password == "1234":
                st.session_state['logged_in'] = True
                st.rerun()
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
        
        with st.expander("Crear Nuevo Jugador a Scoutear"):
            c_a, c_b = st.columns(2)
            reg_nom = c_a.text_input("Nombre Completo", key="reg_nom_input")
            reg_edad = c_a.number_input("Edad", 15, 45, 20, key="reg_edad_input")
            reg_pos = c_a.selectbox("Posición Específica", LISTA_POSICIONES, key="reg_pos_input")
            reg_nac = c_a.text_input("Nacionalidad", key="reg_nac_input")
            
            reg_val = c_b.text_input("Valor de Mercado (ej. €1.2M)", key="reg_val_input")
            reg_ag = c_b.text_input("Agencia de Representación", key="reg_ag_input")
            reg_viab = c_b.selectbox("Viabilidad de Fichaje", ["Alta", "Media", "Baja"], key="reg_viab_input")
            
            reg_liga_sel = c_b.selectbox("Liga / Competición Base", LIGAS_MUNDIALES, key="reg_liga_dyn")
            if "Copa Doméstica" in reg_liga_sel:
                reg_liga = c_b.text_input("Nombre de la Copa (Escribir)", key="reg_liga_copa_txt")
            else:
                reg_liga = reg_liga_sel

            if reg_liga in EQUIPOS_POR_LIGA:
                reg_club = c_b.selectbox("Club", EQUIPOS_POR_LIGA[reg_liga], key="reg_club_dyn")
            else:
                reg_club = c_b.text_input("Club (Escribir nombre)", key="reg_club_txt_dyn")
                
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
                        st.error(f"Error en Supabase: {e}")

        if len(st.session_state['scouting_db']) > 0:
            df_scouting = pd.DataFrame(st.session_state['scouting_db'])
            seleccion = st.dataframe(df_scouting[["Nombre", "Edad", "Club", "Liga", "Posición", "Viabilidad"]], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
            
            if len(seleccion.selection.rows) > 0:
                mostrar_perfil_jugador(st.session_state['scouting_db'][seleccion.selection.rows[0]], 'scouting_db', seleccion.selection.rows[0])

    elif opcion == "Equipo Ignition":
        st.title("Equipo Ignition")
        
        with st.expander("Añadir Jugador a Equipo Ignition"):
            c_a, c_b = st.columns(2)
            eq_nom = c_a.text_input("Nombre Completo", key="eq_nom_input")
            eq_edad = c_a.number_input("Edad", 15, 45, 20, key="eq_edad_input")
            eq_pos = c_a.selectbox("Posición Específica", LISTA_POSICIONES, key="eq_pos_input")
            eq_status = c_a.selectbox("Estatus", ["FIRMADO", "OBJETIVO", "SEGUIMIENTO INTENSIVO"], key="eq_status_input")
            eq_nac = c_a.text_input("Nacionalidad", key="eq_nac_input")
            eq_ag = c_b.text_input("Agencia de Representación", key="eq_ag_input")
            
            eq_liga_sel = c_b.selectbox("Liga / Competición Base", LIGAS_MUNDIALES, key="eq_liga_dyn")
            if "Copa Doméstica" in eq_liga_sel:
                eq_liga = c_b.text_input("Nombre de la Copa (Escribir)", key="eq_liga_copa_txt")
            else:
                eq_liga = eq_liga_sel

            if eq_liga in EQUIPOS_POR_LIGA:
                eq_club = c_b.selectbox("Club", EQUIPOS_POR_LIGA[eq_liga], key="eq_club_dyn")
            else:
                eq_club = c_b.text_input("Club (Escribir nombre)", key="eq_club_txt_dyn")
                
            eq_foto = st.file_uploader("Foto de Perfil (Opcional)", type=['jpg', 'png', 'jpeg'], key="eq_foto_dyn")
            
            if st.button("Guardar en Equipo Ignition", key="btn_reg_equipo"):
                if eq_nom and supabase:
                    f_b64 = procesar_foto(eq_foto)
                    payload = {
                        "nombre": eq_nom, "edad": eq_edad, "posicion": eq_pos,
                        "liga": eq_liga, "club": eq_club, "foto": f_b64, "status": eq_status
                    }
                    if eq_nac: payload["nacionalidad"] = eq_nac
                    if eq_ag: payload["agencia"] = eq_ag

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
        st.title("Registro Manual de Estadísticas de Partido")
        
        tab_captura, tab_edicion = st.tabs(["➕ Capturar Nuevo Partido", "✏️ Editar / Corregir / Borrar Partido Cargado"])
        
        todos_jugadores = []
        if 'scouting_db' in st.session_state:
            todos_jugadores += [j['Nombre'] for j in st.session_state['scouting_db']]
        if 'equipo_ignition' in st.session_state:
            todos_jugadores += [j['Nombre'] for j in st.session_state['equipo_ignition']]
        todos_jugadores = list(set(todos_jugadores))
        
        # PESTAÑA A: CAPTURAR NUEVO PARTIDO
        with tab_captura:
            c1, c2 = st.columns(2)
            if todos_jugadores:
                n_jugador = c1.selectbox("Seleccionar Jugador Registrado", todos_jugadores, key="p_nom_select")
            else:
                n_jugador = c1.text_input("Nombre del Jugador", key="p_nom_input")
                
            n_posicion = c1.selectbox("Posición Específica (Define el Formulario)", LISTA_POSICIONES, key="p_pos_dyn_input")
            
            n_liga_sel = c2.selectbox("Competición / Torneo", LIGAS_MUNDIALES, key="p_liga_dyn")
            if "Copa Doméstica" in n_liga_sel:
                n_liga = c2.text_input("Escribir Nombre de la Copa / Torneo", key="p_liga_copa_txt")
            else:
                n_liga = n_liga_sel

            if n_liga in EQUIPOS_POR_LIGA:
                n_equipo = c2.selectbox("Equipo Rival", EQUIPOS_POR_LIGA[n_liga], key="p_club_dyn")
            else:
                n_equipo = c2.text_input("Equipo Rival (Escribir nombre)", key="p_club_txt_dyn")
                
            n_jornada = c1.selectbox("Jornada / Fase del Juego", JORNADAS_OPCIONES, key="p_jornada_input")
            v_minutos = c2.number_input("Minutos Jugados en el Partido", 0, 120, 90, key="p_min_input")

            st.markdown(f"#### Captura de Métricas para: **{n_posicion}**")
            metricas_pos = obtener_30_metricas(n_posicion)
            
            valores_capturados = {}
            with st.form("form_stats_dinamico"):
                tabs_p = st.tabs(list(metricas_pos.keys()))
                for i, (pilar, lista_m) in enumerate(metricas_pos.items()):
                    with tabs_p[i]:
                        cols = st.columns(4)
                        for j, metrica in enumerate(lista_m):
                            if "xG Evitados" in metrica or "Diferencia" in metrica:
                                val = cols[j % 4].number_input(metrica, -50.0, 50.0, 0.0, step=0.01, key=f"m_{n_posicion}_{i}_{j}")
                            elif "%" in metrica or "xG" in metrica or "xA" in metrica or "km" in metrica or "Distancia" in metrica or "Velocidad" in metrica:
                                val = cols[j % 4].number_input(metrica, 0.0, 100.0, 0.0, step=0.1, key=f"m_{n_posicion}_{i}_{j}")
                            else:
                                val = cols[j % 4].number_input(metrica, 0, 200, 0, step=1, key=f"m_{n_posicion}_{i}_{j}")
                            valores_capturados[metrica] = val
                
                if st.form_submit_button("Guardar Partido en Supabase"):
                    if n_jugador and supabase:
                        goles_cap = int(valores_capturados.get("Goles Totales", valores_capturados.get("Goles Anotados", 0)))
                        asis_cap = int(valores_capturados.get("Asistencias Directas", valores_capturados.get("Asistencias Totales", 0)))
                        tiros_cap = int(valores_capturados.get("Tiros a Puerta", valores_capturados.get("Tiros Totales", 0)))
                        pases_cap = int(valores_capturados.get("Pases Clave", 0))
                        duelos_cap = int(valores_capturados.get("Duelos Ganados", valores_capturados.get("1v1 Ganados %", 0)))
                        inter_cap = int(valores_capturados.get("Intercepciones", 0))
                        
                        stats_partido = {
                            "jugador": n_jugador,
                            "posicion": n_posicion,
                            "liga": n_liga,
                            "equipo": n_equipo,
                            "jornada": n_jornada,
                            "minutos": v_minutos,
                            "goles": goles_cap,
                            "asistencias": asis_cap,
                            "tiros": tiros_cap,
                            "pases_clave": pases_cap,
                            "duelos_ganados": duelos_cap,
                            "intercepciones": inter_cap,
                            "m_data": valores_capturados
                        }
                        try:
                            supabase.table('partidos_stats').insert(stats_partido).execute()
                            st.cache_data.clear()
                            st.success(f"Estadísticas guardadas al instante para {n_jugador}.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al escribir en Supabase: {e}")

        # PESTAÑA B: EDITAR / CORREGIR / BORRAR PARTIDO CARGADO
        with tab_edicion:
            st.markdown("#### Corrección de Metadatos y Métricas de Partido Cargado")
            
            if todos_jugadores:
                j_ed_sel = st.selectbox("Seleccionar Jugador para Administrar Partidos:", todos_jugadores, key="j_ed_sel_k")
                df_p_ed = consultar_partidos_jugador(j_ed_sel)
                
                if not df_p_ed.empty:
                    partidos_lista_ed = [f"ID #{row['id']} - {row['jornada']} vs. {row['equipo']} ({row['liga']})" for _, row in df_p_ed.iterrows()]
                    partido_ed_sel = st.selectbox("Seleccionar Partido a Editar o Eliminar:", partidos_lista_ed, key="p_ed_sel_k")
                    
                    idx_p_ed = partidos_lista_ed.index(partido_ed_sel)
                    p_curr = df_p_ed.iloc[idx_p_ed]
                    m_curr_custom = p_curr.get('m_data') if isinstance(p_curr.get('m_data'), dict) else {}
                    
                    st.info(f"Editando Registro ID **#{p_curr['id']}** de **{j_ed_sel}**")
                    
                    pos_ed = p_curr['posicion']
                    metricas_pos_ed = obtener_30_metricas(pos_ed)
                    valores_corregidos = {}
                    
                    j_curr_val = p_curr.get('jornada', JORNADAS_OPCIONES[0])
                    j_idx = JORNADAS_OPCIONES.index(j_curr_val) if j_curr_val in JORNADAS_OPCIONES else 0
                    
                    l_curr_val = p_curr.get('liga', LIGAS_MUNDIALES[0])
                    l_idx = LIGAS_MUNDIALES.index(l_curr_val) if l_curr_val in LIGAS_MUNDIALES else 0
                    
                    with st.form("form_corregir_partido_completo"):
                        st.markdown("##### 1. Corrección de Contexto (Jornada, Torneo y Rival)")
                        med_c1, med_c2 = st.columns(2)
                        
                        ed_jornada = med_c1.selectbox("Jornada / Fase", JORNADAS_OPCIONES, index=j_idx, key="ed_jornada_k")
                        ed_liga_sel = med_c2.selectbox("Competición / Torneo Base", LIGAS_MUNDIALES, index=l_idx, key="ed_liga_k")
                        
                        if "Copa Doméstica" in ed_liga_sel:
                            ed_liga = med_c2.text_input("Escribir Nombre de la Copa / Torneo", value=p_curr.get('liga', ''), key="ed_liga_copa_txt")
                        else:
                            ed_liga = ed_liga_sel

                        if ed_liga in EQUIPOS_POR_LIGA:
                            eq_opciones = EQUIPOS_POR_LIGA[ed_liga]
                            e_curr_val = p_curr.get('equipo', eq_opciones[0])
                            e_idx = eq_opciones.index(e_curr_val) if e_curr_val in eq_opciones else 0
                            ed_equipo = med_c1.selectbox("Equipo Rival", eq_opciones, index=e_idx, key="ed_equipo_k")
                        else:
                            ed_equipo = med_c1.text_input("Equipo Rival (Escribir nombre)", value=p_curr.get('equipo', ''), key="ed_equipo_txt_k")
                            
                        ed_minutos = med_c2.number_input("Minutos Jugados", 0, 120, int(p_curr.get('minutos', 90)), key="min_ed_val")
                        
                        st.markdown("##### 2. Corrección de Métricas Tácticas")
                        tabs_ed = st.tabs(list(metricas_pos_ed.keys()))
                        for i, (pilar, lista_m) in enumerate(metricas_pos_ed.items()):
                            with tabs_ed[i]:
                                cols = st.columns(4)
                                for j, metrica in enumerate(lista_m):
                                    val_prev = m_curr_custom.get(metrica, 0.0 if ("%" in metrica or "xG" in metrica) else 0)
                                    if "xG Evitados" in metrica or "Diferencia" in metrica:
                                        val_c = cols[j % 4].number_input(metrica, -50.0, 50.0, float(val_prev), step=0.01, key=f"med_{pos_ed}_{i}_{j}")
                                    elif "%" in metrica or "xG" in metrica or "xA" in metrica or "km" in metrica or "Distancia" in metrica or "Velocidad" in metrica:
                                        val_c = cols[j % 4].number_input(metrica, 0.0, 100.0, float(val_prev), step=0.1, key=f"med_{pos_ed}_{i}_{j}")
                                    else:
                                        val_c = cols[j % 4].number_input(metrica, 0, 200, int(val_prev), step=1, key=f"med_{pos_ed}_{i}_{j}")
                                    valores_corregidos[metrica] = val_c
                                    
                        col_ed_b1, col_ed_b2 = st.columns(2)
                        btn_guardar = col_ed_b1.form_submit_button("💾 Guardar Corrección Completa")
                        btn_borrar = col_ed_b2.form_submit_button("🗑️ ELIMINAR ESTE PARTIDO")
                        
                        if btn_guardar:
                            if supabase and p_curr.get('id'):
                                g_c = int(valores_corregidos.get("Goles Totales", valores_corregidos.get("Goles Anotados", 0)))
                                a_c = int(valores_corregidos.get("Asistencias Directas", valores_corregidos.get("Asistencias Totales", 0)))
                                t_c = int(valores_corregidos.get("Tiros a Puerta", valores_corregidos.get("Tiros Totales", 0)))
                                p_c = int(valores_corregidos.get("Pases Clave", 0))
                                d_c = int(valores_corregidos.get("Duelos Ganados", valores_corregidos.get("1v1 Ganados %", 0)))
                                i_c = int(valores_corregidos.get("Intercepciones", 0))
                                
                                payload_update = {
                                    "jornada": ed_jornada,
                                    "liga": ed_liga,
                                    "equipo": ed_equipo,
                                    "minutos": ed_minutos,
                                    "goles": g_c,
                                    "asistencias": a_c,
                                    "tiros": t_c,
                                    "pases_clave": p_c,
                                    "duelos_ganados": d_c,
                                    "intercepciones": i_c,
                                    "m_data": valores_corregidos
                                }
                                try:
                                    supabase.table('partidos_stats').update(payload_update).eq('id', p_curr['id']).execute()
                                    st.cache_data.clear()
                                    st.success(f"Partido #{p_curr['id']} actualizado correctamente.")
                                    st.rerun()
                                except Exception as e_up:
                                    st.error(f"Error al actualizar: {e_up}")

                        if btn_borrar:
                            if supabase and p_curr.get('id'):
                                try:
                                    supabase.table('partidos_stats').delete().eq('id', p_curr['id']).execute()
                                    st.cache_data.clear()
                                    st.success(f"Partido #{p_curr['id']} eliminado permanentemente de Supabase.")
                                    st.rerun()
                                except Exception as e_del:
                                    st.error(f"Error al eliminar: {e_del}")
                                    
                else:
                    st.info("Este jugador no tiene partidos cargados para corregir o borrar.")

    else:
        st.info(f"Módulo '{opcion}' listo para sincronización.")
