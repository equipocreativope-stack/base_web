# BCP Analytics Académico

Dashboard académico de series de tiempo para créditos directos del BCP. No es una aplicación oficial del BCP.

## Incluye
- Base histórica de créditos directos, depósitos totales y patrimonio.
- Modelos aditivo y multiplicativo con sus pronósticos originales 2026–2028.
- Validación retrospectiva de 12, 24 y 36 meses con MAE, RMSE y MAPE.
- Regla única para ganador global: menor MAPE promedio entre los horizontes disponibles, con igual peso por horizonte.
- Tema oscuro con contraste claro, gráficos Plotly oscuros y animación opcional de la evolución histórica.
- Contexto histórico enlazado a fuentes públicas; los acontecimientos no se interpretan como causas demostradas.

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estructura requerida en GitHub
```text
app.py
Base_BCP_Consolidada.xlsx
requirements.txt
README.md
.streamlit/config.toml
```

La base debe conservar las hojas `BASE_BCP`, `ADITIVO` y `MULTIPLICATIVO`. Los valores originales del libro se expresan en miles de soles; la interfaz los convierte a soles multiplicando por 1.000 sin modificar el archivo.

## Nota metodológica
Las pruebas de 12, 24 y 36 meses utilizan ventanas de entrenamiento distintas, dado que cada prueba reserva un tramo final de longitud diferente. El ganador global es un resumen comparativo académico y no garantiza mejor desempeño futuro. Se recomienda complementar esta evaluación con validación de origen rodante antes de usar los pronósticos para decisiones reales.
