from pathlib import Path

import pandas as pd

from retailco_utils import get_connection


QUERIES_PATH = Path(__file__).resolve().parents[1] / "queries.sql"


def parse_queries(path: Path) -> dict[str, str]:
    queries: dict[str, str] = {}
    current_name = None
    current_lines: list[str] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("-- name:"):
            if current_name and current_lines:
                queries[current_name] = "\n".join(current_lines).strip()
            current_name = line.split(":", 1)[1].strip()
            current_lines = []
            continue
        if line.startswith("--"):
            continue
        current_lines.append(line)

    if current_name and current_lines:
        queries[current_name] = "\n".join(current_lines).strip()
    return queries


def main() -> None:
    queries = parse_queries(QUERIES_PATH)

    with get_connection() as conn:
        for name, sql in queries.items():
            print(f"\n--- {name} ---")
            if name == "crear_vista_ventas_por_categoria":
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                conn.commit()
                print("Vista creada o actualizada correctamente.")
                continue

            result = pd.read_sql(sql, conn)
            print(result.to_string(index=False))


if __name__ == "__main__":
    main()
