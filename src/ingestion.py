"""Carga del Excel fuente (hoja servicios)."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.config import EXPECTED_COLUMNS, SERVICIOS_SHEET, resolve_raw_excel_path

logger = logging.getLogger(__name__)


def load_servicios(path: Path | None = None) -> pd.DataFrame:
    """Lee la hoja `servicios` y valida que existan las columnas esperadas."""
    excel_path = path or resolve_raw_excel_path()

    df = pd.read_excel(excel_path, sheet_name=SERVICIOS_SHEET)
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas en el Excel: {missing}")

    logger.info(
        "Ingestión: %s filas, %s columnas desde %s",
        len(df),
        df.shape[1],
        excel_path,
    )
    return df
