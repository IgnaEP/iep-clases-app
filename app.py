import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="IEP Clases - NBA Dashboard", layout="centered")

st.title("🏀 IEP Clases: Dashboard del Profe")
st.markdown("Bienvenido a la Liga. Aquí puedes ver tus estadísticas.")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# CARGAR DATOS (He verificado que tu pestaña se llama Registro_Clases)
df = conn.read(worksheet="Registro_Clases")

# Limpieza: Eliminar filas vacías o con ceros que tienes al final de la hoja
df = df[df["Profesor"] != "0"]
df = df.dropna(subset=["Profesor"])

# LOGIN SIMPLE
profesores_disponibles = df["Profesor"].unique()
nombre_profe = st.selectbox("Selecciona tu nombre de la lista:", profesores_disponibles)

if nombre_profe:
    # Filtrar datos por profe
    profe_df = df[df["Profesor"] == nombre_profe]
    
    # AJUSTE DE COLUMNAS: Usamos "Monto cobrado ($)" que es el nombre real en tu Sheet
    # Convertimos a número por si acaso hay espacios
    profe_df["Monto cobrado ($)"] = pd.to_numeric(profe_df["Monto cobrado ($)"], errors='coerce')
    
    total_generado = profe_df["Monto cobrado ($)"].sum()
    pago_neto = total_generado * 0.55
    escrow = total_generado * 0.05
    total_horas = profe_df["Horas"].sum()

    # PANTALLA PRINCIPAL
    col1, col2, col3 = st.columns(3)
    col1.metric("Mis Ganancias (55%)", f"${pago_neto:,.2f}")
    col2.metric("Bono Escrow (5%)", f"${escrow:,.2f}")
    col3.metric("Horas Totales", f"{total_horas}h")

    st.divider()

    # HISTORIAL
    st.subheader("Historial de Clases")
    # Mostramos las columnas tal cual están en tu Excel
    st.dataframe(profe_df[["Fecha", "Alumno", "Monto cobrado ($)", "Horas", "Estatus de Pago"]], use_container_width=True)
