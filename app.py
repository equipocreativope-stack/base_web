from pathlib import Path
from io import BytesIO
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title='BCP Analytics | Inteligencia financiera', page_icon='📊', layout='wide', initial_sidebar_state='expanded')

# Paleta corporativa
NAVY = '#0B2340'
BLUE = '#1769AA'
CYAN = '#2FA8D8'
TEAL = '#159A91'
GOLD = '#E4AD47'
RED = '#D9534F'
INK = '#172B4D'
MUTED = '#63758B'
BG = '#F3F6FA'
FACTOR_SOLES = 1000  # La fuente SBS del archivo está expresada en miles de soles.

st.markdown(f'''<style>
:root {{ --navy:{NAVY}; --blue:{BLUE}; --cyan:{CYAN}; }}
.stApp {{ background: linear-gradient(180deg,#F5F8FC 0%,#FFFFFF 46%,#F5F8FC 100%); color:{INK}; }}
.block-container {{ padding-top:1.15rem; padding-bottom:2.2rem; max-width:1500px; }}
[data-testid="stMetric"] {{ background:linear-gradient(145deg,#FFFFFF,#F2F6FB); border:1px solid #DFE7F0; padding:16px 18px; border-radius:16px; box-shadow:0 5px 18px rgba(11,35,64,.055); animation:rise .55s ease both; }}
[data-testid="stMetricLabel"] {{ color:{MUTED}; font-weight:600; }}
[data-testid="stMetricValue"] {{ color:{NAVY}; font-weight:750; }}
.hero {{ position:relative; overflow:hidden; background:linear-gradient(115deg,#071A30 0%,#123E68 52%,#1769AA 100%); color:white; padding:28px 30px; border-radius:22px; margin-bottom:16px; box-shadow:0 14px 35px rgba(11,35,64,.16); }}
.hero:after {{ content:""; position:absolute; width:340px;height:340px;right:-65px;top:-170px;border:1px solid rgba(255,255,255,.2);border-radius:50%;box-shadow:0 0 0 28px rgba(255,255,255,.035),0 0 0 58px rgba(255,255,255,.025); animation:orbit 18s linear infinite; }}
.hero h1 {{ font-size:2.15rem; letter-spacing:-.04em; margin:0 0 6px 0; color:white; }}
.hero p {{ color:#D8E9F7; margin:0; max-width:850px; }}
.hero .eyebrow {{ text-transform:uppercase; letter-spacing:.17em; font-size:.72rem; font-weight:700; color:#92D8F2; margin-bottom:8px; }}
.pill {{ display:inline-block; padding:5px 10px; border-radius:999px; background:rgba(255,255,255,.12); color:#E8F5FF; font-size:.78rem; margin-top:14px; border:1px solid rgba(255,255,255,.18); }}
.section-title {{ font-size:1.3rem; font-weight:750; color:{NAVY}; letter-spacing:-.02em; margin:.5rem 0 .25rem; }}
.subtle {{ color:{MUTED}; font-size:.91rem; }}
.winner {{ border:1px solid #A6D8D2; background:linear-gradient(135deg,#F1FBF9,#FFFFFF); border-radius:16px; padding:18px 20px; box-shadow:0 8px 24px rgba(21,154,145,.08); }}
.context-card {{ border-left:4px solid {CYAN}; background:#F6FAFE; border-radius:0 12px 12px 0; padding:12px 15px; margin:8px 0; }}
.small-note {{ color:{MUTED}; font-size:.83rem; }}
@keyframes rise {{ from {{opacity:0; transform:translateY(8px)}} to {{opacity:1;transform:translateY(0)}} }}
@keyframes orbit {{ from {{transform:rotate(0deg)}} to {{transform:rotate(360deg)}} }}
@media (prefers-reduced-motion: reduce) {{ *,*:before,*:after {{animation:none!important;transition:none!important}} }}
</style>''', unsafe_allow_html=True)

DEFAULT_FILE = Path(__file__).with_name('Base_BCP_Consolidada.xlsx')
VARIABLES = ['Créditos directos', 'Depósitos totales', 'Patrimonio']

EVENTS = [
    {'date':'2017-03-01','year':2017,'category':'Clima / desastres','title':'El Niño Costero','summary':'Lluvias e inundaciones dañaron infraestructura y afectaron transporte, agricultura, comercio y otras actividades. Puede ser contexto para cambios de actividad y demanda de crédito; no prueba un efecto directo en el BCP.','source':'https://www.bcrp.gob.pe/eng-docs/Publications/Annual-Reports/2017/annual-report-2017-1.pdf','source_name':'BCRP · Memoria 2017'},
    {'date':'2020-03-01','year':2020,'category':'Salud / economía','title':'Pandemia y restricciones por COVID-19','summary':'La economía peruana se contrajo 11,1% en 2020. El shock alteró actividad, ingresos, consumo, inversión y comportamiento financiero. La serie bancaria puede reflejar varios canales y medidas extraordinarias.','source':'https://m.inei.gob.pe/prensa/noticias/produccion-nacional-disminuyo-1112-durante-el-ano-2020-12741/','source_name':'INEI · Producción nacional 2020'},
    {'date':'2021-06-01','year':2021,'category':'Política / tipo de cambio','title':'Incertidumbre electoral y volatilidad cambiaria','summary':'El BCRP reportó que el tipo de cambio llegó a un máximo histórico intranual y vinculó la volatilidad de 2021 con la incertidumbre del periodo electoral. La exposición del banco depende también de la moneda de sus operaciones y de la composición de su cartera.','source':'https://www.bcrp.gob.pe/docs/Publicaciones/Memoria/2021/memoria-bcrp-2021-5.pdf','source_name':'BCRP · Memoria 2021'},
    {'date':'2022-02-01','year':2022,'category':'Economía global','title':'Inflación global y shocks externos','summary':'El entorno internacional de inflación, tasas y materias primas pudo modificar costos de fondeo, demanda de crédito y preferencias de ahorro. Esta nota es contextual: la serie disponible no incluye variables macroeconómicas para medir el impacto.','source':'https://www.bcrp.gob.pe/reporte-de-inflacion/34-publicaciones/memoria-anual.html','source_name':'BCRP · Memorias anuales'},
    {'date':'2023-01-01','year':2023,'category':'Social / política','title':'Protestas y bloqueos','summary':'En septiembre de 2023, el BCRP señaló que las protestas de inicios de año afectaron actividad económica y operación de empresas. Los efectos específicos sobre los créditos del BCP requieren datos adicionales.','source':'https://www.elperuano.pe/noticia/224122-protestas-impactaron-08-en-pbi','source_name':'El Peruano · Declaraciones del BCRP'},
    {'date':'2023-03-01','year':2023,'category':'Clima / desastres','title':'El Niño y sequías','summary':'El BCRP estimó que El Niño 2023 restó alrededor de 1,1 puntos porcentuales al crecimiento del PBI, por impactos en sectores primarios y no primarios. Puede afectar de forma indirecta a hogares y empresas.','source':'https://www.bcrp.gob.pe/eng-docs/Publications/Annual-Reports/2023/annual-report-2023.pdf','source_name':'BCRP · Memoria 2023'},
    {'date':'2024-01-01','year':2024,'category':'Clima / recuperación','title':'Persistencia de efectos climáticos','summary':'Los shocks climáticos pueden trasladarse a precios, producción y servicios con rezagos. Conviene contrastar esta cronología con indicadores mensuales antes de asociar un evento a una variación concreta del crédito.','source':'https://investigacion.bcrp.gob.pe/es/investigaciones/documentos-de-trabajo/2025/dt-2025-008','source_name':'BCRP · Documento de trabajo sobre ENSO'},
]

@st.cache_data(show_spinner=False)
def load_workbook(file_bytes):
    xls = pd.ExcelFile(BytesIO(file_bytes))
    required_sheets = {'BASE_BCP','ADITIVO','MULTIPLICATIVO'}
    if not required_sheets.issubset(set(xls.sheet_names)):
        raise ValueError('El Excel debe contener las hojas BASE_BCP, ADITIVO y MULTIPLICATIVO.')
    base = pd.read_excel(xls, sheet_name='BASE_BCP')
    additive = pd.read_excel(xls, sheet_name='ADITIVO')
    multiplicative = pd.read_excel(xls, sheet_name='MULTIPLICATIVO')
    for df in (base, additive, multiplicative):
        if 'Fecha' not in df.columns:
            raise ValueError('Falta la columna Fecha en una de las hojas.')
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df.dropna(subset=['Fecha'], inplace=True)
        df.sort_values('Fecha', inplace=True)
    return base, additive, multiplicative

def numeric(series):
    return pd.to_numeric(series, errors='coerce')

def fmt_soles(x, decimals=0):
    if x is None or pd.isna(x): return '—'
    return ('S/ ' + f'{x:,.{decimals}f}').replace(',', 'X').replace('.', ',').replace('X', '.')

def fmt_num(x, decimals=2):
    if x is None or pd.isna(x): return '—'
    return (f'{x:,.{decimals}f}').replace(',', 'X').replace('.', ',').replace('X', '.')

def prep_model(df, model, last_hist_date):
    d = df.copy()
    d['PERIODO'] = numeric(d['PERIODO']) if 'PERIODO' in d else np.nan
    if model == 'Aditivo':
        pred_col = 'Reconstrucción (T+E+C+R)' if 'Reconstrucción (T+E+C+R)' in d else None
        trend_col, seasonal_col = 'Tendencia (Tt)', 'Estacional (Et)'
    else:
        pred_col = 'PRECIO RRECONSTRUIDO' if 'PRECIO RRECONSTRUIDO' in d else ('PRECIO RECONSTRUIDO' if 'PRECIO RECONSTRUIDO' in d else None)
        trend_col, seasonal_col = 'TENDENCIA', 'INDICE ESTACIONAL AJUSTADO'
    if pred_col is None: raise ValueError(f'No se encontró la columna de reconstrucción del modelo {model}.')
    d['Pronostico_original'] = numeric(d[pred_col])
    d['Pronostico_Soles'] = d['Pronostico_original'] * FACTOR_SOLES
    d['Tendencia_Soles'] = numeric(d[trend_col]) * FACTOR_SOLES if trend_col in d else np.nan
    d['Estacional_original'] = numeric(d[seasonal_col]) if seasonal_col in d else np.nan
    d['Es_pronostico'] = d['Fecha'] > last_hist_date
    return d

def validation_holdout(base, variable, holdout_months=12):
    """Complemento metodológico: estima tendencia+estacionalidad solo con entrenamiento y evalúa los últimos 12 meses.
    No altera las hojas originales ni los pronósticos originales del Excel.
    """
    d = base[['Fecha', variable]].copy()
    d[variable] = numeric(d[variable])
    d = d.dropna().sort_values('Fecha').reset_index(drop=True)
    if len(d) < 36: return None, None
    train = d.iloc[:-holdout_months].copy()
    test = d.iloc[-holdout_months:].copy()
    train['t'] = np.arange(1, len(train)+1)
    slope, intercept = np.polyfit(train['t'], train[variable], 1)
    train['trend'] = intercept + slope*train['t']
    train['month'] = train['Fecha'].dt.month
    train['resid'] = train[variable] - train['trend']
    train['ratio'] = np.where(train['trend'] != 0, train[variable] / train['trend'], np.nan)
    add_idx = train.groupby('month')['resid'].mean()
    add_idx = add_idx - add_idx.mean()
    mul_idx = train.groupby('month')['ratio'].mean()
    mul_idx = mul_idx / mul_idx.mean()
    test['t'] = np.arange(len(train)+1, len(train)+len(test)+1)
    test['trend'] = intercept + slope*test['t']
    test['Aditivo'] = test['trend'] + test['Fecha'].dt.month.map(add_idx).to_numpy()
    test['Multiplicativo'] = test['trend'] * test['Fecha'].dt.month.map(mul_idx).to_numpy()
    metrics = []
    for model in ['Aditivo','Multiplicativo']:
        actual = test[variable].to_numpy(dtype=float)
        pred = test[model].to_numpy(dtype=float)
        err = actual-pred
        mape = np.mean(np.abs(err[actual != 0] / actual[actual != 0]))*100
        metrics.append({'Modelo':model,'MAE':float(np.mean(np.abs(err))),'RMSE':float(np.sqrt(np.mean(err**2))),'MAPE (%)':float(mape)})
    return pd.DataFrame(metrics), test

def style_fig(fig, height=430, ytitle=''):
    fig.update_layout(template='plotly_white', height=height, margin=dict(l=10,r=18,t=35,b=10), hovermode='x unified',
                      font=dict(family='Inter, Arial, sans-serif', color=INK), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,.88)',
                      xaxis=dict(showgrid=False, linecolor='#DCE5EF'), yaxis=dict(title=ytitle, gridcolor='#E9EFF5', zerolinecolor='#DCE5EF'),
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0, bgcolor='rgba(255,255,255,.65)'))
    return fig

st.sidebar.markdown(f'<div style="background:linear-gradient(145deg,{NAVY},{BLUE});padding:17px;border-radius:15px;color:white;margin-bottom:12px"><div style="font-size:.72rem;letter-spacing:.14em;color:#9DDBF1;font-weight:700">INTELIGENCIA FINANCIERA</div><div style="font-size:1.45rem;font-weight:800">BCP Analytics</div><div style="font-size:.83rem;color:#D6E9F7">Series de tiempo · SBS</div></div>', unsafe_allow_html=True)
st.sidebar.caption('Datos originales preservados · visualización en soles')
upload = st.sidebar.file_uploader('Actualizar libro Excel', type=['xlsx'], help='Debe contener BASE_BCP, ADITIVO y MULTIPLICATIVO. Si no cargas otro archivo, se usa el Excel incluido.')
source_bytes = upload.getvalue() if upload else (DEFAULT_FILE.read_bytes() if DEFAULT_FILE.exists() else None)
source_name = upload.name if upload else DEFAULT_FILE.name
if source_bytes is None:
    st.error('No se encontró el Excel inicial. Carga el libro con las tres hojas requeridas.')
    st.stop()
try:
    base, add_raw, mult_raw = load_workbook(source_bytes)
except Exception as e:
    st.error(f'No se pudo leer el libro. Detalle: {e}')
    st.stop()

required = {'Fecha', *VARIABLES}
if not required.issubset(base.columns):
    st.error('BASE_BCP debe incluir Fecha, Créditos directos, Depósitos totales y Patrimonio.')
    st.stop()
for v in VARIABLES: base[v] = numeric(base[v])
base = base.sort_values('Fecha').drop_duplicates('Fecha', keep='last')
first_date, last_date = base['Fecha'].min(), base['Fecha'].max()
try:
    ad = prep_model(add_raw, 'Aditivo', last_date)
    mu = prep_model(mult_raw, 'Multiplicativo', last_date)
except Exception as e:
    st.error(f'No se pudieron preparar las hojas de modelos. Detalle: {e}')
    st.stop()
fa = ad[ad['Es_pronostico'] & ad['Pronostico_Soles'].notna()].copy()
fm = mu[mu['Es_pronostico'] & mu['Pronostico_Soles'].notna()].copy()

# Filtros globales
st.sidebar.markdown('---')
st.sidebar.markdown('### Filtros del panel')
variable = st.sidebar.selectbox('Variable histórica', VARIABLES, index=0)
min_date, max_date = first_date.date(), last_date.date()
start_date = st.sidebar.date_input('Desde', value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input('Hasta', value=max_date, min_value=min_date, max_value=max_date)
if start_date > end_date:
    st.sidebar.warning('La fecha inicial debe ser anterior a la final.')
    start_date, end_date = end_date, start_date
hist = base[(base['Fecha'].dt.date >= start_date) & (base['Fecha'].dt.date <= end_date)].copy()
section = st.sidebar.radio('Navegación', ['Resumen ejecutivo','Evolución histórica','Comparador de modelos','Contexto de fluctuaciones','Datos y metodología'])

st.markdown(f'''<div class="hero"><div class="eyebrow">Panel de análisis bancario · Perú</div><h1>BCP Analytics</h1><p>Una lectura visual de la evolución histórica, los pronósticos y el contexto económico que rodea a la serie.</p><span class="pill">S/ SOLES PERUANOS · 2016–2028 · MODELOS ORIGINALES</span></div>''', unsafe_allow_html=True)
st.caption(f'Fuente activa: {source_name}  ·  Histórico: {first_date:%b %Y} – {last_date:%b %Y}  ·  {len(base):,} observaciones mensuales')

# Validación complementaria para identificar el menor error predictivo en un mismo periodo de prueba
metrics, holdout = validation_holdout(base, 'Créditos directos', 12)
winner = None
if metrics is not None and not metrics.empty:
    winner = metrics.sort_values(['MAPE (%)','RMSE']).iloc[0]['Modelo']

if section == 'Resumen ejecutivo':
    st.markdown('<div class="section-title">Vista ejecutiva</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Indicadores principales de la variable seleccionada y comparación de proyecciones de créditos.</div>', unsafe_allow_html=True)
    last_value = hist.iloc[-1][variable] * FACTOR_SOLES if len(hist) else np.nan
    previous = base[base['Fecha'] <= last_date - pd.DateOffset(years=1)]
    prev_value = previous.iloc[-1][variable] if len(previous) else np.nan
    yoy = (base.iloc[-1][variable]/prev_value-1)*100 if pd.notna(prev_value) and prev_value != 0 else np.nan
    total_growth = (base.iloc[-1][variable]/base.iloc[0][variable]-1)*100 if base.iloc[0][variable] else np.nan
    c1,c2,c3,c4 = st.columns(4)
    c1.metric('Último valor en rango', fmt_soles(last_value))
    c2.metric('Variación interanual', f'{fmt_num(yoy)}%' if pd.notna(yoy) else '—')
    c3.metric('Crecimiento histórico', f'{fmt_num(total_growth)}%' if pd.notna(total_growth) else '—')
    c4.metric('Meses proyectados', f'{min(len(fa),len(fm))} meses' if len(fa) and len(fm) else 'Ver hojas')
    st.markdown('')
    left,right = st.columns([1.55,1])
    with left:
        st.markdown('#### Evolución histórica')
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist['Fecha'], y=hist[variable]*FACTOR_SOLES, mode='lines', name=variable, line=dict(color=BLUE,width=3), fill='tozeroy', fillcolor='rgba(23,105,170,.08)'))
        fig.update_layout(hovermode='x unified')
        style_fig(fig, 390, f'{variable} (S/)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
    with right:
        st.markdown('#### Lectura rápida')
        if winner:
            m = metrics.set_index('Modelo').loc[winner]
            st.markdown(f'<div class="winner"><div style="font-size:.75rem;color:{TEAL};font-weight:800;letter-spacing:.08em">MENOR ERROR EN VALIDACIÓN</div><div style="font-size:1.55rem;font-weight:800;color:{NAVY};margin:5px 0">Modelo {winner.lower()}</div><div style="color:{MUTED};font-size:.9rem">MAPE: <b>{fmt_num(m["MAPE (%)"])}%</b><br>RMSE: <b>{fmt_soles(m["RMSE"])}</b></div><div style="font-size:.78rem;color:{MUTED};margin-top:10px">Prueba retrospectiva sobre los últimos 12 meses históricos; es una evaluación adicional, no modifica el Excel.</div></div>', unsafe_allow_html=True)
        else:
            st.info('No hay suficientes observaciones para validar los modelos.')
        st.markdown('')
        st.markdown('#### Hitos del periodo')
        st.markdown('<div class="context-card"><b>2020 · COVID-19</b><br><span class="small-note">Shock sanitario y caída de actividad económica.</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="context-card"><b>2021 · Incertidumbre cambiaria</b><br><span class="small-note">Volatilidad del dólar en el contexto electoral.</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="context-card"><b>2023 · Protestas y El Niño</b><br><span class="small-note">Factores sociales y climáticos sobre la actividad.</span></div>', unsafe_allow_html=True)
    st.markdown('#### Créditos: pronósticos originales de tu Excel')
    if not fa.empty and not fm.empty:
        comp = fa[['Fecha','Pronostico_Soles']].rename(columns={'Pronostico_Soles':'Aditivo'}).merge(fm[['Fecha','Pronostico_Soles']].rename(columns={'Pronostico_Soles':'Multiplicativo'}),on='Fecha',how='inner')
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=base['Fecha'],y=base['Créditos directos']*FACTOR_SOLES,name='Histórico',line=dict(color=NAVY,width=2.6)))
        fig.add_trace(go.Scatter(x=comp['Fecha'],y=comp['Aditivo'],name='Aditivo original',line=dict(color=BLUE,width=3,dash='dash')))
        fig.add_trace(go.Scatter(x=comp['Fecha'],y=comp['Multiplicativo'],name='Multiplicativo original',line=dict(color=TEAL,width=3,dash='dot')))
        style_fig(fig,420,'Créditos directos (S/)')
        st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
        st.caption('Las proyecciones se leen de las columnas de reconstrucción de tus hojas ADITIVO y MULTIPLICATIVO. No se recalculan ni sustituyen.')

elif section == 'Evolución histórica':
    st.markdown('<div class="section-title">Evolución histórica interactiva</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtle">{variable} expresado en soles. Usa el control de rango para concentrarte en una etapa del periodo.</div>', unsafe_allow_html=True)
    chart = hist[['Fecha',variable]].dropna().copy(); chart['Valor (S/)'] = chart[variable]*FACTOR_SOLES
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=chart['Fecha'],y=chart['Valor (S/)'],mode='lines+markers',name=variable,line=dict(color=BLUE,width=3),marker=dict(size=4),fill='tozeroy',fillcolor='rgba(23,105,170,.07)'))
    # Eventos contextuales superpuestos dentro del rango elegido
    visible_events = [e for e in EVENTS if pd.Timestamp(e['date']) >= pd.Timestamp(start_date) and pd.Timestamp(e['date']) <= pd.Timestamp(end_date)]
    for ev in visible_events:
        fig.add_vline(x=pd.Timestamp(ev['date']), line_width=1, line_dash='dot', line_color=GOLD, opacity=.8)
        fig.add_annotation(x=pd.Timestamp(ev['date']), y=1, yref='paper', text=str(ev['year']), showarrow=False, yshift=9, font=dict(size=10,color='#8A641C'), bgcolor='rgba(255,247,220,.9)')
    style_fig(fig,480,f'{variable} (S/)')
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':True,'scrollZoom':True})
    st.markdown('#### Reproducción visual por año')
    animate = st.toggle('Activar recorrido animado', value=False, help='Muestra la curva creciendo a través del tiempo. Es una animación visual, no un cálculo adicional.')
    if animate and not chart.empty:
        years = sorted(chart['Fecha'].dt.year.unique())
        frames=[]
        for yr in years:
            sub=chart[chart['Fecha'].dt.year<=yr]
            frames.append(go.Frame(name=str(yr),data=[go.Scatter(x=sub['Fecha'],y=sub['Valor (S/)'],mode='lines',line=dict(color=CYAN,width=3))],layout=go.Layout(title_text=f'Evolución hasta {yr}')))
        fig_anim=go.Figure(data=[go.Scatter(x=chart['Fecha'].iloc[:1],y=chart['Valor (S/)'].iloc[:1],mode='lines',line=dict(color=CYAN,width=3))],frames=frames)
        fig_anim.update_layout(template='plotly_white',height=400,margin=dict(l=10,r=10,t=50,b=10),xaxis=dict(range=[chart['Fecha'].min(),chart['Fecha'].max()]),yaxis=dict(title='Valor (S/)',gridcolor='#E9EFF5'),updatemenus=[dict(type='buttons',showactive=False,y=1.15,x=1.0,xanchor='right',buttons=[dict(label='▶ Reproducir',method='animate',args=[None,{'frame':{'duration':450,'redraw':True},'transition':{'duration':200},'fromcurrent':True}]),dict(label='❚❚ Pausar',method='animate',args=[[None],{'frame':{'duration':0,'redraw':False},'mode':'immediate','transition':{'duration':0}}])])])
        st.plotly_chart(fig_anim,use_container_width=True)
    st.markdown('#### Datos del periodo filtrado')
    show=hist.copy(); show['Fecha']=show['Fecha'].dt.strftime('%Y-%m');
    for v in VARIABLES: show[v]=show[v]*FACTOR_SOLES
    show=show.rename(columns={v:f'{v} (S/)' for v in VARIABLES})
    st.dataframe(show,use_container_width=True,hide_index=True)
    st.download_button('Descargar histórico en soles (CSV)',show.to_csv(index=False).encode('utf-8-sig'),file_name='historico_bcp_soles.csv',mime='text/csv')

elif section == 'Comparador de modelos':
    st.markdown('<div class="section-title">Comparador de modelos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Contrasta tus proyecciones originales y revisa cuál obtuvo menor error en una prueba retrospectiva comparable.</div>', unsafe_allow_html=True)
    if fa.empty or fm.empty:
        st.warning('No se encontraron meses proyectados. Revisa la columna de reconstrucción de las hojas de modelos.')
    else:
        comp=fa[['Fecha','PERIODO','Pronostico_Soles']].rename(columns={'Pronostico_Soles':'Aditivo'}).merge(fm[['Fecha','Pronostico_Soles']].rename(columns={'Pronostico_Soles':'Multiplicativo'}),on='Fecha',how='inner')
        years=sorted(comp['Fecha'].dt.year.unique().tolist())
        selected=st.multiselect('Años proyectados',years,default=years)
        cf=comp[comp['Fecha'].dt.year.isin(selected)].copy()
        if winner:
            st.markdown(f'<div class="winner"><b>🏆 Modelo con menor MAPE en validación: {winner}</b><br><span class="small-note">Se evalúa una predicción fuera de muestra sobre los últimos 12 meses históricos. El ranking no se basa en los errores de reconstrucción del Excel, que pueden incluir componentes residuales.</span></div>',unsafe_allow_html=True)
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=cf['Fecha'],y=cf['Aditivo'],name='Modelo aditivo (Excel)',line=dict(color=BLUE,width=3),mode='lines+markers',marker=dict(size=4)))
        fig.add_trace(go.Scatter(x=cf['Fecha'],y=cf['Multiplicativo'],name='Modelo multiplicativo (Excel)',line=dict(color=TEAL,width=3,dash='dash'),mode='lines+markers',marker=dict(size=4)))
        style_fig(fig,450,'Créditos directos (S/)')
        st.plotly_chart(fig,use_container_width=True)
        cf['Diferencia (multiplicativo - aditivo)'] = cf['Multiplicativo']-cf['Aditivo']
        cf['Diferencia (%) vs aditivo'] = np.where(cf['Aditivo']!=0,(cf['Multiplicativo']/cf['Aditivo']-1)*100,np.nan)
        annual=cf.assign(Año=cf['Fecha'].dt.year).groupby('Año').agg(Aditivo_promedio=('Aditivo','mean'),Multiplicativo_promedio=('Multiplicativo','mean'),Aditivo_diciembre=('Aditivo','last'),Multiplicativo_diciembre=('Multiplicativo','last')).reset_index()
        st.markdown('#### Resumen anual de proyecciones')
        for col in annual.columns[1:]: annual[col]=annual[col].map(lambda x:fmt_soles(x))
        st.dataframe(annual,use_container_width=True,hide_index=True)
        with st.expander('Ver detalle mensual de proyecciones'):
            disp=cf.copy(); disp['Fecha']=disp['Fecha'].dt.strftime('%Y-%m')
            for col in ['Aditivo','Multiplicativo','Diferencia (multiplicativo - aditivo)']: disp[col]=disp[col].map(lambda x:fmt_soles(x))
            disp['Diferencia (%) vs aditivo']=disp['Diferencia (%) vs aditivo'].map(lambda x:f'{fmt_num(x)}%' if pd.notna(x) else '—')
            st.dataframe(disp,use_container_width=True,hide_index=True)
        st.download_button('Descargar comparación en soles (CSV)',cf.to_csv(index=False).encode('utf-8-sig'),file_name='comparacion_modelos_bcp_soles.csv',mime='text/csv')
    st.markdown('#### Prueba retrospectiva de precisión (últimos 12 meses históricos)')
    st.caption('Esta evaluación complementaria estima tendencia y estacionalidad con datos anteriores al periodo de prueba. No reemplaza ni cambia los pronósticos que ya tienes en Excel.')
    if metrics is not None:
        mdisp=metrics.copy()
        mdisp['MAE (S/)']=mdisp['MAE'].map(fmt_soles)
        mdisp['RMSE (S/)']=mdisp['RMSE'].map(fmt_soles)
        mdisp['MAPE (%)']=mdisp['MAPE (%)'].map(lambda x:f'{fmt_num(x)}%')
        st.dataframe(mdisp[['Modelo','MAE (S/)','RMSE (S/)','MAPE (%)']],use_container_width=True,hide_index=True)
        st.info('MAE y RMSE se expresan en soles; MAPE es porcentual. Menor valor indica menor error en este periodo de prueba, pero no garantiza que el mismo modelo sea siempre superior.')
        if holdout is not None:
            hfig=go.Figure()
            hfig.add_trace(go.Scatter(x=holdout['Fecha'],y=holdout['Créditos directos']*FACTOR_SOLES,name='Real 2025',line=dict(color=NAVY,width=3)))
            hfig.add_trace(go.Scatter(x=holdout['Fecha'],y=holdout['Aditivo']*FACTOR_SOLES,name='Aditivo validación',line=dict(color=BLUE,width=2,dash='dash')))
            hfig.add_trace(go.Scatter(x=holdout['Fecha'],y=holdout['Multiplicativo']*FACTOR_SOLES,name='Multiplicativo validación',line=dict(color=TEAL,width=2,dash='dot')))
            style_fig(hfig,350,'Créditos directos (S/)')
            st.plotly_chart(hfig,use_container_width=True)

elif section == 'Contexto de fluctuaciones':
    st.markdown('<div class="section-title">¿Qué pudo influir en las fluctuaciones?</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Cronología contextual para interpretar la curva del crédito. Los eventos no son variables incluidas en tu Excel y no se deben presentar como causa demostrada.</div>',unsafe_allow_html=True)
    st.warning('Importante: una coincidencia temporal no demuestra causalidad. Para cuantificar el efecto del dólar, inflación, tasas, política o clima, se necesitarían series mensuales adicionales y un análisis econométrico.')
    cats=sorted(set(e['category'] for e in EVENTS))
    selected_cats=st.multiselect('Filtrar por tipo de evento',cats,default=cats)
    events=[e for e in EVENTS if e['category'] in selected_cats and first_date.year<=e['year']<=last_date.year]
    if events:
        for ev in events:
            st.markdown(f'''<div class="context-card"><div style="font-size:.72rem;color:{BLUE};font-weight:800;letter-spacing:.08em">{ev['year']} · {ev['category'].upper()}</div><div style="font-size:1.08rem;font-weight:750;color:{NAVY};margin:3px 0">{ev['title']}</div><div style="color:{INK};font-size:.92rem;line-height:1.55">{ev['summary']}</div><div style="margin-top:8px"><a href="{ev['source']}" target="_blank" style="color:{BLUE};font-weight:650;text-decoration:none">Consultar fuente: {ev['source_name']} ↗</a></div></div>''',unsafe_allow_html=True)
    st.markdown('#### Cómo leer una curva con contexto')
    st.markdown('''1. **Identifica el cambio:** señala el mes donde aumenta o disminuye la serie.
2. **Comprueba la fecha:** busca si un acontecimiento ocurrió en el mismo periodo o con rezago.
3. **Propón un mecanismo:** por ejemplo, menor actividad puede cambiar la demanda de crédito; la volatilidad cambiaria puede afectar a clientes expuestos a dólares; un desastre puede afectar negocios y pagos.
4. **Contrasta con datos:** revisa tasas de interés, inflación, tipo de cambio, PBI, morosidad o crédito del sistema.
5. **Evita afirmar causalidad sin prueba:** formula “podría estar relacionado” hasta realizar una evaluación estadística.''')
    st.markdown('#### Próximo nivel: cruzar las curvas con variables macroeconómicas')
    st.write('La siguiente mejora analítica sería añadir series mensuales oficiales de tipo de cambio, tasa de referencia, inflación y actividad económica para comparar sus movimientos con los créditos del BCP. Por ahora no se han inventado valores macroeconómicos ni se han añadido a tu base original.')

else:
    st.markdown('<div class="section-title">Datos, unidades y metodología</div>',unsafe_allow_html=True)
    st.markdown('#### Estructura del libro original')
    st.write('- **BASE_BCP:** créditos directos, depósitos totales y patrimonio históricos.')
    st.write('- **ADITIVO:** cálculos de tendencia, estacionalidad y reconstrucción/proyección del modelo aditivo.')
    st.write('- **MULTIPLICATIVO:** cálculos del modelo multiplicativo y su columna de reconstrucción/proyección.')
    st.markdown('#### Unidad de visualización')
    st.info('La fuente del Excel está expresada en miles de soles. El dashboard multiplica los valores por 1.000 para presentarlos en soles (S/). Esta conversión solo se aplica a la visualización y a los archivos CSV exportados; no modifica el libro original ni sus fórmulas.')
    st.markdown('#### Límites de interpretación')
    st.write('- Las proyecciones originales son únicamente de créditos directos y abarcan los 36 meses incluidos en el libro.')
    st.write('- Depósitos y patrimonio pueden analizarse históricamente; el archivo no incluye proyecciones propias para esas dos variables.')
    st.write('- La validación retrospectiva es un complemento independiente y no reemplaza los valores de las hojas ADITIVO y MULTIPLICATIVO.')
    st.write('- El contexto histórico es orientativo; para demostrar impactos se necesitan variables explicativas y un análisis específico.')
    with st.expander('Ver datos históricos en soles'):
        display=base.copy(); display['Fecha']=display['Fecha'].dt.strftime('%Y-%m')
        for v in VARIABLES: display[v]=display[v]*FACTOR_SOLES
        display=display.rename(columns={v:f'{v} (S/)' for v in VARIABLES})
        st.dataframe(display,use_container_width=True,hide_index=True)
        st.download_button('Descargar base en soles (CSV)',display.to_csv(index=False).encode('utf-8-sig'),file_name='base_bcp_soles.csv',mime='text/csv')
    with st.expander('Ver proyección original del modelo aditivo'):
        show=ad.copy(); show['Fecha']=show['Fecha'].dt.strftime('%Y-%m'); show['Pronóstico (S/)']=show['Pronostico_Soles']
        st.dataframe(show[show['Es_pronostico']][['Fecha','PERIODO','Pronóstico (S/)']],use_container_width=True,hide_index=True)
    with st.expander('Ver proyección original del modelo multiplicativo'):
        show=mu.copy(); show['Fecha']=show['Fecha'].dt.strftime('%Y-%m'); show['Pronóstico (S/)']=show['Pronostico_Soles']
        st.dataframe(show[show['Es_pronostico']][['Fecha','PERIODO','Pronóstico (S/)']],use_container_width=True,hide_index=True)

st.markdown('---')
st.markdown(f'<div class="small-note">BCP Analytics · Panel académico de series de tiempo · Fuente base: Excel del usuario · Contexto: BCRP, INEI y fuentes oficiales enlazadas. Presentación en soles (S/); proyecciones originales preservadas.</div>',unsafe_allow_html=True)
