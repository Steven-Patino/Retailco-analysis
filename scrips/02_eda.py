import pandas as pd

from retailco_utils import load_raw_dataset


def main() -> None:
    df = load_raw_dataset()

    print("--- Analisis Exploratorio de Datos (EDA) ---")
    print("\nShape del dataset:")
    print(df.shape)

    print("\nTipos de dato por columna:")
    print(df.dtypes.to_string())

    print("\nPorcentaje de nulos por columna:")
    null_pct = (df.isna().mean() * 100).sort_values(ascending=False).round(2)
    print(null_pct.to_string())

    print("\nProblemas de calidad detectados:")
    duplicate_order_ids = int(df.duplicated(subset=["Order ID"]).sum())
    qty_zero = int((pd.to_numeric(df["Qty"], errors="coerce") == 0).sum())
    invalid_dates = int(
        pd.to_datetime(df["Date"], format="%m-%d-%y", errors="coerce").isna().sum()
    )
    issues = [
        (
            "Columnas con alta proporcion de nulos",
            "fulfilled-by, promotion-ids, Unnamed: 22, currency y Amount",
        ),
        (
            "Tipos inconsistentes o ambiguos",
            "Date llega como texto y ship-postal-code como float",
        ),
        (
            "Llave de negocio no unica",
            f"Order ID tiene {duplicate_order_ids} filas repetidas",
        ),
        (
            "Valores que afectan metricas",
            f"Qty tiene {qty_zero} filas en cero e invalid_dates={invalid_dates}",
        ),
    ]
    for title, detail in issues:
        print(f"- {title}: {detail}")

    print("\nEstadisticas descriptivas de columnas numericas clave:")
    numeric_summary = (
        df[["Qty", "Amount", "ship-postal-code"]]
        .apply(pd.to_numeric, errors="coerce")
        .describe()
        .round(2)
    )
    print(numeric_summary.to_string())


if __name__ == "__main__":
    main()

