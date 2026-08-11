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

# 3. POSICIONES Y MÉTRICAS
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
            "Pilar 4: Físico y Contexto (7)": ["Minutos Jugados", "Errores Críticos que terminan en Gol", "Tarjetas Amarillas", "Tarjetas Rojas", "Lesiones", "Distancia Recorrida (km)", "Goles Concedidos"]
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
            "Pilar 4: Presión y Físico (7)": ["Presión Alta Exitosa", "Recuperaciones en Campo Rival", "Minutos Jugados", "Sprints", "Distancia Recorrida (km)", "Velocidad Máxima", "Tarjetas Amarillas"]
        }
    elif posicion == "Extremo":
        return {
            "Pilar 1: Desequilibrio y Regate (8)": ["Regates Exitosos %", "Duelos Ofensivos Ganados", "Desbordes por Banda", "Faltas Recibidas en Ataque", "Aceleraciones", "Conducciones al Área", "Pérdidas de Balón", "Fueras de Lugar"],
            "Pilar 2: Creación y Centros (7)": ["Centros Precisos %", "Pases Clave", "Asistencias Esperadas (xA)", "Asistencias Directas", "Pases al Área Rival", "Toques Totales", "Pases Progresivos Recibidos"],
            "Pilar 3: Finalización (8)": ["Goles Esperados (xG)", "Tiros Totales", "Tiros a Puerta", "Goles Totales", "Toques en Área Rival", "Tiros al Palo", "Conversión de Gol %", "Duelos Aéreos Ganados"],
            "Pilar 4: Físico y Trabajo (7)": ["Presión en Tercio Rival", "Recuperaciones Altas", "Intercepciones", "Minutos Jugados", "Sprints", "Velocidad Máxima (km/h)", "Distancia Recorrida"]
        }
    else: # Delantero Centro
        return {
            "Pilar 1: Finalización Eficaz (8)": ["Goles Totales", "Goles Esperados (xG)", "Tiros a Puerta %", "Tiros Totales", "Conversión de Gol %", "Penales Anotados", "Tiros al Palo", "Fueras de Lugar"],
            "Pilar 2: Presencia en Área (7)": ["Toques en Área Rival", "Duelos Aéreos Ganados %", "Goles de Cabeza", "Faltas Recibidas en Área", "Pases Recibidos en Área", "Anticipaciones Ofensivas", "Rebotes Ganados"],
            "Pilar 3: Asociación y Apoyos (8)": ["Asistencias Directas", "Asistencias Esperadas (xA)", "Pases Clave", "Regates Exitosos", "Duelos Ofensivos Ganados", "Pases Precisos %", "Pérdidas de Balón", "Faltas Cometidas en Ataque"],
            "Pilar 4: Físico y Presión (7)": ["Minutos Jugados", "Presión Exitosa Alta", "Recuperaciones en Campo Rival", "Sprints", "Distancia Recorrida (km)", "Velocidad Máxima", "Tarjetas Amarillas"]
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

def consultar_partidos_jugador(nombre_jugador):
    if supabase and nombre_jugador:
        try:
            res = supabase.table('partidos_stats').select("*").eq('jugador', nombre_jugador).execute()
            if res.data:
                return pd.DataFrame(res.data)
        except Exception:
            pass
    return pd.DataFrame()

# 4. TODAS LAS LIGAS MUNDIALES MAPPED (46 COMPETICIONES)
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

equipos_mx_2026 = [
    "CF América", "CF Atlante", "Atlas FC", "Club Atlético de San Luis", "Cruz Azul", 
    "CD Guadalajara (Chivas)", "FC Juárez", "Club León", "CF Monterrey", "Club Necaxa", 
    "CF Pachuca", "Club Puebla", "Pumas UNAM", "Querétaro FC", "Club Santos Laguna", 
    "Tigres UANL", "Club Tijuana", "Deportivo Toluca"
]

EQUIPOS_POR_LIGA = {
    # MÉXICO
    "🇲🇽 Liga MX": equipos_mx_2026,
    "🇲🇽 Liga de Expansión": ["Alebrijes de Oaxaca", "Atlante FC", "Atlético Morelia", "Cancún FC", "Celaya FC", "Correcaminos UAT", "Dorados de Sinaloa", "Leones Negros UdeG", "Mineros de Zacatecas", "Tepatitlán FC", "Tepatitlán", "Tepatitlan FC", "Tepatitlán", "Tepatitlán FC", "Tlaxcala FC", "Venados FC FC", "CD Tapatío"],
    "🇲🇽 Liga MX U-21": [e + " U-21" for e in equipos_mx_2026],
    "🇲🇽 Liga MX U-19": [e + " U-19" for e in equipos_mx_2026],
    "🇲🇽 Liga MX U-17": [e + " U-17" for e in equipos_mx_2026],
    "🇲🇽 Liga MX U-15": [e + " U-15" for e in equipos_mx_2026],
    
    # ESPAÑA
    "🇪🇸 La Liga": ["Athletic Club", "Club Atlético de Madrid", "CA Osasuna", "CD Leganés", "Deportivo Alavés", "Elche CF", "FC Barcelona", "Getafe CF", "Girona FC", "Levante UD", "RCD Espanyol", "Rayo Vallecano", "Real Betis", "Real Celta Vigo", "Real Madrid", "Real Oviedo", "Real Sociedad", "Sevilla FC", "Valencia CF", "Villarreal CF"],
    "🇪🇸 Liga Hypermotion": ["Albacete Balompié", "Burgos CF", "Cádiz CF", "CD Castellón", "CD Eldense", "CD Mirandés", "CD Tenerife", "Córdoba CF", "Deportivo de La Coruña", "FC Cartagena", "Granada CF", "Málaga CF", "Racing de Ferrol", "Racing de Santander", "Real Zaragoza", "SD Eibar", "SD Huesca", "Sporting de Gijón", "UD Almería", "UD Las Palmas"],
    "🇪🇸 Primera RFEF": ["Andorra CF", "Arenteiro", "Barakaldo", "Bilbao Athletic", "Celta Fortuna", "Cultural Leonesa", "Gimnàstic de Tarragona", "IBiza", "Lugo", "Mérida", "Murcia", "Osasuna B", "Ponferradina", "Real Sociedad B", "Real Unión", "Sabadell", "Sestao River", "Unionistas", "Zamora"],
    "🇪🇸 Segunda RFEF": ["Ávilés Industrial", "Compostela", "Laredo", "Numancia", "Pontevedra", "Rayo Majadahonda", "Tudelano", "Utebo", "Badalona Futur", "Europa", "Lleida Esportiu", "Sant Andreu", "Terrassa", "Alzira", "Orihuela", "Ucam Murcia"],

    # INGLATERRA
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": ["Arsenal FC", "Aston Villa FC", "AFC Bournemouth", "Brentford FC", "Brighton & Hove Albion", "Chelsea FC", "Crystal Palace", "Everton FC", "Fulham FC", "Ipswich Town", "Leeds United", "Liverpool FC", "Manchester City", "Manchester United", "Newcastle United", "Nottingham Forest", "Sunderland AFC", "Tottenham Hotspur", "West Ham United", "Wolverhampton Wanderers"],
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship": ["Blackburn Rovers", "Bristol City", "Burnley FC", "Cardiff City", "Coventry City", "Derby County", "Hull City", "Luton Town", "Middlesbrough FC", "Millwall FC", "Norwich City", "Oxford United", "Plymouth Argyle", "Preston North End", "QPR", "Sheffield United", "Sheffield Wednesday", "Stoke City", "Swansea City", "Watford FC", "West Bromwich Albion"],
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 League One": ["Barnsley", "Birmingham City", "Blackpool", "Bolton Wanderers", "Charlton Athletic", "Exeter City", "Huddersfield Town", "Lincoln City", "Mansfield Town", "Northampton Town", "Peterborough United", "Reading FC", "Rotherham United", "Stockport County", "Wigan Athletic", "Wrexham AFC"],
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 League Two": ["AFC Wimbledon", "Barrow AFC", "Bradford City", "Carlisle United", "Cheltenham Town", "Chesterfield", "Crewe Alexandra", "Doncaster Rovers", "Gillingham FC", "Grimsby Town", "MK Dons", "Notts County", "Port Vale", "Salford City", "Swindon Town", "Walsall FC"],

    # FRANCIA & ITALIA & ALEMANIA
    "🇫🇷 Ligue 1": ["AJ Auxerre", "Angers SCO", "AS Monaco", "AS Saint-Étienne", "FC Nantes", "FC Lorient", "Losc Lille", "Montpellier HSC", "OGC Nice", "Olympique Lyonnais", "Olympique de Marseille", "Paris Saint-Germain", "RC Lens", "RC Strasbourg", "Stade Brestois", "Stade Reims", "Stade Rennais", "Toulouse FC"],
    "🇫🇷 Ligue 2": ["AC Ajaccio", "Amiens SC", "Clermont Foot", "EA Guingamp", "FC Annecy", "FC Metz", "Grenoble Foot", "Girondins de Bordeaux", "Paris FC", "Pau FC", "Rodez AF", "SM Caen", "Troyes AC", "US Quevilly"],
    "🇮🇹 Serie A": ["AC Milan", "ACF Fiorentina", "AS Roma", "Atalanta BC", "Bologna FC", "Cagliari Calcio", "Como 1907", "Empoli FC", "Genoa CFC", "FC Internazionale", "Juventus FC", "SS Lazio", "US Lecce", "AC Monza", "SSC Napoli", "Parma Calcio", "Torino FC", "Udinese Calcio", "U.S. Salernitana", "Venezia FC"],
    "🇮🇹 Serie B": ["Bari", "Brescia", "Carrarese", "Catanzaro", "Cesena", "Cittadella", "Cosenza", "Cremonese", "Frosinone", "Juve Stabia", "Modena", "Palermo", "Pisa", "Reggiana", "Sampdoria", "Sassuolo", "Spezia", "Südtirol"],
    "🇩🇪 Bundesliga": ["1. FC Heidenheim", "1. FC Union Berlin", "1. FSV Mainz 05", "Bayer 04 Leverkusen", "FC Bayern München", "VfL Bochum", "Borussia Dortmund", "Borussia Mönchengladbach", "Eintracht Frankfurt", "FC Augsburg", "RB Leipzig", "SC Freiburg", "SV Werder Bremen", "TSG 1899 Hoffenheim", "VfB Stuttgart", "VfL Wolfsburg", "FC St. Pauli", "Holstein Kiel"],
    "🇩🇪 2. Bundesliga": ["1. FC Kaiserslautern", "1. FC Köln", "1. FC Magdeburg", "Eintracht Braunschweig", "FC Schalke 04", "Fortuna Düsseldorf", "Greuther Fürth", "Hamburger SV", "Hannover 96", "Hertha BSC", "Karlsruher SC", "SC Paderborn 07", "SSV Ulm 1846", "SV Elversberg"],

    # EUROPA DE NORTE Y ORIENTE
    "🇸🇪 Allsvenskan": ["AIK", "BK Häcken", "Djurgårdens IF", "GAIS", "Halmstads BK", "Hammarby IF", "IF Brommapojkarna", "IF Elfsborg", "IFK Göteborg", "IFK Norrköping", "IK Sirius", "Kalmar FF", "Malmö FF", "Mjällby AIF", "Västerås SK"],
    "🇳🇴 Eliteserien": ["Bodø/Glimt", "SK Brann", "Fredrikstad FK", "FK Haugesund", "KFUM Oslo", "Lillestrøm SK", "Molde FK", "Odd BK", "Rosenborg BK", "Sandefjord Fotball", "Sarpsborg 08", "Strømsgodset IF", "Tromsø IL", "Viking FK"],
    "🇳🇱 Eredivisie": ["AFC Ajax", "AZ Alkmaar", "Feyenoord Rotterdam", "Fortuna Sittard", "Go Ahead Eagles", "FC Groningen", "sc Heerenveen", "Heracles Almelo", "NAC Breda", "PEC Zwolle", "PSV Eindhoven", "RKC Waalwijk", "Sparta Rotterdam", "FC Twente", "FC Utrecht", "Vitesse Arnhem", "Willem II"],
    "🇧🇪 Jupiler Pro League": ["RSC Anderlecht", "Antwerp FC", "Cercle Brugge", "Club Brugge", "KRC Genk", "KAA Gent", "KVC Westerlo", "Oud-Heverlee Leuven", "RSC Charleroi", "Royale Union Saint-Gilloise", "Standard Liège"],
    "🇩🇰 Superliga Dinamarca": ["Aalborg BK", "AGF Aarhus", "Brøndby IF", "FC Copenhagen", "FC Midtjylland", "FC Nordsjælland", "Lyngby BK", "Randers FC", "Silkeborg IF", "Viborg FF"],
    "🇵🇱 Ekstraklasa": ["Cracovia", "Górnik Zabrze", "Jagiellonia Białystok", "Lech Poznań", "Legia Warszawa", "Piast Gliwice", "Pogoń Szczecin", "Raków Częstochowa", "Śląsk Wrocław", "Widzew Łódź"],
    "🇧🇬 efbet League Bulgaria": ["Botev Plovdiv", "CSKA 1948", "CSKA Sofia", "Cherno More", "Levski Sofia", "Ludogorets Razgrad", "Lokomotiv Plovdiv", "Spartak Varna"],
    "🇭🇷 SuperSport HNL": ["Dinamo Zagreb", "HNK Gorica", "Hajduk Split", "Istra 1961", "Lokomotiva Zagreb", "NK Osijek", "Rijeka", "Slaven Belupo"],
    "🇨🇿 Chance Liga": ["Baník Ostrava", "Bohemians 1905", "Dukla Praha", "FC Hradec Králové", "MFK Karviná", "SK Sigma Olomouc", "SK Slavia Praha", "FC Slovan Liberec", "AC Sparta Praha", "FC Viktoria Plzeň"],
    "🇷🇸 Superliga Serbia": ["FK TSC Bačka Topola", "FK Čukarički", "FK Partizan", "FK Radnički Niš", "FK Vojvodina", "Red Star Belgrade (Crvena Zvezda)", "OFK Beograd"],
    "🇦🇹 Bundesliga Austria": ["FC Red Bull Salzburg", "FK Austria Wien", "LASK", "SK Rapid Wien", "SK Sturm Graz", "TSV Hartberg", "Wolfsberger AC"],
    "🇨🇭 Superliga de Suiza": ["BSC Young Boys", "FC Basel", "FC Lugano", "FC Luzern", "FC Servette", "FC St. Gallen", "FC Zürich", "Grasshopper Club Zürich"],
    "🇵🇹 Liga Portugal": ["Arouca", "AVS", "SL Benfica", "Boavista FC", "SC Braga", "Casa Pia AC", "GD Estoril Praia", "CF Estrela da Amadora", "FC Famalicão", "SC Farense", "Gil Vicente FC", "Moreirense FC", "CD Nacional", "FC Porto", "Rio Ave FC", "CD Santa Clara", "Sporting CP", "Vitória de Guimarães"],
    "🇵🇹 Liga 2 Portugal": ["Académico de Viseu", "Benfica B", "CD Feirense", "FC Felgueiras", "FC Penafiel", "GD Chaves", "Lousada", "Marítimo", "Oliveirense", "Porto B", "Torreense", "Vizela"],
    "🇸Kb Liga Eslovaquia": ["DAC Dunajská Streda", "FC Košice", "MFK Ružomberok", "ŠK Slovan Bratislava", "FC Spartak Trnava", "AS Trenčín", "MŠK Žilina"],
    "🇸🇮 Liga Eslovenia": ["FC Koper", "NK Celje", "NK Domžale", "NK Maribor", "NK Olimpija Ljubljana", "NK Mura"],

    # AMÉRICA & ASIA
    "🇦🇷 Primera División Argentina": ["Boca Juniors", "River Plate", "Racing Club", "Independiente", "San Lorenzo", "Vélez Sarsfield", "Estudiantes de La Plata", "Gimnasia La Plata", "Talleres de Córdoba", "Belgrano", "Rosario Central", "Newell's Old Boys", "Argentinos Juniors", "CA Huracán", "CA Lanús", "Godoy Cruz", "Defensa y Justicia", "Platense", "Unión de Santa Fe", "Tigre"],
    "🇨🇷 Primera División Costa Rica": ["AD San Carlos", "Alajuelense", "CS Cartaginés", "CS Herediano", "Deportivo Saprissa", "Municipal Liberia", "Puntarenas FC", "Pérez Zeledón", "Santos de Guápiles"],
    "🇨🇴 Primera División Colombia": ["América de Cali", "Atlético Bucaramanga", "Atlético Nacional", "Deportes Tolima", "Deportivo Cali", "Deportivo Independiente Medellín", "Junior de Barranquilla", "Millonarios FC", "Once Caldas", "Santa Fe"],
    "🇧🇷 Brasileirao": ["Athletico Paranaense", "Atlético Mineiro", "Bahia", "Botafogo", "Corinthians", "Cruzeiro", "Flamengo", "Fluminense", "Fortaleza", "Gremio", "Internacional", "Juventude", "Palmeiras", "Red Bull Bragantino", "Sao Paulo", "Vasco da Gama", "Vitoria"],
    "🇧🇷 Brasileirao Série B": ["America Mineiro", "Avaí FC", "Ceará SC", "Chapecoense", "Coritiba", "CRB", "Goiás EC", "Guarani FC", "Itaúna", "Novorizontino", "Operário", "Ponte Preta", "Santos FC", "Sport Recife", "Vila Nova"],
    "🇺🇾 Primera División Uruguay": ["Boston River", "Danubio FC", "Defensor Sporting", "Liverpool Montevideo", "Montevideo Wanderers", "Nacional", "Peñarol", "River Plate Montevideo"],
    "🇨🇱 Primera División Chile": ["Audax Italiano", "Cobreloa", "Cobresal", "Colo-Colo", "Coquimbo Unido", "Everton de Viña del Mar", "Huachipato", "Ñublense", "Palestino", "Unión Española", "Universidad Católica", "Universidad de Chile"],
    "🇺🇸 MLS": ["Atlanta United FC", "Austin FC", "Charlotte FC", "Chicago Fire FC", "FC Cincinnati", "Colorado Rapids", "Columbus Crew", "D.C. United", "FC Dallas", "Houston Dynamo FC", "Inter Miami CF", "LA Galaxy", "LAFC", "Minnesota United FC", "CF Montréal", "Nashville SC", "New England Revolution", "New York City FC", "New York Red Bulls", "Orlando City SC", "Philadelphia Union", "Portland Timbers", "Real Salt Lake", "San Jose Earthquakes", "Seattle Sounders FC", "Sporting Kansas City", "St. Louis City SC", "Toronto FC", "Vancouver Whitecaps FC"],
    "🇺🇸 MLS Next Pro": ["Austin FC II", "Carolina Core FC", "Chattanooga FC", "Chicago Fire II", "Colorado Rapids 2", "Columbus Crew 2", "Crown Legacy FC", "FC Cincinnati 2", "Huntsville City FC", "Inter Miami II", "LA Galaxy II", "MNUFC2", "NYCFC II", "NYRB II", "Orlando City B", "Philadelphia Union II", "Real Monarchs", "St Louis CITY 2", "Tacoma Defiance", "Town FC", "Ventura County FC"],
    "🇺🇸 USL": ["Birmingham Legion FC", "Charleston Battery", "Colorado Springs Switchbacks", "Detroit City FC", "El Paso Locomotive FC", "Indy Eleven", "Louisville City FC", "Memphis 901 FC", "Miami FC", "New Mexico United", "Oakland Roots SC", "Orange County SC", "Phoenix Rising FC", "Pittsburgh Riverhounds", "Sacramento Republic FC", "San Antonio FC", "Tampa Bay Rowdies"],
    "🇯🇵 J-League": ["Albirex Niigata", "Avispa Fukuoka", "Cerezo Osaka", "FC Tokyo", "Gamba Osaka", "Hokkaido Consadole Sapporo", "Júbilo Iwata", "Kashima Antlers", "Kashiwa Reysol", "Kawasaki Frontale", "Machida Zelvia", "Nagoya Grampus", "Sanfrecce Hiroshima", "Shonan Bellmare", "Urawa Red Diamonds", "Vissel Kobe", "Yokohama F. Marinos"]
}

# 5. MOSTRAR PERFIL REESTRUCTURADO
def mostrar_perfil_jugador(jugador, tabla_origen, idx_origen):
    st.markdown("---")
    st.subheader(f"👤 Perfil Analítico: {jugador['Nombre']}")
    
    pestanas_principales = st.tabs(["📋 General & Contrato", "📊 Rendimiento & Data", "💰 Mercado & Viabilidad"])
    
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
            st.markdown("##### 📌 Datos Personales y Deportivos")
            st.markdown(f"**Nombre:** {jugador['Nombre']}")
            st.markdown(f"**Edad:** {jugador['Edad']} años")
            st.markdown(f"**Posición Específica:** {jugador['Posición']}")
            if 'Nacionalidad' in jugador and jugador['Nacionalidad']: 
                st.markdown(f"**Nacionalidad:** {jugador['Nacionalidad']}")
            else:
                st.markdown("**Nacionalidad:** N/D")

        with c_inf2:
            st.markdown("##### 📝 Situación Contractual")
            st.markdown(f"**Club Actual:** {jugador['Club']}")
            st.markdown(f"**Liga / Competición:** {jugador.get('Liga', 'N/D')}")
            if 'Agencia' in jugador and jugador['Agencia']: 
                st.markdown(f"**Agencia / Representante:** {jugador['Agencia']}")
            if 'Status' in jugador: 
                st.markdown(f"**Estatus:** {jugador['Status']}")

    # TAB 2: RENDIMIENTO & DATA
    with pestanas_principales[1]:
        st.markdown("### 📈 Centro de Análisis Estadístico")
        sub_vistas = st.tabs(["🌐 Compendio General (p/90)", "🏆 Promedio por Torneo", "🎯 Ficha de Partido Único"])
        
        tot_min = df_partidos['minutos'].sum() if not df_partidos.empty else 0
        tot_partidos = len(df_partidos) if not df_partidos.empty else 0
        
        # Sub-vista 1: Compendio General
        with sub_vistas[0]:
            c_rad, c_mat = st.columns([1.2, 2.8])
            
            val_radar = [70, 75, 65, 80, 72]
            if tot_min > 0:
                g_p90 = (df_partidos['goles'].sum() / tot_min) * 90
                a_p90 = (df_partidos['asistencias'].sum() / tot_min) * 90
                t_p90 = (df_partidos['tiros'].sum() / tot_min) * 90
                p_p90 = (df_partidos['pases_clave'].sum() / tot_min) * 90
                d_p90 = (df_partidos['duelos_ganados'].sum() / tot_min) * 90
                i_p90 = (df_partidos['intercepciones'].sum() / tot_min) * 90
                
                val_radar = [
                    min(100, int(g_p90 * 30 + t_p90 * 15 + 35)),
                    min(100, int(a_p90 * 35 + p_p90 * 15 + 35)),
                    min(100, int(i_p90 * 20 + d_p90 * 5 + 40)),
                    min(100, int(d_p90 * 8 + 40)),
                    min(100, int(p_p90 * 15 + 45))
                ]
                
            with c_rad:
                st.caption(f"📊 Acumulado: **{tot_partidos} partidos** | **{tot_min} minutos jugados**")
                angulos = [n / 5 * 2 * math.pi for n in range(5)]; angulos += angulos[:1]
                valores_plot = val_radar + val_radar[:1]
                fig, ax = plt.subplots(figsize=(2.2, 2.2), subplot_kw=dict(polar=True))
                plt.xticks(angulos[:-1], ejes_radar, color='#1A2B4C', size=7, weight='bold')
                ax.plot(angulos, valores_plot, color='#1A2B4C', linewidth=2)
                ax.fill(angulos, valores_plot, color='#C8A165', alpha=0.45)
                fig.patch.set_facecolor('none'); ax.set_facecolor('none'); ax.set_yticklabels([])
                st.pyplot(fig, use_container_width=True)
                
            with c_mat:
                st.markdown("#### Matriz Quirúrgica Acumulada p/90")
                metricas_q = obtener_30_metricas(jugador['Posición'])
                m_tabs = st.tabs(list(metricas_q.keys()))
                for i, (pilar, lista_m) in enumerate(metricas_q.items()):
                    with m_tabs[i]:
                        cols = st.columns(4)
                        for j, metrica in enumerate(lista_m):
                            val_str = "0.0 p/90"
                            if tot_min > 0:
                                if "Goles" in metrica: val_str = f"{(df_partidos['goles'].sum()/tot_min)*90:.2f} p/90"
                                elif "Asistencias" in metrica: val_str = f"{(df_partidos['asistencias'].sum()/tot_min)*90:.2f} p/90"
                                elif "Tiros" in metrica: val_str = f"{(df_partidos['tiros'].sum()/tot_min)*90:.2f} p/90"
                                elif "Pases" in metrica: val_str = f"{(df_partidos['pases_clave'].sum()/tot_min)*90:.2f} p/90"
                                elif "Duelos" in metrica: val_str = f"{(df_partidos['duelos_ganados'].sum()/tot_min)*90:.2f} p/90"
                                elif "Intercepciones" in metrica: val_str = f"{(df_partidos['intercepciones'].sum()/tot_min)*90:.2f} p/90"
                                else: val_str = "Acumulado"
                            cols[j % 4].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165; font-weight:bold;'>{val_str}</span></div>", unsafe_allow_html=True)

        # Sub-vista 2: Promedio por Torneo
        with sub_vistas[1]:
            if not df_partidos.empty and 'liga' in df_partidos.columns:
                torneos_disponibles = df_partidos['liga'].unique().tolist()
                torneo_sel = st.selectbox("🏆 Seleccionar Torneo para Evaluar:", torneos_disponibles, key=f"torneo_sel_{jugador['ID']}")
                
                df_torneo = df_partidos[df_partidos['liga'] == torneo_sel]
                min_torneo = df_torneo['minutos'].sum()
                part_torneo = len(df_torneo)
                
                st.info(f"Rendimiento en **{torneo_sel}**: **{part_torneo} partidos** | **{min_torneo} minutos totales**")
                
                c_rad_t, c_mat_t = st.columns([1.2, 2.8])
                with c_rad_t:
                    val_t = [65, 70, 60, 75, 68]
                    if min_torneo > 0:
                        val_t = [
                            min(100, int((df_torneo['goles'].sum()/min_torneo)*90 * 30 + 35)),
                            min(100, int((df_torneo['asistencias'].sum()/min_torneo)*90 * 35 + 35)),
                            min(100, int((df_torneo['intercepciones'].sum()/min_torneo)*90 * 20 + 40)),
                            min(100, int((df_torneo['duelos_ganados'].sum()/min_torneo)*90 * 8 + 40)),
                            min(100, int((df_torneo['pases_clave'].sum()/min_torneo)*90 * 15 + 45))
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
                                val_str = "0.0 p/90"
                                if min_torneo > 0:
                                    if "Goles" in metrica: val_str = f"{(df_torneo['goles'].sum()/min_torneo)*90:.2f} p/90"
                                    elif "Asistencias" in metrica: val_str = f"{(df_torneo['asistencias'].sum()/min_torneo)*90:.2f} p/90"
                                    elif "Tiros" in metrica: val_str = f"{(df_torneo['tiros'].sum()/min_torneo)*90:.2f} p/90"
                                    elif "Pases" in metrica: val_str = f"{(df_torneo['pases_clave'].sum()/min_torneo)*90:.2f} p/90"
                                    elif "Duelos" in metrica: val_str = f"{(df_torneo['duelos_ganados'].sum()/min_torneo)*90:.2f} p/90"
                                    else: val_str = "Promedio Torneo"
                                cols[j % 4].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165; font-weight:bold;'>{val_str}</span></div>", unsafe_allow_html=True)
            else:
                st.info("No hay partidos registrados para filtrar por competición. Registra partidos en 'Ingreso de Data'.")

        # Sub-vista 3: Ficha de Partido Único
        with sub_vistas[2]:
            if not df_partidos.empty and 'jornada' in df_partidos.columns:
                c_f1, c_f2 = st.columns(2)
                torneo_f = c_f1.selectbox("Filtrar Torneo:", df_partidos['liga'].unique().tolist(), key=f"tf_{jugador['ID']}")
                
                df_partidos_torneo = df_partidos[df_partidos['liga'] == torneo_f]
                partidos_lista = [f"{row['jornada']} vs. {row['equipo']}" for _, row in df_partidos_torneo.iterrows()]
                
                partido_sel = c_f2.selectbox("Seleccionar Juego Específico:", partidos_lista, key=f"ps_{jugador['ID']}")
                
                idx_p = partidos_lista.index(partido_sel)
                p_data = df_partidos_torneo.iloc[idx_p]
                
                st.success(f"📌 Ficha Táctica: **{p_data['jornada']}** | Rival: **{p_data['equipo']}** | Torneo: **{p_data['liga']}**")
                
                cp1, cp2, cp3, cp4 = st.columns(4)
                cp1.metric("Minutos Jugados", f"{p_data['minutos']}'")
                cp2.metric("Goles Anotados", p_data['goles'])
                cp3.metric("Asistencias", p_data['asistencias'])
                cp4.metric("Tiros a Puerta", p_data['tiros'])
                
                cp5, cp6, cp7, cp8 = st.columns(4)
                cp5.metric("Pases Clave", p_data['pases_clave'])
                cp6.metric("Duelos Ganados", p_data['duelos_ganados'])
                cp7.metric("Intercepciones", p_data['intercepciones'])
                cp8.metric("Faltas Cometidas", p_data['faltas'])
                
                st.markdown("#### Matriz de Acciones Reales del Partido (Conteos Absolutos)")
                metricas_q = obtener_30_metricas(jugador['Posición'])
                m_tabs_p = st.tabs(list(metricas_q.keys()))
                for i, (pilar, lista_m) in enumerate(metricas_q.items()):
                    with m_tabs_p[i]:
                        cols = st.columns(4)
                        for j, metrica in enumerate(lista_m):
                            val_str = "0"
                            if "Goles" in metrica: val_str = f"{p_data['goles']} en el juego"
                            elif "Asistencias" in metrica: val_str = f"{p_data['asistencias']} en el juego"
                            elif "Tiros" in metrica: val_str = f"{p_data['tiros']} tiro(s)"
                            elif "Pases" in metrica: val_str = f"{p_data['pases_clave']} pases clave"
                            elif "Duelos" in metrica: val_str = f"{p_data['duelos_ganados']} duelos"
                            elif "Intercepciones" in metrica: val_str = f"{p_data['intercepciones']} interc."
                            elif "Minutos" in metrica: val_str = f"{p_data['minutos']} minutos"
                            else: val_str = "Registrado"
                            cols[j % 4].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#1A2B4C; font-weight:bold;'>{val_str}</span></div>", unsafe_allow_html=True)
            else:
                st.info("No hay fichas de partidos individuales cargadas para este jugador.")

    # TAB 3: MERCADO & VIABILIDAD
    with pestanas_principales[2]:
        st.markdown("### 💰 Ficha Financiera y Viabilidad de Fichaje")
        cm1, cm2, cm3 = st.columns(3)
        
        val_m = jugador.get('Valor', 'N/D')
        via_m = jugador.get('Viabilidad', '🟡 Media')
        
        cm1.metric("Valoración Estimada de Mercado", val_m)
        cm2.metric("Semáforo de Viabilidad", via_m)
        cm3.metric("Cupo NMM / Extranjero", "Aplica" if "🇲🇽" not in jugador.get('Nacionalidad', '') else "Nacional")
        
        st.markdown("---")
        st.markdown("##### 📌 Notas Estratégicas de Negociación")
        st.write(f"- **Perfil Financiero:** Jugador tasado en `{val_m}` accesible bajo esquema de cesión o compra de porcentaje de pase.")
        st.write(f"- **Factibilidad:** Calificado con viabilidad `{via_m}` según estatus de contrato actual en {jugador['Club']}.")

    # MÓDULO DE EDICIÓN
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
                    st.error(f"Error en Supabase: {e}")
            
        if col_btn2.button("🗑️ Eliminar Perfil", key=f"dl_{jugador['ID']}"):
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
    
    .login-container { max-width: 420px; margin: 50px auto; padding: 40px; background: #FFFFFF; border-radius: 12px; box-shadow: 0 10px 30px rgba(26, 43, 76, 0.12); border-top: 5px solid #C8A165; text-align: center; }
    .metric-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #1A2B4C; padding: 12px; border-radius: 6px; margin-bottom: 10px; color: #1A2B4C; font-size: 13px; }
    .stButton>button { background-color: #C8A165 !important; color: #1A2B4C !important; font-weight: bold !important; border: none !important; border-radius: 6px !important; width: 100% !important; }
    .stButton>button:hover { background-color: #1A2B4C !important; color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

# 7. SESIÓN Y NAVEGACIÓN
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
                        st.error(f"Error en Supabase: {e}")

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
