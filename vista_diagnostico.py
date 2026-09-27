# =============================================================================
# MÓDULO PÁGINAS 1 Y 2: vista_diagnostico.py
# Objetivo: Entregar por separado la Pestaña 1 (Resumen General + Matriz de KPIs)
#           y la Pestaña 2 (Gráfico de Auditoría + Bitácora por cada SKU).
# =============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import estilos_ui


# -----------------------------------------------------------------------------
# PARTE 1: Tarjetas de Resumen Ejecutivo Global de la Cadena (Para Pestaña 1)
# -----------------------------------------------------------------------------
def mostrar_resumen_global_cadena(df_trazabilidad: pd.DataFrame) -> pd.DataFrame:
    """Calcula y dibuja las 4 tarjetas financieras, 4 operativas y 2 de margen global."""
    col_precio_motor = 'Precio_Motor_Emitido' if 'Precio_Motor_Emitido' in df_trazabilidad.columns else 'Precio_Solufar_Emitido'

    df_calc = df_trazabilidad.dropna(
        subset=['Mes_Ano', 'Ctdad_Ordenada', 'Precio_Unitario', 'Costo_Unitario', col_precio_motor]
    ).copy()
    df_calc['Mes_Ano'] = pd.to_datetime(df_calc['Mes_Ano'])

    # 1. Cálculos financieros acumulados
    ingresos_reales = (df_calc['Precio_Unitario'] * df_calc['Ctdad_Ordenada']).sum()
    ingresos_optimos = (df_calc[col_precio_motor] * df_calc['Ctdad_Ordenada']).sum()

    df_calc['Brecha_Positiva'] = (df_calc[col_precio_motor] - df_calc['Precio_Unitario']).clip(lower=0)
    df_calc['Fuga_Valor'] = df_calc['Brecha_Positiva'] * df_calc['Ctdad_Ordenada']
    fuga_total = df_calc['Fuga_Valor'].sum()

    df_calc['Brecha_Negativa'] = (df_calc['Precio_Unitario'] - df_calc[col_precio_motor]).clip(lower=0)
    df_calc['Perdida_Oportunidad'] = df_calc['Brecha_Negativa'] * df_calc['Ctdad_Ordenada']
    perdida_total = df_calc['Perdida_Oportunidad'].sum()

    upside_pct = ((ingresos_optimos - ingresos_reales) / ingresos_reales) * 100.0 if ingresos_reales > 0 else 0.0

    # 2. Cálculos operativos y de margen
    cantidad_skus = df_calc['Nombre_Producto'].nunique()
    meses_totales = df_calc['Mes_Ano'].nunique()

    df_calc = df_calc.sort_values(by=['Nombre_Producto', 'Mes_Ano'])
    df_calc['Cambio_Precio'] = df_calc.groupby('Nombre_Producto')['Precio_Unitario'].diff().fillna(1)
    meses_congelados_totales = (df_calc['Cambio_Precio'] == 0).sum()
    promedio_congelado_por_sku = meses_congelados_totales / cantidad_skus if cantidad_skus > 0 else 0.0

    costo_total_vendido = (df_calc['Costo_Unitario'] * df_calc['Ctdad_Ordenada']).sum()
    margen_real_pct = ((ingresos_reales - costo_total_vendido) / ingresos_reales) * 100.0 if ingresos_reales > 0 else 0.0
    margen_optimo_pct = ((ingresos_optimos - costo_total_vendido) / ingresos_optimos) * 100.0 if ingresos_optimos > 0 else 0.0
    delta_margen = margen_optimo_pct - margen_real_pct

    # Fila 1: 4 Tarjetas Financieras
    st.markdown("<div style='font-size:18px; font-weight:800; color:#0F172A; margin-bottom:12px;'>💰 Impacto Financiero Acumulado</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        estilos_ui.tarjeta_kpi(
            "Ingresos Reales", f"${ingresos_reales:,.0f}",
            "Facturación histórica cobrada", variante="blanca"
        )
    with c2:
        estilos_ui.tarjeta_kpi(
            "Proyección Motor", f"${ingresos_optimos:,.0f}",
            f"Upside Neto: {upside_pct:+.1f}%",
            variante="esmeralda", color_valor="#047857", color_sub="#059669"
        )
    with c3:
        estilos_ui.tarjeta_kpi(
            "Fuga Identificada", f"+${fuga_total:,.0f}",
            "Por precios bajos sin actualizar",
            variante="azul", color_valor="#1D4ED8", color_sub="#2563EB"
        )
    with c4:
        estilos_ui.tarjeta_kpi(
            "Pérdida Oportunidad", f"-${perdida_total:,.0f}",
            "Por precios altos sobre mercado",
            variante="rosa", color_valor="#B91C1C", color_sub="#DC2626"
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Fila 2: 4 Tarjetas Operativas
    st.markdown("<div style='font-size:16px; font-weight:800; color:#0F172A; margin-bottom:12px;'>⚙️ Alcance del Estudio y Eficiencia</div>", unsafe_allow_html=True)
    o1, o2, o3, o4 = st.columns(4, gap="medium")
    with o1:
        estilos_ui.tarjeta_kpi("SKUs Analizados", f"{cantidad_skus}", "Medicamentos en cartera", variante="blanca")
    with o2:
        estilos_ui.tarjeta_kpi("Periodo (Meses)", f"{meses_totales}", "Meses de historia auditada", variante="blanca")
    with o3:
        estilos_ui.tarjeta_kpi("Capas Algoritmo", "9 Activas", "5 Expertos + 2 Leyes de Blindaje", variante="blanca")
    with o4:
        estilos_ui.tarjeta_kpi(
            "Inercia Promedio", f"{promedio_congelado_por_sku:.1f} Meses/SKU",
            "Sin actualizar precio en mostrador",
            variante="ambar", color_valor="#B45309", color_sub="#D97706"
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Fila 3: 2 Tarjetas Comparativas de Margen
    m1, m2 = st.columns(2, gap="medium")
    with m1:
        estilos_ui.tarjeta_kpi(
            "Margen Bruto Histórico", f"{margen_real_pct:.1f}%",
            "Rentabilidad real obtenida con precios inerciales", variante="blanca"
        )
    with m2:
        estilos_ui.tarjeta_kpi(
            "Margen Proyectado Motor", f"{margen_optimo_pct:.1f}%",
            f"Expansión de {delta_margen:+.1f}% puntos porcentuales de margen",
            variante="indigo", color_valor="#4338CA", color_sub="#4F46E5"
        )

    return df_calc


# -----------------------------------------------------------------------------
# PARTE 2: Mirada General de Todos los Medicamentos (Matriz de KPIs en Pestaña 1)
# -----------------------------------------------------------------------------
def mostrar_matriz_general_skus(df_calc: pd.DataFrame, df_decision: pd.DataFrame):
    """Dibuja la tabla panorámica con todos los KPIs actuales e históricos de los 10 SKUs."""
    st.markdown("<div style='height: 26px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:18px; font-weight:800; color:#0F172A; margin-bottom:6px;'>📋 Mirada General de Medicamentos (Todos los KPIs por SKU)</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13.5px; color:#64748B; margin-bottom:14px;'>Vista consolidada de costos, pisos de seguridad, rotación, inercia, márgenes actuales, fugas históricas y precios sugeridos para toda la cartera.</div>", unsafe_allow_html=True)

    resumen_hist = df_calc.groupby('Nombre_Producto').agg(
        Volumen_Total_Hist=('Ctdad_Ordenada', 'sum'),
        Fuga_Historica=('Fuga_Valor', 'sum'),
        Perdida_Historica=('Perdida_Oportunidad', 'sum')
    ).reset_index()

    df_general = pd.merge(df_decision, resumen_hist, on='Nombre_Producto', how='left')
    df_general = df_general.sort_values(by='Fuga_Historica', ascending=False).reset_index(drop=True)

    tabla_kpi_completa = pd.DataFrame({
        'Medicamento': df_general['Nombre_Producto'],
        'Categoría': df_general['KPI_Categoria'],
        'Meses Hist.': df_general['Total_Meses_Historia'],
        'Costo Actual': df_general['KPI_Costo_Actual'],
        'Piso Blindaje (C6)': df_general['KPI_Piso_Seguridad'],
        'Precio Actual': df_general['KPI_Precio_Actual'],
        'Cajas Últ. Mes': df_general['KPI_Cajas_Ultimo_Mes'],
        'Prom. Cajas Hist.': df_general['KPI_Prom_Cajas_Hist'],
        'Inercia (Meses)': df_general['KPI_Meses_Inercia'],
        'Margen Actual (%)': df_general['KPI_Margen_Actual_Pct'],
        'Ganancia/Caja ($)': df_general['KPI_Ganancia_Caja_Actual'],
        'Fuga Identificada ($)': df_general['Fuga_Historica'],
        'Pérdida Oport. ($)': df_general['Perdida_Historica'],
        'Sugerido t+1 ★': df_general['Precio_Sugerido'],
        'Margen t+1 (%)': df_general['Margen_Sugerido_Pct']
    })

    with st.container(border=True):
        st.dataframe(
            tabla_kpi_completa.style.format({
                'Costo Actual': '${:,.0f}',
                'Piso Blindaje (C6)': '${:,.0f}',
                'Precio Actual': '${:,.0f}',
                'Cajas Últ. Mes': '{:,.0f}',
                'Prom. Cajas Hist.': '{:,.0f}',
                'Margen Actual (%)': '{:.1f}%',
                'Ganancia/Caja ($)': '${:,.0f}',
                'Fuga Identificada ($)': '+${:,.0f}',
                'Pérdida Oport. ($)': '-${:,.0f}',
                'Sugerido t+1 ★': '${:,.0f}',
                'Margen t+1 (%)': '{:.1f}%'
            }),
            use_container_width=True,
            hide_index=True,
            height=410
        )


# -----------------------------------------------------------------------------
# PARTE 3: Orquestador exclusivo para la PESTAÑA 1 (Resumen General)
# -----------------------------------------------------------------------------
def renderizar_pestana_resumen_general(df_trazabilidad: pd.DataFrame, df_decision: pd.DataFrame):
    """Muestra el Resumen Ejecutivo Global seguido de la Matriz General de KPIs."""
    df_calc = mostrar_resumen_global_cadena(df_trazabilidad)
    mostrar_matriz_general_skus(df_calc, df_decision)


# -----------------------------------------------------------------------------
# PARTE 4: Orquestador exclusivo para la PESTAÑA 2 (Diagnóstico por cada SKU)
# -----------------------------------------------------------------------------
def renderizar_pestana_diagnostico_sku(df_trazabilidad: pd.DataFrame):
    """Muestra el selector de SKU, el Gráfico Interactivo de Auditoría y la Bitácora."""
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

    # 1. Gráfico Interactivo de Auditoría por SKU
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

    # 2. Tabla de Bitácora Mes a Mes
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:17px; font-weight:800; color:#0F172A; margin-bottom:10px;'>📝 Bitácora de Decisiones Algorítmicas (Detalle Mes a Mes)</div>", unsafe_allow_html=True)

    tabla_html = estilos_ui.renderizar_tabla_bitacora(df_filtrado)
    st.markdown(tabla_html, unsafe_allow_html=True)
