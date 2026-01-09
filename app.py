import streamlit as st
import pandas as pd

st.set_page_config(page_title="IEP Clases - NBA Dashboard", layout="centered")

st.title("🏀 IEP Clases: Dashboard del Profe")
st.markdown("Bienvenido a la Liga. Aquí puedes ver tus estadísticas.")

# --- MÉTODO ROBUSTO DE CONEXIÓN ---
# Extraemos el ID de tu hoja directamente
sheet_id = "1veVCpGuCSL5GnCBLs-Anc7oSEDbGPPkSHVaVyKMTc54"
sheet_name = "Registro_Clases"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data(ttl=600) # Se actualiza cada 10 minutos
def load_data(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

df = load_data(url)

if df is not None:
    # Limpieza de datos (basado en lo que vi en tu Sheet)
    df = df.dropna(subset=["Profesor"])
    df = df[df["Profesor"] != "0"]

    # LOGIN SIMPLE
    profesores_disponibles = df["Profesor"].unique()
    nombre_profe = st.selectbox("Selecciona tu nombre de la lista:", profesores_disponibles)

    if nombre_profe:
        # Filtrar datos por profe
        profe_df = df[df["Profesor"] == nombre_profe]
        
        # Procesar Monto (asegurando que sea número)
        profe_df["Monto cobrado ($)"] = pd.to_numeric(profe_df["Monto cobrado ($)"], errors='coerce').fillna(0)
        
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
        st.dataframe(profe_df[["Fecha", "Alumno", "Monto cobrado ($)", "Horas", "Estatus de Pago"]], use_container_width=True)
else:
    st.warning("No se pudieron cargar los datos. Verifica que la hoja sea pública.")
