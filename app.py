from pathlib import Path
from io import BytesIO
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title='BCP Analytics | Inteligencia financiera', page_icon='📊', layout='wide', initial_sidebar_state='expanded')

# Paleta corporativa y contraste explícito para evitar texto blanco en tema oscuro.
NAVY = '#EAF2FF'  # Paleta académica inspirada en tonos bancarios; no es una web oficial del BCP
BLUE = '#69AFFF'
CYAN = '#62D9F5'
TEAL = '#55D6BE'
GOLD = '#FFD166'
INK = '#E5EDF7'
MUTED = '#A9BAD0'
BG = '#071426'
PANEL = '#10223A'
PANEL_ALT = '#152B47'
BORDER = '#29415F'
FACTOR_SOLES = 1000  # Los datos del archivo SBS están expresados en miles de soles.
DEFAULT_FILE = Path(__file__).parent / 'Base_BCP_Consolidada.xlsx'
VARIABLES = ['Créditos directos', 'Depósitos totales', 'Patrimonio']

st.markdown(f'''<style>
:root {{ color-scheme: dark; }}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{ background:{BG} !important; color:{INK} !important; }}
[data-testid="stHeader"] {{ background:rgba(7,20,38,.96) !important; }}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {{ background:#0B1B30 !important; color:{INK} !important; border-right:1px solid {BORDER}; }}
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown label, label, p, li {{ color:inherit; }}
h1,h2,h3,h4,h5,h6,[data-testid="stSubheader"] {{ color:{NAVY} !important; }}
[data-testid="stMetric"] {{ background:linear-gradient(145deg,{PANEL},{PANEL_ALT}) !important; border:1px solid {BORDER}; padding:15px 17px; border-radius:15px; box-shadow:0 8px 25px rgba(0,0,0,.18); animation:rise .45s ease both; }}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {{ color:{MUTED} !important; font-weight:650; }}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {{ color:{CYAN} !important; font-weight:750; }}
[data-testid="stDataFrame"], [data-testid="stTable"] {{ background:{PANEL} !important; }}
input, textarea, [data-baseweb="select"] > div {{ background-color:{PANEL_ALT} !important; color:{INK} !important; border-color:{BORDER} !important; }}
[data-testid="stWidgetLabel"] p {{ color:{INK} !important; }}
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label, [data-testid="stToggle"] label {{ color:{INK} !important; }}
.hero {{ position:relative; overflow:hidden; background:linear-gradient(115deg,#06152B 0%,#0B3268 58%,#14549A 100%); color:#FFFFFF !important; padding:27px 30px; border:1px solid #234B78; border-radius:21px; margin-bottom:14px; box-shadow:0 18px 45px rgba(0,0,0,.24); }}
.hero:after {{ content:""; position:absolute; width:320px;height:320px;right:-65px;top:-170px;border:1px solid rgba(140,205,255,.24);border-radius:50%;box-shadow:0 0 0 28px rgba(140,205,255,.045),0 0 0 58px rgba(140,205,255,.025); animation:orbit 24s linear infinite; pointer-events:none; }}
.hero h1 {{ font-size:2.1rem; letter-spacing:-.04em; margin:0 0 6px; color:#FFFFFF !important; }}
.hero p {{ color:#D8E8FA !important; margin:0; max-width:900px; }}
.hero .eyebrow {{ text-transform:uppercase; letter-spacing:.16em; font-size:.72rem; font-weight:750; color:{CYAN} !important; margin-bottom:8px; }}
.pill {{ display:inline-block; padding:5px 10px; border-radius:999px; background:rgba(105,175,255,.13); color:#FFFFFF !important; font-size:.78rem; margin-top:13px; border:1px solid rgba(160,210,255,.25); }}
.section-title {{ font-size:1.28rem; font-weight:800; color:{NAVY} !important; letter-spacing:-.02em; margin:.5rem 0 .25rem; }}
.subtle {{ color:{MUTED} !important; font-size:.91rem; }}
.winner {{ border:1px solid #267B79; background:linear-gradient(135deg,#123C48,{PANEL}); border-radius:15px; padding:17px 19px; box-shadow:0 8px 24px rgba(0,0,0,.16); color:{INK} !important; }}
.context-card {{ border-left:4px solid {CYAN}; background:{PANEL}; border:1px solid {BORDER}; border-left:4px solid {CYAN}; border-radius:0 12px 12px 0; padding:12px 15px; margin:8px 0; box-shadow:0 3px 12px rgba(0,0,0,.12); color:{INK} !important; }}
.small-note {{ color:{MUTED} !important; font-size:.83rem; }}
[data-testid="stAlert"] {{ background:{PANEL} !important; border-color:{BORDER} !important; }}
[data-testid="stAlert"] p {{ color:{INK} !important; }}
hr {{ border-color:{BORDER} !important; }}
.stButton button {{ background:{BLUE}; color:#06152B; border:0; font-weight:750; }}
@keyframes rise {{ from {{opacity:0; transform:translateY(7px)}} to {{opacity:1;transform:translateY(0)}} }}
@keyframes orbit {{ from {{transform:rotate(0deg)}} to {{transform:rotate(360deg)}} }}
@media (prefers-reduced-motion: reduce) {{ *,*:before,*:after {{animation:none!important;transition:none!important}} }}
</style>''', unsafe_allow_html=True)

EVENTS = [
 {'date':'2017-03-01','year':2017,'category':'Clima y desastres','title':'El Niño Costero','summary':'Lluvias e inundaciones dañaron infraestructura y afectaron transporte, agricultura, comercio y otras actividades. Puede ser contexto para cambios de actividad y demanda de crédito; no prueba un efecto directo en el BCP.','source':'https://www.bcrp.gob.pe/eng-docs/Publications/Annual-Reports/2017/annual-report-2017-1.pdf','source_name':'BCRP · Memoria 2017'},
 {'date':'2020-03-01','year':2020,'category':'Salud y economía','title':'Pandemia y restricciones por COVID-19','summary':'La economía peruana se contrajo con fuerza en 2020. El shock alteró actividad, ingresos, consumo, inversión y comportamiento financiero. La serie bancaria puede reflejar varios canales y medidas extraordinarias.','source':'https://m.inei.gob.pe/prensa/noticias/produccion-nacional-disminuyo-1112-durante-el-ano-2020-12741/','source_name':'INEI · Producción nacional 2020'},
 {'date':'2021-06-01','year':2021,'category':'Política y tipo de cambio','title':'Incertidumbre electoral y volatilidad cambiaria','summary':'El BCRP reportó volatilidad cambiaria en el contexto de la incertidumbre del periodo electoral. La exposición del banco depende también de la moneda y composición de las operaciones.','source':'https://www.bcrp.gob.pe/docs/Publicaciones/Memoria/2021/memoria-bcrp-2021-5.pdf','source_name':'BCRP · Memoria 2021'},
 {'date':'2022-02-01','year':2022,'category':'Economía global','title':'Inflación global y shocks externos','summary':'El entorno internacional de inflación, tasas y materias primas pudo modificar costos de fondeo, demanda de crédito y preferencias de ahorro. Es contexto, no una estimación causal sobre el BCP.','source':'https://www.bcrp.gob.pe/reporte-de-inflacion/34-publicaciones/memoria-anual.html','source_name':'BCRP · Memorias anuales'},
 {'date':'2023-01-01','year':2023,'category':'Social y política','title':'Protestas y bloqueos','summary':'Las protestas y bloqueos de inicios de año afectaron la actividad en diversas zonas y sectores. El efecto específico sobre los créditos del BCP requiere datos adicionales.','source':'https://www.elperuano.pe/noticia/224122-protestas-impactaron-08-en-pbi','source_name':'El Peruano · Información económica'},
 {'date':'2023-03-01','year':2023,'category':'Clima y desastres','title':'El Niño y lluvias intensas','summary':'Los eventos climáticos pueden afectar producción, logística, ingresos de hogares y empresas y su demanda o capacidad de pago. La coincidencia temporal no demuestra causalidad.','source':'https://www.bcrp.gob.pe/eng-docs/Publications/Annual-Reports/2023/annual-report-2023.pdf','source_name':'BCRP · Memoria 2023'},
 {'date':'2024-01-01','year':2024,'category':'Clima y recuperación','title':'Recuperación tras shocks climáticos','summary':'Los efectos climáticos pueden trasladarse a precios, producción y servicios con rezagos. Se requiere contrastar la cronología con indicadores mensuales antes de asociar un evento a una variación concreta del crédito.','source':'https://investigacion.bcrp.gob.pe/es/investigaciones/documentos-de-trabajo/2025/dt-2025-008','source_name':'BCRP · Investigación sobre ENSO'},
]

@st.cache_data(show_spinner=False)
def load_workbook(file_bytes):
    xls = pd.ExcelFile(BytesIO(file_bytes))
    required_sheets = {'BASE_BCP','ADITIVO','MULTIPLICATIVO'}
    if not required_sheets.issubset(set(xls.sheet_names)):
        raise ValueError('El libro debe contener BASE_BCP, ADITIVO y MULTIPLICATIVO.')
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
        pred_col = 'Reconstrucción (T+E+C+R)'
        trend_col, seasonal_col = 'Tendencia (Tt)', 'Estacional (Et)'
    else:
        pred_col = 'PRECIO RRECONSTRUIDO' if 'PRECIO RRECONSTRUIDO' in d else 'PRECIO RECONSTRUIDO'
        trend_col, seasonal_col = 'TENDENCIA', 'INDICE ESTACIONAL AJUSTADO'
    if pred_col not in d: raise ValueError(f'No se encontró la columna {pred_col} en el modelo {model}.')
    d['Pronostico_original'] = numeric(d[pred_col])
    d['Pronostico_Soles'] = d['Pronostico_original'] * FACTOR_SOLES
    d['Tendencia_Soles'] = numeric(d[trend_col]) * FACTOR_SOLES if trend_col in d else np.nan
    d['Estacional_original'] = numeric(d[seasonal_col]) if seasonal_col in d else np.nan
    d['Es_pronostico'] = d['Fecha'] > last_hist_date
    return d

def validation_one_horizon(base, variable, horizon):
    """Backtest independiente. Entrena solo con el tramo previo y prueba los últimos horizon meses."""
    d = base[['Fecha', variable]].copy()
    d[variable] = numeric(d[variable])
    d = d.dropna().sort_values('Fecha').reset_index(drop=True)
    if len(d) <= horizon + 24:
        return None
    train, test = d.iloc[:-horizon].copy(), d.iloc[-horizon:].copy()
    train['t'] = np.arange(1, len(train)+1)
    slope, intercept = np.polyfit(train['t'], train[variable].to_numpy(float), 1)
    train['trend'] = intercept + slope*train['t']
    train['month'] = train['Fecha'].dt.month
    train['resid'] = train[variable] - train['trend']
    train['ratio'] = np.where(train['trend'] > 0, train[variable] / train['trend'], np.nan)
    add_idx = train.groupby('month')['resid'].mean()
    add_idx = add_idx - add_idx.mean()
    mul_idx = train.groupby('month')['ratio'].mean()
    mul_idx = mul_idx / mul_idx.mean()
    test['t'] = np.arange(len(train)+1, len(train)+horizon+1)
    test['trend'] = intercept + slope*test['t']
    test['Aditivo'] = test['trend'] + test['Fecha'].dt.month.map(add_idx).to_numpy()
    test['Multiplicativo'] = test['trend'] * test['Fecha'].dt.month.map(mul_idx).to_numpy()
    actual = test[variable].to_numpy(float)
    rows=[]
    for model in ['Aditivo','Multiplicativo']:
        pred = test[model].to_numpy(float)
        err = actual - pred
        nz = actual != 0
        rows.append({'Horizonte (meses)':horizon,'Modelo':model,'MAE (S/)':float(np.mean(np.abs(err))*FACTOR_SOLES),'RMSE (S/)':float(np.sqrt(np.mean(err**2))*FACTOR_SOLES),'MAPE (%)':float(np.mean(np.abs(err[nz]/actual[nz]))*100) if nz.any() else np.nan})
    test['Real_Soles'] = test[variable] * FACTOR_SOLES
    test['Aditivo_Soles'] = test['Aditivo'] * FACTOR_SOLES
    test['Multiplicativo_Soles'] = test['Multiplicativo'] * FACTOR_SOLES
    return pd.DataFrame(rows), test

def style_fig(fig, height=430, ytitle=''):
    fig.update_layout(template='plotly_dark', height=height, margin=dict(l=8,r=15,t=35,b=8), hovermode='x unified',
      font=dict(family='Inter, Arial, sans-serif', color=INK), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=PANEL,
      xaxis=dict(showgrid=False, linecolor=BORDER, color=INK), yaxis=dict(title=ytitle, gridcolor=BORDER, zerolinecolor=BORDER, color=INK),
      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0, bgcolor='rgba(16,34,58,.8)', font=dict(color=INK)))
    return fig

def forecast_chart(model_frame, label, color):
    fig=go.Figure()
    hist=base[['Fecha','Créditos directos']].dropna()
    proj=model_frame[model_frame['Es_pronostico'] & model_frame['Pronostico_Soles'].notna()]
    fig.add_trace(go.Scatter(x=hist['Fecha'],y=hist['Créditos directos']*FACTOR_SOLES,name='Histórico observado',line=dict(color=NAVY,width=2.5)))
    if not proj.empty:
        last=hist.iloc[-1]
        fig.add_trace(go.Scatter(x=[last['Fecha'],*proj['Fecha'].tolist()],y=[last['Créditos directos']*FACTOR_SOLES,*proj['Pronostico_Soles'].tolist()],name=f'Pronóstico {label.lower()} original',line=dict(color=color,width=3.5,dash='dash'),mode='lines'))
        if 'Tendencia_Soles' in proj and proj['Tendencia_Soles'].notna().any():
            fig.add_trace(go.Scatter(x=proj['Fecha'],y=proj['Tendencia_Soles'],name='Tendencia estimada',line=dict(color=GOLD,width=2,dash='dot')))
    style_fig(fig,450,'Créditos directos (S/)')
    return fig

if not DEFAULT_FILE.exists():
    st.error('No se encontró Base_BCP_Consolidada.xlsx junto a app.py. Verifica que el archivo esté en la raíz del repositorio GitHub.')
    st.stop()
try:
    source_bytes = DEFAULT_FILE.read_bytes()
    base, add_raw, mult_raw = load_workbook(source_bytes)
except Exception as e:
    st.error(f'No se pudo leer la base del repositorio. Detalle: {e}')
    st.stop()

required = {'Fecha', *VARIABLES}
if not required.issubset(base.columns):
    st.error('BASE_BCP debe incluir Fecha, Créditos directos, Depósitos totales y Patrimonio.')
    st.stop()
for v in VARIABLES: base[v] = numeric(base[v])
base = base.sort_values('Fecha').drop_duplicates('Fecha', keep='last').reset_index(drop=True)
first_date, last_date = base['Fecha'].min(), base['Fecha'].max()
try:
    ad = prep_model(add_raw, 'Aditivo', last_date)
    mu = prep_model(mult_raw, 'Multiplicativo', last_date)
except Exception as e:
    st.error(f'No se pudieron preparar las hojas de modelos. Detalle: {e}')
    st.stop()
fa = ad[ad['Es_pronostico'] & ad['Pronostico_Soles'].notna()].copy()
fm = mu[mu['Es_pronostico'] & mu['Pronostico_Soles'].notna()].copy()

st.sidebar.markdown(f'<div style="background:linear-gradient(145deg,#06152B,#0B3268);padding:17px;border-radius:15px;color:#FFFFFF !important;margin-bottom:12px"><div style="font-size:.72rem;letter-spacing:.14em;color:#9DDBF1 !important;font-weight:750">INTELIGENCIA FINANCIERA</div><div style="font-size:1.45rem;font-weight:800;color:#FFFFFF !important">BCP Analytics</div><div style="font-size:.83rem;color:#D6E9F7 !important">Series de tiempo · SBS</div></div>', unsafe_allow_html=True)
st.sidebar.caption('Base conectada al archivo del repositorio · presentación en soles')
st.sidebar.markdown('### Filtros')
variable = st.sidebar.selectbox('Variable histórica', VARIABLES, index=0)
min_date, max_date = first_date.date(), last_date.date()
start_date = st.sidebar.date_input('Desde', value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input('Hasta', value=max_date, min_value=min_date, max_value=max_date)
if start_date > end_date: start_date, end_date = end_date, start_date
hist = base[(base['Fecha'].dt.date >= start_date) & (base['Fecha'].dt.date <= end_date)].copy()
sections=['Resumen ejecutivo','Evolución histórica','Modelo aditivo','Modelo multiplicativo','Comparación de modelos','Contexto de fluctuaciones','Datos y metodología']
section=st.sidebar.radio('Navegación',sections)

st.markdown(f'''<div class="hero"><div class="eyebrow">Panel académico de análisis bancario · Perú</div><h1>BCP Analytics</h1><p>Dashboard académico inspirado en una estética bancaria azul. Análisis de tendencias, proyecciones y riesgos de interpretación de la cartera de créditos.</p><span class="pill">SOLES PERUANOS (S/) · HISTÓRICO {first_date:%Y}–{last_date:%Y} · PROYECCIÓN ORIGINAL 2026–2028</span></div>''',unsafe_allow_html=True)
st.caption(f'Fuente: libro consolidado del repositorio · {len(base):,} observaciones mensuales · unidad de origen: miles de soles; conversión de visualización a soles.')

# Backtests por horizontes. El modelo se vuelve a estimar en cada horizonte sin modificar el Excel.
validation_results=[]
validation_tests={}
for horizon in (12,24,36):
    result=validation_one_horizon(base,'Créditos directos',horizon)
    if result is not None:
        met,test=result
        validation_results.append(met)
        validation_tests[horizon]=test
all_metrics=pd.concat(validation_results,ignore_index=True) if validation_results else pd.DataFrame()

if section == 'Resumen ejecutivo':
    st.markdown('<div class="section-title">Resumen ejecutivo</div>',unsafe_allow_html=True)
    st.markdown('<div class="subtle">Lectura para la alta dirección: escala de la cartera, evolución y proyecciones originales de créditos directos.</div>',unsafe_allow_html=True)
    lastrow=base.iloc[-1]
    prev=base[base['Fecha'] <= last_date-pd.DateOffset(years=1)]
    yoy=(lastrow['Créditos directos']/prev.iloc[-1]['Créditos directos']-1)*100 if len(prev) and prev.iloc[-1]['Créditos directos'] else np.nan
    growth=(base.iloc[-1]['Créditos directos']/base.iloc[0]['Créditos directos']-1)*100 if base.iloc[0]['Créditos directos'] else np.nan
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Créditos directos · último dato',fmt_soles(lastrow['Créditos directos']*FACTOR_SOLES))
    c2.metric('Variación interanual',f'{fmt_num(yoy)}%' if pd.notna(yoy) else '—')
    c3.metric('Cambio desde inicio',f'{fmt_num(growth)}%' if pd.notna(growth) else '—')
    c4.metric('Horizonte de proyección',f'{min(len(fa),len(fm))} meses' if len(fa) and len(fm) else '—')
    left,right=st.columns([1.55,1])
    with left:
        fig=go.Figure(); fig.add_trace(go.Scatter(x=hist['Fecha'],y=hist[variable]*FACTOR_SOLES,name=variable,line=dict(color=BLUE,width=3),fill='tozeroy',fillcolor='rgba(23,105,170,.08)'))
        style_fig(fig,370,f'{variable} (S/)'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with right:
        st.markdown('#### Señal de validación')
        if not all_metrics.empty:
            # Usar exactamente el mismo criterio global que en "Comparación de modelos".
            global_score = all_metrics.groupby('Modelo', as_index=False).agg(**{
                'MAPE promedio (%)': ('MAPE (%)', 'mean'),
                'MAE promedio (S/)': ('MAE (S/)', 'mean'),
                'RMSE promedio (S/)': ('RMSE (S/)', 'mean'),
                'Horizontes evaluados': ('Horizonte (meses)', 'nunique')
            }).sort_values('MAPE promedio (%)').reset_index(drop=True)
            win = global_score.iloc[0]
            st.markdown(f'<div class="winner"><div style="font-size:.74rem;color:{TEAL};font-weight:800;letter-spacing:.08em">RECOMENDACIÓN GLOBAL · TODOS LOS HORIZONTES</div><div style="font-size:1.5rem;font-weight:800;color:{NAVY};margin:5px 0">Modelo {win["Modelo"].lower()}</div><div style="color:{MUTED};font-size:.9rem">MAPE promedio: <b>{fmt_num(win["MAPE promedio (%)"])}%</b><br>MAE promedio: <b>{fmt_soles(win["MAE promedio (S/)" ])}</b><br>Horizontes evaluados: <b>{int(win["Horizontes evaluados"])}</b></div></div>',unsafe_allow_html=True)
            st.caption('Este es el ganador global por menor MAPE promedio, con el mismo peso para cada horizonte disponible. Los ganadores de 12, 24 y 36 meses pueden diferir; consulta la comparación para elegir según el plazo de decisión. La validación retrospectiva no garantiza el desempeño futuro.')
        else: st.info('No hay suficientes observaciones para las pruebas retrospectivas.')
        st.markdown('#### Puntos de contexto')
        for title,desc in [('2020 · COVID-19','Shock sanitario y económico.'),('2021 · Tipo de cambio','Volatilidad en el contexto electoral.'),('2023 · Clima y actividad','Protestas y eventos de El Niño.')]:
            st.markdown(f'<div class="context-card"><b>{title}</b><br><span class="small-note">{desc}</span></div>',unsafe_allow_html=True)
    st.markdown('#### Pronósticos originales de créditos directos')
    if not fa.empty and not fm.empty:
        comp=fa[['Fecha','Pronostico_Soles']].rename(columns={'Pronostico_Soles':'Aditivo'}).merge(fm[['Fecha','Pronostico_Soles']].rename(columns={'Pronostico_Soles':'Multiplicativo'}),on='Fecha',how='inner')
        fig=go.Figure(); fig.add_trace(go.Scatter(x=base['Fecha'],y=base['Créditos directos']*FACTOR_SOLES,name='Histórico',line=dict(color=NAVY,width=2.5)))
        fig.add_trace(go.Scatter(x=comp['Fecha'],y=comp['Aditivo'],name='Pronóstico aditivo',line=dict(color=BLUE,width=3,dash='dash')))
        fig.add_trace(go.Scatter(x=comp['Fecha'],y=comp['Multiplicativo'],name='Pronóstico multiplicativo',line=dict(color=TEAL,width=3,dash='dot')))
        style_fig(fig,400,'Créditos directos (S/)'); st.plotly_chart(fig,use_container_width=True)

elif section == 'Evolución histórica':
    st.markdown('<div class="section-title">Evolución histórica</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="subtle">{variable} expresado en soles. Los marcadores contextuales señalan acontecimientos que conviene contrastar con datos económicos.</div>',unsafe_allow_html=True)
    chart=hist[['Fecha',variable]].dropna().copy(); chart['Soles']=chart[variable]*FACTOR_SOLES
    fig=go.Figure(); fig.add_trace(go.Scatter(x=chart['Fecha'],y=chart['Soles'],mode='lines',name=variable,line=dict(color=BLUE,width=3),fill='tozeroy',fillcolor='rgba(23,105,170,.07)'))
    for ev in EVENTS:
        dt=pd.Timestamp(ev['date'])
        if pd.Timestamp(start_date)<=dt<=pd.Timestamp(end_date):
            fig.add_vline(x=dt,line_width=1,line_dash='dot',line_color=GOLD,opacity=.75)
            fig.add_annotation(x=dt,y=1,yref='paper',text=str(ev['year']),showarrow=False,yshift=8,font=dict(size=10,color='#8A641C'),bgcolor='rgba(255,247,220,.9)')
    style_fig(fig,460,f'{variable} (S/)'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':True,'scrollZoom':True})
    animate=st.toggle('Reproducir evolución por año',value=False)
    if animate and not chart.empty:
        years=sorted(chart['Fecha'].dt.year.unique())
        frames=[]
        for yr in years:
            sub=chart[chart['Fecha'].dt.year<=yr]
            frames.append(go.Frame(data=[go.Scatter(x=sub['Fecha'],y=sub['Soles'],mode='lines',line=dict(color=BLUE,width=3))],name=str(yr)))
        anim=go.Figure(data=[go.Scatter(x=chart[chart['Fecha'].dt.year==years[0]]['Fecha'],y=chart[chart['Fecha'].dt.year==years[0]]['Soles'],mode='lines',line=dict(color=BLUE,width=3))],frames=frames)
        anim.update_layout(updatemenus=[dict(type='buttons',showactive=False,buttons=[dict(label='▶ Reproducir',method='animate',args=[None,{'frame':{'duration':180,'redraw':True},'fromcurrent':True}]),dict(label='⏸ Pausar',method='animate',args=[[None],{'mode':'immediate','frame':{'duration':0,'redraw':False},'transition':{'duration':0}}])])])
        style_fig(anim,400,f'{variable} (S/)'); st.plotly_chart(anim,use_container_width=True)

elif section in ('Modelo aditivo','Modelo multiplicativo'):
    is_add=section=='Modelo aditivo'; frame=ad if is_add else mu; label='Aditivo' if is_add else 'Multiplicativo'; color=BLUE if is_add else TEAL
    projection=frame[frame['Es_pronostico'] & frame['Pronostico_Soles'].notna()].copy().sort_values('Fecha')
    st.markdown(f'<div class="section-title">Modelo {label.lower()}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="subtle">Proyección tomada directamente de la hoja {"ADITIVO" if is_add else "MULTIPLICATIVO"}; no se recalculan ni sustituyen tus valores originales.</div>',unsafe_allow_html=True)
    if projection.empty:
        st.warning('No se identificó el tramo de pronóstico en esta hoja. Verifica las fechas y la columna de reconstrucción.')
    else:
        firstp,lastp=projection.iloc[0],projection.iloc[-1]
        delta=(lastp['Pronostico_Soles']/firstp['Pronostico_Soles']-1)*100 if firstp['Pronostico_Soles'] else np.nan
        annual_mean=projection.assign(Año=projection['Fecha'].dt.year).groupby('Año')['Pronostico_Soles'].mean()
        k1,k2,k3,k4=st.columns(4)
        k1.metric('Inicio del pronóstico',fmt_soles(firstp['Pronostico_Soles']))
        k2.metric('Fin del pronóstico',fmt_soles(lastp['Pronostico_Soles']))
        k3.metric('Variación total del horizonte',f'{fmt_num(delta)}%' if pd.notna(delta) else '—')
        k4.metric('Promedio mensual proyectado',fmt_soles(projection['Pronostico_Soles'].mean()))
        fig=forecast_chart(frame,label,color); st.plotly_chart(fig,use_container_width=True)
        st.markdown('#### Indicadores para fundamentar el pronóstico')
        a,b=st.columns(2)
        with a:
            st.markdown('**Resumen por año**')
            annual=projection.assign(Año=projection['Fecha'].dt.year).groupby('Año').agg(Inicio=('Pronostico_Soles','first'),Promedio=('Pronostico_Soles','mean'),Cierre=('Pronostico_Soles','last')).reset_index()
            for col in ['Inicio','Promedio','Cierre']: annual[col]=annual[col].map(fmt_soles)
            st.dataframe(annual,use_container_width=True,hide_index=True)
        with b:
            st.markdown('**Lectura del método**')
            if is_add:
                st.write('El método aditivo representa la serie como tendencia más un componente estacional en unidades absolutas. Es útil cuando las variaciones estacionales mantienen magnitud relativamente estable.')
                if 'Tendencia_Soles' in projection and projection['Tendencia_Soles'].notna().any():
                    gap=(projection['Pronostico_Soles']-projection['Tendencia_Soles']).mean()
                    st.metric('Diferencia media pronóstico–tendencia',fmt_soles(gap))
            else:
                st.write('El método multiplicativo representa la estacionalidad como un factor relativo a la tendencia. Es útil cuando la amplitud estacional cambia en proporción al nivel de la serie.')
                idxcol='Estacional_original'
                if idxcol in projection and projection[idxcol].notna().any():
                    st.metric('Índice estacional medio',fmt_num(projection[idxcol].mean(),4))
        st.caption('Las cifras se muestran en S/. Los datos y cálculos almacenados en el Excel no se modifican.')

elif section == 'Comparación de modelos':
    st.markdown('<div class="section-title">Comparación y selección del modelo</div>',unsafe_allow_html=True)
    st.markdown('<div class="subtle">Evaluación académica para apoyar la decisión: se prioriza el error porcentual medio (MAPE) y se contrasta con MAE y RMSE en los horizontes de 12, 24 y 36 meses.</div>',unsafe_allow_html=True)
    if not all_metrics.empty:
        # Regla transparente: ganador global = menor MAPE promedio entre los horizontes disponibles.
        global_score = all_metrics.groupby('Modelo', as_index=False).agg(**{'MAPE promedio (%)':('MAPE (%)','mean'),'MAE promedio (S/)':('MAE (S/)','mean'),'RMSE promedio (S/)':('RMSE (S/)','mean'),'Horizontes evaluados':('Horizonte (meses)','nunique')})
        global_score = global_score.sort_values('MAPE promedio (%)').reset_index(drop=True)
        overall_winner = global_score.iloc[0]
        runner_up = global_score.iloc[1] if len(global_score)>1 else None
        margin = (runner_up['MAPE promedio (%)'] - overall_winner['MAPE promedio (%)']) if runner_up is not None else np.nan
        st.markdown(f'''<div class="winner"><div style="font-size:.74rem;color:{TEAL};font-weight:800;letter-spacing:.1em">RESULTADO GLOBAL · VALIDACIÓN RETROSPECTIVA</div><div style="font-size:1.7rem;font-weight:850;color:{NAVY};margin:6px 0">Modelo {overall_winner['Modelo'].lower()} recomendado por MAPE promedio</div><div style="color:{INK};line-height:1.65">MAPE promedio: <b>{fmt_num(overall_winner['MAPE promedio (%)'])}%</b> · MAE promedio: <b>{fmt_soles(overall_winner['MAE promedio (S/)'])}</b> · RMSE promedio: <b>{fmt_soles(overall_winner['RMSE promedio (S/)'])}</b><br>Se evaluaron {int(overall_winner['Horizontes evaluados'])} horizontes. {('La diferencia frente al otro modelo es de '+fmt_num(margin)+' puntos porcentuales de MAPE promedio.') if pd.notna(margin) else ''}</div></div>''',unsafe_allow_html=True)
        st.caption('Criterio de selección global: menor MAPE promedio con el mismo peso para cada horizonte disponible. No implica que el modelo gane en todos los horizontes; revisa los resultados individuales antes de elegir según el uso del pronóstico.')
    if not fa.empty and not fm.empty:
        comp=fa[['Fecha','Pronostico_Soles']].rename(columns={'Pronostico_Soles':'Aditivo'}).merge(fm[['Fecha','Pronostico_Soles']].rename(columns={'Pronostico_Soles':'Multiplicativo'}),on='Fecha',how='inner').sort_values('Fecha')
        fig=go.Figure(); fig.add_trace(go.Scatter(x=comp['Fecha'],y=comp['Aditivo'],name='Aditivo',line=dict(color=BLUE,width=3.2),mode='lines'))
        fig.add_trace(go.Scatter(x=comp['Fecha'],y=comp['Multiplicativo'],name='Multiplicativo',line=dict(color=TEAL,width=3.2,dash='dash'),mode='lines'))
        style_fig(fig,400,'Créditos directos proyectados (S/)'); st.plotly_chart(fig,use_container_width=True)
        diff=(comp['Multiplicativo']/comp['Aditivo']-1)*100
        c1,c2,c3=st.columns(3)
        c1.metric('Pronóstico aditivo · promedio',fmt_soles(comp['Aditivo'].mean()))
        c2.metric('Pronóstico multiplicativo · promedio',fmt_soles(comp['Multiplicativo'].mean()))
        c3.metric('Diferencia media relativa',f'{fmt_num(diff.mean())}%')
        annual=comp.assign(Año=comp['Fecha'].dt.year).groupby('Año').agg(**{'Aditivo promedio (S/)':('Aditivo','mean'),'Multiplicativo promedio (S/)':('Multiplicativo','mean'),'Aditivo cierre (S/)':('Aditivo','last'),'Multiplicativo cierre (S/)':('Multiplicativo','last')}).reset_index()
        for col in annual.columns[1:]: annual[col]=annual[col].map(fmt_soles)
        st.markdown('#### Síntesis por año')
        st.dataframe(annual,use_container_width=True,hide_index=True)
    st.markdown('#### Precisión retrospectiva por horizonte')
    st.write('En cada prueba se estima el modelo usando solo meses anteriores y se mide el error sobre los últimos 12, 24 o 36 meses. Así se observa si el resultado cambia con el horizonte.')
    if not all_metrics.empty:
        horizons=sorted(all_metrics['Horizonte (meses)'].unique())
        tabs=st.tabs([f'{h} meses' for h in horizons])
        for tab,h in zip(tabs,horizons):
            with tab:
                subset=all_metrics[all_metrics['Horizonte (meses)']==h].sort_values('MAPE (%)')
                best=subset.iloc[0]
                st.markdown(f'<div class="winner"><b>Ganador para {h} meses: modelo {best["Modelo"].lower()}</b><br><span class="small-note">Se selecciona por el menor MAPE en este horizonte. MAPE {fmt_num(best["MAPE (%)"])}% · MAE {fmt_soles(best["MAE (S/)"])} · RMSE {fmt_soles(best["RMSE (S/)"])}</span></div>',unsafe_allow_html=True)
                show=subset.copy()
                show['MAE (S/)']=show['MAE (S/)'].map(fmt_soles); show['RMSE (S/)']=show['RMSE (S/)'].map(fmt_soles); show['MAPE (%)']=show['MAPE (%)'].map(lambda x:f'{fmt_num(x)}%')
                st.dataframe(show[['Modelo','MAE (S/)','RMSE (S/)','MAPE (%)']],use_container_width=True,hide_index=True)
                test=validation_tests[h]
                hfig=go.Figure(); hfig.add_trace(go.Scatter(x=test['Fecha'],y=test['Real_Soles'],name='Real observado',line=dict(color=NAVY,width=2.8)))
                hfig.add_trace(go.Scatter(x=test['Fecha'],y=test['Aditivo_Soles'],name='Predicción aditiva',line=dict(color=BLUE,width=2.3,dash='dash')))
                hfig.add_trace(go.Scatter(x=test['Fecha'],y=test['Multiplicativo_Soles'],name='Predicción multiplicativa',line=dict(color=TEAL,width=2.3,dash='dot')))
                style_fig(hfig,300,'Créditos directos (S/)'); st.plotly_chart(hfig,use_container_width=True)
    else: st.info('No hay suficientes datos para evaluar los horizontes solicitados.')
    with st.expander('Cómo interpretar las métricas'):
        st.markdown('''- **MAE (error absoluto medio):** promedio de la distancia entre el valor real y el pronosticado. Se expresa en soles; cuanto menor, mejor. Es fácil de interpretar en la escala del negocio.
- **RMSE (raíz del error cuadrático medio):** también se expresa en soles, pero penaliza más los errores grandes. Si supera mucho al MAE, algunos errores pueden ser especialmente elevados.
- **MAPE (error porcentual absoluto medio):** expresa el error absoluto medio como porcentaje del valor real. Facilita comparar periodos, aunque puede ser inestable cuando los valores reales son cercanos a cero.

**Criterio de lectura:** menor error es mejor dentro de la misma prueba. Ninguna métrica garantiza el rendimiento futuro; también se deben considerar estabilidad, supuestos del método y utilidad para la decisión.''')
    st.caption('Estas pruebas son complementarias y no alteran los pronósticos originales del libro.')

elif section == 'Contexto de fluctuaciones':
    st.markdown('<div class="section-title">Contexto de fluctuaciones</div>',unsafe_allow_html=True)
    st.markdown('<div class="subtle">Cronología para formular hipótesis sobre cambios en la curva y contrastarlas con fuentes públicas.</div>',unsafe_allow_html=True)
    st.warning('La coincidencia temporal no demuestra causalidad. Para medir el efecto de dólar, inflación, tasas, política o clima, se necesitan series mensuales adicionales y un análisis estadístico.')
    cats=sorted(set(e['category'] for e in EVENTS)); selected_cats=st.multiselect('Ámbitos',cats,default=cats)
    for ev in [e for e in EVENTS if e['category'] in selected_cats and first_date.year<=e['year']<=last_date.year]:
        st.markdown(f'''<div class="context-card"><div style="font-size:.72rem;color:{BLUE};font-weight:800;letter-spacing:.08em">{ev['year']} · {ev['category'].upper()}</div><div style="font-size:1.08rem;font-weight:750;color:{NAVY};margin:3px 0">{ev['title']}</div><div style="color:{INK};font-size:.92rem;line-height:1.55">{ev['summary']}</div><div style="margin-top:8px"><a href="{ev['source']}" target="_blank" style="color:{BLUE};font-weight:650;text-decoration:none">Consultar fuente: {ev['source_name']} ↗</a></div></div>''',unsafe_allow_html=True)
    st.markdown('#### Cómo convertir contexto en evidencia')
    st.markdown('1. Localizar el mes donde cambia la serie.\n2. Verificar la fecha del evento y considerar posibles rezagos.\n3. Proponer un mecanismo económico plausible.\n4. Contrastar con indicadores mensuales oficiales, por ejemplo tipo de cambio, tasa de referencia, inflación, actividad económica y morosidad.\n5. Evitar afirmar causalidad hasta estimar y validar un modelo con variables explicativas.')

else:
    st.markdown('<div class="section-title">Datos y metodología</div>',unsafe_allow_html=True)
    st.markdown('#### Libro conectado')
    st.write('El dashboard lee automáticamente `Base_BCP_Consolidada.xlsx` desde la misma carpeta que `app.py`. Al actualizar el archivo en el repositorio, la aplicación puede leer la nueva versión tras el despliegue.')
    st.markdown('#### Estructura del libro')
    st.write('- **BASE_BCP:** créditos directos, depósitos totales y patrimonio históricos.\n- **ADITIVO:** componentes y reconstrucción/proyección del método aditivo.\n- **MULTIPLICATIVO:** componentes y reconstrucción/proyección del método multiplicativo.')
    st.markdown('#### Unidades')
    st.info('El archivo fuente está expresado en miles de soles. El panel multiplica por 1.000 para mostrar S/ soles peruanos; las celdas originales del Excel no se modifican.')
    st.markdown('#### Alcance analítico')
    st.write('- Los pronósticos originales disponibles corresponden a créditos directos y abarcan 36 meses (2026–2028).\n- Depósitos y patrimonio se presentan en el análisis histórico; no se generan proyecciones nuevas para ellos.\n- Los backtests de 12, 24 y 36 meses son cálculos adicionales de validación, no sustituyen los resultados del Excel.\n- Los acontecimientos son contexto para formular hipótesis; no son variables explicativas incorporadas al modelo.')
    with st.expander('Consultar histórico en soles'):
        display=base.copy(); display['Fecha']=display['Fecha'].dt.strftime('%Y-%m')
        for v in VARIABLES: display[v]=display[v]*FACTOR_SOLES
        display=display.rename(columns={v:f'{v} (S/)' for v in VARIABLES})
        st.dataframe(display,use_container_width=True,hide_index=True)

st.markdown('---')
st.markdown(f'<div class="small-note">BCP Analytics · Proyecto académico independiente; no es un producto oficial del BCP · Análisis de series de tiempo · Datos históricos: SBS · Acontecimientos: fuentes enlazadas. Los pronósticos son estimaciones y no constituyen garantías de resultados.</div>',unsafe_allow_html=True)
