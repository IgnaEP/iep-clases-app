import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="IEP Clases - NBA Dashboard", layout="centered", page_icon="🏀")

# --- DISEÑO (Separado para evitar el TypeError) ---
style = """
<style>
    .main { background-color: #f5f7f9; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #f0f2f6;
    }
</style>
"""
st.markdown(style, unsafe_allow_content_html=True)

st.title("🏀 IEP Clases")
st.subheader("Panel de Control del Staff")

# --- CONEXIÓN ---
sheet_id = "1veVCpGuCSL5GnCBLs-Anc7oSEDbGPPkSHVaVyKMTc54"

def load_sheet(sheet_name):
    import random
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}&refresh={random.randint(1,1000)}"
    try:
        data = pd.read_csv(url)
        return data
    except:
        return None

df_clases = load_sheet("Registro_Clases")
df_profes = load_sheet("Profesores")

if df_clases is not None and df_profes is not None:
    # --- LOGIN ---
    profesores_lista = df_profes["Profesor"].unique()
    nombre_profe = st.selectbox("Identifícate, Coach:", ["---"] + list(profesores_lista))

    if nombre_profe != "---":
        pin_ingresado = st.text_input("Introduce tu PIN de acceso:", type="password")
        
        fila_profe = df_profes[df_profes["Profesor"] == nombre_profe]
        pin_correcto = str(fila_profe["PIN"].values[0]).replace('.0', '').strip()

        if pin_ingresado.strip() == pin_correcto:
            st.balloons()
            st.success(f"Hola {nombre_profe}, ¡buen trabajo esta semana!")
            
            # --- DATOS ---
            p_df = df_clases[df_clases["Profesor"] == nombre_profe].copy()
            
            # Nombres exactos de tu Excel
            col_neto = "Pago Neto Profe (55%)"
            col_escrow = "Fondo Escrow (5%)"
            col_horas = "Horas"
            col_estatus = "Estatus de Pago"

            # Limpieza de números
            for col in [col_neto, col_escrow, col_horas]:
                p_df[col] = pd.to_numeric(p_df[col], errors='coerce').fillna(0)

            # Filtro de Pendientes (Vacío o que diga Pendiente)
            mask_pendiente = (p_df[col_estatus].isna()) | (p_df[col_estatus].astype(str).str.strip() == "") | (p_df[col_estatus].astype(str).str.contains('Pendiente', case=False))
            solo_pendientes = p_df[mask_pendiente]
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("A cobrar Lunes", f"${solo_pendientes[col_neto].sum():,.2f}")
            col2.metric("Ahorro Escrow", f"${solo_pendientes[col_escrow].sum():,.2f}")
            col3.metric("Horas Totales", f"{solo_pendientes[col_horas].sum()}h")

            st.divider()
            st.subheader("📖 Tu Historial Reciente")
            columnas_reales = [c for c in ["Fecha", "Alumno", "Horas", col_neto, col_estatus] if c in p_df.columns]
            st.dataframe(p_df[columnas_reales].tail(10), use_container_width=True)

            st.divider()
            # Botón de Registro
            url_form = "TU_LINK_AQUI" 
            st.link_button("📝 Registrar Nueva Clase", url_form, use_container_width=True, type="primary")
            
        elif pin_ingresado != "":
            st.error("PIN incorrecto. Revisa tus datos.")
else:
    st.error("Error de conexión. Intenta refrescar la página.")

# Sincronización en la barra lateral
if st.sidebar.button("🔄 Sincronizar Datos"):
    st.cache_data.clear()
    st.rerun()


