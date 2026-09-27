# =============================================================================
# MÓDULO PÁGINA 2: vista_asignacion.py
# Objetivo: Desplegar la Interfaz para Asignación de Precios (t+1) con diseño
#           amplio, descongestionado y con márgenes extendidos.
# =============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import estilos_ui


# -----------------------------------------------------------------------------
# PARTE 1: Validador en vivo de Reglas de Negocio
# -----------------------------------------------------------------------------
def evaluar_regla_en_vivo(precio_elegido: float, costo: float, piso_ley: float, margen_cat: float) -> dict:
    """Calcula en tiempo real el margen, la ganancia por caja y el cumplimiento del Piso."""
    ganancia = precio_elegido - costo
    margen_pct = ((ganancia / precio_elegido) * 100.0) if precio_elegido > 0 else 0.0
    respeta_piso = precio_elegido >= piso_ley
    cumple_meta = margen_pct >= (margen_cat - 0.1)

    if not respeta_piso:
        texto = f"🚨 Perfora Piso de Blindaje Capa 6 (${piso_ley:,.0f})"
        ok = False
    elif cumple_meta:
        texto = f"✅ Cumple margen mínimo ({margen_cat:.0f}%) y respeta Piso (${piso_ley:,.0f})"
        ok = True
    else:
        texto = f"✅ Respeta Piso (${piso_ley:,.0f}) | En rampa a meta categoría ({margen_cat:.0f}%)"
        ok = True

    return {
        "Margen_Pct": round(margen_pct, 1),
        "Ganancia_Caja": round(ganancia, 0),
        "Estado_OK": ok,
        "Texto_Regla": texto
    }


# -----------------------------------------------------------------------------
# PARTE 2: Constructor del Gráfico Histórico + Proyección Mes Entrante (t+1)
# -----------------------------------------------------------------------------
def crear_grafico_historico_y_t1(df_trazabilidad: pd.DataFrame, row_dec: pd.Series, precio_activo: float):
    """Toma la historia del Cuaderno 1 y acopla dinámicamente la estrella ★ del mes t+1."""
    sku = row_dec['Nombre_Producto']
    col_precio_motor = 'Precio_Motor_Emitido' if 'Precio_Motor_Emitido' in df_trazabilidad.columns else 'Precio_Solufar_Emitido'

    df_real = df_trazabilidad[df_trazabilidad['Nombre_Producto'] == sku].copy()
    df_real['Mes_Ano'] = pd.to_datetime(df_real['Mes_Ano'])
    df_real = df_real.sort_values('Mes_Ano').reset_index(drop=True)
    df_real['Mes_Str'] = df_real['Mes_Ano'].dt.strftime('%Y-%m')

    mes_t1_str = pd.to_datetime(row_dec['Mes_Proyectado']).strftime('%Y-%m')
    costo_t1 = float(row_dec['KPI_Costo_Actual'])

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. Barras celestes de ventas históricas
    fig.add_trace(
        go.Bar(
            x=df_real['Mes_Str'], y=df_real['Ctdad_Ordenada'],
            name="Ventas históricas (Cajas)", marker_color='#BAE6FD', opacity=0.55
        ),
        secondary_y=True
    )

    # 2. Línea punteada de Costo de Adquisición
    x_costo = df_real['Mes_Str'].tolist() + [mes_t1_str]
    y_costo = df_real['Costo_Unitario'].tolist() + [costo_t1]
    fig.add_trace(
        go.Scatter(
            x=x_costo, y=y_costo,
            mode='lines', name='Costo',
            line=dict(color='#94A3B8', width=2.5, dash='dot'),
            hovertemplate="Costo: $%{y:,.0f}<extra></extra>"
        ),
        secondary_y=False
    )

    # 3. Línea discontinua de Precio Cobrado en mostrador
    fig.add_trace(
        go.Scatter(
            x=df_real['Mes_Str'], y=df_real['Precio_Unitario'],
            mode='lines', name='Cobrado',
            line=dict(color='#64748B', width=2, dash='dash'),
            hovertemplate="Cobrado: $%{y:,.0f}<extra></extra>"
        ),
        secondary_y=False
    )

    # 4. Línea azul sólida de Precio Sugerido histórico
    fig.add_trace(
        go.Scatter(
            x=df_real['Mes_Str'], y=df_real[col_precio_motor],
            mode='lines+markers', name='Sugerido histórico',
            line=dict(color='#2563EB', width=3),
            marker=dict(size=6, color='#2563EB'),
            hovertemplate="Sugerido: $%{y:,.0f}<extra></extra>"
        ),
        secondary_y=False
    )

    # 5. Tramo punteado hacia el Mes Entrante (t+1) rematado en Estrella ★
    if not df_real.empty:
        x_tramo = [df_real['Mes_Str'].iloc[-1], mes_t1_str]
        y_tramo = [float(df_real[col_precio_motor].iloc[-1]), float(precio_activo)]

        fig.add_trace(
            go.Scatter(
                x=x_tramo, y=y_tramo,
                mode='lines+markers', name='Proyección t+1 ★',
                line=dict(color='#4F46E5', width=3, dash='dot'),
                marker=dict(symbol=['circle', 'star'], size=[6, 18], color='#4F46E5'),
                hovertemplate="Proyección t+1: $%{y:,.0f}<extra></extra>"
            ),
            secondary_y=False
        )

    fig.update_layout(
        title=dict(text="<b>Gráfico histórico y proyectado para el siguiente periodo</b>", font=dict(size=17, color="#0F172A")),
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=440,
        margin=dict(l=25, r=25, t=55, b=25),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=12.5))
    )
    fig.update_yaxes(title_text="<b>Precio ($ CLP)</b>", tickformat="$,.0f", secondary_y=False, gridcolor='#F1F5F9')
    fig.update_yaxes(title_text="<b>Cajas</b>", secondary_y=True, showgrid=False)
    fig.update_xaxes(tickangle=-45, showgrid=False)

    return fig


# -----------------------------------------------------------------------------
# PARTE 3: Renderizador Principal de la Interfaz de Asignación de Precios
# -----------------------------------------------------------------------------
def renderizar_vista_asignacion(df_trazabilidad: pd.DataFrame, df_decision: pd.DataFrame):
    """Construye la pantalla de decisión con espaciado amplio en 4 bloques claros."""
    # --- SUBPARTE 3.1: Memoria de sesión y barra selectora de SKU ---
    if 'confirmados_pos' not in st.session_state:
        st.session_state.confirmados_pos = {}
    if 'indice_sku' not in st.session_state:
        st.session_state.indice_sku = 0

    lista_skus = df_decision['Nombre_Producto'].tolist()
    total_skus = len(lista_skus)

    col_titulo, col_selector, col_progreso = st.columns([3.8, 4.7, 1.5], gap="medium")

    with col_titulo:
        st.markdown("<div style='font-size:21px; font-weight:800; color:#0F172A; padding-top:4px;'>Interfaz para asignación de precios</div>", unsafe_allow_html=True)

    with col_selector:
        def formato_estado_sku(nombre):
            icono = "🟢" if nombre in st.session_state.confirmados_pos else "🔴"
            estado = "Confirmado" if nombre in st.session_state.confirmados_pos else "Pendiente"
            return f"🔍 {icono} {estado} — {nombre}"

        sku_seleccionado = st.selectbox(
            "Selector SKU",
            options=lista_skus,
            index=st.session_state.indice_sku,
            format_func=formato_estado_sku,
            label_visibility="collapsed"
        )
        st.session_state.indice_sku = lista_skus.index(sku_seleccionado)

    with col_progreso:
        listos = len(st.session_state.confirmados_pos)
        st.markdown(
            f"<div style='background:#FFFFFF; border:1px solid #CBD5E1; padding:9px 14px; border-radius:8px; text-align:center; font-weight:700; font-size:13px; color:#334155;'>"
            f"Progreso: {listos} de {total_skus} listos</div>",
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Datos del medicamento activo
    row = df_decision[df_decision['Nombre_Producto'] == sku_seleccionado].iloc[0]
    costo = float(row['KPI_Costo_Actual'])
    piso = float(row.get('P_Ley_Piso', row['KPI_Piso_Seguridad']))
    p_actual = float(row['KPI_Precio_Actual'])
    m_cat = float(row.get('Margen_Teorico_Categoria_Pct', 25.0))

    # --- SUBPARTE 3.2: Fila Superior de 5 Tarjetas KPI con separación amplia ---
    k1, k2, k3, k4, k5 = st.columns(5, gap="medium")
    with k1:
        flecha = "▲" if row['KPI_Var_Costo_Pct'] >= 0 else "▼"
        estilos_ui.tarjeta_kpi(
            "Costo última compra", f"${costo:,.0f}",
            f"{flecha} {row['KPI_Var_Costo_Pct']:+.1f}% vs. ant. | 🛡️ Piso: ${piso:,.0f}",
            variante="blanca", color_sub="#16A34A"
        )
    with k2:
        estilos_ui.tarjeta_kpi(
            "Precio Venta actual", f"${p_actual:,.0f}",
            "Precio vigente en mostrador", variante="blanca"
        )
    with k3:
        estilos_ui.tarjeta_kpi(
            "Categorías & Rotación", f"{row['KPI_Categoria']}",
            f"📦 {row['KPI_Cajas_Ultimo_Mes']:.0f} cajas últ. mes (Prom: {row['KPI_Prom_Cajas_Hist']:.0f})",
            variante="blanca"
        )
    with k4:
        estilos_ui.tarjeta_kpi(
            "Sin cambios / Último", f"{int(row['KPI_Meses_Inercia'])}m ({row['KPI_Fecha_Ultimo_Cambio']})",
            f"Historia analizada: {int(row['Total_Meses_Historia'])} meses",
            variante="blanca"
        )
    with k5:
        estilos_ui.tarjeta_kpi(
            "Margen actual", f"{row['KPI_Margen_Actual_Pct']:.1f}%",
            f"Ganancia actual: ${row['KPI_Ganancia_Caja_Actual']:,.0f} / caja",
            variante="indigo", color_valor="#4338CA", color_sub="#4F46E5"
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # --- SUBPARTE 3.3: Estado de la estrategia elegida por el usuario ---
    clave_est = f"estrategia_{sku_seleccionado}"
    clave_man = f"manual_{sku_seleccionado}"

    if clave_est not in st.session_state:
        st.session_state[clave_est] = "Sugerido motor ★"
    if clave_man not in st.session_state:
        st.session_state[clave_man] = float(row['Precio_Sugerido'])

    estrategia_activa = st.session_state[clave_est]
    valor_manual = st.session_state[clave_man]

    if estrategia_activa == "Estrategia cauta":
        precio_elegido = float(row['Precio_Cauto'])
    elif estrategia_activa == "Estrategia agresiva":
        precio_elegido = float(row['Precio_Agresivo'])
    elif estrategia_activa == "✏️ Precio Manual":
        precio_elegido = float(valor_manual)
    else:
        precio_elegido = float(row['Precio_Sugerido'])

    # --- SUBPARTE 3.4: Bloque Central en 2 Columnas Amplias (Gráfico | Expertos) ---
    col_grafico, col_expertos = st.columns([5.6, 4.4], gap="large")

    with col_grafico:
        with st.container(border=True):
            fig_t1 = crear_grafico_historico_y_t1(df_trazabilidad, row, precio_elegido)
            st.plotly_chart(fig_t1, use_container_width=True)

    with col_expertos:
        w_el = int(row['Barra_Elasticidad_Pct'])
        w_es = int(row['Barra_Estrategia_Pct'])
        w_in = int(row['Barra_Inflacion_Pct'])
        w_st = int(row['Barra_Stock_Pct'])

        st.markdown(f"""
        <div style="background:#FFFFFF; padding:22px; border-radius:12px; border:1px solid #E2E8F0; min-height:472px;">
            <div style="font-size:17px; font-weight:800; color:#0F172A; margin-bottom:12px;">Análisis de los expertos</div>
            <div style="display:flex; height:14px; border-radius:6px; overflow:hidden; margin-bottom:8px;">
                <div style="width:{w_el}%; background:#3B82F6;"></div>
                <div style="width:{w_es}%; background:#8B5CF6;"></div>
                <div style="width:{w_in}%; background:#10B981;"></div>
                <div style="width:{w_st}%; background:#F59E0B;"></div>
            </div>
            <div style="font-size:12px; color:#475569; margin-bottom:16px; font-weight:600;">
                🧠 Elasticidad {w_el}% &nbsp;|&nbsp; 🏢 Estrategia {w_es}% &nbsp;|&nbsp; 📈 Inflación {w_in}% &nbsp;|&nbsp; 📦 Stock {w_st}%
            </div>
            <div class="expert-box" style="border-left: 4px solid #2563EB;">
                <div style="font-weight:700; color:#1D4ED8; margin-bottom:4px;">¿Qué detectó el motor?</div>
                <i>"{row['Texto_Azul_Deteccion']}"</i>
            </div>
            <div class="expert-box" style="border-left: 4px solid #7C3AED;">
                <div style="font-weight:700; color:#6D28D9; margin-bottom:4px;">¿Qué decisión se tomó en el tribunal?</div>
                <i>"{row['Texto_Morado_Tribunal']}"</i>
            </div>
            <div class="expert-box" style="border-left: 4px solid #10B981;">
                <div style="font-weight:700; color:#047857; margin-bottom:4px;">¿Por qué la farmacia está protegida?</div>
                <i>"{row['Texto_Verde_Proteccion']}"</i>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # --- SUBPARTE 3.5: Panel Inferior Descongestionado (2 Filas Amplias) ---
    with st.container(border=True):
        st.markdown("<div style='font-size:17px; font-weight:800; color:#0F172A; margin-bottom:10px;'>Asignar Precio para el Mes Entrante</div>", unsafe_allow_html=True)

        # Fila A dentro del panel: Selector y las 4 Tarjetas a ancho completo
        opcion_sel = st.radio(
            "Seleccione la estrategia comercial a aplicar:",
            options=["Estrategia cauta", "Sugerido motor ★", "Estrategia agresiva", "✏️ Precio Manual"],
            horizontal=True,
            key=clave_est
        )

        t1, t2, t3, t4 = st.columns(4, gap="medium")
        def estilo_borde(op):
            return "border:2px solid #4F46E5; background:#EEF2FF;" if opcion_sel == op else "border:1px solid #CBD5E1; background:#FFFFFF;"

        with t1:
            st.markdown(f"""
            <div class="strat-card" style="{estilo_borde('Estrategia cauta')}">
                <div style="font-size:13px; font-weight:700; color:#475569;">Estrategia cauta</div>
                <div style="font-size:26px; font-weight:800; color:#0F172A; margin:6px 0;">${row['Precio_Cauto']:,.0f}</div>
                <div style="font-size:12px; color:#64748B;">{row['Subtitulo_Cauto']} | Margen: {row['Margen_Cauto_Pct']:.1f}%</div>
            </div>""", unsafe_allow_html=True)

        with t2:
            st.markdown(f"""
            <div class="strat-card" style="{estilo_borde('Sugerido motor ★')}">
                <div style="font-size:13px; font-weight:700; color:#4F46E5;">Sugerido motor ★</div>
                <div style="font-size:26px; font-weight:800; color:#312E81; margin:6px 0;">${row['Precio_Sugerido']:,.0f}</div>
                <div style="font-size:12px; color:#4F46E5;">{row['Subtitulo_Sugerido']} | Margen: {row['Margen_Sugerido_Pct']:.1f}%</div>
            </div>""", unsafe_allow_html=True)

        with t3:
            st.markdown(f"""
            <div class="strat-card" style="{estilo_borde('Estrategia agresiva')}">
                <div style="font-size:13px; font-weight:700; color:#475569;">Estrategia agresiva</div>
                <div style="font-size:26px; font-weight:800; color:#0F172A; margin:6px 0;">${row['Precio_Agresivo']:,.0f}</div>
                <div style="font-size:12px; color:#64748B;">{row['Subtitulo_Agresivo']} | Margen: {row['Margen_Agresivo_Pct']:.1f}%</div>
            </div>""", unsafe_allow_html=True)

        with t4:
            st.number_input(
                "✏️ Ingresar Precio Manual ($ CLP):",
                min_value=0.0,
                step=100.0,
                key=clave_man
            )

        st.markdown("<hr style='border:none; border-top:1px solid #E2E8F0; margin:16px 0;'>", unsafe_allow_html=True)

        # Fila B dentro del panel: Validación, Nuevo Margen y Botón de Confirmación en 3 columnas amplias
        eval_vivo = evaluar_regla_en_vivo(precio_elegido, costo, piso, m_cat)
        nuevo_margen = eval_vivo["Margen_Pct"]
        nueva_ganancia = eval_vivo["Ganancia_Caja"]
        delta_un = precio_elegido - p_actual
        var_pct = ((delta_un / p_actual) * 100.0) if p_actual > 0 else 0.0

        c_alerta, c_margen, c_boton = st.columns([4.2, 3.0, 2.8], gap="large")

        with c_alerta:
            bg_alerta = "#ECFDF5" if eval_vivo["Estado_OK"] else "#FEF2F2"
            bd_alerta = "#6EE7B7" if eval_vivo["Estado_OK"] else "#FCA5A5"
            tx_alerta = "#065F46" if eval_vivo["Estado_OK"] else "#991B1B"

            st.markdown(f"""
            <div style="background:{bg_alerta}; border:1px solid {bd_alerta}; color:{tx_alerta}; padding:12px 16px; border-radius:10px; font-size:13px; font-weight:600;">
                <b>Validación de Regla de Negocio:</b><br>{eval_vivo["Texto_Regla"]}
            </div>
            """, unsafe_allow_html=True)

        with c_margen:
            st.markdown(f"""
            <div style="padding-top:2px;">
                <div style="font-size:13px; font-weight:700; color:#64748B; text-transform:uppercase;">Nuevo Margen Proyectado</div>
                <div style="font-size:28px; font-weight:800; color:#0F172A; line-height:1.15;">{nuevo_margen:.1f}% <span style="font-size:14px; color:#16A34A; font-weight:600;">({delta_un:+,.0f}/caja vs. actual)</span></div>
            </div>
            """, unsafe_allow_html=True)

        with c_boton:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-size:13px; font-weight:700; color:#475569;">Precio a aplicar: <b style="font-size:22px; color:#0F172A;">${precio_elegido:,.0f}</b></span>
                <span style="background:#E0F2FE; color:#0369A1; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:700;">
                    💵 +${nueva_ganancia:,.0f}/caja ({var_pct:+.1f}%)
                </span>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Confirmar y Guardar Precio ⏭️", type="primary", use_container_width=True):
                st.session_state.confirmados_pos[sku_seleccionado] = {
                    'Nombre_Producto': sku_seleccionado,
                    'Mes_Aplicacion': str(row['Mes_Proyectado'])[:7],
                    'Costo_Actual': costo,
                    'Precio_Anterior': p_actual,
                    'Estrategia_Elegida': opcion_sel,
                    'Precio_Confirmado_POS': precio_elegido,
                    'Nuevo_Margen_Pct': nuevo_margen,
                    'Ganancia_Caja_CLP': nueva_ganancia
                }
                if st.session_state.indice_sku + 1 < total_skus:
                    st.session_state.indice_sku += 1
                st.rerun()

    # --- SUBPARTE 3.6: Planilla descargable para el sistema de caja (POS) ---
    if len(st.session_state.confirmados_pos) > 0:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        with st.expander(f"📋 Planilla de Precios Confirmados para Caja POS ({len(st.session_state.confirmados_pos)} de {total_skus} SKUs listos)", expanded=True):
            df_pos = pd.DataFrame(list(st.session_state.confirmados_pos.values()))
            st.dataframe(df_pos, use_container_width=True, hide_index=True)
            st.download_button(
                label="📥 Descargar CSV de Precios Confirmados (POS)",
                data=df_pos.to_csv(index=False).encode('utf-8'),
                file_name="lista_precios_confirmados_pos.csv",
                mime="text/csv"
            )
