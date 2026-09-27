# =============================================================================
# MÓDULO PÁGINA 1: vista_resumen.py
# Objetivo: Codificar exclusivamente la Pestaña 1 (Resumen General) con las
#           tarjetas globales y el Ranking Ejecutivo por Fuga de Margen.
# =============================================================================
import streamlit as st
import pandas as pd
import estilos_ui


# -----------------------------------------------------------------------------
# PARTE 1: Tarjetas de Resumen Ejecutivo Global de la Cadena
# -----------------------------------------------------------------------------
def mostrar_kpis_globales(df_trazabilidad: pd.DataFrame) -> pd.DataFrame:
    """Calcula y dibuja las 4 tarjetas financieras, 4 operativas y 2 de margen."""
    col_precio_motor = 'Precio_Motor_Emitido' if 'Precio_Motor_Emitido' in df_trazabilidad.columns else 'Precio_Solufar_Emitido'

    df_calc = df_trazabilidad.dropna(
        subset=['Mes_Ano', 'Ctdad_Ordenada', 'Precio_Unitario', 'Costo_Unitario', col_precio_motor]
    ).copy()
    df_calc['Mes_Ano'] = pd.to_datetime(df_calc['Mes_Ano'])

    # 1. Métricas financieras bifurcadas
    ingresos_reales = (df_calc['Precio_Unitario'] * df_calc['Ctdad_Ordenada']).sum()
    ingresos_optimos = (df_calc[col_precio_motor] * df_calc['Ctdad_Ordenada']).sum()

    df_calc['Brecha_Positiva'] = (df_calc[col_precio_motor] - df_calc['Precio_Unitario']).clip(lower=0)
    df_calc['Fuga_Valor'] = df_calc['Brecha_Positiva'] * df_calc['Ctdad_Ordenada']
    fuga_total = df_calc['Fuga_Valor'].sum()

    df_calc['Brecha_Negativa'] = (df_calc['Precio_Unitario'] - df_calc[col_precio_motor]).clip(lower=0)
    df_calc['Perdida_Oportunidad'] = df_calc['Brecha_Negativa'] * df_calc['Ctdad_Ordenada']
    perdida_total = df_calc['Perdida_Oportunidad'].sum()

    upside_pct = ((ingresos_optimos - ingresos_reales) / ingresos_reales) * 100.0 if ingresos_reales > 0 else 0.0

    # 2. Métricas operativas y de margen
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
            "Fuga de Margen Identificada", f"+${fuga_total:,.0f}",
            "Capital perdido por precios bajos",
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
# PARTE 2: Tabla Ejecutiva Rankeada por Fuga de Margen (Solo datos esenciales)
# -----------------------------------------------------------------------------
def mostrar_ranking_ejecutivo_fuga(df_calc: pd.DataFrame):
    """Muestra la tabla ejecutiva limpia ordenada desde el SKU que pierde más margen."""
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:18px; font-weight:800; color:#0F172A; margin-bottom:4px;'>📋 Ranking Ejecutivo de Impacto por Medicamento (Ordenado por Mayor Fuga de Margen)</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13.5px; color:#64748B; margin-bottom:14px;'>Priorización directa desde el SKU que concentra la mayor fuga de margen recuperable hasta el de menor impacto.</div>", unsafe_allow_html=True)

    # Agrupación ejecutiva y ordenamiento estricto de mayor a menor Fuga
    resumen_sku = df_calc.groupby('Nombre_Producto').agg(
        Cajas_Vendidas=('Ctdad_Ordenada', 'sum'),
        Meses_Inercia=('Cambio_Precio', lambda x: (x == 0).sum()),
        Fuga=('Fuga_Valor', 'sum'),
        Perdida=('Perdida_Oportunidad', 'sum')
    ).reset_index().sort_values(by='Fuga', ascending=False).reset_index(drop=True)

    # Renderizado en tabla HTML ejecutiva de alta legibilidad
    html = "<table class='bitacora-table'><thead><tr>"
    html += "<th style='text-align:center; width:70px;'>Ranking</th>"
    html += "<th>Medicamento (SKU)</th>"
    html += "<th style='text-align:center;'>Volumen (Cajas)</th>"
    html += "<th style='text-align:center;'>Inercia (Sin cambio)</th>"
    html += "<th style='text-align:right;'>Fuga Identificada (CLP)</th>"
    html += "<th style='text-align:right;'>Pérdida Oportunidad (CLP)</th>"
    html += "</tr></thead><tbody>"

    for idx, row in resumen_sku.iterrows():
        rank = idx + 1
        medalla = "🥇 #1" if rank == 1 else ("🥈 #2" if rank == 2 else ("🥉 #3" if rank == 3 else f"#{rank}"))
        bg_rank = "background:#EEF2FF; color:#4F46E5; font-weight:800;" if rank <= 3 else "color:#64748B; font-weight:700;"

        html += (
            f"<tr>"
            f"<td style='text-align:center; {bg_rank}'>{medalla}</td>"
            f"<td style='font-weight:700; color:#0F172A;'>{row['Nombre_Producto']}</td>"
            f"<td style='text-align:center; font-weight:700; color:#334155;'>{row['Cajas_Vendidas']:,.0f}</td>"
            f"<td style='text-align:center; color:#B45309; font-weight:600;'>{int(row['Meses_Inercia'])} meses</td>"
            f"<td style='text-align:right; color:#059669; font-weight:800; font-size:15px;'>+${row['Fuga']:,.0f}</td>"
            f"<td style='text-align:right; color:#DC2626; font-weight:700;'>-${row['Perdida']:,.0f}</td>"
            f"</tr>"
        )

    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PARTE 3: Función Principal de la Pestaña 1
# -----------------------------------------------------------------------------
def renderizar_vista_resumen(df_trazabilidad: pd.DataFrame):
    """Ejecuta la vista completa de la Pestaña 1 (Resumen General)."""
    df_calc = mostrar_kpis_globales(df_trazabilidad)
    mostrar_ranking_ejecutivo_fuga(df_calc)
