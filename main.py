import streamlit as st
from collections import Counter
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go

st.set_page_config(page_title="Demo modelo reserva", page_icon="./img/logo_pernexium.png", layout="wide")
num2curr = lambda x: f"${x:,.2f}"

# Menú lateral
st.sidebar.header("Navegación")
opcion = st.sidebar.selectbox("Selecciona una opción:", ["Principal", "Dashboard"])

if opcion == 'Principal':
    if 'ID' not in st.session_state:
        st.session_state.ID = 0
    
    def get_info(var):
        clientes_keys = list(clientes.keys())
        return clientes[clientes_keys[st.session_state.ID]][var]
    
    def simulate(datos, n_periodos = 12, simulaciones = 100, perc_cubierto = 70):
        # Crear la figura
        fig = go.Figure()
        
        
        pagos = datos["pagos"]
        probabilidad_pago = datos["probabilidad_pago"] / 100
        total_adeudado = datos["total_adeudado"]
        
        # Calcular la media y desviación estándar de los pagos
        media_pago = np.mean(pagos)
        desviacion_pago = np.std(pagos)
        
        # Realizar simulaciones
        caminos = []
        for _ in range(simulaciones):
            pagos_futuros = []
            for _ in range(n_periodos):
                if np.random.rand() < probabilidad_pago:
                    pago = np.random.normal(media_pago, desviacion_pago)
                    pagos_futuros.append(max(0, pago))  # Asegurar que el pago no sea negativo
                else:
                    pagos_futuros.append(0)
            caminos.append(np.cumsum(pagos_futuros))
        
        # Encontrar el periodo en el que el 95% de las simulaciones han cubierto el total adeudado
        caminos = np.array(caminos)
        
        
        # Agregar todas las simulaciones a la figura
        for camino in caminos:
            fig.add_trace(go.Scatter(
                x=np.arange(1, n_periodos + 1),
                y=camino,
                mode='lines',
                line=dict(width=1, color='rgba(0, 0,255,0.1)'),
                #name=f'{cliente} - Simulación'
            ))
        enter = False
        for paso_umbral in range(n_periodos):
            if sum(caminos.T[paso_umbral] > total_adeudado) > perc_cubierto:
                enter = True
                break
        paso_umbral = paso_umbral if enter else "None"
                
        # Agregar la línea vertical punteada en el periodo 95
        fig.add_trace(go.Scatter(
            x=[paso_umbral, paso_umbral],
            y=[0, np.max(caminos)],
            mode='lines',
            line=dict(color='red', dash='dash'),
            #name=f'{cliente} - {perc_cubierto}% Cubierto en Periodo {periodo_95}'
        ))
        
        # Configurar el diseño del gráfico
        fig.update_layout(
            title=f'Simulaciones de Pagos futuros ({perc_cubierto}% cubierto en Periodo {paso_umbral})',
            xaxis_title='Periodo',
            yaxis_title='Total pagado esperado ($)',
            showlegend=False
        )
    
        fig.update_layout(
            autosize=True,  # Ajustar automáticamente el tamaño
            #margin=dict(r=50, b=0)  # Eliminar márgenes para llenar el contenedor
        )
        
        return fig
    
    
    def seleccionar_planes_pago(monto_adeudado, seed):
        # Definir los planes de pago basados en el monto adeudado
        planes_pago = [
            f"3 pagos quincenales de {num2curr(monto_adeudado / 3)}",
            f"6 pagos mensuales de {num2curr(monto_adeudado / 6)}",
            f"2 pagos mensuales de {num2curr(monto_adeudado / 2)}",
            f"4 pagos semanales de {num2curr(monto_adeudado / 4)}",
            f"1 pago único de {num2curr(monto_adeudado)}",
            f"5 pagos quincenales de {num2curr(monto_adeudado / 5)}",
            f"12 pagos mensuales de {num2curr(monto_adeudado / 12)}",
            f"6 pagos quincenales de {num2curr(monto_adeudado / 6)}",
            f"8 pagos semanales de {num2curr(monto_adeudado / 8)}",
            f"2 pagos quincenales de {num2curr(monto_adeudado / 2)}"
        ]
    
        # Seleccionar 3 planes de pago aleatoriamente
        random.seed(seed)
        planes_seleccionados = random.sample(planes_pago, 3)
    
        return planes_seleccionados
        
    clientes = {
        "Carlos Pérez": {
            "pagos": [3200.50, 3300.75, 4400.00, 3100.25],
            "probabilidad_pago": 75.5,  # Porcentaje
            "probabilidad_contacto": 85.0,  # Porcentaje
            "total_adeudado": 10000.00,
            "vencido_actual": 5000.00,
            "promesas_pago": ["Sin promesa", "Cumplida", "promesa activa"],
            "reserva": 990,
            "pares_actuales": "150 a 179"
        },
        "Ana García": {
            "pagos": [5000.00, 2000.00, 1500.00, 2200.00],
            "probabilidad_pago": 68.2,
            "probabilidad_contacto": 70.3,
            "total_adeudado": 12000.00,
            "vencido_actual": 4000.00,
            "promesas_pago": ["No cumplida", "Cumplida"],
            "reserva": 1100,
            "pares_actuales": "120 a 149"
        },
        "Luis Rodríguez": {
            "pagos": [1900.00, 2950.00, 1325.00, 1880.00],
            "probabilidad_pago": 82.7,
            "probabilidad_contacto": 90.1,
            "total_adeudado": 8000.00,
            "vencido_actual": 3000.00,
            "promesas_pago": ["promesa mañana", "Sin promesa", "Cumplida"],
            "reserva": 770,
            "pares_actuales": "120 a 149"
        },
        "María López": {
            "pagos": [3500.00, 2600.00, 1550.50],
            "probabilidad_pago": 60.0,
            "probabilidad_contacto": 65.4,
            "total_adeudado": 9000.00,
            "vencido_actual": 6000.00,
            "promesas_pago": ["Sin promesa", "promesa activa", "No cumplida"],
            "reserva": 830,
            "pares_actuales": "150 a 179"
        },
        "Juan Martínez": {
            "pagos": [1100.00, 1150.00, 1050.50, 1250.00],
            "probabilidad_pago": 78.9,
            "probabilidad_contacto": 82.5,
            "total_adeudado": 24000.00,
            "vencido_actual": 4800.00,
            "promesas_pago": ["Cumplida", "promesa activa", "promesa mañana"],
            "reserva": 2100,
            "pares_actuales": "120 a 149"
        }
    }
    
    col1, col2 = st.columns(2)
    with col1:
        st.header(list(clientes.keys())[st.session_state.ID])
    with col2:
        st.session_state.ID = int(st.number_input("ID", step=1)) % 4
    
    
    
    col1, col2 = st.columns(2)
    with col1:
        
        #st.write("#")
    
        st.subheader("Planes de pago:")
    
        # Crear un DataFrame de pandas con los planes seleccionados
        df_planes = pd.DataFrame(seleccionar_planes_pago(get_info("total_adeudado"), st.session_state.ID), columns=["plan sugerido"])
        
        # Añadir una columna de prioridad como índice
        df_planes.index += 1
        df_planes.index.name = "prioridad"
    
        st.write(df_planes)
    
        col1_, col2_ = st.columns(2)
        
        col1_.metric("Total adeudado", f"{num2curr(get_info('total_adeudado'))}")
        col1_.metric("Reserva a liberar", f"{num2curr(get_info('reserva'))}")
        
        col2_.metric("Vencido actual", f"{num2curr(get_info('vencido_actual'))}")
        col2_.metric("Pares actuales", f"{get_info('pares_actuales')}")
    
        
        
        st.write("#")
        st.write("#")
        #st.write("#")
        #st.write("#")
        #st.write("#")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=list(range(1, len(get_info("pagos")) + 1)),  # Eje X como índice de pagos
            y=get_info("pagos"),  # Valores de los pagos
            mode='lines+markers',  # Líneas con puntos
            name='Pagos',
            line=dict(color='royalblue', width=2),
            marker=dict(size=8)
        ))
    
    
        fig.add_trace(go.Scatter(
            x=[1, len(get_info("pagos"))],
            y=[np.mean(get_info("pagos")), np.mean(get_info("pagos"))],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name=f'Pago medio: {num2curr(np.mean(get_info("pagos")))}'
        ))
    
        # Título y etiquetas
        fig.update_layout(
            title='Historial de Pagos',
            xaxis_title='Número de Pago',
            yaxis_title='Monto ($)',
            template='plotly_dark'
        )
    
        fig.update_layout(
            autosize=True,  # Ajustar automáticamente el tamaño
            #margin=dict(r=250, b=0)  # Eliminar márgenes para llenar el contenedor
        )
    
        st.plotly_chart(fig)
        
        
    
    with col2:
        #st.write("#")
        col1_, col2_ = st.columns(2)
        with col1_:
            st.metric("Probabilidad de pago", f"{get_info('probabilidad_pago')}%")
        with col2_:
            st.metric("Probabilidad de contacto", f"{get_info('probabilidad_contacto')}%")
    
    
        fig = simulate(clientes[list(clientes.keys())[st.session_state.ID]], n_periodos = 12, simulaciones = 100, perc_cubierto = 90)
    
        st.plotly_chart(fig)
    
        
    
        promesas = get_info("promesas_pago")
        
        # Contar las categorías
        promesas_counts = Counter(promesas)
        
        # Crear DataFrame para Plotly
        df = pd.DataFrame(list(promesas_counts.items()), columns=['Categoría', 'Conteo'])
        
        # Crear el gráfico de pastel
        fig = go.Figure(data=[go.Pie(labels=df['Categoría'], values=df['Conteo'], hole=0.3)])
        
        # Configurar el diseño del gráfico
        fig.update_layout(
            title=f'Distribución de Promesas de Pago',
            #autosize=True,
            margin=dict(l=100)
        )
        
        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig, use_container_width=True)
    
    
else:
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.graph_objs as go
    
    # Simulación de datos
    np.random.seed(42)
    
    # Datos simulados
    total_reserva = 135  # Total de reserva en millones
    reserva_libera = total_reserva * 0.22  # Reserva liberada
    mes_actual = pd.to_datetime("2024-10-15")  # Suponiendo que estamos en el 15 de octubre
    meses = pd.date_range(start='2024-10-01', end=mes_actual, freq='D')
    
    # Generar reservas diarias aleatorias y crecientes
    reservas_diarias = np.zeros(len(meses))
    for i in range(len(meses)):
        reservas_diarias[i] = reservas_diarias[i - 1] + np.random.uniform(0, reserva_libera / len(meses)) if i > 0 else np.random.uniform(0, reserva_libera / len(meses))
    
    # Ajuste para no exceder la reserva liberada
    reservas_diarias = np.clip(reservas_diarias, 0, reserva_libera)
    
    # Datos de cuentas
    cuentas_asignadas = 50000  # Total de cuentas asignadas
    cuentas_consultadas = int(cuentas_asignadas * (2 / 3))  # Aproximadamente 2/3 de cuentas consultadas
    consultas_realizadas = int(cuentas_consultadas * 2.5)  # Aproximadamente 2.5 veces las cuentas consultadas
    
    # Datos para la migración de morosidad
    buckets = ['Bucket 0', 'Bucket 1', 'Bucket 2', 'Bucket 3', 'Bucket 4', 'Bucket 5', 'Bucket 6+']
    inicial_morosidad = np.random.rand(7) * 100  # Porcentaje inicial
    final_morosidad = inicial_morosidad.copy()
    final_morosidad[0] += 20  # Aumentar Bucket 0
    final_morosidad[3:] -= (np.random.rand(4) * 20)  # Disminuir Buckets 4, 5 y 6+
    final_morosidad = np.clip(final_morosidad, 0, None)  # Asegurarse de que no sea negativo
    
    # Normalizar para que la suma sea 100%
    inicial_morosidad /= inicial_morosidad.sum() / 100
    final_morosidad /= final_morosidad.sum() / 100
    
    # Configuración del título del dashboard
    st.title("Dashboard de Liberación de Reserva")
    
    # Indicadores en la parte superior
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Reserva liberada (Millones)", f"{reservas_diarias[-1]:,.2f}")
    col2.metric("Cuentas asignadas", f"{cuentas_asignadas:,}")
    col3.metric("Cuentas consultadas", f"{cuentas_consultadas:,}")
    col4.metric("Consultas hasta el momento", f"{consultas_realizadas:,}")
    
    # Leyenda
    st.markdown("**Fecha actual: 15 de octubre de 2024**")
    
    # Gráfico de barras para la reserva liberada en el mes (crecimiento aleatorio)
    st.subheader("Reserva liberada en el mes")
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=meses, y=reservas_diarias, name='Reserva liberada', marker_color='blue'))
    fig1.update_layout(title="Reserva liberada en el mes actual",
                       xaxis_title="Día",
                       yaxis_title="Reserva (Millones)",
                       template='plotly_white')
    st.plotly_chart(fig1)
    
    # Gráfico de barras para la migración de morosidad
    st.subheader("Migración de Morosidad")
    migracion_morosidad = pd.DataFrame({
        'Bucket': buckets,
        'Inicial': inicial_morosidad,
        'Final': final_morosidad
    })
    
    # Crear gráfico de barras
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=migracion_morosidad['Bucket'], y=migracion_morosidad['Inicial'], name='Inicial', marker_color='orange'))
    fig2.add_trace(go.Bar(x=migracion_morosidad['Bucket'], y=migracion_morosidad['Final'], name='Final', marker_color='lightblue'))
    
    fig2.update_layout(title="Migración de Morosidad (%)",
                       xaxis_title="Buckets de Morosidad",
                       yaxis_title="Porcentaje (%)",
                       barmode='group',  # Agrupado
                       template='plotly_white')
    st.plotly_chart(fig2)
    
    # Gráfico de líneas de tendencias temporales desde enero hasta octubre
    st.subheader("Tendencias temporales de pagos")
    fechas_tendencias = pd.date_range(start='2024-01-01', end='2024-10-31', freq='M')
    tendencias_temporales = np.random.randint(50, 150, size=len(fechas_tendencias))
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=fechas_tendencias, y=tendencias_temporales, mode='lines+markers', name='Tendencia', line=dict(color='green')))
    fig3.update_layout(title="Tendencias Temporales de Pagos",
                       xaxis_title="Fecha",
                       yaxis_title="Valor",
                       xaxis=dict(tickmode='array', tickvals=fechas_tendencias, ticktext=fechas_tendencias.strftime('%B')),
                       template='plotly_white')
    st.plotly_chart(fig3)
