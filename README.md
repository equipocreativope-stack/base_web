# BCP Analytics — Dashboard de modelos de series de tiempo

Aplicación Streamlit para explorar el libro Excel del proyecto BCP.

## Incluye
- Resumen ejecutivo e histórico de créditos, depósitos y patrimonio.
- Visualización del modelo aditivo desde la hoja `ADITIVO`.
- Visualización del modelo multiplicativo desde la hoja `MULTIPLICATIVO`.
- Comparación de las proyecciones ya calculadas para créditos directos.
- Tablas anuales/mensuales y exportación CSV.

## Ejecutar localmente
1. Instala Python 3.10 o superior.
2. Abre una terminal en esta carpeta.
3. Ejecuta `pip install -r requirements.txt`.
4. Ejecuta `streamlit run app.py`.

El libro `Base_BCP_Consolidada.xlsx` está incluido como archivo inicial. También puedes cargar otra versión desde el panel lateral, siempre que conserve las hojas `BASE_BCP`, `ADITIVO` y `MULTIPLICATIVO`.

## Alcance actual
Las hojas de modelos suministradas contienen proyecciones para **Créditos directos**. Depósitos totales y patrimonio se muestran como series históricas desde `BASE_BCP`.
