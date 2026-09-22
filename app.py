import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuración de página
st.set_page_config(page_title="Gemelo Digital Solufar", layout="wide")

# 1. CARGA LIGERA DE DATOS
# Como el CSV ya viene procesado desde Colab, esto cargará instantáneamente
@st.cache_data(ttl=60) # Recarga caché cada minuto
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

# 3. CONSTRUCCIÓN DEL GRÁFICO (Sin lógica pesada, solo visual)
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Colores de marcadores: Rojo si mandó el humano, Azul si mandó la máquina
colores_marcadores = np.where(df_filtrado['Driver_Precio'] == 'MANDATO_HUMANO', '#E74C3C', '#2E86C1')

# Barras de Volumen
fig.add_trace(go.Bar(
    x=df_filtrado['Mes_Ano'], 
    y=df_filtrado['Ctdad_Ordenada'], 
    name="Ventas (Cajas)", 
    marker_color='lightblue', 
    opacity=0.4
), secondary_y=True)

# Línea Principal de Precio Solufar (NUEVO: Lee el customdata directo del CSV)
fig.add_trace(go.Scatter(
    x=df_filtrado['Mes_Ano'], 
    y=df_filtrado['Precio_Solufar_Emitido'], 
    mode='lines+markers', 
    name='Precio Final Emitido', 
    line=dict(color='#2E86C1', width=3), 
    marker=dict(size=12, color=colores_marcadores, line=dict(width=2, color='white')), 
    customdata=df_filtrado['Explicacion_Dinamica'],  # <--- Lee la bitácora armada en Colab
    hovertemplate="%{customdata}<br><br><b>Precio Final:</b> $%{y:,.0f}<extra></extra>"
), secondary_y=False)

# Línea Inercial (El pasado)
fig.add_trace(go.Scatter(
    x=df_filtrado['Mes_Ano'], 
    y=df_filtrado['Precio_Unitario'], 
    name="Precio Inercial (Cobrado)", 
    line=dict(color='gray', width=2, dash='dash')
), secondary_y=False)

# Línea de Costos
fig.add_trace(go.Scatter(
    x=df_filtrado['Mes_Ano'], 
    y=df_filtrado['Costo_Unitario'], 
    mode='lines', 
    name='Costo Adquisición', 
    line=dict(color='gray', width=4, dash='dot'), 
    hovertemplate="Costo: $%{y:,.0f}<extra></extra>"
), secondary_y=False)

# Diseño del gráfico
fig.update_layout(
    title=f"<b>Auditoría Algorítmica: {sku_seleccionado}</b>", 
    hovermode="x unified", 
    plot_bgcolor="white", 
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
fig.update_yaxes(title_text="<b>Precio ($ CLP)</b>", tickformat="$,.0f", secondary_y=False, gridcolor='lightgray')
fig.update_yaxes(title_text="<b>Volumen (Cajas)</b>", secondary_y=True, showgrid=False)
fig.update_xaxes(title_text="<b>Mes</b>", tickangle=-45)

# Renderizamos en Streamlit
st.plotly_chart(fig, use_container_width=True)

# 4. TABLA DE DATOS RESUMIDA Opcional
st.markdown("### 📋 Resumen de Métricas Clave")
columnas_tabla = ['Mes_Ano', 'Costo_Unitario', 'Precio_Solufar_Emitido', 'Margen_Pct_Final', 'Driver_Precio']
st.dataframe(df_filtrado[columnas_tabla].tail(6), use_container_width=True)
