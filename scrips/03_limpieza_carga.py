from retailco_utils import (
    get_connection,
    load_raw_dataset,
    load_star_schema,
    prepare_retailco_dataframe,
)


def main() -> None:
    raw_df = load_raw_dataset()
    clean_df, report = prepare_retailco_dataframe(raw_df)

    print("--- Limpieza y carga a PostgreSQL ---")
    print(
        "Duplicados eliminados:",
        report["duplicate_rows_removed"],
        "| Criterio: order_id + sku + order_date + qty + amount",
    )
    print(
        "Nulos en Amount:",
        report["missing_amount_before"],
        "->",
        report["missing_amount_after"],
    )
    print("Filas con Qty = 0:", report["qty_zero_rows"])
    print("Fechas invalidas detectadas:", report["invalid_dates"])
    print(
        "Columnas derivadas generadas: month, week_of_year, quarter y ticket_promedio."
    )

    with get_connection() as conn:
        table_counts = load_star_schema(conn, clean_df)

    print("\nRegistros finales por tabla:")
    for table_name, total_rows in table_counts.items():
        print(f"- {table_name}: {total_rows}")


if __name__ == "__main__":
    main()

