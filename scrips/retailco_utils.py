from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT_DIR / "data" / "Amazon Sale Report.csv"
SCHEMA_PATH = ROOT_DIR / "schema.sql"

RAW_TO_CLEAN_COLUMNS = {
    "index": "source_row_id",
    "Order ID": "order_id",
    "Date": "order_date",
    "Status": "status",
    "Fulfilment": "fulfilment",
    "Sales Channel ": "sales_channel",
    "ship-service-level": "ship_service_level",
    "Style": "style",
    "SKU": "sku",
    "Category": "category",
    "Size": "size",
    "ASIN": "asin",
    "Courier Status": "courier_status",
    "Qty": "qty",
    "currency": "currency",
    "Amount": "amount",
    "ship-city": "ship_city",
    "ship-state": "ship_state",
    "ship-postal-code": "ship_postal_code",
    "ship-country": "ship_country",
    "promotion-ids": "promotion_ids",
    "B2B": "b2b",
    "fulfilled-by": "fulfilled_by",
    "Unnamed: 22": "unnamed_22",
}

STRING_COLUMNS = [
    "order_id",
    "status",
    "fulfilment",
    "sales_channel",
    "ship_service_level",
    "style",
    "sku",
    "category",
    "size",
    "asin",
    "courier_status",
    "currency",
    "ship_city",
    "ship_state",
    "ship_postal_code",
    "ship_country",
    "promotion_ids",
    "fulfilled_by",
    "unnamed_22",
]


def load_env_file(env_path: Path | None = None) -> None:
    env_file = env_path or ROOT_DIR / ".env"
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#") or "=" not in cleaned:
            continue
        key, value = cleaned.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def get_db_config() -> Dict[str, str]:
    load_env_file()
    required = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        missing_str = ", ".join(missing)
        raise RuntimeError(
            f"Faltan variables de entorno para la base de datos: {missing_str}."
        )

    return {
        "host": os.environ["DB_HOST"],
        "port": os.environ["DB_PORT"],
        "dbname": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
    }


def get_connection():
    import psycopg2

    return psycopg2.connect(**get_db_config())


def read_sql_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_raw_dataset(csv_path: Path | None = None) -> pd.DataFrame:
    dataset_path = csv_path or DATASET_PATH
    return pd.read_csv(dataset_path, low_memory=False)


def _normalize_strings(df: pd.DataFrame) -> pd.DataFrame:
    for column in STRING_COLUMNS:
        if column not in df.columns:
            continue
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
        )
    return df


def prepare_retailco_dataframe(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = raw_df.rename(columns=RAW_TO_CLEAN_COLUMNS).copy()
    df = _normalize_strings(df)

    df["source_row_id"] = pd.to_numeric(df["source_row_id"], errors="coerce").astype("Int64")
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(0).astype(int)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["ship_postal_code"] = (
        df["ship_postal_code"].astype("string").str.replace(r"\.0$", "", regex=True)
    )
    df["order_date"] = pd.to_datetime(df["order_date"], format="%m-%d-%y", errors="coerce")
    df["b2b"] = df["b2b"].astype("string").str.lower().map({"true": True, "false": False})
    df["b2b"] = df["b2b"].fillna(False).astype(bool)

    duplicate_keys = ["order_id", "sku", "order_date", "qty", "amount"]
    duplicate_rows = int(df.duplicated(subset=duplicate_keys).sum())
    df = df.drop_duplicates(subset=duplicate_keys).copy()

    missing_amount_before = int(df["amount"].isna().sum())
    cancelled_or_zero_mask = df["status"].str.contains("cancel", case=False, na=False) | df["qty"].eq(0)
    df.loc[df["amount"].isna() & cancelled_or_zero_mask, "amount"] = 0

    sku_median = df.groupby("sku")["amount"].transform("median")
    category_median = df.groupby("category")["amount"].transform("median")
    df["amount"] = df["amount"].fillna(sku_median).fillna(category_median).fillna(0).round(2)

    currency_mode = df["currency"].mode(dropna=True)
    df["currency"] = df["currency"].fillna(currency_mode.iloc[0] if not currency_mode.empty else "INR")

    shipping_fill_columns = [
        "ship_city",
        "ship_state",
        "ship_postal_code",
        "ship_country",
        "courier_status",
        "fulfilled_by",
    ]
    for column in shipping_fill_columns:
        df[column] = df[column].fillna("UNKNOWN")

    df["promotion_ids"] = df["promotion_ids"].fillna("NO_PROMOTION")
    df["unnamed_22"] = df["unnamed_22"].fillna("NOT_INFORMED")
    df["sales_channel"] = df["sales_channel"].fillna("UNKNOWN")
    df["ship_service_level"] = df["ship_service_level"].fillna("UNKNOWN")
    df["fulfilment"] = df["fulfilment"].fillna("UNKNOWN")
    df["category"] = df["category"].fillna("UNKNOWN")
    df["size"] = df["size"].fillna("UNKNOWN")
    df["style"] = df["style"].fillna("UNKNOWN")
    df["asin"] = df["asin"].fillna("UNKNOWN")
    df["sku"] = df["sku"].fillna("UNKNOWN")

    df["day"] = df["order_date"].dt.day
    df["month"] = df["order_date"].dt.month
    df["month_name"] = df["order_date"].dt.month_name()
    df["quarter"] = df["order_date"].dt.quarter
    df["year"] = df["order_date"].dt.year
    df["week_of_year"] = df["order_date"].dt.isocalendar().week.astype("Int64")
    df["ticket_promedio"] = np.where(df["qty"] > 0, (df["amount"] / df["qty"]).round(2), np.nan)
    df["customer_nk"] = np.where(df["b2b"], "B2B", "B2C")
    df["shipping_nk"] = (
        df["status"].fillna("UNKNOWN")
        + "|"
        + df["sales_channel"].fillna("UNKNOWN")
        + "|"
        + df["ship_service_level"].fillna("UNKNOWN")
        + "|"
        + df["ship_city"].fillna("UNKNOWN")
        + "|"
        + df["ship_state"].fillna("UNKNOWN")
        + "|"
        + df["ship_postal_code"].fillna("UNKNOWN")
        + "|"
        + df["ship_country"].fillna("UNKNOWN")
        + "|"
        + df["fulfilled_by"].fillna("UNKNOWN")
    )

    report = {
        "input_rows": int(len(raw_df)),
        "rows_after_cleaning": int(len(df)),
        "duplicate_rows_removed": duplicate_rows,
        "missing_amount_before": missing_amount_before,
        "missing_amount_after": int(df["amount"].isna().sum()),
        "missing_shipping_country_after": int(df["ship_country"].isna().sum()),
        "qty_zero_rows": int(df["qty"].eq(0).sum()),
        "invalid_dates": int(df["order_date"].isna().sum()),
    }
    return df, report


def analytical_sales_view(df: pd.DataFrame) -> pd.DataFrame:
    return df[
        ~df["status"].str.contains("cancel", case=False, na=False)
        & df["amount"].gt(0)
        & df["qty"].gt(0)
    ].copy()


def execute_schema(conn, schema_path: Path | None = None) -> None:
    sql = read_sql_file(schema_path or SCHEMA_PATH)
    with conn.cursor() as cursor:
        cursor.execute(sql)
    conn.commit()


def _insert_many(cursor, query: str, rows: Iterable[tuple]) -> None:
    from psycopg2.extras import execute_values

    normalized_rows = []
    for row in rows:
        normalized_row = []
        for value in row:
            if isinstance(value, np.generic):
                normalized_row.append(value.item())
            elif pd.isna(value):
                normalized_row.append(None)
            else:
                normalized_row.append(value)
        normalized_rows.append(tuple(normalized_row))
    rows = normalized_rows
    if rows:
        execute_values(cursor, query, rows)


def load_star_schema(conn, df: pd.DataFrame) -> dict:
    from psycopg2.extras import RealDictCursor

    execute_schema(conn)

    dim_producto = (
        df[["sku", "style", "category", "size", "asin"]]
        .drop_duplicates(subset=["sku"], keep="last")
        .assign(name=lambda frame: frame["style"])
    )
    dim_cliente = (
        df[["customer_nk", "b2b"]]
        .drop_duplicates(subset=["customer_nk"], keep="last")
        .assign(tipo_cliente=lambda frame: np.where(frame["b2b"], "B2B", "B2C"))
    )
    dim_envio = df[
        [
            "shipping_nk",
            "status",
            "courier_status",
            "fulfilment",
            "sales_channel",
            "ship_service_level",
            "ship_city",
            "ship_state",
            "ship_postal_code",
            "ship_country",
            "fulfilled_by",
        ]
    ].drop_duplicates(subset=["shipping_nk"], keep="last")
    dim_tiempo = df[
        ["order_date", "day", "month", "month_name", "quarter", "year", "week_of_year"]
    ].drop_duplicates(subset=["order_date"], keep="last")

    with conn.cursor() as cursor:
        _insert_many(
            cursor,
            """
            INSERT INTO dim_producto (sku, name, category, size, style, asin)
            VALUES %s
            ON CONFLICT (sku) DO UPDATE
            SET name = EXCLUDED.name,
                category = EXCLUDED.category,
                size = EXCLUDED.size,
                style = EXCLUDED.style,
                asin = EXCLUDED.asin
            """,
            dim_producto[["sku", "name", "category", "size", "style", "asin"]].itertuples(
                index=False, name=None
            ),
        )
        _insert_many(
            cursor,
            """
            INSERT INTO dim_cliente (customer_nk, b2b)
            VALUES %s
            ON CONFLICT (customer_nk) DO UPDATE
            SET b2b = EXCLUDED.b2b
            """,
            dim_cliente[["customer_nk", "b2b"]].itertuples(index=False, name=None),
        )
        _insert_many(
            cursor,
            """
            INSERT INTO dim_envio (
                shipping_nk,
                status,
                courier_status,
                fulfillment,
                sales_chanel,
                ship_service_level,
                ship_city,
                ship_state,
                ship_postal_code,
                ship_country,
                fulfilled_by
            )
            VALUES %s
            ON CONFLICT (shipping_nk) DO UPDATE
            SET status = EXCLUDED.status,
                courier_status = EXCLUDED.courier_status,
                fulfillment = EXCLUDED.fulfillment,
                sales_chanel = EXCLUDED.sales_chanel,
                ship_service_level = EXCLUDED.ship_service_level,
                ship_city = EXCLUDED.ship_city,
                ship_state = EXCLUDED.ship_state,
                ship_postal_code = EXCLUDED.ship_postal_code,
                ship_country = EXCLUDED.ship_country,
                fulfilled_by = EXCLUDED.fulfilled_by
            """,
            dim_envio.itertuples(index=False, name=None),
        )
        _insert_many(
            cursor,
            """
            INSERT INTO dim_tiempo (
                date,
                day,
                month,
                month_name,
                trimester,
                year,
                week
            )
            VALUES %s
            ON CONFLICT (date) DO UPDATE
            SET day = EXCLUDED.day,
                month = EXCLUDED.month,
                month_name = EXCLUDED.month_name,
                trimester = EXCLUDED.trimester,
                year = EXCLUDED.year,
                week = EXCLUDED.week
            """,
            dim_tiempo.itertuples(index=False, name=None),
        )
    conn.commit()

    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT sku FROM dim_producto")
        producto_map = {row["sku"]: row["sku"] for row in cursor.fetchall()}
        cursor.execute("SELECT cliente_id, customer_nk FROM dim_cliente")
        cliente_map = {row["customer_nk"]: row["cliente_id"] for row in cursor.fetchall()}
        cursor.execute("SELECT id_envio, shipping_nk FROM dim_envio")
        envio_map = {row["shipping_nk"]: row["id_envio"] for row in cursor.fetchall()}
        cursor.execute('SELECT "date" FROM dim_tiempo')
        tiempo_map = {row["date"]: row["date"] for row in cursor.fetchall()}

    fact_df = df.copy()
    fact_df["sku_fk"] = fact_df["sku"].map(producto_map)
    fact_df["cliente_id"] = fact_df["customer_nk"].map(cliente_map)
    fact_df["envio_id"] = fact_df["shipping_nk"].map(envio_map)
    fact_df["fecha_fk"] = fact_df["order_date"].dt.date.map(tiempo_map)

    fact_rows = fact_df[
        [
            "source_row_id",
            "order_id",
            "sku_fk",
            "cliente_id",
            "envio_id",
            "fecha_fk",
            "qty",
            "amount",
            "ticket_promedio",
            "currency",
        ]
    ].copy()
    fact_rows = fact_rows.rename(columns={"sku_fk": "sku", "fecha_fk": "date"})

    with conn.cursor() as cursor:
        _insert_many(
            cursor,
            """
            INSERT INTO fact_ventas (
                source_row_id,
                order_id,
                sku,
                cliente_id,
                id_envio,
                date,
                quantity,
                amount,
                ticket_promedio,
                currency
            )
            VALUES %s
            ON CONFLICT (source_row_id) DO NOTHING
            """,
            fact_rows.itertuples(index=False, name=None),
        )
    conn.commit()

    table_counts = {}
    with conn.cursor() as cursor:
        for table_name in [
            "dim_producto",
            "dim_cliente",
            "dim_envio",
            "dim_tiempo",
            "fact_ventas",
        ]:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            table_counts[table_name] = cursor.fetchone()[0]
    return table_counts
