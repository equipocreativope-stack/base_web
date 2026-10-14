import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title='BCP Analytics | Series de tiempo', page_icon='📈', layout='wide')

NAVY = '#12304A'
BLUE = '#2878B5'
TEAL = '#1F9D8B'
ORANGE = '#E59B3D'
MUTED = '#64748B'

st.markdown('''
<style>
.block-container {padding-top: 1.3rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background: #F4F7FB; border: 1px solid #E1E8F0; padding: 15px 17px; border-radius: 12px;}
.hero {background: linear-gradient(120deg,#12304A,#205A7D); color:white; padding:24px 28px; border-radius:16px; margin-bottom:18px;}
.hero h1 {font-size:2rem; margin:0 0 6px 0;}
.hero p {color:#E4EDF5; margin:0;}
.small-note {font-size:0.9rem;color:#64748B;}
</style>
''', unsafe_allow_html=True)

DEFAULT_FILE = Path(__file__).with_name('Base_BCP_Consolidada.xlsx')

@st.cache_data(show_spinner=False)
def load_workbook(file_bytes):
    from io import BytesIO
    xls = pd.ExcelFile(BytesIO(file_bytes))
    base = pd.read_excel(xls, sheet_name='BASE_BCP')
    additive = pd.read_excel(xls, sheet_name='ADITIVO')
    multiplicative = pd.read_excel(xls, sheet_name='MULTIPLICATIVO')
    for df in (base, additive, multiplicative):
        if 'Fecha' in df:
            df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    base = base.dropna(subset=['Fecha']).sort_values('Fecha')
    additive = additive.dropna(subset=['Fecha']).sort_values('Fecha')
    multiplicative = multiplicative.dropna(subset=['Fecha']).sort_values('Fecha')
    return base, additive, multiplicative

st.sidebar.title('BCP Analytics')
st.sidebar.caption('Panel de análisis de series de tiempo')

# Cargar automáticamente la base incluida en el repositorio
from pathlib import Path

DEFAULT_FILE = Path(__file__).parent / "Base_BCP_Consolidada.xlsx"

st.sidebar.success("Base de datos del BCP cargada automáticamente")

if DEFAULT_FILE.exists():
    source_bytes = DEFAULT_FILE.read_bytes()
    source_name = DEFAULT_FILE.name
else:
    source_bytes = None
    source_name = None


if source_bytes is None:
    st.error('Carga el archivo Excel para comenzar.')
    st.stop()
try:
    base, add, mult = load_workbook(source_bytes)
except Exception as e:
    st.error(f'No se pudo leer el libro. Verifica que incluya BASE_BCP, ADITIVO y MULTIPLICATIVO. Detalle: {e}')
    st.stop()

required = {'Fecha','Créditos directos','Depósitos totales','Patrimonio'}
if not required.issubset(base.columns):
    st.error('La hoja BASE_BCP debe contener Fecha, Créditos directos, Depósitos totales y Patrimonio.')
    st.stop()

variables = ['Créditos directos', 'Depósitos totales', 'Patrimonio']
variable = st.sidebar.selectbox('Variable histórica', variables, index=0)
section = st.sidebar.radio('Navegación', ['Resumen ejecutivo','Evolución histórica','Modelo aditivo','Modelo multiplicativo','Comparación de pronósticos','Datos y metodología'])

last_hist_date = base['Fecha'].max()
first_hist_date = base['Fecha'].min()
last_value = base.loc[base['Fecha'].idxmax(), variable]
prev_year = base[base['Fecha'] <= last_hist_date - pd.DateOffset(years=1)]
prev_value = prev_year.iloc[-1][variable] if len(prev_year) else None
pct_yoy = (last_value / prev_value - 1) * 100 if prev_value and pd.notna(prev_value) and prev_value != 0 else None

st.markdown(f'''<div class="hero"><h1>BCP Analytics</h1><p>Explorador interactivo de series de tiempo · Créditos, depósitos y patrimonio</p></div>''', unsafe_allow_html=True)
st.caption(f'Archivo activo: {source_name} · Periodo histórico: {first_hist_date:%b %Y} – {last_hist_date:%b %Y}')

# Forecast data are the rows beyond the actual base range. Forecast columns use the workbook's own reconstructed values.
def prepare_model(df, model):
    d = df.copy()
    d['Fecha'] = pd.to_datetime(d['Fecha'], errors='coerce')
    d['PERIODO'] = pd.to_numeric(d.get('PERIODO'), errors='coerce')
    if model == 'Aditivo':
        pred_col = 'Reconstrucción (T+E+C+R)' if 'Reconstrucción (T+E+C+R)' in d.columns else d.columns[10]
        trend_col = 'Tendencia (Tt)'
        seasonal_col = 'Estacional (Et)'
    else:
        pred_col = 'PRECIO RRECONSTRUIDO' if 'PRECIO RRECONSTRUIDO' in d.columns else 'PRECIO RECONSTRUIDO'
        trend_col = 'TENDENCIA'
        seasonal_col = 'INDICE ESTACIONAL AJUSTADO'
    d['Pronostico'] = pd.to_numeric(d[pred_col], errors='coerce')
    d['Tendencia_graf'] = pd.to_numeric(d[trend_col], errors='coerce') if trend_col in d else None
    d['Estacional_graf'] = pd.to_numeric(d[seasonal_col], errors='coerce') if seasonal_col in d else None
    d['Real'] = pd.to_numeric(d.iloc[:, 2], errors='coerce')
    d['Es_pronostico'] = d['Fecha'] > last_hist_date
    return d

ad = prepare_model(add, 'Aditivo')
mu = prepare_model(mult, 'Multiplicativo')
forecast_add = ad[ad['Es_pronostico'] & ad['Pronostico'].notna()].copy()
forecast_mul = mu[mu['Es_pronostico'] & mu['Pronostico'].notna()].copy()

fmt = lambda x: f'{x:,.0f}' if pd.notna(x) else '—'

if section == 'Resumen ejecutivo':
    st.subheader('Resumen ejecutivo')
    st.write('Vista rápida para presentar la evolución del BCP y consultar las proyecciones ya calculadas en las hojas del Excel.')
    c1,c2,c3,c4 = st.columns(4)
    c1.metric('Meses históricos', f'{len(base):,}')
    c2.metric('Último dato de ' + variable, fmt(last_value))
    c3.metric('Variación interanual', f'{pct_yoy:+.2f}%' if pct_yoy is not None else 'No disponible')
    c4.metric('Meses proyectados', f'{min(len(forecast_add),len(forecast_mul)):,}' if len(forecast_add) and len(forecast_mul) else 'Revisar hojas')
    st.markdown('### Evolución histórica')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=base['Fecha'], y=base[variable], mode='lines', name=variable, line=dict(color=BLUE,width=3)))
    fig.update_layout(template='plotly_white', height=400, margin=dict(l=15,r=15,t=20,b=15), xaxis_title='', yaxis_title='Valor (unidad del archivo)', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('### Pronósticos de créditos directos')
    if not forecast_add.empty and not forecast_mul.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=base['Fecha'], y=base['Créditos directos'], name='Histórico', line=dict(color=NAVY,width=2.5)))
        fig2.add_trace(go.Scatter(x=forecast_add['Fecha'], y=forecast_add['Pronostico'], name='Aditivo', line=dict(color=BLUE,width=3,dash='dash')))
        fig2.add_trace(go.Scatter(x=forecast_mul['Fecha'], y=forecast_mul['Pronostico'], name='Multiplicativo', line=dict(color=TEAL,width=3,dash='dot')))
        fig2.update_layout(template='plotly_white', height=420, hovermode='x unified', xaxis_title='', yaxis_title='Créditos directos (unidad del archivo)')
        st.plotly_chart(fig2, use_container_width=True)
    st.info('En este archivo, las hojas ADITIVO y MULTIPLICATIVO contienen el desarrollo del modelo para Créditos directos. Depósitos y patrimonio están disponibles como series históricas en BASE_BCP.')

elif section == 'Evolución histórica':
    st.subheader('Evolución histórica')
    st.write(f'Variable seleccionada: **{variable}**')
    start, end = st.columns(2)
    min_date, max_date = base['Fecha'].min().date(), base['Fecha'].max().date()
    d1 = start.date_input('Desde', value=min_date, min_value=min_date, max_value=max_date)
    d2 = end.date_input('Hasta', value=max_date, min_value=min_date, max_value=max_date)
    hist = base[(base['Fecha'].dt.date >= d1) & (base['Fecha'].dt.date <= d2)]
    fig = go.Figure(go.Scatter(x=hist['Fecha'], y=hist[variable], mode='lines+markers', name=variable, line=dict(color=BLUE,width=2.5), marker=dict(size=4)))
    fig.update_layout(template='plotly_white', height=470, hovermode='x unified', xaxis_title='', yaxis_title='Valor (unidad del archivo)')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(hist, use_container_width=True, hide_index=True)

elif section in ['Modelo aditivo','Modelo multiplicativo']:
    is_add = section == 'Modelo aditivo'
    d = ad if is_add else mu
    f = forecast_add if is_add else forecast_mul
    st.subheader(section)
    st.write('Se muestran los valores calculados en la hoja correspondiente del Excel; la interfaz no vuelve a estimar el modelo.')
    pred_label = 'Reconstrucción (T + E + C + R)' if is_add else 'Precio reconstruido (T × índice estacional)'
    c1,c2,c3 = st.columns(3)
    c1.metric('Observaciones históricas', f'{d[~d["Es_pronostico"]].shape[0]:,}')
    c2.metric('Meses proyectados', f'{len(f):,}')
    c3.metric('Último pronóstico', fmt(f['Pronostico'].iloc[-1]) if not f.empty else 'No encontrado')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=base['Fecha'], y=base['Créditos directos'], name='Créditos observados', line=dict(color=NAVY,width=2.5)))
    fig.add_trace(go.Scatter(x=f['Fecha'], y=f['Pronostico'], name='Pronóstico', line=dict(color=BLUE if is_add else TEAL,width=3,dash='dash')))
    fig.update_layout(template='plotly_white', height=440, hovermode='x unified', xaxis_title='', yaxis_title='Créditos directos (unidad del archivo)')
    st.plotly_chart(fig, use_container_width=True)
    years = sorted(f['Fecha'].dt.year.unique().tolist()) if not f.empty else []
    if years:
        chosen_year = st.selectbox('Año proyectado', years, index=0)
        table = f[f['Fecha'].dt.year == chosen_year].copy()
        table['Fecha'] = table['Fecha'].dt.strftime('%Y-%m')
        table = table[['Fecha','PERIODO','Pronostico','Tendencia_graf','Estacional_graf']]
        table.columns = ['Mes','Periodo','Pronóstico','Tendencia','Componente estacional']
        st.dataframe(table, use_container_width=True, hide_index=True)
        csv = table.to_csv(index=False).encode('utf-8-sig')
        st.download_button('Descargar tabla anual CSV', csv, file_name=f'{section.lower().replace(" ","_")}_{chosen_year}.csv', mime='text/csv')
    with st.expander('Ver tabla completa del modelo'):
        show = d.copy()
        show['Fecha'] = show['Fecha'].dt.strftime('%Y-%m')
        st.dataframe(show, use_container_width=True, hide_index=True)

elif section == 'Comparación de pronósticos':
    st.subheader('Comparación de modelos')
    st.write('Comparación mensual entre las proyecciones aditiva y multiplicativa para los periodos futuros incluidos en el libro.')
    if forecast_add.empty or forecast_mul.empty:
        st.warning('No se encontraron pronósticos en una o ambas hojas. Revisa las columnas de reconstrucción.')
    else:
        comp = forecast_add[['Fecha','PERIODO','Pronostico']].merge(forecast_mul[['Fecha','Pronostico']], on='Fecha', how='inner', suffixes=('_Aditivo','_Multiplicativo'))
        comp = comp.rename(columns={'Pronostico_Aditivo':'Aditivo','Pronostico_Multiplicativo':'Multiplicativo'})
        comp['Diferencia (Multiplicativo - Aditivo)'] = comp['Multiplicativo'] - comp['Aditivo']
        comp['Diferencia porcentual vs aditivo (%)'] = (comp['Multiplicativo']/comp['Aditivo'] - 1)*100
        years = sorted(comp['Fecha'].dt.year.unique().tolist())
        selected_years = st.multiselect('Años a comparar', years, default=years)
        filtered = comp[comp['Fecha'].dt.year.isin(selected_years)]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=filtered['Fecha'],y=filtered['Aditivo'],name='Modelo aditivo',line=dict(color=BLUE,width=3)))
        fig.add_trace(go.Scatter(x=filtered['Fecha'],y=filtered['Multiplicativo'],name='Modelo multiplicativo',line=dict(color=TEAL,width=3,dash='dash')))
        fig.update_layout(template='plotly_white',height=440,hovermode='x unified',xaxis_title='',yaxis_title='Pronóstico de créditos directos')
        st.plotly_chart(fig,use_container_width=True)
        annual = filtered.assign(Año=filtered['Fecha'].dt.year).groupby('Año').agg(Aditivo_promedio=('Aditivo','mean'),Multiplicativo_promedio=('Multiplicativo','mean'),Aditivo_diciembre=('Aditivo','last'),Multiplicativo_diciembre=('Multiplicativo','last')).reset_index()
        st.markdown('#### Resumen anual')
        st.dataframe(annual, use_container_width=True, hide_index=True)
        display = filtered.copy(); display['Fecha'] = display['Fecha'].dt.strftime('%Y-%m')
        st.markdown('#### Detalle mensual')
        st.dataframe(display, use_container_width=True, hide_index=True)
        st.download_button('Descargar comparación CSV', display.to_csv(index=False).encode('utf-8-sig'), file_name='comparacion_pronosticos_bcp.csv', mime='text/csv')

else:
    st.subheader('Datos y metodología')
    st.markdown('#### Estructura del archivo')
    st.write('- **BASE_BCP:** datos históricos mensuales de créditos directos, depósitos totales y patrimonio.')
    st.write('- **ADITIVO:** cálculos del modelo aditivo y su columna de reconstrucción/proyección.')
    st.write('- **MULTIPLICATIVO:** cálculos del modelo multiplicativo y su columna de precio reconstruido/proyección.')
    st.markdown('#### Notas de lectura')
    st.warning('Las proyecciones que se muestran son las ya registradas en tu Excel. La comparación visual no implica que uno de los modelos sea estadísticamente mejor: para decidirlo se requieren errores de validación comparables, calculados sobre el mismo periodo.')
    st.info('Las hojas de modelos contienen pronósticos de Créditos directos. La selección de depósitos o patrimonio afecta únicamente los gráficos históricos hasta que existan modelos proyectivos para esas variables.')
    st.markdown('#### Vista de la base')
    st.dataframe(base, use_container_width=True, hide_index=True)
    st.download_button('Descargar base histórica CSV', base.to_csv(index=False).encode('utf-8-sig'), file_name='base_historica_bcp.csv', mime='text/csv')

st.markdown('---')
st.markdown('<div class="small-note">Panel académico de análisis de series de tiempo · Fuente de datos: libro Excel proporcionado por el usuario. Las cifras conservan la escala/unidad del archivo original.</div>', unsafe_allow_html=True)
