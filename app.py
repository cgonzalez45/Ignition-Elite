import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# Configuración de página
st.set_page_config(
    page_title="Scouting Pro - Christian González",
    page_icon="⚽",
    layout="wide"
)

# Estilos CSS con paleta institucional (Azul Marino #1A2B4C y Oro #C8A165)
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #1A2B4C;
        color: white;
    }
    h1, h2, h3 {
        color: #1A2B4C;
    }
    .login-card {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 12px;
        border: 2px solid #C8A165;
        text-align: center;
        max-width: 450px;
        margin: auto;
    }
    .stButton>button {
        background-color: #1A2B4C;
        color: #C8A165;
        font-weight: bold;
        border: 2px solid #C8A165;
        border-radius: 6px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #C8A165;
        color: #1A2B4C;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialización de estado de sesión y base de datos local
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'base_jugadores' not in st.session_state:
    st.session_state['base_jugadores'] = [
        {
            "Jugador": "Alisana Yirajang", "Posición": "Extremo Izquierdo", "Club": "Slovan", 
            "Edad": 21, "Valor": "€800k", "Contrato": "Dic 2026", "Score": 85, 
            "Viabilidad": "🔴 Baja (Europa)", "Agencia": "XYZ Sports",
            "Radar": [80, 75, 40, 85, 60],
            "Percentiles": {"xG (Goles Esperados)": 85, "Tiros a Puerta": 78, "Regates Exitosos %": 92, "Toques Área Rival": 65}
        }
    ]

if 'plantilla_agencia' not in st.session_state:
    st.session_state['plantilla_agencia'] = [
        {"Jugador": "José Juan Macías", "Posición": "Delantero Centro", "Club": "Pumas", "Categoría": "Primera División", "Estatus": "FIRMADO 🟡"},
        {"Jugador": "Oscar García", "Posición": "Portero", "Club": "León", "Categoría": "Primera División", "Estatus": "FIRMADO 🟡"},
        {"Jugador": "Kevin Mora", "Posición": "Lateral Izquierdo", "Club": "León", "Categoría": "Primera División", "Estatus": "FIRMADO 🟡"},
        {"Jugador": "Miguel Mendoza", "Posición": "Lateral Izquierdo", "Club": "León", "Categoría": "Sub-17", "Estatus": "FIRMADO 🟡"},
        {"Jugador": "Sergio Luna", "Posición": "Mediocentro", "Club": "León", "Categoría": "Sub-19", "Estatus": "FIRMADO 🟡"},
        {"Jugador": "Bryan Destin", "Posición": "Delantero Centro", "Club": "CT United", "Categoría": "Internacional", "Estatus": "OBJETIVO 🔵"}
    ]

# Función para dibujar el Radar Táctico
def generar_radar(jugador_nombre, valores_radar):
    categorias = ['Ataque', 'Creación', 'Defensa', 'Físico', 'Posesión']
    N = len(categorias)
    angulos = [n / float(N) * 2 * math.pi for n in range(N)]
    angulos += angulos[:1]
    
    valores = valores_radar + valores_radar[:1]
    
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    plt.xticks(angulos[:-1], categorias, color='#1A2B4C', size=10, weight='bold')
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="#888888", size=8)
    plt.ylim(0, 100)
    
    ax.plot(angulos, valores, linewidth=2, linestyle='solid', color='#1A2B4C')
    ax.fill(angulos, valores, color='#C8A165', alpha=0.4)
    fig.patch.set_facecolor('white')
    return fig

# -------------------------------------------------------------
# PANTALLA 1: LOGIN
# -------------------------------------------------------------
if not st.session_state['logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="login-card">
            <h1 style="color: #1A2B4C; margin: 0; font-size: 32px;">CG</h1>
            <h4 style="color: #C8A165; margin-top: 5px; font-weight: bold;">SCOUTING PRO</h4>
            <p style="color: #888888; font-size: 13px;">Dirección Deportiva & Scouting Institucional</p>
            <hr style="border-color: #C8A165; margin: 15px 0;">
            <p style="color: #1A2B4C; font-weight: bold;">Bienvenido, Christian González</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR AL SISTEMA"):
            if usuario.lower() == "christian" and password == "1234":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

# -------------------------------------------------------------
# PANTALLA 2: DASHBOARD Y MÓDULOS INTERNOS
# -------------------------------------------------------------
else:
    with st.sidebar:
        st.markdown("<h2 style='color: #C8A165; text-align: center;'>CG</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: white; text-align: center; font-weight: bold;'>SCOUTING PRO</p>", unsafe_allow_html=True)
        st.write("---")
        
        opcion = st.radio(
            "Navegación Main",
            ["Jugadores (Dashboard)", "+ Añadir Jugador", "Mi Plantilla", "Shortlists", "Comparador", "Scoring por Perfil"]
        )
        
        st.write("---")
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.rerun()

    # MÓDULO 1: DASHBOARD GENERAL
    if opcion == "Jugadores (Dashboard)":
        st.title("Base de Datos de Jugadores")
        st.caption("Panel de Inteligencia de Mercado y Scouting")
        
        busqueda = st.text_input("🔍 Buscar por nombre, club o posición...", "")
        df = pd.DataFrame(st.session_state['base_jugadores'])
        
        # Filtro de búsqueda
        if busqueda and not df.empty:
            df = df[
                df['Jugador'].str.contains(busqueda, case=False) |
                df['Club'].str.contains(busqueda, case=False) |
                df['Posición'].str.contains(busqueda, case=False)
            ]
            
        columnas_visibles = ["Jugador", "Posición", "Club", "Edad", "Valor", "Contrato", "Score", "Viabilidad"]
        st.dataframe(df[columnas_visibles], use_container_width=True, hide_index=True)
        
        st.write("---")
        st.subheader("👤 Ver Perfil de Jugador")
        nombres = [j["Jugador"] for j in st.session_state['base_jugadores']]
        seleccionado = st.selectbox("Selecciona un jugador para ver su radiografía táctica:", nombres)
        
        jugador_data = next(j for j in st.session_state['base_jugadores'] if j["Jugador"] == seleccionado)
        
        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            st.markdown(f"### **{jugador_data['Jugador']}**")
            st.write(f"**Posición:** {jugador_data['Posición']}")
            st.write(f"**Club Actual:** {jugador_data['Club']}")
            st.write(f"**Edad:** {jugador_data['Edad']} años")
            st.write(f"**Valor Estimado:** {jugador_data['Valor']}")
            st.write(f"**Fin de Contrato:** {jugador_data['Contrato']}")
            st.write(f"**Viabilidad de Fichaje:** {jugador_data['Viabilidad']}")
            st.write(f"**Agencia:** {jugador_data.get('Agencia', 'N/D')}")
            
        with col_m2:
            st.markdown("### **Radiografía Táctica**")
            fig = generar_radar(jugador_data['Jugador'], jugador_data['Radar'])
            st.pyplot(fig)

        st.markdown("### **Percentiles de Rendimiento (vs Liga p/90 mins)**")
        for metrica, p_val in jugador_data['Percentiles'].items():
            st.write(f"**{metrica}:** p{p_val}")
            st.progress(p_val / 100)

    # MÓDULO 2: FORMULARIO PARA AÑADIR JUGADOR
    elif opcion == "+ Añadir Jugador":
        st.title("➕ Registrar Nuevo Jugador en la Base de Datos")
        st.caption("Ingresa la información biográfica, de mercado y métricas calculadas.")
        
        with st.form("nuevo_jugador_form"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                nombre = st.text_input("Nombre Completo del Jugador")
                posicion = st.selectbox("Posición Principal", ["Portero", "Defensas Centrales", "Laterales", "Pivotes", "Mediocentros", "MCO", "Extremos", "Delanteros"])
                club = st.text_input("Club Actual")
                edad = st.number_input("Edad", min_value=15, max_value=45, value=20)
                agencia = st.text_input("Agencia Representante")
            with col_f2:
                valor = st.text_input("Valor de Mercado Estimado (ej. €1.5M)")
                contrato = st.text_input("Fin de Contrato (ej. Dic 2026)")
                viabilidad = st.selectbox("Viabilidad de Fichaje", ["🟢 Alta", "🟡 Media", "🔴 Baja (Europa / Inalcanzable)"])
                score = st.slider("Score General (1-100)", 1, 100, 75)
            
            st.markdown("---")
            st.subheader("🎯 Valores de Radar Táctico (0 a 100)")
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                r_ataque = st.slider("Ataque", 0, 100, 50)
                r_creacion = st.slider("Creación", 0, 100, 50)
            with col_r2:
                r_defensa = st.slider("Defensa", 0, 100, 50)
                r_fisico = st.slider("Físico", 0, 100, 50)
            with col_r3:
                r_posesion = st.slider("Posesión", 0, 100, 50)
                
            submitted = st.form_submit_button("Guardar Jugador en Base de Datos")
            
            if submitted:
                nuevo_dict = {
                    "Jugador": nombre, "Posición": posicion, "Club": club,
                    "Edad": edad, "Valor": valor, "Contrato": contrato, "Score": score,
                    "Viabilidad": viabilidad, "Agencia": agencia,
                    "Radar": [r_ataque, r_creacion, r_defensa, r_fisico, r_posesion],
                    "Percentiles": {"Métrica Clave 1": 70, "Métrica Clave 2": 80}
                }
                st.session_state['base_jugadores'].append(nuevo_dict)
                st.success(f"¡{nombre} guardado exitosamente en tu Base de Datos!")

    # MÓDULO 3: MI PLANTILLA
    elif opcion == "Mi Plantilla":
        st.title("💼 Mi Plantilla (Gestión de Agencia)")
        st.caption("Jugadores representados y prospectos bajo seguimiento directo.")
        
        df_p = pd.DataFrame(st.session_state['plantilla_agencia'])
        st.dataframe(df_p, use_container_width=True, hide_index=True)

    else:
        st.info(f"Módulo de **{opcion}** listo para conectar.")
