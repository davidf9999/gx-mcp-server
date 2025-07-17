from __future__ import annotations

from urllib.parse import urlparse

import pandas as pd


def load(uri: str) -> pd.DataFrame:
    """Load a table from BigQuery given a connection URI."""
    try:
        from google.cloud import bigquery  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "google-cloud-bigquery is required for BigQuery URIs"
        ) from exc

    parsed = urlparse(uri)
    if parsed.scheme != "bigquery":
        raise ValueError("Invalid BigQuery URI")

    project = parsed.hostname or parsed.netloc
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise ValueError(
            "BigQuery URI must be bigquery://project/dataset/table"
        )
    dataset, table = parts[:2]

    client = bigquery.Client(project=project)
    query = f"SELECT * FROM `{project}.{dataset}.{table}`"
    df = client.query(query).to_dataframe()
    return df
