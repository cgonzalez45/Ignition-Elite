import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import base64
from datetime import date, datetime

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

def procesar_video(uploaded_file):
    if uploaded_file is not None:
        mime_type = uploaded_file.type if uploaded_file.type else "video/mp4"
        return f"data:{mime_type};base64," + base64.b64encode(uploaded_file.getvalue()).decode()
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

st.session_state['scouting_db'] = cargar_desde_supabase('scouting_db')
st.session_state['equipo_ignition'] = cargar_desde_supabase('equipo_ignition')

# 3. POSICIONES Y MÉTRICAS POR ROL
LISTA_POSICIONES = [
    "Portero", "Defensa Central", "Lateral Izquierdo", "Lateral Derecho", 
    "Pivote Defensivo (MCD)", "Mediocentro (MC)", "Medio Centro Ofensivo (MCO)", 
    "Extremo", "Delantero Centro"
]

# =====================================================================
# 🚨 NOTA IMPORTANTE PARA CHRISTIAN 🚨
# Para evitar el error de memoria, colapsé esta función.
# BORRA la palabra 'pass' y PEGA AQUÍ TU FUNCIÓN COMPLETA obtener_30_metricas
# (Asegúrate que tenga la Velocidad Máxima como la armamos hace rato)
# =====================================================================
def obtener_30_metricas(posicion):
    pass 

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

# ==============================================================
# MOTOR MATEMÁTICO: "DATO DURO" + CANDADOS DE COHERENCIA LÓGICA
# ==============================================================
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
            # Filtro para ignorar los nuevos metadatos de texto y que no tire error matemático
            if k in ["video_clip", "video_titulo", "estatus_participacion", "fecha", "marcador"]: continue
            try:
                val_f = float(v)
                sumas[k] = sumas.get(k, 0.0) + val_f
            except Exception:
                pass
                
        if "Goles Totales" not in m_custom and "Goles Anotados" not in m_custom:
            sumas["Goles Totales"] = sumas.get("Goles Totales", 0.0) + float(row.get('goles', 0) or 0)
        if "Asistencias Directas" not in m_custom and "Asistencias Totales" not in m_custom:
            sumas["Asistencias Directas"] = sumas.get("Asistencias Directas", 0.0) + float(row.get('asistencias', 0) or 0)
        if "Tiros a Puerta" not in m_custom and "Tiros Totales" not in m_custom:
            sumas["Tiros a Puerta"] = sumas.get("Tiros a Puerta", 0.0) + float(row.get('tiros', 0) or 0)
        if "Pases Clave" not in m_custom:
            sumas["Pases Clave"] = sumas.get("Pases Clave", 0.0) + float(row.get('pases_clave', 0) or 0)
        if "Duelos Ganados" not in m_custom and "1v1 Ganados %" not in m_custom:
            sumas["Duelos Ganados"] = sumas.get("Duelos Ganados", 0.0) + float(row.get('duelos_ganados', 0) or 0)
        if "Intercepciones" not in m_custom:
            sumas["Intercepciones"] = sumas.get("Intercepciones", 0.0) + float(row.get('intercepciones', 0) or 0)

    for k, total_val in sumas.items():
        if "%" in k or "Velocidad" in k or "km/h" in k:
            promedios[k] = round(total_val / tot_partidos, 1)
        elif "Minutos" in k:
            promedios[k] = round(total_val / tot_partidos, 0)
        else:
            promedios[k] = round(total_val / tot_partidos, 2)

    if promedios.get("Goles Totales", 0) > promedios.get("Tiros a Puerta", 0):
        promedios["Tiros a Puerta"] = promedios["Goles Totales"]
        
    if promedios.get("Tiros a Puerta", 0) > promedios.get("Tiros Totales", promedios.get("Tiros a Puerta", 0)):
        promedios["Tiros Totales"] = promedios["Tiros a Puerta"]
        
    return promedios, tot_partidos, tot_min

# 4. LIGAS MUNDIALES Y EQUIPOS
# =====================================================================
# 🚨 NOTA IMPORTANTE PARA CHRISTIAN 🚨
# PEGA AQUÍ ABAJO TUS LISTAS DE: 
# LIGAS_MUNDIALES, JORNADAS_OPCIONES y EQUIPOS_POR_LIGA (y los arreglos de MLS, Liga MX, etc.)
# =====================================================================
LIGAS_MUNDIALES = ["Champions League", "Ekstraklasa"] # Reemplaza con tus listas
JORNADAS_OPCIONES = ["Fase de Grupos", "Jornada 1"] # Reemplaza
EQUIPOS_POR_LIGA = {} # Reemplaza


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
        sub_vistas = st.tabs(["Compendio General (Promedio por Partido)", "Promedio por Torneo", "Ficha de Partido Único"])
        
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
                st.markdown(f"#### Matriz Quirúrgica (Dato Duro por Partido - p/P)")
                metricas_q = obtener_30_metricas(jugador['Posición'])
                m_tabs = st.tabs(list(metricas_q.keys()))
                for i, (pilar, lista_m) in enumerate(metricas_q.items()):
                    with m_tabs[i]:
                        cols = st.columns(4)
                        for j, metrica in enumerate(lista_m):
                            val_calculado = promedios_gen.get(metrica, 0.0)
                            unit = "%" if "%" in metrica else (" km/h" if ("Velocidad" in metrica or "km/h" in metrica) else ("" if "Minutos" in metrica else " p/P"))
                            cols[j % 4].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165; font-weight:bold;'>{val_calculado}{unit}</span></div>", unsafe_allow_html=True)

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
                    st.markdown(f"#### Promedios Reales (p/P) en {torneo_sel}")
                    metricas_q = obtener_30_metricas(jugador['Posición'])
                    m_tabs_t = st.tabs(list(metricas_q.keys()))
                    for i, (pilar, lista_m) in enumerate(metricas_q.items()):
                        with m_tabs_t[i]:
                            cols = st.columns(4)
                            for j, metrica in enumerate(lista_m):
                                val_calc_t = promedios_torneo.get(metrica, 0.0)
                                unit_t = "%" if "%" in metrica else (" km/h" if ("Velocidad" in metrica or "km/h" in metrica) else ("" if "Minutos" in metrica else " p/P"))
                                cols[j % 4].markdown(f"<div class='metric-card'><b>{metrica}</b><br><span style='color:#C8A165; font-weight:bold;'>{val_calc_t}{unit_t}</span></div>", unsafe_allow_html=True)
            else:
                st.info("No hay partidos registrados para filtrar por competición. Registra partidos en 'Ingreso de Data'.")

        with sub_vistas[2]:
            if not df_partidos.empty and 'jornada' in df_partidos.columns:
                c_f1, c_f2 = st.columns(2)
                torneo_f = c_f1.selectbox("Filtrar Torneo:", df_partidos['liga'].unique().tolist(), key=f"tf_{jugador['ID']}")
                
                df_partidos_torneo = df_partidos[df_partidos['liga'] == torneo_f]
                
                # Leemos la fecha y marcador escondidos en m_data
                partidos_lista = []
                for _, row in df_partidos_torneo.iterrows():
                    m_tmp = row.get('m_data') if isinstance(row.get('m_data'), dict) else {}
                    f_str = m_tmp.get('fecha', 'S/F')
                    m_str = m_tmp.get('marcador', 'N/D')
                    partidos_lista.append(f"{f_str} | {row['jornada']} vs. {row['equipo']} ({m_str})")
                
                partido_sel = c_f2.selectbox("Seleccionar Juego Específico:", partidos_lista, key=f"ps_{jugador['ID']}")
                
                idx_p = partidos_lista.index(partido_sel)
                p_data = df_partidos_torneo.iloc[idx_p]
                
                m_custom = p_data.get('m_data') if (isinstance(p_data.get('m_data'), dict)) else {}
                e_part = m_custom.get("estatus_participacion", "Jugó (Titular / Cambio)")
                p_fecha_str = m_custom.get("fecha", "N/D")
                p_marcador_str = m_custom.get("marcador", "N/D")

                if "Sin Participación" in e_part:
                    st.warning(f"Ficha Táctica: **{p_data['jornada']}** | Rival: **{p_data['equipo']}** | Marcador: **{p_marcador_str}** | Fecha: **{p_fecha_str}** | **ESTATUS: EN BANCA**")
                elif "No Convocado" in e_part:
                    st.error(f"Ficha Táctica: **{p_data['jornada']}** | Rival: **{p_data['equipo']}** | Marcador: **{p_marcador_str}** | Fecha: **{p_fecha_str}** | **ESTATUS: NO CONVOCADO**")
                else:
                    st.success(f"Ficha Táctica: **{p_data['jornada']}** | Rival: **{p_data['equipo']}** | Marcador: **{p_marcador_str}** | Fecha: **{p_fecha_str}** | Torneo: **{p_data['liga']}**")

                video_data = m_custom.get("video_clip")
                video_titulo = m_custom.get("video_titulo", "Clip de la Acción")
                if video_data:
                    with st.expander(f"🎬 VER VIDEO: {video_titulo}", expanded=True):
                        st.video(video_data)

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

    # MÓDULO DE EDICIÓN PROTEGIDO POR ROLES (SOLO ADMIN)
    if st.session_state.get('role') == 'admin':
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
                    "nombre": nuevo_nom, "edad": nueva_edad, "posicion": nueva_pos,
                    "liga": nueva_liga, "club": nuevo_club, "foto": foto_base64
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

# 6. ESTÉTICA GLOBAL
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA !important; }
    [data-testid="stHeader"] { background-color: transparent !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .block-container { padding-top: 2rem !important; }
    [data-testid="stSidebar"] { background-color: #1A2B4C !important; border-right: 2px solid #C8A165 !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .player-photo-card { width: 150px; height: 180px; border-radius: 8px; border: 2px solid #C8A165; overflow: hidden; background-color: #111D35; display: flex; justify-content: center; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.15); }
    .player-photo-img { max-width: 100%; max-height: 100%; object-fit: contain; object-position: center; }
    .metric-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #1A2B4C; padding: 12px; border-radius: 6px; margin-bottom: 10px; color: #1A2B4C; font-size: 13px; }
    .stButton>button { background-color: #C8A165 !important; color: #1A2B4C !important; font-weight: bold !important; border: none !important; border-radius: 6px !important; width: 100% !important; padding: 10px !important; }
    .stButton>button:hover { background-color: #1A2B4C !important; color: #FFFFFF !important; }
    .login-container { max-width: 440px; margin: 40px auto; padding: 40px; background: #FFFFFF; border-radius: 12px; box-shadow: 0 10px 30px rgba(26, 43, 76, 0.12); border-top: 5px solid #C8A165; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 7. SESIÓN Y NAVEGACIÓN
if 'logged_in' not in st.session_state: 
    st.session_state['logged_in'] = False
    st.session_state['role'] = 'viewer'

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        if os.path.exists("image_8fb87b.jpeg"): st.image("image_8fb87b.jpeg", use_container_width=True)
        elif os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.markdown("<h1 style='text-align:center; color:#1A2B4C; font-size:36px; margin:0;'>IGNITION</h1>", unsafe_allow_html=True)
        
        st.markdown("""
            <h2 style='color:#1A2B4C; margin-top:15px; margin-bottom:0; font-size:22px; text-align:center;'>SCOUTING PRO</h2>
            <p style='color:#C8A165; font-size:12px; font-weight:bold; letter-spacing:1px; margin-top:4px; text-align:center;'>SCOUTING INTERNACIONAL Y DIRECCIÓN DEPORTIVA</p>
            <hr style='border-color:#E2E8F0; margin: 20px 0;'>
        """, unsafe_allow_html=True)
        
        usuario = st.text_input("Usuario Corporativo", key="login_usr_txt")
        password = st.text_input("Contraseña", type="password", key="login_pwd_txt")
        st.write("")
        if st.button("INGRESAR AL SISTEMA", key="login_btn_submit"):
            u_lower = usuario.lower()
            if u_lower == "christian" and password == "Saopaulo45":
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'admin'
                st.rerun()
            elif u_lower in ["sebastian", "gerardo"]:
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'viewer'
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.markdown("<h2 style='color:#C8A165; text-align:center;'>IGNITION ELITE</h2>", unsafe_allow_html=True)
        st.write("---")
        menu_items = ["Dashboard General (Scouting)", "Equipo Ignition", "Shortlists", "Comparador", "Scoring por Perfil"]
        if st.session_state.get('role') == 'admin':
            menu_items.insert(2, "Ingreso de Data (Partidos)")
            
        opcion = st.radio("Navegación Táctica", menu_items)
        st.write("---")
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['role'] = 'viewer'
            st.rerun()

    if opcion == "Dashboard General (Scouting)":
        st.title("Inteligencia de Mercado y Seguimiento")
        if st.session_state.get('role') == 'admin':
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
        if st.session_state.get('role') == 'admin':
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
        if st.session_state.get('role') != 'admin':
            st.error("Acceso denegado. No tienes permisos para ingresar o editar datos tácticos.")
        else:
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
                c1, c2, c3 = st.columns(3)
                if todos_jugadores:
                    n_jugador = c1.selectbox("Seleccionar Jugador Registrado", todos_jugadores, key="p_nom_select")
                else:
                    n_jugador = c1.text_input("Nombre del Jugador", key="p_nom_input")
                    
                n_posicion = c1.selectbox("Posición Específica (Define el Formulario)", LISTA_POSICIONES, key="p_pos_dyn_input")
                
                n_fecha = c2.date_input("Fecha del Partido", value=date.today(), key="p_fecha_input")
                n_marcador = c2.text_input("Marcador Final (ej. 2 - 1)", key="p_marcador_input")
                
                n_liga_sel = c3.selectbox("Competición / Torneo", LIGAS_MUNDIALES, key="p_liga_dyn")
                if "Copa Doméstica" in n_liga_sel:
                    n_liga = c3.text_input("Escribir Nombre de la Copa / Torneo", key="p_liga_copa_txt")
                else:
                    n_liga = n_liga_sel

                if n_liga in EQUIPOS_POR_LIGA:
                    n_equipo = c3.selectbox("Equipo Rival", EQUIPOS_POR_LIGA[n_liga], key="p_club_dyn")
                else:
                    n_equipo = c3.text_input("Equipo Rival (Escribir nombre)", key="p_club_txt_dyn")
                    
                n_jornada = c1.selectbox("Jornada / Fase del Juego", JORNADAS_OPCIONES, key="p_jornada_input")
                
                # BOTONES DE ESTATUS RÁPIDO DE PARTICIPACIÓN
                estatus_part = st.radio("Estatus de Participación del Jugador", ["Jugó (Titular / Cambio)", "Sin Participación (En Banca)", "No Convocado"], horizontal=True, key="p_estatus_part")
                
                if estatus_part == "Jugó (Titular / Cambio)":
                    v_minutos = c2.number_input("Minutos Jugados en el Partido", 1, 120, 90, key="p_min_input")
                else:
                    v_minutos = 0
                    st.info(f"Se registrará automáticamente con **0 minutos** y todas las métricas en cero ({estatus_part}).")

                st.markdown("##### 🎬 Adjuntar Clip de Video del Partido (Opcional)")
                v_titulo = st.text_input("Título del Video (ej. Gol de Cabeza al '84)", key="p_v_tit")
                v_archivo = st.file_uploader("Subir Archivo de Video (MP4 / MOV)", type=['mp4', 'mov'], key="p_v_file")

                st.markdown(f"#### Captura de Métricas para: **{n_posicion}**")
                metricas_pos = obtener_30_metricas(n_posicion)
                
                valores_capturados = {}
                with st.form("form_stats_dinamico"):
                    tabs_p = st.tabs(list(metricas_pos.keys()))
                    for i, (pilar, lista_m) in enumerate(metricas_pos.items()):
                        with tabs_p[i]:
                            cols = st.columns(4)
                            for j, metrica in enumerate(lista_m):
                                default_v = 0.0 if ("%" in metrica or "xG" in metrica or "xA" in metrica or "km" in metrica or "Distancia" in metrica or "Velocidad" in metrica or "km/h" in metrica) else 0
                                if estatus_part != "Jugó (Titular / Cambio)":
                                    val = default_v
                                    cols[j % 4].markdown(f"**{metrica}:** 0")
                                else:
                                    if "xG Evitados" in metrica or "Diferencia" in metrica:
                                        val = cols[j % 4].number_input(metrica, -50.0, 50.0, 0.0, step=0.01, key=f"m_{n_posicion}_{i}_{j}")
                                    elif "%" in metrica or "xG" in metrica or "xA" in metrica or "km" in metrica or "Distancia" in metrica or "Velocidad" in metrica or "km/h" in metrica:
                                        val = cols[j % 4].number_input(metrica, 0.0, 100.0, 0.0, step=0.1, key=f"m_{n_posicion}_{i}_{j}")
                                    else:
                                        val = cols[j % 4].number_input(metrica, 0, 200, 0, step=1, key=f"m_{n_posicion}_{i}_{j}")
                                valores_capturados[metrica] = val
                    
                    if st.form_submit_button("Guardar Partido en Supabase"):
                        if n_jugador and supabase:
                            # GUARDAR FECHA Y MARCADOR DENTRO DE M_DATA PARA NO ALTERAR LA BD
                            valores_capturados["estatus_participacion"] = estatus_part
                            valores_capturados["fecha"] = str(n_fecha)
                            valores_capturados["marcador"] = n_marcador if n_marcador else "N/D"
                            
                            goles_cap = int(valores_capturados.get("Goles Totales", valores_capturados.get("Goles Anotados", 0)))
                            asis_cap = int(valores_capturados.get("Asistencias Directas", valores_capturados.get("Asistencias Totales", 0)))
                            tiros_cap = int(valores_capturados.get("Tiros a Puerta", valores_capturados.get("Tiros Totales", 0)))
                            pases_cap = int(valores_capturados.get("Pases Clave", 0))
                            duelos_cap = int(valores_capturados.get("Duelos Ganados", valores_capturados.get("1v1 Ganados %", 0)))
                            inter_cap = int(valores_capturados.get("Intercepciones", 0))
                            
                            if v_archivo is not None:
                                valores_capturados["video_clip"] = procesar_video(v_archivo)
                                valores_capturados["video_titulo"] = v_titulo if v_titulo else "Clip de la Acción"
                            
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
                st.markdown("#### Corrección de Metadatos, Métricas y Videos de Partido Cargado")
                if todos_jugadores:
                    j_ed_sel = st.selectbox("Seleccionar Jugador para Administrar Partidos:", todos_jugadores, key="j_ed_sel_k")
                    df_p_ed = consultar_partidos_jugador(j_ed_sel)
                    
                    if not df_p_ed.empty:
                        # Extraer fecha y marcador de m_data para mostrar en la lista desplegable
                        partidos_lista_ed = []
                        for _, row in df_p_ed.iterrows():
                            m_tmp = row.get('m_data') if isinstance(row.get('m_data'), dict) else {}
                            f_str = m_tmp.get('fecha', 'S/F')
                            m_str = m_tmp.get('marcador', 'N/D')
                            partidos_lista_ed.append(f"ID #{row['id']} - {f_str} | {row['jornada']} vs. {row['equipo']} ({m_str})")
                        
                        partido_ed_sel = st.selectbox("Seleccionar Partido a Editar o Eliminar:", partidos_lista_ed, key="p_ed_sel_k")
                        idx_p_ed = partidos_lista_ed.index(partido_ed_sel)
                        p_curr = df_p_ed.iloc[idx_p_ed]
                        p_id = p_curr['id']
                        m_curr_custom = p_curr.get('m_data') if isinstance(p_curr.get('m_data'), dict) else {}
                        
                        st.info(f"Editando Registro ID **#{p_id}** de **{j_ed_sel}**")
                        
                        pos_ed = p_curr['posicion']
                        metricas_pos_ed = obtener_30_metricas(pos_ed)
                        
                        st.markdown("##### 1. Corrección de Contexto (Jornada, Fecha, Torneo y Rival)")
                        med_c1, med_c2, med_c3 = st.columns(3)
                        
                        j_curr_val = p_curr.get('jornada', JORNADAS_OPCIONES[0])
                        j_idx = JORNADAS_OPCIONES.index(j_curr_val) if j_curr_val in JORNADAS_OPCIONES else 0
                        ed_jornada = med_c1.selectbox("Jornada / Fase", JORNADAS_OPCIONES, index=j_idx, key=f"ed_jornada_{p_id}")
                        
                        fecha_raw = m_curr_custom.get('fecha')
                        try:
                            fecha_default = datetime.strptime(fecha_raw, "%Y-%m-%d").date() if fecha_raw else date.today()
                        except Exception:
                            fecha_default = date.today()
                        ed_fecha = med_c2.date_input("Fecha del Partido", value=fecha_default, key=f"ed_fecha_{p_id}")
                        ed_marcador = med_c3.text_input("Marcador Final", value=m_curr_custom.get('marcador', ''), key=f"ed_marcador_{p_id}")

                        l_curr_val = p_curr.get('liga', LIGAS_MUNDIALES[0])
                        l_idx = LIGAS_MUNDIALES.index(l_curr_val) if l_curr_val in LIGAS_MUNDIALES else 0
                        ed_liga_sel = med_c1.selectbox("Competición / Torneo Base", LIGAS_MUNDIALES, index=l_idx, key=f"ed_liga_sel_{p_id}")
                        
                        if "Copa Doméstica" in ed_liga_sel:
                            ed_liga = med_c1.text_input("Escribir Nombre de la Copa / Torneo", value=p_curr.get('liga', ''), key=f"ed_liga_copa_{p_id}")
                        else:
                            ed_liga = ed_liga_sel

                        if ed_liga in EQUIPOS_POR_LIGA:
                            eq_opciones = EQUIPOS_POR_LIGA[ed_liga]
                            e_curr_val = p_curr.get('equipo', eq_opciones[0])
                            e_idx = eq_opciones.index(e_curr_val) if e_curr_val in eq_opciones else 0
                            ed_equipo = med_c2.selectbox("Equipo Rival", eq_opciones, index=e_idx, key=f"ed_equipo_{p_id}_{ed_liga}")
                        else:
                            ed_equipo = med_c2.text_input("Equipo Rival (Escribir nombre)", value=p_curr.get('equipo', ''), key=f"ed_equipo_txt_{p_id}")
                            
                        ed_estatus_prev = m_curr_custom.get("estatus_participacion", "Jugó (Titular / Cambio)")
                        estatus_opts = ["Jugó (Titular / Cambio)", "Sin Participación (En Banca)", "No Convocado"]
                        est_idx = estatus_opts.index(ed_estatus_prev) if ed_estatus_prev in estatus_opts else 0
                        ed_estatus_part = st.radio("Estatus de Participación del Jugador", estatus_opts, index=est_idx, horizontal=True, key=f"ed_estatus_part_{p_id}")

                        if ed_estatus_part == "Jugó (Titular / Cambio)":
                            ed_minutos = med_c3.number_input("Minutos Jugados", 1, 120, int(p_curr.get('minutos', 90)), key=f"min_ed_val_{p_id}")
                        else:
                            ed_minutos = 0
                            st.info(f"Se actualizará automáticamente con **0 minutos** ({ed_estatus_part}).")

                        st.markdown("##### 🎬 2. Adjuntar / Actualizar Clip de Video del Partido")
                        v_tit_prev = m_curr_custom.get("video_titulo", "")
                        v_tit_ed = st.text_input("Título del Video", value=v_tit_prev, key=f"ed_v_tit_{p_id}")
                        v_arch_ed = st.file_uploader("Subir / Reemplazar Clip de Video (MP4 / MOV)", type=['mp4', 'mov'], key=f"ed_v_file_{p_id}")

                        valores_corregidos = {}
                        with st.form(f"form_corregir_partido_{p_id}"):
                            st.markdown("##### 3. Corrección de Métricas Tácticas")
                            tabs_ed = st.tabs(list(metricas_pos_ed.keys()))
                            for i, (pilar, lista_m) in enumerate(metricas_pos_ed.items()):
                                with tabs_ed[i]:
                                    cols = st.columns(4)
                                    for j, metrica in enumerate(lista_m):
                                        val_prev = m_curr_custom.get(metrica, 0.0 if ("%" in metrica or "xG" in metrica or "xA" in metrica or "km" in metrica or "Distancia" in metrica or "Velocidad" in metrica or "km/h" in metrica) else 0)
                                        if ed_estatus_part != "Jugó (Titular / Cambio)":
                                            val_c = 0.0 if ("%" in metrica or "xG" in metrica or "xA" in metrica or "km" in metrica or "Distancia" in metrica or "Velocidad" in metrica or "km/h" in metrica) else 0
                                            cols[j % 4].markdown(f"**{metrica}:** 0")
                                        else:
                                            if "xG Evitados" in metrica or "Diferencia" in metrica:
                                                val_c = cols[j % 4].number_input(metrica, -50.0, 50.0, float(val_prev), step=0.01, key=f"med_{pos_ed}_{i}_{j}_{p_id}")
                                            elif "%" in metrica or "xG" in metrica or "xA" in metrica or "km" in metrica or "Distancia" in metrica or "Velocidad" in metrica or "km/h" in metrica:
                                                val_c = cols[j % 4].number_input(metrica, 0.0, 100.0, float(val_prev), step=0.1, key=f"med_{pos_ed}_{i}_{j}_{p_id}")
                                            else:
                                                val_c = cols[j % 4].number_input(metrica, 0, 200, int(val_prev), step=1, key=f"med_{pos_ed}_{i}_{j}_{p_id}")
                                        valores_corregidos[metrica] = val_c
                                        
                            col_ed_b1, col_ed_b2 = st.columns(2)
                            btn_guardar = col_ed_b1.form_submit_button("💾 Guardar Corrección Completa")
                            btn_borrar = col_ed_b2.form_submit_button("🗑️ ELIMINAR ESTE PARTIDO")
                            
                            if btn_guardar:
                                if supabase and p_id:
                                    valores_corregidos["estatus_participacion"] = ed_estatus_part
                                    valores_corregidos["fecha"] = str(ed_fecha)
                                    valores_corregidos["marcador"] = ed_marcador if ed_marcador else "N/D"
                                    
                                    g_c = int(valores_corregidos.get("Goles Totales", valores_corregidos.get("Goles Anotados", 0)))
                                    a_c = int(valores_corregidos.get("Asistencias Directas", valores_corregidos.get("Asistencias Totales", 0)))
                                    t_c = int(valores_corregidos.get("Tiros a Puerta", valores_corregidos.get("Tiros Totales", 0)))
                                    p_c = int(valores_corregidos.get("Pases Clave", 0))
                                    d_c = int(valores_corregidos.get("Duelos Ganados", valores_corregidos.get("1v1 Ganados %", 0)))
                                    i_c = int(valores_corregidos.get("Intercepciones", 0))
                                    
                                    if v_arch_ed is not None:
                                        valores_corregidos["video_clip"] = procesar_video(v_arch_ed)
                                        valores_corregidos["video_titulo"] = v_tit_ed if v_tit_ed else "Clip de la Acción"
                                    else:
                                        if "video_clip" in m_curr_custom:
                                            valores_corregidos["video_clip"] = m_curr_custom["video_clip"]
                                        if v_tit_ed:
                                            valores_corregidos["video_titulo"] = v_tit_ed
                                        elif "video_titulo" in m_curr_custom:
                                            valores_corregidos["video_titulo"] = m_curr_custom["video_titulo"]
                                    
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
                                        supabase.table('partidos_stats').update(payload_update).eq('id', p_id).execute()
                                        st.cache_data.clear()
                                        st.success(f"Partido #{p_id} actualizado correctamente.")
                                        st.rerun()
                                    except Exception as e_up:
                                        st.error(f"Error al actualizar: {e_up}")

                            if btn_borrar:
                                if supabase and p_id:
                                    try:
                                        supabase.table('partidos_stats').delete().eq('id', p_id).execute()
                                        st.cache_data.clear()
                                        st.success(f"Partido #{p_id} eliminado permanentemente de Supabase.")
                                        st.rerun()
                                    except Exception as e_del:
                                        st.error(f"Error al eliminar: {e_del}")
                                        
                    else:
                        st.info("Este jugador no tiene partidos cargados para corregir o borrar.")

    else:
        st.info(f"Módulo '{opcion}' listo para sincronización.")
