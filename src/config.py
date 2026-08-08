"""Rutas y parámetros globales del proyecto."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

RAW_EXCEL_FILENAME = "datos_proyecto_final_servicios_tecnicos.xlsx"
# Preferido: data/ del proyecto. Respaldo: carpeta padre (…/Diplomado).
RAW_EXCEL_CANDIDATES = (
    DATA_DIR / RAW_EXCEL_FILENAME,
    PROJECT_ROOT.parent / RAW_EXCEL_FILENAME,
)
RAW_EXCEL_PATH = RAW_EXCEL_CANDIDATES[0]
CLEAN_CSV_PATH = DATA_DIR / "servicios_limpios.csv"
CLEANING_LOG_PATH = DATA_DIR / "cleaning_log.txt"


def resolve_raw_excel_path() -> Path:
    """Devuelve la primera ruta existente del Excel fuente.

    Orden:
    1. ``data/datos_proyecto_final_servicios_tecnicos.xlsx``
    2. ``../datos_proyecto_final_servicios_tecnicos.xlsx`` (carpeta Diplomado)
    """
    for path in RAW_EXCEL_CANDIDATES:
        if path.exists():
            return path
    searched = ", ".join(str(p) for p in RAW_EXCEL_CANDIDATES)
    raise FileNotFoundError(
        "No se encontró el Excel fuente. Colócalo en data/ o en la carpeta "
        f"padre del proyecto. Rutas buscadas: {searched}"
    )

SERVICIOS_SHEET = "servicios"

EXPECTED_COLUMNS = [
    "ID_servicio",
    "Fecha_solicitud",
    "Ciudad",
    "Tipo_servicio",
    "Canal",
    "Tecnico_id",
    "Antiguedad_tecnico_meses",
    "Tiempo_respuesta_horas",
    "Duracion_servicio_min",
    "Costo_repuestos",
    "Valor_servicio",
    "Reproceso",
    "Satisfaccion",
    "Estado",
]

CITY_MAP = {
    "barranquilla": "Barranquilla",
    "bquilla": "Barranquilla",
    "santa marta": "Santa Marta",
    "sta marta": "Santa Marta",
    "cartagena": "Cartagena",
    "valledupar": "Valledupar",
    "monteria": "Montería",
    "montería": "Montería",
    "sincelejo": "Sincelejo",
}

SERVICE_TYPE_MAP = {
    "instalacion": "Instalación",
    "instalación": "Instalación",
    "reparacion": "Reparación",
    "reparación": "Reparación",
    "mantenimiento": "Mantenimiento",
    "garantia": "Garantía",
    "garantía": "Garantía",
}

CHANNEL_MAP = {
    "app": "App",
    "call center": "Call center",
    "web": "Web",
    "presencial": "Presencial",
}

STATUS_MAP = {
    "completado": "Completado",
    "reprogramado": "Reprogramado",
    "cancelado": "Cancelado",
}
