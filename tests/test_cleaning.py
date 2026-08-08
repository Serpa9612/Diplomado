"""Pruebas de reglas críticas de limpieza."""

from __future__ import annotations

import pandas as pd

from src.cleaning import clean_servicios
from src.validation import validate_clean_servicios


def _sample_dirty() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ID_servicio": ["S1", "S1", "S2", "S3", "S4"],
            "Fecha_solicitud": [
                "2025-04-18",
                "2025-04-18",
                "18/04/2025",
                "2025-05-01",
                "2025-05-02",
            ],
            "Ciudad": ["Bquilla", "Bquilla", "Sta Marta", "Monteria", "Cartagena"],
            "Tipo_servicio": [
                "Reparacion",
                "Reparacion",
                "INSTALACION",
                "Garantía",
                "Mantenimiento",
            ],
            "Canal": ["APP", "APP", "Call Center", "web", "Presencial"],
            "Tecnico_id": ["T001", "T001", "T002", "T003", "T004"],
            "Antiguedad_tecnico_meses": [10, 10, -2, 20, 15],
            "Tiempo_respuesta_horas": [12.0, 12.0, "sin dato", 999, 8.5],
            "Duracion_servicio_min": [60, 60, 70, 80, 90],
            "Costo_repuestos": [1000, 1000, 0, 500, 200],
            "Valor_servicio": [100000, 100000, "pendiente", -50, 0],
            "Reproceso": [0, 0, 1, 0, 0],
            "Satisfaccion": [4, 4, 5, 9, 3],
            "Estado": ["completado", "completado", "COMPLETADO", "Cancelado", "Completado"],
        }
    )


def test_drop_duplicates_and_canonical_categories() -> None:
    clean, report = clean_servicios(_sample_dirty())
    assert report.duplicates_removed == 1
    assert set(clean["Ciudad"]) <= {
        "Barranquilla",
        "Santa Marta",
        "Montería",
        "Cartagena",
    }
    assert validate_clean_servicios(clean) == []


def test_impossible_values_become_nan() -> None:
    clean, report = clean_servicios(_sample_dirty())
    assert report.impossible_tiempo_999 >= 1
    assert report.impossible_satisfaccion >= 1
    assert clean["Tiempo_respuesta_horas"].isna().sum() >= 2  # sin dato + 999
    assert clean.loc[clean["ID_servicio"] == "S3", "Satisfaccion"].isna().all()
