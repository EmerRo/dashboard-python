import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

def conectar_a_base_de_datos():
    try:
        engine = create_engine('mssql+pyodbc://DESKTOP-6F5MTV8/AdventureWorks2012?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
        return engine
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {str(e)}")
        return None

def ejecutar_consulta_sql(engine, consulta):
    try:
        with engine.connect() as connection:
            df = pd.read_sql(consulta, connection)
        return df
    except Exception as e:
        st.error(f"Error al ejecutar la consulta SQL: {str(e)}")
        return pd.DataFrame()

def crear_grafico(df, tipo_grafico):
    if df.empty:
        st.warning("El DataFrame está vacío. No se puede crear el gráfico.")
        return None

    if tipo_grafico == "Gráfico de Barras":
        return px.bar(df, x=df.columns[0], y=df.columns[1], title=f'{tipo_grafico} - {df.columns[0]} vs {df.columns[1]}')
    elif tipo_grafico == "Gráfico Lineal":
        return px.line(df, x=df.columns[0], y=df.columns[1], title=f'{tipo_grafico} - {df.columns[0]} vs {df.columns[1]}')
    elif tipo_grafico == "Histograma":
        return px.histogram(df, x=df.columns[0], title=f'{tipo_grafico} - {df.columns[0]}')
    elif tipo_grafico == "Gráfico Circular (Pie)":
        return px.pie(df, names=df.columns[0], title=f'{tipo_grafico} - {df.columns[0]}')
    elif tipo_grafico == "Gráfico de Embudo":
        return px.funnel(df, x=df.columns[0], y=df.columns[1], title=f'{tipo_grafico} - {df.columns[0]} vs {df.columns[1]}')
    elif tipo_grafico == "Gráfico de Dispersión":
        columnas_numericas = df.select_dtypes(include=['number']).columns
        if len(columnas_numericas) >= 2:
            max_size = df[columnas_numericas[1]].max() if len(columnas_numericas) > 1 else 1
            return px.scatter(df, x=df.columns[0], y=df.columns[1], size=columnas_numericas[1], title=f'{tipo_grafico} - {df.columns[0]} vs {df.columns[1]}', size_max=max_size)
        else:
            st.warning("No hay suficientes columnas numéricas para crear un gráfico de dispersión.")
    elif tipo_grafico == "Diagrama de Caja":
        return px.box(df, x=df.columns[0], y=df.columns[1], title=f'{tipo_grafico} - {df.columns[0]} vs {df.columns[1]}')
    elif tipo_grafico == "Gráfico de Área":
        return px.area(df, x=df.columns[0], y=df.columns[1], title=f'{tipo_grafico} - {df.columns[0]} vs {df.columns[1]}')
    elif tipo_grafico == "Gráfico de Radar":
        return px.line_polar(df, r=df.columns[1], theta=df.columns[0], title=f'{tipo_grafico} - {df.columns[0]} vs {df.columns[1]}')
    elif tipo_grafico == "Gráfico de Cascada":
        return px.bar(df, x=df.columns[0], y=df.columns[1], title=f'{tipo_grafico} - {df.columns[0]} vs {df.columns[1]}', text=df.columns[1], color=df.columns[1])
    elif tipo_grafico == "Sparklines":
        return crear_sparklines(df)
    else:
        st.warning("Tipo de gráfico no reconocido.")
        return None

def crear_sparklines(df):
    fig = go.Figure()
    for col in df.columns:
        if df[col].dtype in [int, float]:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col))
    fig.update_layout(title='Sparklines - Tendencias de Métricas', xaxis_title='Fecha', yaxis_title='Valor')
    return fig

# Preguntas para la tabla Sales.SalesOrderHeader
preguntas_sales_order = [
    "¿Cuál es el total de ventas por año?",
    "¿Cuántos pedidos se realizaron por cliente?",
    # Agrega más preguntas según sea necesario
]

# Preguntas para la tabla Sales.Customer
preguntas_customer = [
    "¿Cuántos clientes tenemos en total?",
    "¿Cuál es la distribución de clientes por región?",
    # Agrega más preguntas según sea necesario
]

# Preguntas para la tabla Production.Product
preguntas_product = [
    "¿Cuántos productos tenemos en cada subcategoría?",
    "¿Cuál es la subcategoría más común de productos?",
    # Agrega más preguntas según sea necesario
]

# Mapa de tablas a preguntas
preguntas_por_tabla = {
    "Sales.SalesOrderHeader": preguntas_sales_order,
    "Sales.Customer": preguntas_customer,
    "Production.Product": preguntas_product,
}

# 'este lo expongo yo
# Configuración de la página
st.set_page_config(
    page_title="AdventureWorks Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Conexión a la base de datos
engine = conectar_a_base_de_datos()

if engine:
    # Obtener información de las tablas incluyendo el esquema
    consulta_tablas = "SELECT table_schema, table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'"
    informacion_tablas = ejecutar_consulta_sql(engine, consulta_tablas)

    # Obtener información de las tablas importantes
    tablas_importantes = ["Sales.SalesOrderHeader", "Sales.Customer", "Production.Product"]

    # Iniciar la aplicación Streamlit
    st.title("Dashboard de AdventureWorks2012 📊")

    # Panel de Ciencia de Datos en la parte izquierda
    st.sidebar.title("Ciencia de Datos 📊")

    # Dropdown para seleccionar la tabla y el esquema en el panel izquierdo
    fila_seleccionada = st.sidebar.selectbox("Seleccione una tabla", [] if informacion_tablas.empty else informacion_tablas.apply(lambda x: f"{x['table_schema']}.{x['table_name']}", axis=1), index=0 if informacion_tablas.empty else None)
    # 'hasta qui

    # Separar el esquema y el nombre de la tabla
    if not informacion_tablas.empty and fila_seleccionada:
        esquema_seleccionado, tabla_seleccionada = fila_seleccionada.split('.')
    else:
        esquema_seleccionado, tabla_seleccionada = None, None

    # Mostrar información de las tablas en el panel izquierdo
    st.sidebar.subheader("Información de Tablas")
    st.sidebar.write(informacion_tablas)

    # Mostrar las tablas importantes y preguntas relacionadas
    st.sidebar.subheader("Tablas Importantes 🌟")
    tabla_elegida = st.sidebar.selectbox("Seleccione una tabla importante", tablas_importantes)

    # Obtener preguntas para la tabla seleccionada
    preguntas = preguntas_por_tabla.get(tabla_elegida, [])

    # Mostrar preguntas en el panel izquierdo
    st.sidebar.subheader("Preguntas Relacionadas")
    pregunta_seleccionada = st.sidebar.selectbox("Seleccione una pregunta", preguntas, index=0 if preguntas else None)

    # Consultar datos para la tabla importante seleccionada
    consulta_datos_tabla_importante = f"SELECT TOP 5 * FROM {tabla_elegida}"
    df_tabla_importante = ejecutar_consulta_sql(engine, consulta_datos_tabla_importante)

    # Mostrar información de la tabla importante en la columna izquierda
    st.sidebar.subheader(f"Información de {tabla_elegida}")
    st.sidebar.write(df_tabla_importante)

    # Consultar datos
    consulta_datos = f"SELECT TOP 100 * FROM {esquema_seleccionado}.{tabla_seleccionada}" if esquema_seleccionado and tabla_seleccionada else None

    # Modificar la consulta para excluir la columna problemática (reemplazar 'columna_problema' con el nombre real)
    consulta_datos = consulta_datos.replace(", columna_problema", "") if consulta_datos else None

    df = ejecutar_consulta_sql(engine, consulta_datos) if consulta_datos else pd.DataFrame()

    # Dividir la interfaz en dos columnas
    col1, col2 = st.columns(2)

    # Mostrar información de la tabla en la columna izquierda
    col1.subheader("Información de la Tabla")
    col1.write(df)

    # Slider para seleccionar el número de filas a mostrar
    num_filas = st.slider("Número de Filas a Mostrar", min_value=1, max_value=100, value=10)
    df_muestra = ejecutar_consulta_sql(engine, f"{consulta_datos.replace('TOP 100', f'TOP {num_filas}')}") if consulta_datos else pd.DataFrame()

    # Dropdown para seleccionar el tipo de gráfico en la parte inferior
    tipo_grafico_seleccionado = st.selectbox("Seleccione un tipo de gráfico", ["Gráfico de Barras", "Gráfico Lineal", "Histograma", "Gráfico Circular (Pie)", "Gráfico de Embudo", "Gráfico de Dispersión", "Sparklines", "Diagrama de Caja", "Gráfico de Área", "Gráfico de Radar", "Gráfico de Cascada"])

    # Gráfico correspondiente según la selección en la parte inferior
    st.subheader(f'{tipo_grafico_seleccionado} - {fila_seleccionada}' if fila_seleccionada else tipo_grafico_seleccionado)

    # Crear y mostrar el gráfico
    figura = crear_grafico(df_muestra, tipo_grafico_seleccionado)
    if figura is not None:
        st.plotly_chart(figura)

    # Ejecutar análisis de datos basado en la pregunta seleccionada
    if pregunta_seleccionada and tabla_elegida == "Sales.SalesOrderHeader":
        if pregunta_seleccionada == "¿Cuál es el total de ventas por año?":
            # Consulta SQL para obtener el total de ventas por año
            consulta_ventas_por_anio = f"""
            SELECT YEAR(OrderDate) AS Anio, SUM(TotalDue) AS TotalVentas
            FROM {tabla_elegida}
            GROUP BY YEAR(OrderDate)
            ORDER BY Anio
            """
            
            # Ejecutar la consulta
            df_ventas_por_anio = ejecutar_consulta_sql(engine, consulta_ventas_por_anio)

            # Mostrar los resultados
            st.sidebar.write("Respuesta:")
            st.sidebar.write(df_ventas_por_anio)

            # Crear un gráfico de barras con los resultados
            st.sidebar.subheader("Gráfico de Barras - Total de Ventas por Año")
            fig_ventas_por_anio = px.bar(df_ventas_por_anio, x='Anio', y='TotalVentas', title='Total de Ventas por Año')
            st.sidebar.plotly_chart(fig_ventas_por_anio)

    # Ejecutar análisis de datos para la tabla Sales.Customer
    elif pregunta_seleccionada and tabla_elegida == "Sales.Customer":
        if pregunta_seleccionada == "¿Cuántos clientes tenemos en total?":
            # Consulta SQL para obtener el número total de clientes
            consulta_clientes_totales = f"""
            SELECT COUNT(*) AS TotalClientes
            FROM {tabla_elegida}
            """
            
            # Ejecutar la consulta
            df_clientes_totales = ejecutar_consulta_sql(engine, consulta_clientes_totales)

            # Mostrar los resultados
            st.sidebar.write("Respuesta:")
            st.sidebar.write(df_clientes_totales)

    # Ejecutar análisis de datos para la tabla Production.Product
    elif pregunta_seleccionada and tabla_elegida == "Production.Product":
        if pregunta_seleccionada == "¿Cuántos productos tenemos en cada subcategoría?":
            # Consulta SQL para obtener el número de productos por subcategoría
            consulta_productos_por_subcategoria = f"""
            SELECT ProductSubcategoryID, COUNT(*) AS TotalProductos
            FROM {tabla_elegida}
            GROUP BY ProductSubcategoryID
            """
            
            # Ejecutar la consulta
            df_productos_por_subcategoria = ejecutar_consulta_sql(engine, consulta_productos_por_subcategoria)

            # Mostrar los resultados
            st.sidebar.write("Respuesta:")
            st.sidebar.write(df_productos_por_subcategoria)

            # Crear un gráfico de barras con los resultados
            st.sidebar.subheader("Gráfico de Barras - Total de Productos por Subcategoría")
            fig_productos_por_subcategoria = px.bar(df_productos_por_subcategoria, x='ProductSubcategoryID', y='TotalProductos', title='Total de Productos por Subcategoría')
            st.sidebar.plotly_chart(fig_productos_por_subcategoria)