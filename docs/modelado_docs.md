# Decisiones de modelado

Este documento resume las decisiones principales del modelo de datos analitico de RetailCo y explica por que se eligio esta estructura.

---

## Por que se eligio un esquema estrella

Se eligio un **esquema estrella** en lugar de una tabla plana o un esquema copo de nieve porque ofrece un mejor equilibrio entre rendimiento, claridad y facilidad de analisis.

### Ventajas principales

- **Consultas mas rapidas:** los motores analiticos estan optimizados para resolver `star joins` de forma eficiente.
- **Menos complejidad:** al reducir la cantidad de uniones entre tablas, las consultas son mas faciles de construir y mantener.
- **Mejor experiencia en BI:** herramientas como Power BI trabajan muy bien con este tipo de estructura.
- **Jerarquias mas simples:** facilita analizar la informacion por niveles como `dia -> mes -> anio` sin configuraciones complejas.

### Comparacion con otras opciones

| Opcion | Ventajas | Desventajas |
| --- | --- | --- |
| **Tabla plana** | Sencilla de entender al inicio | Duplica datos, ocupa mas espacio y complica el mantenimiento |
| **Esquema estrella** | Rapido, claro y comodo para analisis | Requiere una separacion inicial entre hechos y dimensiones |
| **Copo de nieve** | Mayor normalizacion | Introduce mas joins y vuelve mas complejas las consultas |

### Conclusion

Para RetailCo, el esquema estrella es la mejor opcion porque permite analizar datos de forma rapida, ordenada y compatible con herramientas de visualizacion.

---

## Diferencia entre OLTP y OLAP

RetailCo necesita tanto una base **OLTP** como una base **OLAP** porque cumplen funciones distintas dentro del negocio.

### Base OLTP

La base de datos **OLTP** se usa para la operacion diaria. Su objetivo es procesar transacciones de forma rapida y segura.

#### Se utiliza para:

- insertar nuevos registros,
- actualizar informacion,
- eliminar datos cuando corresponde,
- soportar el funcionamiento del sistema en tiempo real.

En otras palabras, es la base que sostiene el trabajo cotidiano de la aplicacion, tanto en backend como en frontend.

### Base OLAP

La base de datos **OLAP** se usa para analisis y toma de decisiones. Aunque no participa directamente en la operacion del dia a dia, es clave para estudiar el comportamiento del negocio.

#### Se utiliza para:

- generar reportes,
- analizar tendencias,
- comparar periodos,
- construir tableros e indicadores.

Su estructura esta pensada para consultar grandes volumenes de informacion de manera eficiente.

---

## Por que RetailCo necesita ambas

Separar OLTP y OLAP evita mezclar la operacion diaria con los procesos analiticos.

- La base **OLTP** prioriza velocidad transaccional y estabilidad operativa.
- La base **OLAP** prioriza lectura, analisis historico y consultas complejas.
- Ejecutar analisis pesados sobre la base OLTP podria afectar el rendimiento del sistema productivo.
- Mantener una base analitica separada reduce riesgos para la operacion principal.

### Idea central

La base OLTP permite que la empresa funcione dia a dia, mientras que la base OLAP permite entender lo que ocurre en el negocio y apoyar la toma de decisiones sin poner en riesgo el sistema en produccion.
