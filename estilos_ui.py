# =============================================================================
# MÓDULO DE DISEÑO UX/UI: estilos_ui.py
# Objetivo: Centralizar el estilo visual luminoso, la casilla resaltada de
#           Precio Manual y el formato de tablas ejecutivas.
# =============================================================================
import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# PARTE 1: Sistema visual CSS (Ancho 98%, casilla manual destacada y tarjetas)
# -----------------------------------------------------------------------------
def aplicar_estilos_globales():
    """Inyecta la hoja de estilos UX/UI con énfasis en la casilla de Precio Manual."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-variant-numeric: tabular-nums;
        }

        /* Ampliación de márgenes de izquierda a derecha (98% del ancho) */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            padding-left: 2.2rem !important;
            padding-right: 2.2rem !important;
            max-width: 98% !important;
        }

        /* Cabecera principal */
        .ux-header {
            background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
            padding: 22px 28px;
            border-radius: 14px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .ux-header-title { font-size: 26px; font-weight: 800; color: #0F172A; margin: 0; letter-spacing: -0.4px; }
        .ux-header-subtitle { font-size: 14px; color: #64748B; margin: 4px 0 0 0; font-weight: 500; }
        .ux-badge-pill {
            background: #EEF2FF; color: #4F46E5; border: 1px solid #C7D2FE;
            padding: 8px 16px; border-radius: 999px; font-size: 13px; font-weight: 700;
        }

        /* Tarjetas KPI */
        .ui-card {
            background: #FFFFFF; padding: 18px 22px; border-radius: 12px;
            border: 1px solid #E2E8F0; box-shadow: 0 2px 5px rgba(15, 23, 42, 0.03);
            min-height: 122px; display: flex; flex-direction: column; justify-content: space-between;
        }
        .ui-card-indigo  { background: #EEF2FF; border: 1px solid #C7D2FE; }
        .ui-card-emerald { background: #ECFDF5; border: 1px solid #A7F3D0; }
        .ui-card-blue    { background: #EFF6FF; border: 1px solid #BFDBFE; }
        .ui-card-rose    { background: #FEF2F2; border: 1px solid #FECACA; }
        .ui-card-amber   { background: #FFFBEB; border: 1px solid #FDE68A; }

        .ui-card-label { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #64748B; margin: 0; }
        .ui-card-value { font-size: 28px; font-weight: 800; color: #0F172A; margin: 6px 0; letter-spacing: -0.5px; line-height: 1.15; }
        .ui-card-sub { font-size: 12.5px; font-weight: 600; color: #475569; margin: 0; }

        /* Recuadros de "La Voz del Consultor" */
        .expert-box {
            background: #F8FAFC; padding: 14px 18px; border-radius: 10px;
            margin-bottom: 12px; font-size: 13.5px; color: #334155; line-height: 1.55; border: 1px solid #F1F5F9;
        }

        /* Tarjetas de estrategia */
        .strat-card {
            padding: 16px 18px; border-radius: 12px; text-align: left; min-height: 120px;
        }

        /* =====================================================================
           ESTILO PROTAGONISTA PARA LA CELDA DE PRECIO MANUAL DEL USUARIO
           ===================================================================== */
        div[data-testid="stNumberInput"] div[data-baseweb="input"] {
            border: 2px solid #4F46E5 !important;
            border-radius: 10px !important;
            background-color: #FFFFFF !important;
            min-height: 54px !important;
            box-shadow: 0 4px 10px rgba(79, 70, 229, 0.12) !important;
        }
        div[data-testid="stNumberInput"] input {
            font-size: 24px !important;
            font-weight: 800 !important;
            color: #1E1B4B !important;
            padding-left: 14px !important;
        }
        div[data-testid="stNumberInput"] label p {
            font-size: 13.5px !important;
            font-weight: 800 !important;
            color: #312E81 !important;
        }

        /* Tabla ejecutiva */
        .bitacora-table {
            width: 100%; border-collapse: separate; border-spacing: 0;
            background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden;
        }
        .bitacora-table th {
            background-color: #F8FAFC; color: #475569; text-align: left;
            padding: 14px 18px; font-size: 12.5px; font-weight: 700; text-transform: uppercase; border-bottom: 1px solid #E2E8F0;
        }
        .bitacora-table td {
            border-bottom: 1px solid #F1F5F9; padding: 15px 18px; font-size: 14px; color: #1E293B; vertical-align: middle; line-height: 1.5;
        }
        .bitacora-table tr:hover td { background-color: #F8FAFC; }

        /* Barra de pestañas principal */
        div[data-baseweb="tab-list"] {
            gap: 10px; background-color: #F1F5F9; padding: 6px 8px; border-radius: 12px; margin-bottom: 22px;
        }
        button[data-baseweb="tab"] {
            border-radius: 8px !important; padding: 10px 22px !important; font-size: 15px !important; font-weight: 700 !important; color: #475569 !important; border: none !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #FFFFFF !important; color: #4F46E5 !important; box-shadow: 0 1px 4px rgba(15, 23, 42, 0.08) !important;
        }
    </style>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PARTE 2: Componente de Cabecera Superior
# -----------------------------------------------------------------------------
def renderizar_cabecera(titulo: str, subtitulo: str, texto_insignia: str = "9 Capas Activas"):
    html = f"""
    <div class="ux-header">
        <div>
            <h1 class="ux-header-title">{titulo}</h1>
            <p class="ux-header-subtitle">{subtitulo}</p>
        </div>
        <div class="ux-badge-pill">{texto_insignia}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PARTE 3: Componente de Tarjeta KPI Reutilizable
# -----------------------------------------------------------------------------
def tarjeta_kpi(titulo: str, valor: str, subtitulo: str = "", variante: str = "blanca", color_valor: str = "#0F172A", color_sub: str = "#64748B"):
    clases_variante = {
        "blanca": "ui-card",
        "indigo": "ui-card ui-card-indigo",
        "esmeralda": "ui-card ui-card-emerald",
        "azul": "ui-card ui-card-blue",
        "rosa": "ui-card ui-card-rose",
        "ambar": "ui-card ui-card-amber"
    }
    clase = clases_variante.get(variante, "ui-card")
    html = f"""
    <div class="{clase}">
        <div class="ui-card-label">{titulo}</div>
        <div class="ui-card-value" style="color: {color_valor};">{valor}</div>
        <div class="ui-card-sub" style="color: {color_sub};">{subtitulo}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PARTE 4: Renderizador de Tabla Bitácora
# -----------------------------------------------------------------------------
def renderizar_tabla_bitacora(df_filtrado: pd.DataFrame) -> str:
    html = "<table class='bitacora-table'><thead><tr>"
    html += "<th>Mes</th><th>Costo Adquisición</th><th>Precio Cobrado</th>"
    html += "<th>Precio Sugerido Motor</th><th>Margen Proyectado</th><th>Diagnóstico del Tribunal (9 Capas)</th>"
    html += "</tr></thead><tbody>"

    for _, row in df_filtrado.iterrows():
        explicacion = row['Explicacion_Dinamica'] if pd.notna(row.get('Explicacion_Dinamica')) else "Sin datos"
        p_motor = row.get('Precio_Motor_Emitido', row.get('Precio_Unitario', 0))
        html += (
            f"<tr>"
            f"<td style='font-weight: 700; color: #0F172A; white-space: nowrap;'>{row['Mes_Str']}</td>"
            f"<td style='color: #64748B;'>${row['Costo_Unitario']:,.0f}</td>"
            f"<td style='font-weight: 500;'>${row['Precio_Unitario']:,.0f}</td>"
            f"<td style='color: #2563EB; font-weight: 800; font-size: 15px;'>${p_motor:,.0f}</td>"
            f"<td style='font-weight: 700; color: #059669;'>{row['Margen_Pct_Final']:.1f}%</td>"
            f"<td>{explicacion}</td>"
            f"</tr>"
        )

    html += "</tbody></table>"
    return html
