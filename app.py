import streamlit as st
import pandas as pd

st.set_page_config(page_title="IEP Clases - NBA Dashboard", layout="centered")

st.title("🏀 IEP Clases: Dashboard del Profe")

# --- CONFIGURACIÓN DE CONEXIÓN ---
sheet_id = "1veVCpGuCSL5GnCBLs-Anc7oSEDbGPPkSHVaVyKMTc54"

@st.cache_data(ttl=60) # Bajamos el tiempo a 1 min para probar rápido
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        data = pd.read_csv(url)
        # ESTO LIMPIA LOS NOMBRES DE LAS COLUMNAS (Quita espacios y pone minúsculas)
        data.columns = data.columns.str.strip()
        return data
    except:
        return None

# Cargar tablas
df_clases = load_sheet("Registro_Clases")
df_profes = load_sheet("Profesores")

if df_clases is not None and df_profes is not None:
    # 1. LOGIN (Usamos "Profesor" con P mayúscula porque lo normalizamos abajo si hace falta)
    # Pero para estar seguros, buscamos la columna que se parezca a 'profesor'
    col_profe = [c for c in df_profes.columns if 'profesor' in c.lower()][0]
    col_pin = [c for c in df_profes.columns if 'pin' in c.lower()][0]
    
    profesores_lista = df_profes[col_profe].unique()
    nombre_profe = st.selectbox("Selecciona tu nombre:", ["---"] + list(profesores_lista))

    if nombre_profe != "---":
        pin_ingresado = st.text_input("Introduce tu PIN de seguridad:", type="password")
        
        # Validar PIN
        fila_profe = df_profes[df_profes[col_profe] == nombre_profe]
        pin_correcto = str(fila_profe[col_pin].values[0])

        if pin_ingresado == pin_correcto:
            st.success(f"¡Bienvenido, {nombre_profe}!")
            
            # 2. FILTRAR Y CALCULAR (Buscamos la columna del monto dinámicamente)
            col_monto = [c for c in df_clases.columns if 'monto' in c.lower()][0]
            col_horas = [c for c in df_clases.columns if 'horas' in c.lower()][0]
            
            profe_df = df_clases[df_clases[col_profe] == nombre_profe].copy()
            profe_df[col_monto] = pd.to_numeric(profe_df[col_monto], errors='coerce').fillna(0)
            
            pago_neto = profe_df[col_monto].sum() * 0.55
            escrow = profe_df[col_monto].sum() * 0.05
            total_horas = profe_df[col_horas].sum()

            # 3. DASHBOARD
            col1, col2, col3 = st.columns(3)
            col1.metric("Mis Ganancias", f"${pago_neto:,.2f}")
            col2.metric("Bono Escrow", f"${escrow:,.2f}")
            col3.metric("Horas Totales", f"{total_horas}h")

            st.divider()
            st.subheader("Historial de Clases")
            st.dataframe(profe_df, use_container_width=True)
            
        elif pin_ingresado != "":
            st.error("PIN incorrecto.")
else:
    st.error("No se pudo leer la pestaña 'Profesores'. Revisa el nombre en Google Sheets.")
