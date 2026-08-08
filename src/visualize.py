"""Gráficos finales con títulos que expresan el hallazgo."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.analysis import AnalysisResults, analysis_subset, pivot_city_bucket
from src.config import FIGURES_DIR


def _setup_style() -> None:
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["figure.dpi"] = 120


def create_figures(df_clean: pd.DataFrame, results: AnalysisResults) -> list[Path]:
    """Genera 3 PNG en reports/figures/. Devuelve las rutas."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    _setup_style()
    paths: list[Path] = []

    df_an = analysis_subset(df_clean)
    x_hours = int(results.committed_hours)

    # 1 ¿QUIÉN/QUÉ? — demora vs satisfacción (barras por bucket)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    plot_df = results.sat_by_bucket.copy()
    sns.barplot(data=plot_df, x="bucket", y="media", color="#2F6F8F", ax=ax)
    ax.set_ylim(0, 5)
    ax.set_xlabel("Tiempo de respuesta")
    ax.set_ylabel("Satisfacción media (1-5)")
    ax.set_title(
        f"La satisfacción cae de {plot_df.iloc[0]['media']:.2f} a "
        f"{plot_df.iloc[-2]['media']:.2f} cuando la demora pasa de ≤12h a 48-72h"
    )
    ax.axhline(4.0, color="#C45C26", linestyle="--", linewidth=1.5, label="Umbral CSAT 4.0")
    ax.legend(loc="lower left")
    path1 = FIGURES_DIR / "01_satisfaccion_por_demora.png"
    fig.tight_layout()
    fig.savefig(path1, bbox_inches="tight")
    plt.close(fig)
    paths.append(path1)

    # 2 ¿DÓNDE? — ciudades con mayor demora y peor CSAT
    # CSAT legible en cada barra; sin leyenda de valores interminables.
    fig, ax = plt.subplots(figsize=(10, 5.5))
    city = results.sat_by_city.sort_values("tiempo_medio", ascending=True).reset_index(
        drop=True
    )
    worst = city.iloc[-1]
    colors = [
        "#C45C26" if row["Ciudad"] == worst["Ciudad"] else "#2F6F8F"
        for _, row in city.iterrows()
    ]
    ax.barh(city["Ciudad"], city["tiempo_medio"], color=colors)
    for _, row in city.iterrows():
        ax.text(
            row["tiempo_medio"] + 0.4,
            row["Ciudad"],
            f"CSAT {row['sat_media']:.2f}",
            va="center",
            fontsize=11,
        )
    ax.set_xlim(0, max(city["tiempo_medio"]) + 8)
    ax.set_xlabel("Tiempo de respuesta medio (horas)")
    ax.set_ylabel("")
    ax.set_title(
        f"{worst['Ciudad']} concentra la mayor demora "
        f"({worst['tiempo_medio']:.1f} h) y el menor CSAT ({worst['sat_media']:.2f})"
    )
    path2 = FIGURES_DIR / "02_demora_por_ciudad.png"
    fig.tight_layout()
    fig.savefig(path2, bbox_inches="tight")
    plt.close(fig)
    paths.append(path2)

    # 3 ¿POR QUÉ? — dispersión tiempo vs satisfacción + correlación
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sample = df_an.sample(n=min(2500, len(df_an)), random_state=42)
    sns.scatterplot(
        data=sample,
        x="Tiempo_respuesta_horas",
        y="Satisfaccion",
        alpha=0.35,
        color="#2F6F8F",
        ax=ax,
    )
    ax.axvline(
        x_hours,
        color="#C45C26",
        linestyle="--",
        linewidth=1.8,
        label=f"Compromiso propuesto: {x_hours} h",
    )
    ax.set_xlabel("Tiempo de respuesta (horas)")
    ax.set_ylabel("Satisfacción (1-5)")
    ax.set_title(
        f"A mayor demora, menor satisfacción (r = {results.correlation:.2f}); "
        f"por debajo de {x_hours} h el CSAT medio es {results.sat_below_threshold:.2f}"
    )
    ax.set_ylim(0.5, 5.5)
    ax.legend(loc="upper right")
    path3 = FIGURES_DIR / "03_correlacion_demora_satisfaccion.png"
    fig.tight_layout()
    fig.savefig(path3, bbox_inches="tight")
    plt.close(fig)
    paths.append(path3)

    # Heatmap auxiliar (opcional, útil para informe)
    pivot = pivot_city_bucket(df_clean)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="RdYlGn", vmin=2.5, vmax=5, ax=ax)
    ax.set_title(
        "En todas las ciudades el CSAT empeora al cruzar ventanas largas de respuesta"
    )
    ax.set_xlabel("Ventana de tiempo de respuesta")
    ax.set_ylabel("Ciudad")
    path4 = FIGURES_DIR / "04_heatmap_ciudad_demora.png"
    fig.tight_layout()
    fig.savefig(path4, bbox_inches="tight")
    plt.close(fig)
    paths.append(path4)

    return paths
