# BCP Analytics — Dashboard de series de tiempo

Dashboard en Streamlit que lee el libro `Base_BCP_Consolidada.xlsx` con las hojas `BASE_BCP`, `ADITIVO` y `MULTIPLICATIVO`.

## Mejoras incluidas
- Interfaz corporativa financiera azul, blanca y gris, con animaciones CSS sutiles y gráficos interactivos.
- Presentación de los importes en soles (S/) mediante factor de visualización 1.000; el Excel original no se modifica.
- Filtros por variable y periodo histórico.
- Comparación de los pronósticos originales aditivo y multiplicativo para 2026–2028.
- Validación retrospectiva adicional en los últimos 12 meses históricos, con MAE, RMSE y MAPE para elegir el menor error en una prueba comparable. Esta prueba no sustituye las proyecciones del Excel.
- Cronología contextual de acontecimientos económicos, políticos, sociales y climáticos del Perú con fuentes enlazadas y advertencia explícita de que no demuestra causalidad.
- Exportación de tablas a CSV en soles.

## Ejecutar localmente
1. Instala Python 3.10 o posterior.
2. En esta carpeta, ejecuta `pip install -r requirements.txt`.
3. Ejecuta `streamlit run app.py`.
4. El dashboard abrirá en el navegador.

## Publicar en Streamlit Community Cloud
Sube `app.py`, `requirements.txt`, `README.md` y `Base_BCP_Consolidada.xlsx` a la raíz del repositorio GitHub. En Streamlit Community Cloud selecciona el repositorio, rama y archivo `app.py`.

## Integridad de datos
La aplicación no reestima ni modifica las columnas originales de reconstrucción/proyección. Solo multiplica por 1.000 los valores presentados porque el libro fuente está expresado en miles de soles. La validación de precisión es una comparación complementaria separada, entrenada antes de los últimos 12 meses.
