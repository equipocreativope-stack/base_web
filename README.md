# BCP Analytics · Académico

Dashboard académico independiente de series de tiempo para créditos directos del BCP, con datos históricos de créditos, depósitos y patrimonio.

## Funciones
- Base `Base_BCP_Consolidada.xlsx` cargada automáticamente desde la misma carpeta que `app.py`.
- Hojas requeridas: `BASE_BCP`, `ADITIVO` y `MULTIPLICATIVO`.
- Pronósticos originales de las hojas ADITIVO y MULTIPLICATIVO presentados por separado.
- Comparación de pronósticos originales y validación retrospectiva en horizontes de 12, 24 y 36 meses.
- Selección de ganador por horizonte y ganador global por menor MAPE promedio entre horizontes, con MAE y RMSE como medidas complementarias.
- Valores mostrados en soles (S/); el libro original está en miles de soles y se multiplica por 1.000 únicamente en la visualización.
- Tema claro azul y blanco, con acentos dorados y textos de alto contraste.
- Cronología contextual de eventos, sin atribuir causalidad sin análisis estadístico.

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue
Sube `app.py`, `requirements.txt`, `README.md`, `.streamlit/config.toml` y `Base_BCP_Consolidada.xlsx` a la raíz del repositorio (la carpeta `.streamlit` debe contener `config.toml`). Configura Streamlit Community Cloud para ejecutar `app.py`.

## Nota académica
Este proyecto es independiente y no es una web ni una herramienta oficial del Banco de Crédito del Perú. Los resultados retrospectivos son evidencia comparativa, no garantía de precisión futura. El ganador global usa el menor MAPE promedio con el mismo peso para cada horizonte disponible; las métricas individuales y la estabilidad también deben considerarse.
