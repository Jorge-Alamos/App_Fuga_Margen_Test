import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuración de página
st.set_page_config(page_title="Gemelo Digital Solufar", layout="wide")

# 1. CARGA LIGERA DE DATOS
@st.cache_data(ttl=60)
def load_data():
    url = "https://raw.githubusercontent.com/Jorge-Alamos/App_Fuga_Margen_Test/main/resultados_solufar_multisku.csv"
    df = pd.read_csv(url)
    return df

df_trazabilidad = load_data()

st.title("📊 Auditoría de Precios: Gemelo Digital Solufar")
st.markdown("Esta plataforma lee el modelo de 4 Expertos orquestados y leyes de blindaje desde Google Colab.")

# 2. SELECTOR DE MEDICAMENTOS
lista_productos = df_trazabilidad['Nombre_Producto'].dropna().unique().tolist()
sku_seleccionado = st.selectbox("Selecciona un Medicamento a auditar:", lista_productos)

# Filtramos la tabla web solo para el producto seleccionado
df_filtrado = df_trazabilidad[df_trazabilidad['Nombre_Producto'] == sku_seleccionado].copy()

# 3. CONSTRUCCIÓN DEL GRÁFICO 
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

# 4. BITÁCORA DE DECISIONES ALGORÍTMICAS (TABLA HTML RENDERIZADA)
st.markdown("### 📝 Bitácora de Decisiones Algorítmicas")

# Formatear la fecha para que solo muestre Año-Mes
df_filtrado['Mes_Str'] = pd.to_datetime(df_filtrado['Mes_Ano']).dt.strftime('%Y-%m')

# Construcción de la tabla (sin sangrías problemáticas para Markdown)
tabla_html = """<style>
.bitacora-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Segoe UI', Arial, sans-serif;
    background-color: white;
    border: 1px solid #e0e0e0;
}
.bitacora-table th {
    background-color: #34495e;
    color: white;
    text-align: left;
    padding: 12px;
    font-size: 14px;
}
.bitacora-table td {
    border-bottom: 1px solid #e0e0e0;
    padding: 12px;
    font-size: 13px;
    color: #2c3e50;
    vertical-align: top;
}
.bitacora-table tr:hover {
    background-color: #f8f9fa;
}
</style>
<table class="bitacora-table">
<thead>
<tr>
<th>Mes</th>
<th>Costo Adquisición</th>
<th>Precio Histórico (Cobrado)</th>
<th>Precio Óptimo (Solufar)</th>
<th>Margen Proyectado</th>
<th>Diagnóstico de Capas (Algoritmo)</th>
</tr>
</thead>
<tbody>"""

# Iterar sobre las filas estructurando el HTML en una sola línea continua para evitar el parseo de código
for _, row in df_filtrado.iterrows():
    explicacion = row['Explicacion_Dinamica'] if pd.notna(row['Explicacion_Dinamica']) else "Sin datos"
    
    fila = f"<tr><td>{row['Mes_Str']}</td><td>${row['Costo_Unitario']:,.0f}</td><td>${row['Precio_Unitario']:,.0f}</td><td style='color: #2E86C1; font-weight: bold;'>${row['Precio_Solufar_Emitido']:,.0f}</td><td>{row['Margen_Pct_Final']:.1f}%</td><td>{explicacion}</td></tr>"
    tabla_html += fila

tabla_html += "</tbody></table>"

# Renderizar el HTML en Streamlit
st.markdown(tabla_html, unsafe_allow_html=True)
