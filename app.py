import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(
    page_title="Scouting Pro - Christian González",
    page_icon="⚽",
    layout="wide"
)

# Estilos CSS con tus colores oficiales (Azul Marino #1A2B4C y Oro #C8A165)
st.markdown("""
    <style>
    /* Estilo del menú lateral */
    [data-testid="stSidebar"] {
        background-color: #1A2B4C;
        color: white;
    }
    /* Estilo de los encabezados */
    h1, h2, h3 {
        color: #1A2B4C;
    }
    /* Tarjeta de Login */
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

# Manejo de Estado de Sesión (Login)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# -------------------------------------------------------------
# PANTALLA 1: LOGIN DE ACCESO
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
# PANTALLA 2: DASHBOARD PRINCIPAL (SISTEMA INTERNO)
# -------------------------------------------------------------
else:
    # Sidebar / Menú Lateral
    with st.sidebar:
        st.markdown("<h2 style='color: #C8A165; text-align: center;'>CG</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: white; text-align: center; font-weight: bold;'>SCOUTING PRO</p>", unsafe_allow_html=True)
        st.write("---")
        
        opcion = st.radio(
            "Navegación Main",
            ["Jugadores (Dashboard)", "Mi Plantilla", "Shortlists", "Comparador", "Scoring por Perfil"]
        )
        
        st.write("---")
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.rerun()

    # Área Principal
    st.title("Base de Datos de Jugadores")
    st.caption("Panel de Inteligencia de Mercado y Scouting")

    if opcion == "Jugadores (Dashboard)":
        # Barra de Búsqueda
        busqueda = st.text_input("🔍 Buscar por nombre, club o posición...", "")
        
        # Datos de prueba
        raw_data = [
            {"Jugador": "Alisana Yirajang", "Posición": "Extremo Izq.", "Club": "Slovan", "Edad": 21, "Valor": "€800k", "Contrato": "Dic 2026", "Score": 85, "Viabilidad": "🔴 Baja (Europa)"},
            {"Jugador": "Juan Escobar", "Posición": "Defensa Cen.", "Club": "Toluca", "Edad": 29, "Valor": "€2.5M", "Contrato": "Jun 2025", "Score": 90, "Viabilidad": "🟢 Alta"},
            {"Jugador": "Ramón Juárez", "Posición": "Defensa Cen.", "Club": "América", "Edad": 23, "Valor": "€3.0M", "Contrato": "Dic 2027", "Score": 88, "Viabilidad": "🟡 Media"},
            {"Jugador": "Santiago Giménez", "Posición": "Delantero", "Club": "Feyenoord", "Edad": 23, "Valor": "€40.0M", "Contrato": "Jun 2028", "Score": 95, "Viabilidad": "🔴 Baja"},
            {"Jugador": "Fidel Ambriz", "Posición": "Pivote", "Club": "Monterrey", "Edad": 21, "Valor": "€4.5M", "Contrato": "Dic 2028", "Score": 87, "Viabilidad": "🟡 Media"}
        ]
        
        df = pd.DataFrame(raw_data)
        
        # Filtro de Búsqueda
        if busqueda:
            df = df[
                df['Jugador'].str.contains(busqueda, case=False) |
                df['Club'].str.contains(busqueda, case=False) |
                df['Posición'].str.contains(busqueda, case=False)
            ]
            
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif opcion == "Mi Plantilla":
        st.subheader("💼 Mi Plantilla (Gestión de Agencia)")
        st.caption("Jugadores representados y prospectos bajo seguimiento directo.")
        
        plantilla_data = [
            {"Jugador": "José Juan Macías", "Posición": "Delantero Centro", "Club": "Pumas", "Categoría": "Primera División", "Estatus": "FIRMADO 🟡"},
            {"Jugador": "Oscar García", "Posición": "Portero", "Club": "León", "Categoría": "Primera División", "Estatus": "FIRMADO 🟡"},
            {"Jugador": "Kevin Mora", "Posición": "Lateral Izquierdo", "Club": "León", "Categoría": "Primera División", "Estatus": "FIRMADO 🟡"},
            {"Jugador": "Miguel Mendoza", "Posición": "Lateral Izquierdo", "Club": "León", "Categoría": "Sub-17", "Estatus": "FIRMADO 🟡"},
            {"Jugador": "Sergio Luna", "Posición": "Mediocentro", "Club": "León", "Categoría": "Sub-19", "Estatus": "FIRMADO 🟡"},
            {"Jugador": "Bryan Destin", "Posición": "Delantero Centro", "Club": "CT United", "Categoría": "Internacional", "Estatus": "OBJETIVO 🔵"}
        ]
        
        df_p = pd.DataFrame(plantilla_data)
        st.dataframe(df_p, use_container_width=True, hide_index=True)

    else:
        st.info(f"Módulo de **{opcion}** listo para conectar con la Base de Datos.")
