import streamlit as st
import pandas as pd

st.set_page_config(page_title="IEP Clases - NBA Dashboard", layout="centered")

st.title("🏀 IEP Clases: Dashboard del Profe")

# --- CONFIGURACIÓN DE CONEXIÓN ---
sheet_id = "1veVCpGuCSL5GnCBLs-Anc7oSEDbGPPkSHVaVyKMTc54"

@st.cache_data(ttl=600)
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url)
    except:
        return None

# Cargar ambas tablas
df_clases = load_sheet("Registro_Clases")
df_profes = load_sheet("Profesores")

if df_clases is not None and df_profes is not None:
    # 1. LOGIN
    profesores_lista = df_profes["Profesor"].unique()
    nombre_profe = st.selectbox("Selecciona tu nombre:", ["---"] + list(profesores_lista))

    if nombre_profe != "---":
        pin_ingresado = st.text_input("Introduce tu PIN de seguridad:", type="password")
        
        # Obtener el PIN correcto desde el Excel
        pin_correcto = str(df_profes[df_profes["Profesor"] == nombre_profe]["PIN"].values[0])

        if pin_ingresado == pin_correcto:
            st.success(f"¡Bienvenido, {nombre_profe}!")
            
            # 2. FILTRAR Y CALCULAR
            profe_df = df_clases[df_clases["Profesor"] == nombre_profe].copy()
            profe_df["Monto cobrado ($)"] = pd.to_numeric(profe_df["Monto cobrado ($)"], errors='coerce').fillna(0)
            
            pago_neto = profe_df["Monto cobrado ($)"].sum() * 0.55
            escrow = profe_df["Monto cobrado ($)"].sum() * 0.05
            total_horas = profe_df["Horas"].sum()

            # 3. DASHBOARD
            col1, col2, col3 = st.columns(3)
            col1.metric("Mis Ganancias", f"${pago_neto:,.2f}")
            col2.metric("Bono Escrow", f"${escrow:,.2f}")
            col3.metric("Horas Totales", f"{total_horas}h")

            st.divider()
            st.subheader("Historial de Clases")
            st.dataframe(profe_df[["Fecha", "Alumno", "Monto cobrado ($)", "Horas", "Estatus de Pago"]], use_container_width=True)
            
        elif pin_ingresado != "":
            st.error("PIN incorrecto. Inténtalo de nuevo.")
else:
    st.error("Error al conectar con la base de datos. Verifica la pestaña 'Profesores'.")
