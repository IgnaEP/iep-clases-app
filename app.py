import streamlit as st
import pandas as pd

st.set_page_config(page_title="IEP Clases - NBA Dashboard", layout="centered")

st.title("🏀 IEP Clases: Dashboard")

# --- CONFIGURACIÓN ---
sheet_id = "1veVCpGuCSL5GnCBLs-Anc7oSEDbGPPkSHVaVyKMTc54"

@st.cache_data(ttl=10)
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        data = pd.read_csv(url)
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        return None

# Intentar cargar tablas
df_clases = load_sheet("Registro_Clases")
df_profes = load_sheet("Profesores")

if df_profes is not None:
    cols_encontradas = df_profes.columns.tolist()
    col_profe_list = [c for c in cols_encontradas if 'profesor' in c.lower()]
    col_pin_list = [c for c in cols_encontradas if 'pin' in c.lower()]

    if not col_profe_list or not col_pin_list:
        st.warning("⚠️ Problema de columnas en la pestaña 'Profesores'")
        st.stop() 
    
    col_profe = col_profe_list[0]
    col_pin = col_pin_list[0]
    
    # --- LOGIN ---
    profesores_lista = df_profes[col_profe].unique()
    nombre_profe = st.selectbox("Selecciona tu nombre:", ["---"] + list(profesores_lista))

    if nombre_profe != "---":
        pin_ingresado = st.text_input("Introduce tu PIN:", type="password")
        
        # Validar PIN (Limpieza de decimales por si acaso)
        fila_profe = df_profes[df_profes[col_profe] == nombre_profe]
        pin_correcto = str(fila_profe[col_pin].values[0]).replace('.0', '').strip()

        if pin_ingresado == pin_correcto:
            st.success(f"¡Bienvenido, {nombre_profe}!")
            
            # --- FILTRAR Y MOSTRAR DATOS ---
            col_m_list = [c for c in df_clases.columns if 'monto' in c.lower()]
            col_h_list = [c for c in df_clases.columns if 'horas' in c.lower()]
            
            if col_m_list and col_h_list:
                c_m, c_h = col_m_list[0], col_h_list[0]
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
                st.subheader("Tu historial de clases")
                st.dataframe(p_df, use_container_width=True)

                # --- BOTÓN DE REGISTRO (Dentro del login exitoso) ---
                st.divider()
                st.subheader("📝 Gestión de Clases")
                
                # REEMPLAZA ESTE LINK
                url_formulario = "https://docs.google.com/forms/d/e/1FAIpQLSfjvI1e0--e36nmtT8gNQy1kT_fzG7LQP_ZsrLu0AKcuJ7NvQ/viewform?usp=header"
                
                st.markdown(f"""
                    <a href="{url_formulario}" target="_blank">
                        <button style="
                            width: 100%;
                            background-color: #f63366;
                            color: white;
                            padding: 15px;
                            border: none;
                            border-radius: 10px;
                            font-size: 18px;
                            cursor: pointer;
                            font-weight: bold;">
                            ➕ Registrar Nueva Clase
                        </button>
                    </a>
                """, unsafe_allow_content_html=True)
                
                st.info("Al terminar de registrar, refresca esta página para ver tus números actualizados.")
        
        elif pin_ingresado != "":
            st.error("PIN incorrecto.")
else:
    st.error("No se pudo leer la base de datos.")
