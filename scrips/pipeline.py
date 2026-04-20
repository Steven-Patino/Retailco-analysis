from pathlib import Path

from retailco_utils import (
    get_connection,
    load_raw_dataset,
    load_star_schema,
    prepare_retailco_dataframe,
)


def extraer(ruta: str | Path):
    csv_path = Path(ruta)
    df = load_raw_dataset(csv_path)
    print(f"[extraer] Registros entrantes: {len(df)} desde {csv_path}")
    return df


def transformar(df):
    clean_df, report = prepare_retailco_dataframe(df)
    print(
        "[transformar] Registros despues de limpieza:",
        report["rows_after_cleaning"],
    )
    print(
        "[transformar] Duplicados eliminados:",
        report["duplicate_rows_removed"],
        "| nulos en Amount resueltos:",
        report["missing_amount_before"] - report["missing_amount_after"],
    )
    return clean_df


def cargar(df, conn):
    table_counts = load_star_schema(conn, df)
    print("[cargar] Insercion finalizada.")
    for table_name, total_rows in table_counts.items():
        print(f"[cargar] {table_name}: {total_rows}")
    return table_counts


def main() -> None:
    dataset_path = Path(__file__).resolve().parents[1] / "data" / "Amazon Sale Report.csv"
    raw_df = extraer(dataset_path)
    clean_df = transformar(raw_df)
    with get_connection() as conn:
        cargar(clean_df, conn)


if __name__ == "__main__":
    main()

