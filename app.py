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

df_clases = load_sheet("Registro_Clases")
df_profes = load_sheet("Profesores")

if df_clases is not None and df_profes is not None:
    profesores_lista = df_profes["Profesor"].unique()
    nombre_profe = st.selectbox("Selecciona tu nombre:", ["---"] + list(profesores_lista))

    if nombre_profe != "---":
        pin_ingresado = st.text_input("Introduce tu PIN:", type="password")
        
        fila_profe = df_profes[df_profes["Profesor"] == nombre_profe]
        pin_correcto = str(fila_profe["PIN"].values[0]).replace('.0', '').strip()

        if pin_ingresado.strip() == pin_correcto:
            st.success("¡Bienvenido!")
            
            p_df = df_clases[df_clases["Profesor"] == nombre_profe].copy()
            p_df["Monto cobrado ($)"] = pd.to_numeric(p_df["Monto cobrado ($)"], errors='coerce').fillna(0)
            
            p_neto = p_df["Monto cobrado ($)"].sum() * 0.55
            escrow = p_df["Monto cobrado ($)"].sum() * 0.05
            t_horas = p_df["Horas"].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Mis Ganancias", f"${p_neto:,.2f}")
            col2.metric("Bono Escrow", f"${escrow:,.2f}")
            col3.metric("Horas Totales", f"{t_horas}h")

            st.divider()
            st.subheader("Tu historial de clases")
            st.dataframe(p_df, use_container_width=True)

            # --- BOTÓN REGISTRO (Corregido para evitar el TypeError) ---
            st.divider()
            st.subheader("📝 Gestión de Clases")
            
            url_form = "TU_LINK_DE_GOOGLE_FORM_AQUI" # <--- PEGA TU LINK ACÁ
            
            # Usamos un link de Streamlit nativo que es más seguro
            st.link_button("➕ Registrar Nueva Clase", url_form, use_container_width=True, type="primary")
            
            st.info("Al terminar de registrar, refresca esta página para ver tus números actualizados.")
        
        elif pin_ingresado != "":
            st.error("PIN incorrecto.")
else:
    st.error("Error de conexión con el Excel.")

if st.button("🔄 Actualizar datos"):
    st.cache_data.clear()
    st.rerun()

