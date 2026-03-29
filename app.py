import streamlit as st
import pandas as pd

st.set_page_config(page_title="IEP Clases - NBA Dashboard", layout="centered", page_icon="🏀")

# --- ESTILO VISUAL PERSONALIZADO ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_content_html=True)

# --- ENCABEZADO CON LOGO ---
# Si tienes un link de imagen de tu logo, ponlo acá. Si no, queda el texto.
logo_url = "https://tu-sitio.com/logo.png" 
try:
    # st.image(logo_url, width=150) # Descomenta esto cuando tengas el link del logo
    st.title("🏀 IEP Clases")
    st.subheader("Panel de Control del Staff")
except:
    st.title("🏀 IEP Clases")

# --- EL RESTO DEL CÓDIGO (Igual al anterior con pequeñas mejoras de texto) ---
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
    profesores_lista = df_profes["Profesor"].unique()
    nombre_profe = st.selectbox("Identifícate, Coach:", ["---"] + list(profesores_lista))

    if nombre_profe != "---":
        pin_ingresado = st.text_input("Introduce tu PIN de acceso:", type="password")
        
        fila_profe = df_profes[df_profes["Profesor"] == nombre_profe]
        pin_correcto = str(fila_profe["PIN"].values[0]).replace('.0', '').strip()

        if pin_ingresado.strip() == pin_correcto:
            st.balloons() # ¡Efecto de celebración al entrar!
            st.success(f"Hola {nombre_profe}, ¡buen trabajo esta semana!")
            
            p_df = df_clases[df_clases["Profesor"] == nombre_profe].copy()
            
            col_neto = "Pago Neto Profe (55%)"
            col_escrow = "Fondo Escrow (5%)"
            col_horas = "Horas"
            col_estatus = "Estatus de Pago"

            p_df[col_neto] = pd.to_numeric(p_df[col_neto], errors='coerce').fillna(0)
            p_df[col_escrow] = pd.to_numeric(p_df[col_escrow], errors='coerce').fillna(0)
            p_df[col_horas] = pd.to_numeric(p_df[col_horas], errors='coerce').fillna(0)

            mask_pendiente = (p_df[col_estatus].isna()) | (p_df[col_estatus].astype(str).str.strip() == "") | (p_df[col_estatus].astype(str).str.contains('Pendiente', case=False))
            solo_pendientes = p_df[mask_pendiente]
            
            p_neto_total = solo_pendientes[col_neto].sum()
            escrow_total = solo_pendientes[col_escrow].sum()
            total_horas = solo_pendientes[col_horas].sum()

            # Métricas con nombres más amigables
            col1, col2, col3 = st.columns(3)
            col1.metric("A cobrar el Lunes", f"${p_neto_total:,.2f}")
            col2.metric("Ahorro Escrow", f"${escrow_total:,.2f}")
            col3.metric("Horas Dictadas", f"{total_horas}h")

            st.divider()
            st.subheader("📖 Tu Historial Reciente")
            columnas_ver = ["Fecha", "Alumno", "Horas", col_neto, col_estatus]
            columnas_reales = [c for c in columnas_ver if c in p_df.columns]
            st.dataframe(p_df[columnas_reales].tail(10), use_container_width=True)

            st.divider()
            url_form = "TU_LINK_DE_GOOGLE_FORM_AQUI"
            st.link_button("📝 Registrar Nueva Clase", url_form, use_container_width=True, type="primary")
            
        elif pin_ingresado != "":
            st.error("PIN incorrecto. Revisa tus datos.")
else:
    st.error("Error de conexión. Intenta refrescar.")

if st.sidebar.button("🔄 Sincronizar Excel"):
    st.cache_data.clear()
    st.rerun()



