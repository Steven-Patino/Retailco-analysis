# Dashboard ejecutivo

## Objetivo

El dashboard ejecutivo debe responder en menos de 90 segundos estas preguntas:

- como evolucionan las ventas totales,
- que categoria lidera el negocio,
- cual es la tendencia mensual,
- si existe alguna alerta o anomalia visible.

---

## Componentes recomendados

### 1. KPI card

**Metrica sugerida:** revenue total del periodo.

Se utiliza porque permite mostrar de inmediato el tamaño del negocio sin obligar al usuario a interpretar un grafico primero.

### 2. Grafico de tendencia temporal

**Tipo sugerido:** linea mensual de ventas.

Es el mas adecuado para mostrar comportamiento en el tiempo, identificar picos y detectar caidas anormales.

### 3. Comparacion por categoria

**Tipo sugerido:** barras verticales por categoria.

Ayuda a detectar rapidamente la categoria lider y la distancia respecto a las demas.

### 4. Filtro interactivo

**Filtro sugerido:** mes o categoria.

Permite que el director explore periodos concretos sin recargar el dashboard con demasiadas visualizaciones.

---

## Buenas practicas de visualizacion aplicadas

1. **Jerarquia visual:** primero se destaca el KPI principal, luego la tendencia y despues el detalle por categoria.
2. **Consistencia de color:** el mismo color base representa revenue y se reservan colores de alerta para caidas o anomalias.
3. **Eliminacion de ruido:** se reducen lineas, bordes y elementos decorativos innecesarios para priorizar la lectura.

---

## Alerta o anomalia sugerida

Vale la pena incluir una señal visual cuando ocurra alguno de estos casos:

- caida fuerte frente al mes anterior,
- categoria lider con desaceleracion,
- aumento atipico de ordenes canceladas,
- ticket promedio significativamente por debajo de la media historica.

