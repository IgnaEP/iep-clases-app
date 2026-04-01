import streamlit as st
import pandas as pd

# Configuración básica (Sin CSS externo para evitar errores)
st.set_page_config(page_title="IEP Clases - NBA Dashboard", layout="centered", page_icon="🏀")

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

# Cargar tablas
df_clases = load_sheet("Registro_Clases")
df_profes = load_sheet("Profesores")

if df_clases is not None and df_profes is not None:
    # --- LOGIN ---
    profesores_lista = df_profes["Profesor"].unique()
    nombre_profe = st.selectbox("Identifícate, Coach:", ["---"] + list(profesores_lista))

    if nombre_profe != "---":
        pin_ingresado = st.text_input("Introduce tu PIN de acceso:", type="password")
        
        # Validar PIN
        fila_profe = df_profes[df_profes["Profesor"] == nombre_profe]
        pin_correcto = str(fila_profe["PIN"].values[0]).replace('.0', '').strip()

        if pin_ingresado.strip() == pin_correcto:
            st.balloons()
            st.success(f"Hola {nombre_profe}, ¡bienvenido!")
            
            # --- PROCESAMIENTO DE DATOS ---
            p_df = df_clases[df_clases["Profesor"] == nombre_profe].copy()
            
            # Nombres exactos de tu Excel (Captura 3184ba.png)
            col_neto = "Pago Neto Profe (55%)"
            col_escrow = "Fondo Escrow (5%)"
            col_horas = "Horas"
            col_estatus = "Estatus de Pago"

            # Limpiar columnas numéricas
            for col in [col_neto, col_escrow, col_horas]:
                if col in p_df.columns:
                    p_df[col] = pd.to_numeric(p_df[col], errors='coerce').fillna(0)

            # Filtro de Pendientes (Captura ffb10a.png)
            # Consideramos pendiente si la celda está vacía o no dice "Pagado"
            if col_estatus in p_df.columns:
                mask_pendiente = (p_df[col_estatus].isna()) | (p_df[col_estatus].astype(str).str.strip() == "") | (~p_df[col_estatus].astype(str).str.contains('Pagado', case=False))
                solo_pendientes = p_df[mask_pendiente]
            else:
                solo_pendientes = p_df

            # --- DASHBOARD ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("A cobrar Lunes", f"${solo_pendientes[col_neto].sum():,.2f}")
            with col2:
                st.metric("Ahorro Escrow", f"${solo_pendientes[col_escrow].sum():,.2f}")
            with col3:
                st.metric("Horas Totales", f"{solo_pendientes[col_horas].sum()}h")

            st.divider()
            st.subheader("📖 Tu Historial Reciente")
            
            # Mostrar tabla (Captura 3184ba.png)
            columnas_mostrar = ["Fecha", "Alumno", "Horas", col_neto, col_estatus]
            columnas_reales = [c for c in columnas_mostrar if c in p_df.columns]
            st.dataframe(p_df[columnas_reales].tail(10), use_container_width=True)

            st.divider()
            # Botón de Registro (Simple y directo)
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSfjvI1e0--e36nmtT8gNQy1kT_fzG7LQP_ZsrLu0AKcuJ7NvQ/viewform?usp=header" 
            st.link_button("➕ Registrar Nueva Clase", url_form, use_container_width=True, type="primary")
            
        elif pin_ingresado != "":
            st.error("PIN incorrecto. Revisa tus datos.")
else:
    st.error("Error de conexión. Verifica que el Excel sea público y las pestañas existan.")

# Sincronización en la barra lateral
with st.sidebar:
    if st.button("🔄 Sincronizar Datos"):
        st.cache_data.clear()
        st.rerun()
