import pandas as pd

from retailco_utils import get_connection


BASE_FILTER = """
WHERE e.status NOT ILIKE 'Cancelled%%'
  AND f.amount > 0
  AND f.quantity > 0
"""


def run_query(conn, title: str, query: str) -> None:
    print(f"\n--- {title} ---")
    result = pd.read_sql(query, conn)
    print(result.to_string(index=False))


def main() -> None:
    top_sku_query = f"""
    SELECT p.sku, p.category, ROUND(SUM(f.amount)::numeric, 2) AS revenue_total
    FROM fact_ventas f
    JOIN dim_producto p ON p.sku = f.sku
    JOIN dim_envio e ON e.id_envio = f.id_envio
    {BASE_FILTER}
    GROUP BY p.sku, p.category
    ORDER BY revenue_total DESC
    LIMIT 10
    """

    sales_by_month_query = f"""
    SELECT
        CONCAT(t.year, '-', LPAD(t.month::text, 2, '0')) AS mes,
        ROUND(SUM(f.amount)::numeric, 2) AS ventas_totales
    FROM fact_ventas f
    JOIN dim_tiempo t ON t.date = f.date
    JOIN dim_envio e ON e.id_envio = f.id_envio
    {BASE_FILTER}
    GROUP BY t.year, t.month
    ORDER BY t.year, t.month
    """

    avg_ticket_query = f"""
    SELECT
        p.category,
        ROUND((SUM(f.amount) / NULLIF(SUM(f.quantity), 0))::numeric, 2) AS ticket_promedio
    FROM fact_ventas f
    JOIN dim_producto p ON p.sku = f.sku
    JOIN dim_envio e ON e.id_envio = f.id_envio
    {BASE_FILTER}
    GROUP BY p.category
    ORDER BY ticket_promedio DESC
    """

    revenue_by_channel_query = f"""
    SELECT
        e.ship_service_level AS canal_venta,
        ROUND(SUM(f.amount)::numeric, 2) AS revenue_total
    FROM fact_ventas f
    JOIN dim_envio e ON e.id_envio = f.id_envio
    {BASE_FILTER}
    GROUP BY e.ship_service_level
    ORDER BY revenue_total DESC
    """

    with get_connection() as conn:
        run_query(conn, "Top 10 SKU por revenue total", top_sku_query)
        run_query(conn, "Ventas totales por mes", sales_by_month_query)
        run_query(conn, "Ticket promedio por categoria", avg_ticket_query)
        run_query(conn, "Revenue por canal de venta", revenue_by_channel_query)


if __name__ == "__main__":
    main()
