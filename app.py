import streamlit as st
import pandas as pd

st.set_page_config(page_title="IEP Clases - NBA Dashboard", layout="centered")

st.title("🏀 IEP Clases: Dashboard")

# --- CONFIGURACIÓN ---
sheet_id = "1veVCpGuCSL5GnCBLs-Anc7oSEDbGPPkSHVaVyKMTc54"

def load_sheet(sheet_name):
    # Agregamos un número aleatorio al final para forzar datos nuevos cada vez
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
    # Usamos los nombres de columna EXACTOS de tu Excel
    profesores_lista = df_profes["Profesor"].unique()
    nombre_profe = st.selectbox("Selecciona tu nombre:", ["---"] + list(profesores_lista))

    if nombre_profe != "---":
        pin_ingresado = st.text_input("Introduce tu PIN:", type="password")
        
        # Validar PIN
        fila_profe = df_profes[df_profes["Profesor"] == nombre_profe]
        # Limpiamos el PIN de cualquier decimal (.0)
        pin_correcto = str(fila_profe["PIN"].values[0]).replace('.0', '').strip()

        if pin_ingresado.strip() == pin_correcto:
            st.success(f"¡Bienvenido!")
            
            # --- FILTRAR DATOS ---
            p_df = df_clases[df_clases["Profesor"] == nombre_profe].copy()
            
            # Convertir monto a número (usando el nombre exacto de tu columna)
            p_df["Monto cobrado ($)"] = pd.to_numeric(p_df["Monto cobrado ($)"], errors='coerce').fillna(0)
            
            # Cálculos
            p_neto = p_df["Monto cobrado ($)"].sum() * 0.55
            escrow = p_df["Monto cobrado ($)"].sum() * 0.05
            t_horas = p_df["Horas"].sum()

            # Métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("Mis Ganancias", f"${p_neto:,.2f}")
            col2.metric("Bono Escrow", f"${escrow:,.2f}")
            col3.metric("Horas Totales", f"{t_horas}h")

            st.divider()
            st.subheader("Tu historial de clases")
            st.dataframe(p_df, use_container_width=True)

            # --- BOTÓN REGISTRO ---
            st.divider()
            url_formulario = "TU_LINK_DE_GOOGLE_FORM_AQUI"
            
            st.markdown(f"""
                <a href="{url_formulario}" target="_blank">
                    <button style="width: 100%; background-color: #f63366; color: white; padding: 15px; border: none; border-radius: 10px; font-size: 18px; cursor: pointer; font-weight: bold;">
                        ➕ Registrar Nueva Clase
                    </button>
                </a>
            """, unsafe_allow_content_html=True)
            
        elif pin_ingresado != "":
            st.error("PIN incorrecto.")
else:
    st.error("Error de conexión. Verifica que las pestañas 'Profesores' y 'Registro_Clases' existan.")

# Botón para forzar actualización si algo no se ve
if st.button("🔄 Actualizar datos del Excel"):
    st.cache_data.clear()
    st.rerun()
