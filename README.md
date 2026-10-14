# BCP Analytics

Dashboard ejecutivo de series de tiempo para créditos directos del BCP, con análisis histórico de créditos, depósitos y patrimonio; pronósticos originales aditivo y multiplicativo; y validación retrospectiva por horizontes de 12, 24 y 36 meses.

## Datos

La aplicación lee automáticamente `Base_BCP_Consolidada.xlsx` desde la misma carpeta que `app.py`. No solicita al visitante cargar el Excel. Mantén el archivo en la raíz del repositorio junto a `app.py`.

El libro debe incluir las hojas `BASE_BCP`, `ADITIVO` y `MULTIPLICATIVO`. Los datos originales se encuentran expresados en miles de soles; la interfaz convierte la visualización a soles multiplicando por 1.000, sin editar el archivo fuente.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar con GitHub y Streamlit Community Cloud

1. Sube `app.py`, `requirements.txt`, `README.md`, `.streamlit/config.toml` y `Base_BCP_Consolidada.xlsx` al mismo repositorio.
2. Conecta el repositorio en Streamlit Community Cloud y selecciona `app.py` como archivo principal.
3. Cuando actualices el código o el Excel en GitHub, el servicio desplegará los cambios.

## Secciones

- Resumen ejecutivo
- Evolución histórica
- Modelo aditivo (pronóstico original)
- Modelo multiplicativo (pronóstico original)
- Comparación de modelos y backtesting a 12, 24 y 36 meses
- Contexto de fluctuaciones
- Datos y metodología

Los backtests son complementarios y no reemplazan las proyecciones originales del Excel. La cronología de acontecimientos no demuestra causalidad.
