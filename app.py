import streamlit as st
import pandas as pd

st.set_page_config(page_title="IEP Clases - NBA Dashboard", layout="centered")

st.title("🏀 IEP Clases: Dashboard")

# --- CONFIGURACIÓN ---
sheet_id = "1veVCpGuCSL5GnCBLs-Anc7oSEDbGPPkSHVaVyKMTc54"

# Función para cargar datos con bypass de caché
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        # Añadimos un parámetro aleatorio al final para forzar a Google a darnos datos frescos
        data = pd.read_csv(url)
        data.columns = [str(c).strip().lower() for c in data.columns] # Todo a minúsculas y sin espacios
        return data
    except:
        return None

# Cargar tablas
df_clases = load_sheet("Registro_Clases")
df_profes = load_sheet("Profesores")

if df_profes is not None and df_clases is not None:
    # Identificar columnas automáticamente
    try:
        col_profe = [c for c in df_profes.columns if 'profe' in c][0]
        col_pin = [c for c in df_profes.columns if 'pin' in c][0]
        
        # --- LOGIN ---
        profesores_lista = df_profes[col_profe].unique()
        nombre_profe = st.selectbox("Selecciona tu nombre:", ["---"] + list(profesores_lista))

        if nombre_profe != "---":
            pin_ingresado = st.text_input("Introduce tu PIN:", type="password")
            
            # Obtener PIN correcto
            fila_profe = df_profes[df_profes[col_profe] == nombre_profe]
            pin_correcto = str(fila_profe[col_pin].values[0]).replace('.0', '').strip()

            if pin_ingresado.strip() == pin_correcto:
                st.success(f"¡Bienvenido!")
                
                # --- DATOS ---
                c_m = [c for c in df_clases.columns if 'monto' in c][0]
                c_h = [c for c in df_clases.columns if 'horas' in c][0]
                
                p_df = df_clases[df_clases[col_profe] == nombre_profe].copy()
                p_df[c_m] = pd.to_numeric(p_df[c_m], errors='coerce').fillna(0)
                
                p_neto = p_df[c_m].sum() * 0.55
                escrow = p_df[c_m].sum() * 0.05
                t_horas = p_df[c_h].sum()

                col1, col2, col3 = st.columns(3)
                col1.metric("Mis Ganancias", f"${p_neto:,.2f}")
                col2.metric("Bono Escrow", f"${escrow:,.2f}")
                col3.metric("Horas Totales", f"{t_horas}h")

                st.divider()
                st.dataframe(p_df, use_container_width=True)

                # --- BOTÓN REGISTRO ---
                st.divider()
                url_formulario = "TU_LINK_AQUI" # <--- PEGA TU LINK ACÁ
                
                st.markdown(f"""
                    <a href="{url_formulario}" target="_blank">
                        <button style="width: 100%; background-color: #f63366; color: white; padding: 15px; border: none; border-radius: 10px; font-size: 18px; cursor: pointer; font-weight: bold;">
                            ➕ Registrar Nueva Clase
                        </button>
                    </a>
                """, unsafe_allow_content_html=True)
                
            elif pin_ingresado != "":
                st.error("PIN incorrecto.")
    except Exception as e:
        st.error("Error técnico: No se encuentran las columnas. Revisa los encabezados del Excel.")
else:
    st.error("No se pudo conectar con las pestañas del Excel.")
