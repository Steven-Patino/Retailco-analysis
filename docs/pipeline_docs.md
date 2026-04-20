# Documentacion del pipeline

## Este proceso es ETL o ELT

El proceso implementado es **ETL**.

- **Extract:** se lee el archivo CSV original.
- **Transform:** se corrigen tipos, nulos, duplicados y se generan columnas derivadas antes de insertar.
- **Load:** solo despues de limpiar y transformar se cargan los datos al esquema estrella en PostgreSQL.

Se considera ETL porque la transformacion ocurre antes de la carga final al Data Warehouse.

---

## Que cambiaria si los datos llegaran en streaming

Si los datos llegaran en streaming, el diseño deberia cambiar en varios frentes:

- El pipeline dejaria de procesar archivos completos y pasaria a manejar eventos o micro-lotes.
- La logica de deduplicacion tendria que ser incremental y basada en llaves de negocio o identificadores de evento.
- Se necesitarian controles de idempotencia y ventanas de tiempo para manejar retrasos y reprocesos.
- La capa de almacenamiento podria incluir una zona intermedia para datos crudos antes de consolidarlos en el modelo estrella.

---

## Herramienta sugerida para orquestacion en produccion

La opcion mas razonable seria **Apache Airflow**.

### Por que

- Permite programar ejecuciones recurrentes del ETL.
- Hace visible el estado de cada tarea y los posibles errores.
- Facilita reintentos, dependencias y trazabilidad.
- Es una herramienta muy usada para pipelines batch con Python y bases de datos relacionales.

Si el escenario evolucionara a streaming, una alternativa mas adecuada podria ser combinar un broker de eventos como Kafka con un motor de procesamiento como Spark Structured Streaming o Flink.

