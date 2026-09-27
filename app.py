# =============================================================================
# ARCHIVO PRINCIPAL ORQUESTADOR: app.py
# Objetivo: Cargar los datos de GitHub, aplicar el sistema de diseño UX/UI y
#           conectar los módulos independientes (Diagnóstico y Asignación t+1).
# =============================================================================
import streamlit as st
import pandas as pd
import estilos_ui
import vista_diagnostico
import vista_asignacion

# -----------------------------------------------------------------------------
# PARTE 1: Configuración general de la página y aplicación del diseño luminoso
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Gemelo Digital de Pricing",
    page_icon="💊",
    layout="wide"
)

estilos_ui.aplicar_estilos_globales()


# -----------------------------------------------------------------------------
# PARTE 2: Carga centralizada de los 2 archivos CSV (Cuaderno 1 y Cuaderno 2)
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
# PARTE 3: Cabecera y Navegación Modular por Pestañas
# -----------------------------------------------------------------------------
estilos_ui.renderizar_cabecera(
    titulo="💊 Plataforma Inteligente de Pricing Farmacéutico",
    subtitulo="Orquestación algorítmica de 5 expertos, blindaje de margen y asignación t+1.",
    texto_insignia="9 Capas Activas"
)

tab_asignacion, tab_diagnostico = st.tabs([
    "🎯 Asignación de Precios (Mes Entrante t+1)",
    "📊 Diagnóstico y Auditoría Histórica"
])

with tab_asignacion:
    vista_asignacion.renderizar_vista_asignacion(df_trazabilidad, df_decision_t1)

with tab_diagnostico:
    vista_diagnostico.renderizar_vista_diagnostico(df_trazabilidad)
