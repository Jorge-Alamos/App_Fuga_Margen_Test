import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuración de página
st.set_page_config(page_title="Gemelo Digital Solufar", layout="wide", page_icon="💊")

# =============================================================================
# 1. CARGA LIGERA DE DATOS
# =============================================================================
@st.cache_data(ttl=60)
def load_data():
    url = "https://raw.githubusercontent.com/Jorge-Alamos/App_Fuga_Margen_Test/main/resultados_solufar_multisku.csv"
    df = pd.read_csv(url)
    return df

df_trazabilidad = load_data()

# =============================================================================
# 2. FUNCIÓN AISLADA PARA RENDERIZAR HTML DE LA BITÁCORA
# =============================================================================
def renderizar_tabla_html(df_filtrado):
    html = "<style>"
    html += ".bitacora-table { width: 100%; border-collapse: collapse; font-family: 'Segoe UI', Arial, sans-serif; background-color: white; border: 1px solid #e0e0e0; }"
    html += ".bitacora-table th { background-color: #34495e; color: white; text-align: left; padding: 12px; font-size: 14px; }"
    html += ".bitacora-table td { border-bottom: 1px solid #e0e0e0; padding: 12px; font-size: 13px; color: #2c3e50; vertical-align: top; }"
    html += ".bitacora-table tr:hover { background-color: #f8f9fa; }"
    html += "</style>"
    html += "<table class='bitacora-table'><thead><tr>"
    html += "<th>Mes</th><th>Costo Adquisición</th><th>Precio Histórico (Cobrado)</th>"
    html += "<th>Precio Óptimo (Solufar)</th><th>Margen Proyectado</th><th>Diagnóstico de Capas (Algoritmo)</th>"
    html += "</tr></thead><tbody>"

    for _, row in df_filtrado.iterrows():
        explicacion = row['Explicacion_Dinamica'] if pd.notna(row['Explicacion_Dinamica']) else "Sin datos"
        html += f"<tr><td>{row['Mes_Str']}</td><td>${row['Costo_Unitario']:,.0f}</td><td>${row['Precio_Unitario']:,.0f}</td><td style='color: #2E86C1; font-weight: bold;'>${row['Precio_Solufar_Emitido']:,.0f}</td><td>{row['Margen_Pct_Final']:.1f}%</td><td>{explicacion}</td></tr>"

    html += "</tbody></table>"
    return html

# =============================================================================
# 3. INTERFAZ DE USUARIO PRINCIPAL
# =============================================================================
st.title("📊 Gemelo Digital Solufar: Pricing Inteligente")
st.markdown("Plataforma de auditoría basada en un motor de 5 Expertos orquestados y leyes de blindaje.")

# Creamos las dos pestañas de navegación superior
tab1, tab2 = st.tabs(["🌎 Resumen Ejecutivo Global", "🔍 Auditoría Detallada por SKU"])

# =============================================================================
# PESTAÑA 1: RESUMEN EJECUTIVO GLOBAL
# =============================================================================
with tab1:
    st.header("Diagnóstico de Portafolio")
    
    # Filtramos nulos
    df_calc = df_trazabilidad.dropna(subset=['Mes_Ano', 'Ctdad_Ordenada', 'Precio_Unitario', 'Costo_Unitario', 'Precio_Solufar_Emitido']).copy()
    df_calc['Mes_Ano'] = pd.to_datetime(df_calc['Mes_Ano'])
    
    # 🔴 1. MÉTRICAS FINANCIERAS BIFURCADAS (NUEVO)
    ingresos_reales = (df_calc['Precio_Unitario'] * df_calc['Ctdad_Ordenada']).sum()
    ingresos_solufar = (df_calc['Precio_Solufar_Emitido'] * df_calc['Ctdad_Ordenada']).sum()
    
    # A) Fuga Identificada (Solufar > Histórico)
    df_calc['Brecha_Positiva'] = (df_calc['Precio_Solufar_Emitido'] - df_calc['Precio_Unitario']).clip(lower=0)
    df_calc['Fuga_Valor'] = df_calc['Brecha_Positiva'] * df_calc['Ctdad_Ordenada']
    fuga_total = df_calc['Fuga_Valor'].sum()
    
    # B) Pérdida de Oportunidad (Solufar < Histórico)
    df_calc['Brecha_Negativa'] = (df_calc['Precio_Unitario'] - df_calc['Precio_Solufar_Emitido']).clip(lower=0)
    df_calc['Perdida_Oportunidad'] = df_calc['Brecha_Negativa'] * df_calc['Ctdad_Ordenada']
    perdida_total = df_calc['Perdida_Oportunidad'].sum()
    
    upside_pct = ((ingresos_solufar - ingresos_reales) / ingresos_reales) * 100 if ingresos_reales > 0 else 0.0

    cantidad_skus = df_calc['Nombre_Producto'].nunique()
    meses_totales = df_calc['Mes_Ano'].nunique()
    
    # Cálculo de Inercia
    df_calc = df_calc.sort_values(by=['Nombre_Producto', 'Mes_Ano'])
    df_calc['Cambio_Precio'] = df_calc.groupby('Nombre_Producto')['Precio_Unitario'].diff().fillna(1)
    meses_congelados_totales = (df_calc['Cambio_Precio'] == 0).sum()
    promedio_congelado_por_sku = meses_congelados_totales / cantidad_skus if cantidad_skus > 0 else 0

    costo_total_vendido = (df_calc['Costo_Unitario'] * df_calc['Ctdad_Ordenada']).sum()
    margen_real_pct = ((ingresos_reales - costo_total_vendido) / ingresos_reales) * 100 if ingresos_reales > 0 else 0
    margen_solufar_pct = ((ingresos_solufar - costo_total_vendido) / ingresos_solufar) * 100 if ingresos_solufar > 0 else 0

    # 🔴 RENDERIZADO DE 4 TARJETAS PRINCIPALES
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ingresos Reales (Inercia)", f"${ingresos_reales:,.0f}")
    col2.metric("Proyección Solufar", f"${ingresos_solufar:,.0f}", f"{upside_pct:+.1f}% Upside Neto")
    col3.metric("Fuga Identificada (Bajos precios)", f"+${fuga_total:,.0f}", delta_color="normal")
    col4.metric("Pérdida Oportunidad (Altos precios)", f"-${perdida_total:,.0f}", delta_color="inverse")
    
    st.divider()

    # Renderizado de Tarjetas (Row 2: Operaciones)
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("SKUs Analizados", cantidad_skus)
    col6.metric("Periodo Analizado", f"{meses_totales} meses")
    col7.metric("Capas Algoritmo", "9 Activas")
    col8.metric("Inercia Promedio", f"{promedio_congelado_por_sku:.1f} meses/SKU")
    
    st.divider()

    # Renderizado de Tarjetas (Row 3: Márgenes)
    col9, col10 = st.columns(2)
    col9.metric("Margen Bruto Histórico", f"{margen_real_pct:.1f}%")
    col10.metric("Margen Proyectado Solufar", f"{margen_solufar_pct:.1f}%", f"+{(margen_solufar_pct - margen_real_pct):.1f}%")

    st.markdown("### 📋 Desglose de Impacto por SKU")
    
    # 🔴 PREPARAR TABLA RESUMEN CON LAS NUEVAS 5 COLUMNAS
    resumen_sku = df_calc.groupby('Nombre_Producto').agg(
        Cajas_Vendidas=('Ctdad_Ordenada', 'sum'),
        Meses_Inercia=('Cambio_Precio', lambda x: (x == 0).sum()),
        Fuga=('Fuga_Valor', 'sum'),
        Perdida=('Perdida_Oportunidad', 'sum')
    ).reset_index().sort_values(by='Fuga', ascending=False)
    
    resumen_sku.rename(columns={
        'Nombre_Producto': 'Medicamento',
        'Cajas_Vendidas': 'Volumen (Cajas)',
        'Meses_Inercia': 'Inercia (Meses sin actualizar)',
        'Fuga': 'Fuga Recuperable (CLP)',
        'Perdida': 'Pérdida Oportunidad (CLP)'
    }, inplace=True)

    st.dataframe(
        resumen_sku.style.format({
            'Volumen (Cajas)': '{:,.0f}',
            'Fuga Recuperable (CLP)': '${:,.0f}',
            'Pérdida Oportunidad (CLP)': '${:,.0f}'
        }),
        use_container_width=True,
        hide_index=True
    )

# =============================================================================
# PESTAÑA 2: AUDITORÍA DETALLADA POR SKU
# =============================================================================
with tab2:
    lista_productos = df_trazabilidad['Nombre_Producto'].dropna().unique().tolist()
    sku_seleccionado = st.selectbox("Selecciona un Medicamento a auditar:", lista_productos)

    df_filtrado = df_trazabilidad[df_trazabilidad['Nombre_Producto'] == sku_seleccionado].copy()

    # GRÁFICO
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    colores_marcadores = np.where(df_filtrado['Driver_Precio'] == 'MANDATO_HUMANO', '#E74C3C', '#2E86C1')

    fig.add_trace(go.Bar(
        x=df_filtrado['Mes_Ano'], y=df_filtrado['Ctdad_Ordenada'], name="Ventas (Cajas)", marker_color='lightblue', opacity=0.4
    ), secondary_y=True)

    fig.add_trace(go.Scatter(
        x=df_filtrado['Mes_Ano'], y=df_filtrado['Precio_Solufar_Emitido'], mode='lines+markers', name='Precio Final Emitido', 
        line=dict(color='#2E86C1', width=3), marker=dict(size=12, color=colores_marcadores, line=dict(width=2, color='white')), 
        customdata=df_filtrado['Explicacion_Dinamica'],
        hovertemplate="%{customdata}<br><br><b>Precio Final:</b> $%{y:,.0f}<extra></extra>"
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df_filtrado['Mes_Ano'], y=df_filtrado['Precio_Unitario'], name="Precio Inercial (Cobrado)", line=dict(color='gray', width=2, dash='dash')
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df_filtrado['Mes_Ano'], y=df_filtrado['Costo_Unitario'], mode='lines', name='Costo Adquisición', line=dict(color='gray', width=4, dash='dot'), 
        hovertemplate="Costo: $%{y:,.0f}<extra></extra>"
    ), secondary_y=False)

    fig.update_layout(
        title=f"<b>Auditoría Algorítmica: {sku_seleccionado}</b>", hovermode="x unified", plot_bgcolor="white", 
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(title_text="<b>Precio ($ CLP)</b>", tickformat="$,.0f", secondary_y=False, gridcolor='lightgray')
    fig.update_yaxes(title_text="<b>Volumen (Cajas)</b>", secondary_y=True, showgrid=False)
    fig.update_xaxes(title_text="<b>Mes</b>", tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)

    # BITÁCORA HTML RENDERIZADA CON LA FUNCIÓN SEGURA
    st.markdown("### 📝 Bitácora de Decisiones Algorítmicas")
    df_filtrado['Mes_Str'] = pd.to_datetime(df_filtrado['Mes_Ano']).dt.strftime('%Y-%m')
    
    tabla_html_segura = renderizar_tabla_html(df_filtrado)
    st.markdown(tabla_html_segura, unsafe_allow_html=True)
