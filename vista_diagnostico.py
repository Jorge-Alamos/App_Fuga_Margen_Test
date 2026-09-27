# =============================================================================
# MÓDULO PÁGINA 2: vista_diagnostico.py
# Objetivo: Codificar exclusivamente la Pestaña 2 (Diagnóstico por SKU) con su
#           gráfico interactivo de auditoría algorítmica y su bitácora mensual.
# =============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import estilos_ui


# -----------------------------------------------------------------------------
# PARTE 1: Selector y Gráfico Interactivo de Auditoría Histórica por SKU
# -----------------------------------------------------------------------------
def mostrar_grafico_auditoria(df_trazabilidad: pd.DataFrame) -> pd.DataFrame:
    """Dibuja el selector de medicamento y el gráfico histórico de las 9 capas."""
    col_precio_motor = 'Precio_Motor_Emitido' if 'Precio_Motor_Emitido' in df_trazabilidad.columns else 'Precio_Solufar_Emitido'

    st.markdown("<div style='font-size:18px; font-weight:800; color:#0F172A; margin-bottom:12px;'>🔍 Diagnóstico y Auditoría Algorítmica por Medicamento</div>", unsafe_allow_html=True)

    lista_productos = df_trazabilidad['Nombre_Producto'].dropna().unique().tolist()

    col_sel, col_leyenda = st.columns([5.5, 4.5], gap="large")
    with col_sel:
        sku_seleccionado = st.selectbox(
            "Selecciona un SKU para auditar su comportamiento histórico mes a mes:",
            options=lista_productos,
            key="selector_diagnostico_sku"
        )

    with col_leyenda:
        st.markdown("<div style='height: 26px;'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='background:#FFFFFF; border:1px solid #E2E8F0; padding:10px 16px; border-radius:8px; font-size:13px; color:#475569;'>"
            "🔴 <b>Punto Rojo:</b> Mandato Humano (Cambio manual) &nbsp;|&nbsp; 🔵 <b>Punto Azul:</b> Orquestación del Motor</div>",
            unsafe_allow_html=True
        )

    df_filtrado = df_trazabilidad[df_trazabilidad['Nombre_Producto'] == sku_seleccionado].copy()
    df_filtrado['Mes_Ano'] = pd.to_datetime(df_filtrado['Mes_Ano'])
    df_filtrado = df_filtrado.sort_values('Mes_Ano').reset_index(drop=True)
    df_filtrado['Mes_Str'] = df_filtrado['Mes_Ano'].dt.strftime('%Y-%m')

    with st.container(border=True):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        colores_marcadores = np.where(df_filtrado.get('Driver_Precio', '') == 'MANDATO_HUMANO', '#EF4444', '#2563EB')

        fig.add_trace(
            go.Bar(
                x=df_filtrado['Mes_Str'], y=df_filtrado['Ctdad_Ordenada'],
                name="Ventas (Cajas)", marker_color='#BAE6FD', opacity=0.55
            ),
            secondary_y=True
        )

        fig.add_trace(
            go.Scatter(
                x=df_filtrado['Mes_Str'], y=df_filtrado[col_precio_motor],
                mode='lines+markers', name='Precio Final Emitido (Motor)',
                line=dict(color='#2563EB', width=3),
                marker=dict(size=12, color=colores_marcadores, line=dict(width=2, color='white')),
                customdata=df_filtrado.get('Explicacion_Dinamica', ''),
                hovertemplate="%{customdata}<br><br><b>Precio Final:</b> $%{y:,.0f}<extra></extra>"
            ),
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=df_filtrado['Mes_Str'], y=df_filtrado['Precio_Unitario'],
                name="Precio Inercial (Cobrado)",
                line=dict(color='#64748B', width=2.2, dash='dash'),
                hovertemplate="Cobrado: $%{y:,.0f}<extra></extra>"
            ),
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=df_filtrado['Mes_Str'], y=df_filtrado['Costo_Unitario'],
                mode='lines', name='Costo Adquisición',
                line=dict(color='#94A3B8', width=3.5, dash='dot'),
                hovertemplate="Costo: $%{y:,.0f}<extra></extra>"
            ),
            secondary_y=False
        )

        fig.update_layout(
            title=dict(text=f"<b>Auditoría Algorítmica: {sku_seleccionado}</b>", font=dict(size=19, color="#0F172A")),
            hovermode="x unified",
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=620,
            margin=dict(l=30, r=30, t=65, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=13.5)),
            hoverlabel=dict(font_size=13.5, font_family="Inter, Segoe UI, sans-serif")
        )
        fig.update_yaxes(title=dict(text="<b>Precio ($ CLP)</b>", font=dict(size=15)), tickformat="$,.0f", secondary_y=False, gridcolor='#F1F5F9')
        fig.update_yaxes(title=dict(text="<b>Volumen (Cajas)</b>", font=dict(size=15)), secondary_y=True, showgrid=False)
        fig.update_xaxes(title=dict(text="<b>Mes</b>", font=dict(size=15)), tickangle=-45, showgrid=False)

        st.plotly_chart(fig, use_container_width=True)

    return df_filtrado


# -----------------------------------------------------------------------------
# PARTE 2: Bitácora de Decisiones Algorítmicas Mes a Mes
# -----------------------------------------------------------------------------
def mostrar_bitacora_sku(df_filtrado: pd.DataFrame):
    """Muestra la tabla detallada con la explicación de capas de cada mes."""
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:17px; font-weight:800; color:#0F172A; margin-bottom:10px;'>📝 Bitácora de Decisiones Algorítmicas (Detalle Mes a Mes)</div>", unsafe_allow_html=True)

    tabla_html = estilos_ui.renderizar_tabla_bitacora(df_filtrado)
    st.markdown(tabla_html, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PARTE 3: Función Principal de la Pestaña 2
# -----------------------------------------------------------------------------
def renderizar_vista_diagnostico(df_trazabilidad: pd.DataFrame):
    """Ejecuta la vista completa de la Pestaña 2 (Diagnóstico por SKU)."""
    df_filtrado = mostrar_grafico_auditoria(df_trazabilidad)
    mostrar_bitacora_sku(df_filtrado)
