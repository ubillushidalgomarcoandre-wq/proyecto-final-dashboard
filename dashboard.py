"""
FASE 5 - DASHBOARD INTERACTIVO
Proyecto: Análisis de Datos Empresariales mediante Minería de Datos

Dashboard ejecutivo construido con Streamlit + Plotly.

Para ejecutarlo:
    streamlit run dashboard.py

Requiere (si no los tienes instalados):
    pip install streamlit plotly pandas
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Ejecutivo - Superstore",
    page_icon="📊",
    layout="wide",
)

# IMPORTANTE: ajusta esta ruta a donde tengas tu dataset limpio
RUTA_DATOS = "superstore_clean.csv"


@st.cache_data
def cargar_datos(ruta):
    df = pd.read_csv(ruta)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df


df = cargar_datos(RUTA_DATOS)

# -----------------------------------------------------------------
# BARRA LATERAL - FILTROS (SEGMENTADORES)
# -----------------------------------------------------------------
st.sidebar.header("🔎 Filtros")

regiones = sorted(df["Region"].unique())
region_sel = st.sidebar.multiselect("Región", regiones, default=regiones)

categorias = sorted(df["Category"].unique())
categoria_sel = st.sidebar.multiselect("Categoría", categorias, default=categorias)

fecha_min = df["Order Date"].min().date()
fecha_max = df["Order Date"].max().date()
rango_fechas = st.sidebar.date_input(
    "Rango de fechas", value=(fecha_min, fecha_max),
    min_value=fecha_min, max_value=fecha_max
)

# Aplicar filtros
df_filtrado = df[
    (df["Region"].isin(region_sel)) &
    (df["Category"].isin(categoria_sel))
]

if len(rango_fechas) == 2:
    inicio, fin = rango_fechas
    df_filtrado = df_filtrado[
        (df_filtrado["Order Date"].dt.date >= inicio) &
        (df_filtrado["Order Date"].dt.date <= fin)
    ]

if df_filtrado.empty:
    st.warning("No hay datos para los filtros seleccionados. Ajusta los filtros en la barra lateral.")
    st.stop()

# -----------------------------------------------------------------
# TÍTULO
# -----------------------------------------------------------------
st.title("📊 Dashboard Ejecutivo - Análisis de Ventas")
st.markdown("Análisis interactivo de ventas, clientes y rentabilidad — Dataset *Sample Superstore*")

# -----------------------------------------------------------------
# KPIs PRINCIPALES
# -----------------------------------------------------------------
total_ventas = df_filtrado["Sales"].sum()
total_clientes = df_filtrado["Customer Name"].nunique()
promedio_ventas = df_filtrado["Sales"].mean()
producto_top = df_filtrado.groupby("Product Name")["Sales"].sum().idxmax()
total_ganancia = df_filtrado["Profit"].sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Total de Ventas", f"${total_ventas:,.0f}")
col2.metric("👥 Total de Clientes", f"{total_clientes:,}")
col3.metric("📈 Promedio por Venta", f"${promedio_ventas:,.2f}")
col4.metric("💵 Ganancia Total", f"${total_ganancia:,.0f}")
col5.metric("🏆 Producto Más Vendido", producto_top[:20] + ("..." if len(producto_top) > 20 else ""))

st.divider()

# -----------------------------------------------------------------
# FILA 1: VENTAS POR REGIÓN (barras) + VENTAS POR CATEGORÍA (circular)
# -----------------------------------------------------------------
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("Ventas por Región")
    ventas_region = df_filtrado.groupby("Region")["Sales"].sum().sort_values(ascending=False).reset_index()
    fig_region = px.bar(
        ventas_region, x="Region", y="Sales",
        color="Region", text_auto=".2s",
        labels={"Sales": "Ventas ($)"},
    )
    fig_region.update_layout(showlegend=False)
    st.plotly_chart(fig_region, use_container_width=True)

with col_der:
    st.subheader("Distribución de Ventas por Categoría")
    ventas_cat = df_filtrado.groupby("Category")["Sales"].sum().reset_index()
    fig_cat = px.pie(
        ventas_cat, names="Category", values="Sales",
        hole=0.4,
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# -----------------------------------------------------------------
# FILA 2: EVOLUCIÓN TEMPORAL DE VENTAS (línea)
# -----------------------------------------------------------------
st.subheader("Tendencia Temporal de Ventas")
ventas_mes = (
    df_filtrado.groupby(df_filtrado["Order Date"].dt.to_period("M"))["Sales"]
    .sum()
    .reset_index()
)
ventas_mes["Order Date"] = ventas_mes["Order Date"].dt.to_timestamp()

fig_tendencia = px.line(
    ventas_mes, x="Order Date", y="Sales",
    markers=True, labels={"Sales": "Ventas ($)", "Order Date": "Fecha"},
)
st.plotly_chart(fig_tendencia, use_container_width=True)

# -----------------------------------------------------------------
# FILA 3: TOP PRODUCTOS Y TOP CLIENTES
# -----------------------------------------------------------------
col_izq2, col_der2 = st.columns(2)

with col_izq2:
    st.subheader("Top 10 Productos Más Vendidos")
    top_productos = (
        df_filtrado.groupby("Product Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig_prod = px.bar(
        top_productos, x="Sales", y="Product Name",
        orientation="h", labels={"Sales": "Ventas ($)", "Product Name": ""},
    )
    fig_prod.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_prod, use_container_width=True)

with col_der2:
    st.subheader("Top 10 Clientes Más Importantes")
    top_clientes = (
        df_filtrado.groupby("Customer Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig_cli = px.bar(
        top_clientes, x="Sales", y="Customer Name",
        orientation="h", labels={"Sales": "Ventas ($)", "Customer Name": ""},
    )
    fig_cli.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_cli, use_container_width=True)

# -----------------------------------------------------------------
# FILA 4: RENTABILIDAD POR CATEGORÍA
# -----------------------------------------------------------------
st.subheader("Rentabilidad por Categoría")
cat_resumen = df_filtrado.groupby("Category").agg(
    Ventas=("Sales", "sum"),
    Ganancia=("Profit", "sum")
).reset_index()

fig_rent = px.bar(
    cat_resumen, x="Category", y=["Ventas", "Ganancia"],
    barmode="group", labels={"value": "Monto ($)", "Category": "Categoría"},
)
st.plotly_chart(fig_rent, use_container_width=True)

# -----------------------------------------------------------------
# TABLA DE DATOS (opcional, al final)
# -----------------------------------------------------------------
with st.expander("📋 Ver datos filtrados en tabla"):
    st.dataframe(df_filtrado.head(200))

st.caption(f"Mostrando {len(df_filtrado):,} de {len(df):,} registros totales según los filtros aplicados.")
