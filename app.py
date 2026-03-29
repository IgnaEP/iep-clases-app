import streamlit as st
import pandas as pd

st.set_page_config(page_title="IEP Clases - NBA Dashboard", layout="centered")

st.title("🏀 IEP Clases: Dashboard")

# --- CONFIGURACIÓN ---
sheet_id = "1veVCpGuCSL5GnCBLs-Anc7oSEDbGPPkSHVaVyKMTc54"

def load_sheet(sheet_name):
    import random
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}&refresh={random.randint(1,1000)}"
    try:
        data = pd.read_csv(url)
        return data
    except:
        return None

# Cargar tablas
df_clases = load_sheet("Registro_Clases")
df_profes = load_sheet("Profesores")

if df_clases is not None and df_profes is not None:
    # --- LOGIN ---
    profesores_lista = df_profes["Profesor"].unique()
    nombre_profe = st.selectbox("Selecciona tu nombre:", ["---"] + list(profesores_lista))

    if nombre_profe != "---":
        pin_ingresado = st.text_input("Introduce tu PIN:", type="password")
        
        # Validar PIN
        fila_profe = df_profes[df_profes["Profesor"] == nombre_profe]
        pin_correcto = str(fila_profe["PIN"].values[0]).replace('.0', '').strip()

        if pin_ingresado.strip() == pin_correcto:
            st.success("¡Bienvenido!")
            
            # --- FILTRAR Y MOSTRAR DATOS (Fragmento Nuevo) ---
            p_df = df_clases[df_clases["Profesor"] == nombre_profe].copy()
            
            # Nombres de columnas según tus capturas
            col_neto = "Pago Neto Profe (55%)"
            col_escrow = "Fondo Escrow (5%)"
            col_horas = "Horas"
            col_estatus = "Estatus de Pago"

            # Convertir a números
            p_df[col_neto] = pd.to_numeric(p_df[col_neto], errors='coerce').fillna(0)
            p_df[col_escrow] = pd.to_numeric(p_df[col_escrow], errors='coerce').fillna(0)
            p_df[col_horas] = pd.to_numeric(p_df[col_horas], errors='coerce').fillna(0)

            # Lógica de Pendientes (Suma si está vacío o dice Pendiente)
            mask_pendiente = (p_df[col_estatus].isna()) | (p_df[col_estatus].astype(str).str.strip() == "") | (p_df[col_estatus].astype(str).str.contains('Pendiente', case=False))
            solo_pendientes = p_df[mask_pendiente]
            
            p_neto_total = solo_pendientes[col_neto].sum()
            escrow_total = solo_pendientes[col_escrow].sum()
            total_horas = solo_pendientes[col_horas].sum()

            # Métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("Pendiente de Pago", f"${p_neto_total:,.2f}")
            col2.metric("Fondo Escrow", f"${escrow_total:,.2f}")
            col3.metric("Horas Totales", f"{total_horas}h")

            st.divider()
            st.subheader("Historial Completo")
            # Mostramos historial con las columnas que ya tienes
            columnas_ver = ["Fecha", "Alumno", "Horas", col_neto, col_estatus]
            # Solo mostramos columnas que realmente existan para evitar errores
            columnas_reales = [c for c in columnas_ver if c in p_df.columns]
            st.dataframe(p_df[columnas_reales], use_container_width=True)

            # --- BOTÓN REGISTRO ---
            st.divider()
            url_form = "TU_LINK_DE_GOOGLE_FORM_AQUI" # <--- ¡NO OLVIDES PEGAR TU LINK!
            st.link_button("➕ Registrar Nueva Clase", url_form, use_container_width=True, type="primary")
            
        elif pin_ingresado != "":
            st.error("PIN incorrecto.")
else:
    st.error("Error de conexión con el Excel.")

if st.button("🔄 Actualizar datos"):
    st.cache_data.clear()
    st.rerun()


