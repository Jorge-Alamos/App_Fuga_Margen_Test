# =============================================================================
# ARCHIVO PRINCIPAL ORQUESTADOR: app.py
# Objetivo: Conectar las 3 Pestañas Principales en el orden de flujo de trabajo:
#           1) Resumen General, 2) Diagnóstico por SKU y 3) Asignación (t+1).
# =============================================================================
import streamlit as st
import pandas as pd
import estilos_ui
import vista_diagnostico
import vista_asignacion

# -----------------------------------------------------------------------------
# PARTE 1: Configuración de página panorámica y aplicación de diseño UX/UI
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
# PARTE 3: Cabecera Principal y Barra de 3 Pestañas en Orden Ejecutivo
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

# Pestaña 1: Resumen Ejecutivo Global + Mirada General de todos los KPIs por SKU
with tab_resumen:
    vista_diagnostico.renderizar_pestana_resumen_general(df_trazabilidad, df_decision_t1)

# Pestaña 2: Gráfico Interactivo de Auditoría Histórica + Bitácora por cada SKU
with tab_diagnostico_sku:
    vista_diagnostico.renderizar_pestana_diagnostico_sku(df_trazabilidad)

# Pestaña 3: Interfaz de Asignación de Precios para el Mes Entrante (t+1)
with tab_asignacion:
    vista_asignacion.renderizar_vista_asignacion(df_trazabilidad, df_decision_t1)
