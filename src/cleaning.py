"""Limpieza y estandarización según botiquín Clase 3 y guía del trabajo final."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd

from src.config import (
    CHANNEL_MAP,
    CITY_MAP,
    SERVICE_TYPE_MAP,
    STATUS_MAP,
)

logger = logging.getLogger(__name__)


@dataclass
class CleaningReport:
    """Resumen cuantitativo de la limpieza para el informe académico."""

    rows_before: int = 0
    rows_after: int = 0
    duplicates_removed: int = 0
    nulls_before: dict[str, int] = field(default_factory=dict)
    nulls_after: dict[str, int] = field(default_factory=dict)
    text_to_nan_tiempo: int = 0
    text_to_nan_valor: int = 0
    impossible_tiempo_999: int = 0
    impossible_satisfaccion: int = 0
    impossible_antiguedad: int = 0
    impossible_valor_negativo: int = 0
    notes: list[str] = field(default_factory=list)

    def as_text(self) -> str:
        lines = [
            "=== LOG DE LIMPIEZA ===",
            f"Filas antes: {self.rows_before}",
            f"Duplicados eliminados: {self.duplicates_removed}",
            f"Filas después: {self.rows_after}",
            f"'sin dato' / no numéricos en Tiempo_respuesta_horas: {self.text_to_nan_tiempo}",
            f"'pendiente' / no numéricos en Valor_servicio: {self.text_to_nan_valor}",
            f"Tiempo_respuesta_horas == 999 → NaN: {self.impossible_tiempo_999}",
            f"Satisfaccion fuera de 1-5 → NaN: {self.impossible_satisfaccion}",
            f"Antiguedad_tecnico_meses < 0 → NaN: {self.impossible_antiguedad}",
            f"Valor_servicio < 0 → NaN: {self.impossible_valor_negativo}",
            "",
            "Nulos antes:",
        ]
        for k, v in self.nulls_before.items():
            lines.append(f"  {k}: {v}")
        lines.append("Nulos después:")
        for k, v in self.nulls_after.items():
            lines.append(f"  {k}: {v}")
        lines.append("")
        lines.extend(self.notes)
        return "\n".join(lines)


def _normalize_category(series: pd.Series, mapping: dict[str, str]) -> pd.Series:
    cleaned = series.astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    keys = cleaned.str.casefold()
    return keys.map(mapping).fillna(cleaned)


def clean_servicios(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """Aplica el botiquín de limpieza y devuelve el DataFrame limpio + reporte."""
    report = CleaningReport(rows_before=len(df))
    report.nulls_before = df.isna().sum().astype(int).to_dict()
    out = df.copy()

    # Enemigo 7 + 5: espacios invisibles y categorías inconsistentes
    out["Ciudad"] = _normalize_category(out["Ciudad"], CITY_MAP)
    out["Tipo_servicio"] = _normalize_category(out["Tipo_servicio"], SERVICE_TYPE_MAP)
    out["Canal"] = _normalize_category(out["Canal"], CHANNEL_MAP)
    out["Estado"] = _normalize_category(out["Estado"], STATUS_MAP)
    for col in ("ID_servicio", "Tecnico_id"):
        out[col] = out[col].astype(str).str.strip()

    # Enemigo 2: duplicados (guardar el resultado)
    before_dedup = len(out)
    out = out.drop_duplicates()
    report.duplicates_removed = before_dedup - len(out)

    # Fechas mezcladas (receta de la guía: ISO primero, luego DD/MM/YYYY)
    fecha_original = out["Fecha_solicitud"].copy()
    out["Fecha_solicitud"] = pd.to_datetime(
        fecha_original, format="%Y-%m-%d", errors="coerce"
    )
    out["Fecha_solicitud"] = out["Fecha_solicitud"].fillna(
        pd.to_datetime(fecha_original, format="%d/%m/%Y", errors="coerce")
    )

    # Enemigo 3: texto en números
    tiempo_raw = out["Tiempo_respuesta_horas"]
    tiempo_num = pd.to_numeric(tiempo_raw, errors="coerce")
    report.text_to_nan_tiempo = int(tiempo_raw.notna().sum() - tiempo_num.notna().sum())
    out["Tiempo_respuesta_horas"] = tiempo_num

    valor_raw = out["Valor_servicio"]
    valor_num = pd.to_numeric(valor_raw, errors="coerce")
    report.text_to_nan_valor = int(valor_raw.notna().sum() - valor_num.notna().sum())
    out["Valor_servicio"] = valor_num

    out["Duracion_servicio_min"] = pd.to_numeric(out["Duracion_servicio_min"], errors="coerce")
    out["Costo_repuestos"] = pd.to_numeric(out["Costo_repuestos"], errors="coerce")
    out["Antiguedad_tecnico_meses"] = pd.to_numeric(
        out["Antiguedad_tecnico_meses"], errors="coerce"
    )
    out["Satisfaccion"] = pd.to_numeric(out["Satisfaccion"], errors="coerce")
    out["Reproceso"] = pd.to_numeric(out["Reproceso"], errors="coerce").astype("Int64")

    # Enemigo 4: valores imposibles → None (NaN)
    mask_999 = out["Tiempo_respuesta_horas"] == 999
    report.impossible_tiempo_999 = int(mask_999.sum())
    out.loc[mask_999, "Tiempo_respuesta_horas"] = None

    mask_sat = out["Satisfaccion"].notna() & ~out["Satisfaccion"].isin([1, 2, 3, 4, 5])
    report.impossible_satisfaccion = int(mask_sat.sum())
    out.loc[mask_sat, "Satisfaccion"] = None

    mask_ant = out["Antiguedad_tecnico_meses"] < 0
    report.impossible_antiguedad = int(mask_ant.sum())
    out.loc[mask_ant, "Antiguedad_tecnico_meses"] = None

    mask_val = out["Valor_servicio"] < 0
    report.impossible_valor_negativo = int(mask_val.sum())
    out.loc[mask_val, "Valor_servicio"] = None

    report.rows_after = len(out)
    report.nulls_after = out.isna().sum().astype(int).to_dict()
    report.notes.append(
        "Decisión vacíos: no se imputaron Tiempo_respuesta_horas ni Satisfaccion "
        "(variables clave del análisis). Se dejan NaN y se filtran en el análisis."
    )
    report.notes.append(
        "Valor_servicio = 0 en Garantía se conserva como dato válido de negocio."
    )

    logger.info(
        "Limpieza: %s → %s filas (%s duplicados removidos)",
        report.rows_before,
        report.rows_after,
        report.duplicates_removed,
    )
    return out.reset_index(drop=True), report
