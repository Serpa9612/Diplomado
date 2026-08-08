"""Validaciones post-limpieza."""

from __future__ import annotations

import logging

import pandas as pd

from src.config import EXPECTED_COLUMNS

logger = logging.getLogger(__name__)

CANONICAL_CITIES = {
    "Barranquilla",
    "Santa Marta",
    "Cartagena",
    "Valledupar",
    "Montería",
    "Sincelejo",
}
CANONICAL_TYPES = {"Instalación", "Reparación", "Mantenimiento", "Garantía"}
CANONICAL_CHANNELS = {"App", "Call center", "Web", "Presencial"}
CANONICAL_STATUS = {"Completado", "Reprogramado", "Cancelado"}


def validate_clean_servicios(df: pd.DataFrame) -> list[str]:
    """Devuelve lista de errores; lista vacía si todo está bien."""
    errors: list[str] = []

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"Columnas faltantes: {missing}")

    if df.duplicated().any():
        errors.append(f"Aún hay duplicados: {int(df.duplicated().sum())}")

    if not pd.api.types.is_datetime64_any_dtype(df["Fecha_solicitud"]):
        errors.append("Fecha_solicitud no es datetime")

    bad_cities = set(df["Ciudad"].dropna().unique()) - CANONICAL_CITIES
    if bad_cities:
        errors.append(f"Ciudades no canónicas: {sorted(bad_cities)}")

    bad_types = set(df["Tipo_servicio"].dropna().unique()) - CANONICAL_TYPES
    if bad_types:
        errors.append(f"Tipos no canónicos: {sorted(bad_types)}")

    bad_channels = set(df["Canal"].dropna().unique()) - CANONICAL_CHANNELS
    if bad_channels:
        errors.append(f"Canales no canónicos: {sorted(bad_channels)}")

    bad_status = set(df["Estado"].dropna().unique()) - CANONICAL_STATUS
    if bad_status:
        errors.append(f"Estados no canónicos: {sorted(bad_status)}")

    if (df["Tiempo_respuesta_horas"] == 999).any():
        errors.append("Persisten valores 999 en Tiempo_respuesta_horas")

    sat = df["Satisfaccion"].dropna()
    if not sat.empty and not sat.isin([1, 2, 3, 4, 5]).all():
        errors.append("Satisfaccion con valores fuera de 1-5")

    if errors:
        for err in errors:
            logger.error("Validación: %s", err)
    else:
        logger.info("Validación OK (%s filas)", len(df))

    return errors
