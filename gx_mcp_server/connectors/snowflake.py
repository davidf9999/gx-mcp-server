from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pandas as pd


def load(uri: str) -> pd.DataFrame:
    """Load a table from Snowflake given a connection URI."""
    try:
        import snowflake.connector  # type: ignore[import]
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "snowflake-connector-python is required for Snowflake URIs"
        ) from exc

    parsed = urlparse(uri)
    if parsed.scheme != "snowflake":
        raise ValueError("Invalid Snowflake URI")

    user = parsed.username or ""
    password = parsed.password or ""
    account = parsed.hostname or ""

    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 3:
        raise ValueError(
            "Snowflake URI must be snowflake://user:pass@account/db/schema/table"
        )
    database, schema, table = parts[:3]

    params = parse_qs(parsed.query)
    warehouse = params.get("warehouse", [None])[0]

    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        database=database,
        schema=schema,
    )
    try:
        query = f'SELECT * FROM "{database}"."{schema}"."{table}"'
        cur = conn.cursor()
        cur.execute(query)
        df = cur.fetch_pandas_all()
    finally:
        conn.close()

    return df
