import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Scouting Pro - Christian González",
    page_icon="⚽",
    layout="centered"
)

# Estilos visuales en Azul Marino y Oro
st.markdown("""
    <style>
    .stApp {
        background-color: #1A2B4C;
        color: white;
    }
    .main-card {
        background-color: #FFFFFF;
        padding: 40px;
        border-radius: 15px;
        border: 2px solid #C8A165;
        color: #333333;
        text-align: center;
    }
    .stButton>button {
        background-color: #1A2B4C;
        color: #C8A165;
        font-weight: bold;
        border: 2px solid #C8A165;
        border-radius: 8px;
        width: 100%;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #C8A165;
        color: #1A2B4C;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown("""
    <div class="main-card">
        <h1 style="color: #1A2B4C; margin-bottom: 0;">SCOUTING PRO</h1>
        <p style="color: #888888; font-size: 14px;">Dirección Deportiva & Scouting Institucional</p>
        <hr style="border-color: #C8A165; margin-bottom: 25px;">
        <h3 style="color: #1A2B4C;">Bienvenido, Christian González</h3>
    </div>
""", unsafe_allow_html=True)

st.write("")

# Formulario
usuario = st.text_input("Usuario / Correo Electrónico")
password = st.text_input("Contraseña", type="password")

if st.button("INGRESAR AL SISTEMA"):
    if usuario == "christian" and password == "1234":
        st.success("¡Acceso concedido! Cargando Dashboard...")
    else:
        st.error("Credenciales incorrectas")
