# =============================================================================
# MÓDULO PÁGINA 1: vista_diagnostico.py
# Objetivo: Mostrar el Resumen Ejecutivo Global y la Auditoría Histórica por SKU
#           consumiendo los datos del Cuaderno 1 (resultados_motor_multisku.csv).
# =============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import estilos_ui


# -----------------------------------------------------------------------------
# PARTE 1: Vista de Resumen Ejecutivo Global (Portafolio Completo)
# -----------------------------------------------------------------------------
def mostrar_resumen_ejecutivo(df_trazabilidad: pd.DataFrame):
    """Calcula las métricas financieras y operativas de la cadena y dibuja las tarjetas KPI."""
    # Compatibilidad segura con el nombre de la columna del motor
    col_precio_motor = 'Precio_Motor_Emitido' if 'Precio_Motor_Emitido' in df_trazabilidad.columns else 'Precio_Solufar_Emitido'

    df_calc = df_trazabilidad.dropna(
        subset=['Mes_Ano', 'Ctdad_Ordenada', 'Precio_Unitario', 'Costo_Unitario', col_precio_motor]
    ).copy()
    df_calc['Mes_Ano'] = pd.to_datetime(df_calc['Mes_Ano'])

    # 1. Cálculos financieros bifurcados (Ingresos, Fuga y Pérdida de Oportunidad)
    ingresos_reales = (df_calc['Precio_Unitario'] * df_calc['Ctdad_Ordenada']).sum()
    ingresos_optimos = (df_calc[col_precio_motor] * df_calc['Ctdad_Ordenada']).sum()

    # A) Fuga Identificada (Cuando se cobró más barato que lo sugerido por el motor)
    df_calc['Brecha_Positiva'] = (df_calc[col_precio_motor] - df_calc['Precio_Unitario']).clip(lower=0)
    df_calc['Fuga_Valor'] = df_calc['Brecha_Positiva'] * df_calc['Ctdad_Ordenada']
    fuga_total = df_calc['Fuga_Valor'].sum()

    # B) Pérdida de Oportunidad (Cuando se cobró más caro que lo sugerido por el motor)
    df_calc['Brecha_Negativa'] = (df_calc['Precio_Unitario'] - df_calc[col_precio_motor]).clip(lower=0)
    df_calc['Perdida_Oportunidad'] = df_calc['Brecha_Negativa'] * df_calc['Ctdad_Ordenada']
    perdida_total = df_calc['Perdida_Oportunidad'].sum()

    upside_pct = ((ingresos_optimos - ingresos_reales) / ingresos_reales) * 100.0 if ingresos_reales > 0 else 0.0

    # 2. Cálculos operativos, inercia de precios y márgenes
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

    # 3. Fila 1: 4 Tarjetas de Impacto Financiero
    st.markdown("<div style='font-size:15px; font-weight:800; color:#0F172A; margin-bottom:10px;'>💰 Impacto Financiero Acumulado</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        estilos_ui.tarjeta_kpi(
            "Ingresos Reales (Inercia)", f"${ingresos_reales:,.0f}",
            "Facturación histórica cobrada", variante="blanca"
        )
    with c2:
        estilos_ui.tarjeta_kpi(
            "Proyección Motor", f"${ingresos_optimos:,.0f}",
            f"▲ {upside_pct:+.1f}% Upside Neto potencial",
            variante="esmeralda", color_valor="#047857", color_sub="#059669"
        )
    with c3:
        estilos_ui.tarjeta_kpi(
            "Fuga Identificada", f"+${fuga_total:,.0f}",
            "Por precios bajos no actualizados",
            variante="azul", color_valor="#1D4ED8", color_sub="#2563EB"
        )
    with c4:
        estilos_ui.tarjeta_kpi(
            "Pérdida de Oportunidad", f"-${perdida_total:,.0f}",
            "Fricción comercial por sobreprecio",
            variante="rosa", color_valor="#B91C1C", color_sub="#DC2626"
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 4. Fila 2: 6 Tarjetas de Alcance Operativo y Eficiencia de Margen
    st.markdown("<div style='font-size:15px; font-weight:800; color:#0F172A; margin-bottom:10px;'>⚙️ Alcance del Estudio y Eficiencia de Margen</div>", unsafe_allow_html=True)
    o1, o2, o3, o4, o5, o6 = st.columns(6)
    with o1:
        estilos_ui.tarjeta_kpi("SKUs Analizados", f"{cantidad_skus}", "Cartera auditada", variante="blanca")
    with o2:
        estilos_ui.tarjeta_kpi("Periodo Estudio", f"{meses_totales} meses", "Trazabilidad mensual", variante="blanca")
    with o3:
        estilos_ui.tarjeta_kpi("Arquitectura", "9 Capas", "5 Expertos + 2 Leyes", variante="blanca")
    with o4:
        estilos_ui.tarjeta_kpi(
            "Inercia Promedio", f"{promedio_congelado_por_sku:.1f} m",
            "Meses sin actualizar precio",
            variante="ambar", color_valor="#B45309", color_sub="#D97706"
        )
    with o5:
        estilos_ui.tarjeta_kpi("Margen Histórico", f"{margen_real_pct:.1f}%", "Margen bruto real", variante="blanca")
    with o6:
        estilos_ui.tarjeta_kpi(
            "Margen Motor", f"{margen_optimo_pct:.1f}%",
            f"Mejora de {delta_margen:+.1f}% pts",
            variante="indigo", color_valor="#4338CA", color_sub="#4F46E5"
        )

    st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)

    # 5. Tabla ejecutiva de desglose de impacto por SKU
    st.markdown("<div style='font-size:16px; font-weight:800; color:#0F172A; margin-bottom:10px;'>📋 Desglose de Impacto por Medicamento (SKU)</div>", unsafe_allow_html=True)

    resumen_sku = df_calc.groupby('Nombre_Producto').agg(
        Cajas_Vendidas=('Ctdad_Ordenada', 'sum'),
        Meses_Inercia=('Cambio_Precio', lambda x: (x == 0).sum()),
        Fuga=('Fuga_Valor', 'sum'),
        Perdida=('Perdida_Oportunidad', 'sum')
    ).reset_index().sort_values(by='Fuga', ascending=False)

    resumen_sku.rename(columns={
        'Nombre_Producto': 'Medicamento',
        'Cajas_Vendidas': 'Volumen Total (Cajas)',
        'Meses_Inercia': 'Inercia (Meses congelado)',
        'Fuga': 'Fuga Identificada (CLP)',
        'Perdida': 'Pérdida Oportunidad (CLP)'
    }, inplace=True)

    with st.container(border=True):
        st.dataframe(
            resumen_sku.style.format({
                'Volumen Total (Cajas)': '{:,.0f}',
                'Fuga Identificada (CLP)': '+${:,.0f}',
                'Pérdida Oportunidad (CLP)': '-${:,.0f}'
            }),
            use_container_width=True,
            hide_index=True
        )


# -----------------------------------------------------------------------------
# PARTE 2: Vista de Auditoría Detallada y Bitácora Mes a Mes por SKU
# -----------------------------------------------------------------------------
def mostrar_auditoria_sku(df_trazabilidad: pd.DataFrame):
    """Dibuja el gráfico interactivo de auditoría y la tabla de bitácora del SKU elegido."""
    col_precio_motor = 'Precio_Motor_Emitido' if 'Precio_Motor_Emitido' in df_trazabilidad.columns else 'Precio_Solufar_Emitido'

    lista_productos = df_trazabilidad['Nombre_Producto'].dropna().unique().tolist()

    col_sel, col_leyenda = st.columns([6, 4])
    with col_sel:
        sku_seleccionado = st.selectbox("🔍 Selecciona un Medicamento para auditar su historia:", lista_productos)

    df_filtrado = df_trazabilidad[df_trazabilidad['Nombre_Producto'] == sku_seleccionado].copy()
    df_filtrado['Mes_Ano'] = pd.to_datetime(df_filtrado['Mes_Ano'])
    df_filtrado = df_filtrado.sort_values('Mes_Ano').reset_index(drop=True)
    df_filtrado['Mes_Str'] = df_filtrado['Mes_Ano'].dt.strftime('%Y-%m')

    with col_leyenda:
        st.markdown("<div style='height: 26px;'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='background:#FFFFFF; border:1px solid #E2E8F0; padding:9px 14px; border-radius:8px; font-size:12.5px; color:#475569;'>"
            "🔴 <b>Punto Rojo:</b> Mandato Humano (Cambio manual) &nbsp;|&nbsp; 🔵 <b>Punto Azul:</b> Orquestación del Motor</div>",
            unsafe_allow_html=True
        )

    # 1. Gráfico Histórico Interactivo sobre tarjeta blanca
    with st.container(border=True):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        colores_marcadores = np.where(df_filtrado.get('Driver_Precio', '') == 'MANDATO_HUMANO', '#EF4444', '#2563EB')

        # Barras celestes de volumen
        fig.add_trace(
            go.Bar(
                x=df_filtrado['Mes_Str'], y=df_filtrado['Ctdad_Ordenada'],
                name="Ventas (Cajas)", marker_color='#BAE6FD', opacity=0.55
            ),
            secondary_y=True
        )

        # Curva principal del motor con explicación emergente
        fig.add_trace(
            go.Scatter(
                x=df_filtrado['Mes_Str'], y=df_filtrado[col_precio_motor],
                mode='lines+markers', name='Precio Sugerido Motor',
                line=dict(color='#2563EB', width=3),
                marker=dict(size=11, color=colores_marcadores, line=dict(width=2, color='white')),
                customdata=df_filtrado.get('Explicacion_Dinamica', ''),
                hovertemplate="%{customdata}<br><br><b>Precio Motor:</b> $%{y:,.0f}<extra></extra>"
            ),
            secondary_y=False
        )

        # Línea gris discontinua de precio cobrado en mostrador
        fig.add_trace(
            go.Scatter(
                x=df_filtrado['Mes_Str'], y=df_filtrado['Precio_Unitario'],
                name="Precio Inercial (Cobrado)",
                line=dict(color='#64748B', width=2.2, dash='dash'),
                hovertemplate="Cobrado: $%{y:,.0f}<extra></extra>"
            ),
            secondary_y=False
        )

        # Línea gris punteada de costo de adquisición
        fig.add_trace(
            go.Scatter(
                x=df_filtrado['Mes_Str'], y=df_filtrado['Costo_Unitario'],
                mode='lines', name='Costo Adquisición',
                line=dict(color='#94A3B8', width=3, dash='dot'),
                hovertemplate="Costo: $%{y:,.0f}<extra></extra>"
            ),
            secondary_y=False
        )

        fig.update_layout(
            title=dict(text=f"<b>Trazabilidad Histórica: {sku_seleccionado}</b>", font=dict(size=18, color="#0F172A")),
            hovermode="x unified",
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=560,
            margin=dict(l=30, r=30, t=60, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=13)),
            hoverlabel=dict(font_size=13, font_family="Inter, Segoe UI, sans-serif")
        )
        fig.update_yaxes(title=dict(text="<b>Precio ($ CLP)</b>", font=dict(size=14)), tickformat="$,.0f", secondary_y=False, gridcolor='#F1F5F9')
        fig.update_yaxes(title=dict(text="<b>Volumen (Cajas)</b>", font=dict(size=14)), secondary_y=True, showgrid=False)
        fig.update_xaxes(title=dict(text="<b>Mes</b>", font=dict(size=14)), tickangle=-45, showgrid=False)

        st.plotly_chart(fig, use_container_width=True)

    # 2. Tabla de Bitácora renderizada con el módulo de estilos_ui.py
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:16px; font-weight:800; color:#0F172A; margin-bottom:10px;'>📝 Bitácora de Decisiones Algorítmicas (Mes a Mes)</div>", unsafe_allow_html=True)

    tabla_html = estilos_ui.renderizar_tabla_bitacora(df_filtrado)
    st.markdown(tabla_html, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PARTE 3: Orquestador Principal del Módulo de Diagnóstico
# -----------------------------------------------------------------------------
def renderizar_vista_diagnostico(df_trazabilidad: pd.DataFrame):
    """Organiza las dos sub-pestañas de diagnóstico histórico."""
    sub_tab1, sub_tab2 = st.tabs([
        "🌎 Resumen Ejecutivo Global",
        "🔍 Auditoría Detallada por SKU"
    ])
    with sub_tab1:
        mostrar_resumen_ejecutivo(df_trazabilidad)
    with sub_tab2:
        mostrar_auditoria_sku(df_trazabilidad)
