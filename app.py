# =============================================================================
# ARCHIVO PRINCIPAL ORQUESTADOR: app.py
# Objetivo: Conectar los 3 archivos modulares (1 archivo por cada pestaña):
#           - Pestaña 1 -> vista_resumen.py
#           - Pestaña 2 -> vista_diagnostico.py
#           - Pestaña 3 -> vista_asignacion.py
# =============================================================================
import streamlit as st
import pandas as pd
import estilos_ui
import vista_resumen
import vista_diagnostico
import vista_asignacion

# -----------------------------------------------------------------------------
# PARTE 1: Configuración de página panorámica y diseño UX/UI
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Gemelo Digital de Pricing",
    page_icon="💊",
    layout="wide"
)

estilos_ui.aplicar_estilos_globales()


# -----------------------------------------------------------------------------
# PARTE 2: Carga centralizada de los archivos de datos (Cuaderno 1 y Cuaderno 2)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def cargar_datos_repositorio():
    df_hist = pd.read_csv("resultados_motor_multisku.csv")
    df_dec = pd.read_csv("decision_t1_skus.csv")
    return df_hist, df_dec

try:
    df_trazabilidad, df_decision_t1 = cargar_datos_repositorio()
except Exception as e:
    st.error(f"⚠️ Error al leer los archivos CSV del repositorio: {e}")
    st.stop()


# -----------------------------------------------------------------------------
# PARTE 3: Cabecera Principal y 3 Pestañas (1 Archivo Python por Pestaña)
# -----------------------------------------------------------------------------
estilos_ui.renderizar_cabecera(
    titulo="💊 Plataforma Inteligente de Pricing Farmacéutico",
    subtitulo="Orquestación algorítmica de 5 expertos, blindaje de margen y asignación de precios t+1.",
    texto_insignia="9 Capas Activas"
)

tab_resumen, tab_diagnostico_sku, tab_asignacion = st.tabs([
    "🌎 1. Resumen General",
    "🔍 2. Diagnóstico por SKU",
    "🎯 3. Asignación de Precios (t+1)"
])

# Pestaña 1 -> Codificada en vista_resumen.py
with tab_resumen:
    vista_resumen.renderizar_vista_resumen(df_trazabilidad)

# Pestaña 2 -> Codificada en vista_diagnostico.py
with tab_diagnostico_sku:
    vista_diagnostico.renderizar_vista_diagnostico(df_trazabilidad)

# Pestaña 3 -> Codificada en vista_asignacion.py
with tab_asignacion:
    vista_asignacion.renderizar_vista_asignacion(df_trazabilidad, df_decision_t1)
