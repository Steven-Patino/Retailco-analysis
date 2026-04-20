-- Consulta 1: total de ventas y cantidad de ordenes por mes.
-- name: ventas_y_ordenes_por_mes
SELECT
    CONCAT(t.year, '-', LPAD(t.month::text, 2, '0')) AS mes,
    ROUND(SUM(f.amount)::numeric, 2) AS total_ventas,
    COUNT(*) AS cantidad_ordenes
FROM fact_ventas f
JOIN dim_tiempo t ON t.date = f.date
JOIN dim_envio e ON e.id_envio = f.id_envio
WHERE e.status NOT ILIKE 'Cancelled%'
GROUP BY t.year, t.month
ORDER BY t.year, t.month;

-- Consulta 2: CTE para identificar SKU cuyo ultimo mes supera su promedio historico.
-- name: sku_sobre_promedio_ultimo_mes
WITH promedio_historico AS (
    SELECT
        p.sku,
        AVG(f.amount) AS promedio_historico
    FROM fact_ventas f
    JOIN dim_producto p ON p.sku = f.sku
    JOIN dim_envio e ON e.id_envio = f.id_envio
    WHERE e.status NOT ILIKE 'Cancelled%'
    GROUP BY p.sku
),
ultimo_mes AS (
    SELECT MAX(DATE_TRUNC('month', t.date)) AS mes_maximo
    FROM dim_tiempo t
),
ventas_ultimo_mes AS (
    SELECT
        p.sku,
        AVG(f.amount) AS promedio_ultimo_mes
    FROM fact_ventas f
    JOIN dim_producto p ON p.sku = f.sku
    JOIN dim_tiempo t ON t.date = f.date
    JOIN dim_envio e ON e.id_envio = f.id_envio
    CROSS JOIN ultimo_mes um
    WHERE DATE_TRUNC('month', t.date) = um.mes_maximo
      AND e.status NOT ILIKE 'Cancelled%'
    GROUP BY p.sku
)
SELECT
    vum.sku,
    ROUND(vum.promedio_ultimo_mes::numeric, 2) AS promedio_ultimo_mes,
    ROUND(ph.promedio_historico::numeric, 2) AS promedio_historico
FROM ventas_ultimo_mes vum
JOIN promedio_historico ph ON ph.sku = vum.sku
WHERE vum.promedio_ultimo_mes > ph.promedio_historico
ORDER BY promedio_ultimo_mes DESC;

-- Consulta 3: vista con amount total, qty total y ticket promedio por categoria.
-- name: crear_vista_ventas_por_categoria
CREATE OR REPLACE VIEW ventas_por_categoria AS
SELECT
    p.category,
    ROUND(SUM(f.amount)::numeric, 2) AS amount_total,
    SUM(f.quantity) AS qty_total,
    ROUND((SUM(f.amount) / NULLIF(SUM(f.quantity), 0))::numeric, 2) AS ticket_promedio
FROM fact_ventas f
JOIN dim_producto p ON p.sku = f.sku
JOIN dim_envio e ON e.id_envio = f.id_envio
WHERE e.status NOT ILIKE 'Cancelled%'
GROUP BY p.category;

-- name: consultar_vista_ventas_por_categoria
SELECT
    category,
    amount_total,
    qty_total,
    ticket_promedio
FROM ventas_por_categoria
ORDER BY amount_total DESC;

-- Consulta 4: top 5 estados por revenue y porcentaje sobre el total.
-- name: top_5_estados_por_revenue
SELECT
    e.ship_state,
    ROUND(SUM(f.amount)::numeric, 2) AS revenue_total,
    ROUND(
        100 * SUM(f.amount) / NULLIF(SUM(SUM(f.amount)) OVER (), 0),
        2
    ) AS porcentaje_total
FROM fact_ventas f
JOIN dim_envio e ON e.id_envio = f.id_envio
WHERE e.status NOT ILIKE 'Cancelled%'
GROUP BY e.ship_state
ORDER BY revenue_total DESC
LIMIT 5;
