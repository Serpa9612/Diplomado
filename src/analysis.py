"""Análisis estadístico para la pregunta de demora vs satisfacción."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class AnalysisResults:
    n_clean: int
    n_analysis: int
    period_min: str
    period_max: str
    tiempo_mean: float
    tiempo_median: float
    tiempo_std: float
    tiempo_p25: float
    tiempo_p75: float
    tiempo_p90: float
    sat_mean: float
    sat_median: float
    correlation: float
    reproceso_rate: float
    sat_by_bucket: pd.DataFrame
    sat_by_city: pd.DataFrame
    committed_hours: float
    sat_below_threshold: float
    sat_above_threshold: float
    n_below_threshold: int
    n_above_threshold: int
    reproceso_below: float
    reproceso_above: float


def analysis_subset(df: pd.DataFrame) -> pd.DataFrame:
    """Filas con las variables clave válidas (dropna de la pregunta de negocio)."""
    cols = ["Tiempo_respuesta_horas", "Satisfaccion"]
    out = df.dropna(subset=cols).copy()
    out = out[out["Satisfaccion"].isin([1, 2, 3, 4, 5])]
    out = out[out["Tiempo_respuesta_horas"] > 0]
    return out


def _response_buckets(series: pd.Series) -> pd.Series:
    return pd.cut(
        series,
        bins=[0, 12, 24, 36, 48, 72, np.inf],
        labels=["≤12h", "12-24h", "24-36h", "36-48h", "48-72h", ">72h"],
        right=True,
    )


def find_commitment_threshold(df_an: pd.DataFrame) -> float:
    """
    Tiempo máximo comprometible = límite superior del último bucket cuya
    satisfacción media es >= 4.0 (cliente satisfecho o muy satisfecho).

    Se calcula desde los datos (no se inventa). Si ningún bucket alcanza 4.0,
    se usa el percentil 75 como referencia operativa (Clase 4).
    """
    tmp = df_an.copy()
    tmp["bucket"] = _response_buckets(tmp["Tiempo_respuesta_horas"])
    means = tmp.groupby("bucket", observed=True)["Satisfaccion"].mean()
    # Etiquetas ordenadas: ≤12h, 12-24h, 24-36h, ...
    upper_by_label = {
        "≤12h": 12.0,
        "12-24h": 24.0,
        "24-36h": 36.0,
        "36-48h": 48.0,
        "48-72h": 72.0,
    }
    best = None
    for label, upper in upper_by_label.items():
        if label in means.index and means.loc[label] >= 4.0:
            best = upper
        else:
            break
    if best is not None:
        return best
    return float(df_an["Tiempo_respuesta_horas"].quantile(0.75))


def run_analysis(df_clean: pd.DataFrame) -> AnalysisResults:
    """Calcula métricas, buckets, correlación y umbral comprometible."""
    df_an = analysis_subset(df_clean)
    df_an = df_an.copy()
    df_an["bucket"] = _response_buckets(df_an["Tiempo_respuesta_horas"])

    sat_by_bucket = (
        df_an.groupby("bucket", observed=True)["Satisfaccion"]
        .agg(media="mean", mediana="median", n="count")
        .reset_index()
    )

    sat_by_city = (
        df_an.groupby("Ciudad")
        .agg(
            tiempo_medio=("Tiempo_respuesta_horas", "mean"),
            sat_media=("Satisfaccion", "mean"),
            n=("Satisfaccion", "count"),
        )
        .reset_index()
        .sort_values("tiempo_medio", ascending=False)
    )

    threshold = find_commitment_threshold(df_an)
    below = df_an["Tiempo_respuesta_horas"] <= threshold
    above = df_an["Tiempo_respuesta_horas"] > threshold

    reproceso_rate = float(df_an["Reproceso"].mean()) if "Reproceso" in df_an else float("nan")

    return AnalysisResults(
        n_clean=len(df_clean),
        n_analysis=len(df_an),
        period_min=str(pd.to_datetime(df_clean["Fecha_solicitud"]).min().date()),
        period_max=str(pd.to_datetime(df_clean["Fecha_solicitud"]).max().date()),
        tiempo_mean=float(df_an["Tiempo_respuesta_horas"].mean()),
        tiempo_median=float(df_an["Tiempo_respuesta_horas"].median()),
        tiempo_std=float(df_an["Tiempo_respuesta_horas"].std()),
        tiempo_p25=float(df_an["Tiempo_respuesta_horas"].quantile(0.25)),
        tiempo_p75=float(df_an["Tiempo_respuesta_horas"].quantile(0.75)),
        tiempo_p90=float(df_an["Tiempo_respuesta_horas"].quantile(0.90)),
        sat_mean=float(df_an["Satisfaccion"].mean()),
        sat_median=float(df_an["Satisfaccion"].median()),
        correlation=float(df_an["Tiempo_respuesta_horas"].corr(df_an["Satisfaccion"])),
        reproceso_rate=reproceso_rate,
        sat_by_bucket=sat_by_bucket,
        sat_by_city=sat_by_city,
        committed_hours=threshold,
        sat_below_threshold=float(df_an.loc[below, "Satisfaccion"].mean()),
        sat_above_threshold=float(df_an.loc[above, "Satisfaccion"].mean()),
        n_below_threshold=int(below.sum()),
        n_above_threshold=int(above.sum()),
        reproceso_below=float(df_an.loc[below, "Reproceso"].mean()),
        reproceso_above=float(df_an.loc[above, "Reproceso"].mean()),
    )


def pivot_city_bucket(df_clean: pd.DataFrame) -> pd.DataFrame:
    """Pivot satisfacción media: ciudad × bucket de tiempo."""
    df_an = analysis_subset(df_clean)
    df_an = df_an.copy()
    df_an["bucket"] = _response_buckets(df_an["Tiempo_respuesta_horas"])
    return df_an.pivot_table(
        values="Satisfaccion",
        index="Ciudad",
        columns="bucket",
        aggfunc="mean",
    )
