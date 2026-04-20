# Reporte EDA

## Resumen general

El dataset contiene `128,975` filas y `24` columnas. A nivel general, la informacion es util para analisis comerciales, pero requiere una etapa de limpieza antes de cargarla al modelo estrella o usarla en reportes ejecutivos.

---

## Problemas de calidad de datos encontrados

### 1. Columnas con alta proporcion de nulos

- `fulfilled-by`: 69.55% de valores nulos.
- `promotion-ids`: 38.11% de valores nulos.
- `Unnamed: 22`: 38.03% de valores nulos.
- `Amount` y `currency`: 6.04% de valores nulos.

**Impacto potencial**

- Dificultan el analisis operacional y la trazabilidad del proceso de entrega.
- En el caso de `Amount`, afectan directamente metricas clave como revenue, ticket promedio y comparativos mensuales.
- `Unnamed: 22` no aporta valor analitico claro y genera ruido.

### 2. Tipos de dato incorrectos o ambiguos

- `Date` llega como texto y no como fecha.
- `ship-postal-code` fue inferida como numerica (`float64`) cuando realmente es un identificador geografico.

**Impacto potencial**

- Si `Date` no se convierte correctamente, no se pueden construir tendencias mensuales, semanales o trimestrales de forma confiable.
- Si `ship-postal-code` se trata como numero, se pueden perder ceros, deformar codigos y dañar agrupaciones geograficas.

### 3. Llave de negocio no unica

- `Order ID` presenta `8,597` repeticiones.

**Impacto potencial**

- No se puede asumir que una orden equivale a una sola fila.
- Si se usa `Order ID` como llave unica, se producirian duplicados falsos o perdida de detalle en la tabla de hechos.

### 4. Filas con `Qty = 0`

- Se identificaron `12,807` filas con cantidad igual a cero.

**Impacto potencial**

- El calculo de `ticket_promedio = Amount / Qty` puede producir division por cero.
- Muchas de estas filas estan asociadas a ordenes canceladas, por lo que es importante decidir si se excluyen o se mantienen para analisis operativo.

---

## Columnas con tipo de dato incorrecto y por que es critico corregirlas

| Columna | Tipo actual | Tipo esperado | Por que es critico |
| --- | --- | --- | --- |
| `Date` | `object` | `datetime` | Permite agrupar por mes, trimestre, semana y construir la dimension tiempo |
| `ship-postal-code` | `float64` | `string` | Es un codigo, no una medida; si se trata como numero se deforma |
| `Amount` | `float64` con nulos | `decimal` limpio | Es la base del revenue y del ticket promedio |
| `B2B` | booleano correcto, pero debe estandarizarse | `boolean` | Se usa para segmentacion de clientes en el modelo |

---

## Conclusion

Antes del analisis y la carga a PostgreSQL es necesario:

- normalizar tipos de dato,
- resolver nulos en campos clave,
- definir un criterio realista de duplicados,
- proteger los calculos frente a `Qty = 0`.

Sin esta limpieza, cualquier dashboard o consulta SQL podria entregar resultados engañosos.

