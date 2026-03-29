import streamlit as st
import pandas as pd

st.set_page_config(page_title="IEP Clases - NBA Dashboard", layout="centered")

st.title("🏀 IEP Clases: Dashboard")

# --- CONFIGURACIÓN ---
sheet_id = "1veVCpGuCSL5GnCBLs-Anc7oSEDbGPPkSHVaVyKMTc54"

@st.cache_data(ttl=10) # Tiempo corto para ver cambios rápido
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        data = pd.read_csv(url)
        data.columns = data.columns.str.strip() # Limpiar espacios
        return data
    except Exception as e:
        st.error(f"Error cargando {sheet_name}: {e}")
        return None

# Intentar cargar tablas
df_clases = load_sheet("Registro_Clases")
df_profes = load_sheet("Profesores")

# --- MODO DIAGNÓSTICO ---
if df_profes is not None:
    # Buscamos las columnas de forma segura
    cols_encontradas = df_profes.columns.tolist()
    
    col_profe_list = [c for c in cols_encontradas if 'profesor' in c.lower()]
    col_pin_list = [c for c in cols_encontradas if 'pin' in c.lower()]

    if not col_profe_list or not col_pin_list:
        st.warning("⚠️ Problema de columnas en la pestaña 'Profesores'")
        st.write("Columnas detectadas actualmente:", cols_encontradas)
        st.info("Asegúrate de que la primera fila de tu Excel tenga los nombres: 'Profesor' y 'PIN'")
        st.stop() # Detiene la app aquí para que veamos el error
    
    col_profe = col_profe_list[0]
    col_pin = col_pin_list[0]
    
    # --- LOGIN ---
    profesores_lista = df_profes[col_profe].unique()
    nombre_profe = st.selectbox("Selecciona tu nombre:", ["---"] + list(profesores_lista))

    if nombre_profe != "---":
        pin_ingresado = st.text_input("Introduce tu PIN:", type="password")
        
        # Validar
        fila_profe = df_profes[df_profes[col_profe] == nombre_profe]
        pin_correcto = str(fila_profe[col_pin].values[0])

        if pin_ingresado == pin_correcto:
            st.success(f"¡Bienvenido!")
            
            # FILTRAR DATOS
            # (Buscamos columna monto y horas en la otra tabla)
            col_m_list = [c for c in df_clases.columns if 'monto' in c.lower()]
            col_h_list = [c for c in df_clases.columns if 'horas' in c.lower()]
            
            if col_m_list and col_h_list:
                c_m = col_m_list[0]
                c_h = col_h_list[0]
                
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
        elif pin_ingresado != "":
            st.error("PIN incorrecto.")
else:
    st.error("No se pudo leer la pestaña 'Profesores'. ¿La creaste con ese nombre exacto?")
