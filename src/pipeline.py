"""Orquestación: recolectar → limpiar → validar → analizar → visualizar."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from src.analysis import AnalysisResults, run_analysis
from src.cleaning import CleaningReport, clean_servicios
from src.config import CLEAN_CSV_PATH, CLEANING_LOG_PATH, DATA_DIR, FIGURES_DIR
from src.ingestion import load_servicios
from src.validation import validate_clean_servicios
from src.visualize import create_figures

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline() -> tuple[CleaningReport, AnalysisResults, list[Path]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    raw = load_servicios()
    clean, report = clean_servicios(raw)
    errors = validate_clean_servicios(clean)
    if errors:
        raise ValueError("Validación falló:\n" + "\n".join(errors))

    clean.to_csv(CLEAN_CSV_PATH, index=False, encoding="utf-8")
    CLEANING_LOG_PATH.write_text(report.as_text(), encoding="utf-8")

    results = run_analysis(clean)
    figures = create_figures(clean, results)

    summary = {
        "rows_raw": report.rows_before,
        "rows_clean": report.rows_after,
        "duplicates_removed": report.duplicates_removed,
        "n_analysis": results.n_analysis,
        "correlation": results.correlation,
        "committed_hours": results.committed_hours,
        "sat_mean": results.sat_mean,
        "sat_below": results.sat_below_threshold,
        "sat_above": results.sat_above_threshold,
        "n_below": results.n_below_threshold,
        "n_above": results.n_above_threshold,
        "tiempo_mean": results.tiempo_mean,
        "tiempo_median": results.tiempo_median,
        "tiempo_p90": results.tiempo_p90,
        "period": [results.period_min, results.period_max],
        "figures": [str(p) for p in figures],
    }
    (DATA_DIR / "analysis_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("Resumen: %s", summary)
    return report, results, figures


if __name__ == "__main__":
    run_pipeline()
