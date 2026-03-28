from __future__ import annotations

from typing import Any, Protocol

try:
    import psycopg
except ImportError:  # pragma: no cover - optional dependency for portfolio artifact.
    psycopg = None


class DatabaseClient(Protocol):
    def query_rows(self, sql: str) -> list[dict[str, Any]]:
        ...


class PostgresQueryClient:
    """Portfolio-safe representation of the database layer used by retrieval."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        db_name: str,
        user: str,
        password: str,
    ) -> None:
        self._host = host
        self._port = port
        self._db_name = db_name
        self._user = user
        self._password = password

    def query_rows(self, sql: str) -> list[dict[str, Any]]:
        if psycopg is None:
            raise RuntimeError("psycopg is not installed. The database layer is included for architecture fidelity.")
        if not all([self._host, self._db_name, self._user, self._password]):
            raise RuntimeError(
                "Database credentials are not configured. This repository intentionally omits private infrastructure."
            )

        with psycopg.connect(
            host=self._host,
            port=self._port,
            dbname=self._db_name,
            user=self._user,
            password=self._password,
        ) as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
        return list(rows)
