# Justificacion de graficos para el analisis

## 1. Top 10 SKU por revenue

Se propone un **grafico de barras horizontales** porque permite comparar categorias discretas con nombres largos de SKU sin sacrificar legibilidad. Ademas, facilita identificar rapidamente los productos lideres y su diferencia relativa en revenue.

## 2. Evolucion mensual de ventas

Se propone un **grafico de lineas** porque la variable principal es temporal. Este tipo de grafico muestra con claridad la tendencia mes a mes, ayuda a detectar estacionalidad y permite destacar visualmente el mes pico con una anotacion.

## 3. Ticket promedio por categoria

Se propone un **grafico de barras verticales** porque el objetivo es comparar una metrica agregada entre categorias discretas. Las barras facilitan ordenar categorias y detectar rapidamente cuales tienen mayor valor promedio por venta.

## 4. Revenue por canal de venta

Se propone un **grafico de barras** en lugar de un grafico circular. Aunque hay pocas categorias, el analisis busca comparar magnitudes exactas entre canales, y las barras hacen esta comparacion con mayor precision.

---

## Nota sobre Power BI

Para mantener coherencia con el ejercicio 5:

- el dashboard debe conectarse directamente a PostgreSQL,
- las metricas deben filtrar ordenes canceladas si el objetivo es medir revenue efectivo,
- el formato visual debe ser consistente en colores, etiquetas y unidades monetarias.

