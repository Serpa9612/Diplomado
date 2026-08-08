"""Genera un PDF auxiliar a partir del pipeline (ReportLab).

La entrega académica final es reports/Trabajo_Final_Sergio_Martinez.pdf
(versión corregida v2). Este script escribe un archivo distinto para no
sobrescribirla.
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "reports" / "figures"
# No sobrescribe la entrega final corregida en Trabajo_Final_Sergio_Martinez.pdf
OUT_PDF = ROOT / "reports" / "Trabajo_Final_Sergio_Martinez_auto.pdf"
SUMMARY = json.loads((ROOT / "data" / "analysis_summary.json").read_text(encoding="utf-8"))

MARGIN = 2.5 * cm


def _styles() -> dict:
    base = getSampleStyleSheet()
    styles = {
        "cover_title": ParagraphStyle(
            "cover_title",
            parent=base["Heading1"],
            fontName="Times-Bold",
            fontSize=16,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=24,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=12,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="Times-Bold",
            fontSize=14,
            leading=20,
            spaceBefore=14,
            spaceAfter=10,
            alignment=TA_LEFT,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Times-Bold",
            fontSize=12,
            leading=18,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=12,
            leading=18,  # interlineado 1.5 sobre 12 pt
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        "caption": ParagraphStyle(
            "caption",
            parent=base["Normal"],
            fontName="Times-Italic",
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            spaceBefore=4,
            spaceAfter=12,
        ),
        "ref": ParagraphStyle(
            "ref",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=11,
            leading=16,
            leftIndent=18,
            firstLineIndent=-18,
            spaceAfter=8,
            alignment=TA_LEFT,
        ),
    }
    return styles


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def _figure(path: Path, caption: str, styles: dict, width: float = 15.5 * cm) -> list:
    img = Image(str(path), width=width, height=width * 0.52)
    return [KeepTogether([img, _p(caption, styles["caption"])])]


def build_pdf() -> Path:
    styles = _styles()
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title="Demora en la respuesta y satisfacción del cliente en servicios técnicos",
        author="Sergio Martinez",
    )

    r = SUMMARY
    corr = r["correlation"]
    hours = int(r["committed_hours"])
    sat_below = r["sat_below"]
    sat_above = r["sat_above"]
    n_an = r["n_analysis"]
    pct_over = 100 * (r["n_above"] / n_an)

    story: list = []

    # ----- PORTADA -----
    story.append(Spacer(1, 2.2 * cm))
    story.append(
        _p(
            "Diagnóstico del impacto de la demora en la respuesta sobre la satisfacción "
            "del cliente y definición de un tiempo máximo comprometible en servicios "
            "técnicos a domicilio",
            styles["cover_title"],
        )
    )
    story.append(Spacer(1, 1.2 * cm))
    story.append(_p("Sergio Martinez", styles["cover_meta"]))
    story.append(_p("C.C. 1023956351", styles["cover_meta"]))
    story.append(_p("Diplomado en Análisis de Datos — opción de grado", styles["cover_meta"]))
    story.append(_p("Ingeniería Informática", styles["cover_meta"]))
    story.append(
        _p("Corporación Universitaria Reformada (UNIREFORMADA)", styles["cover_meta"])
    )
    story.append(_p("Bogotá, 07 de agosto de 2026", styles["cover_meta"]))
    story.append(PageBreak())

    # ----- 2. INTRODUCCIÓN -----
    story.append(_p("1. Introducción", styles["h1"]))
    story.append(
        _p(
            "El Diplomado en Análisis de Datos de la Corporación Universitaria Reformada "
            "articula un ciclo profesional de cinco etapas —recolectar, limpiar, explorar, "
            "visualizar y decidir— que convierte registros operativos en evidencia útil para "
            "la gestión (McKinney, 2022). En un entorno de servicios técnicos a domicilio, "
            "esa evidencia es crítica: la demora en llegar al cliente no solo afecta la "
            "experiencia percibida, también condiciona reprocesos, costos y reputación.",
            styles["body"],
        )
    )
    story.append(
        _p(
            "El análisis se realiza sobre la base de datos de servicios técnicos "
            "suministrada en el diplomado (Opción B), correspondiente a 15.587 órdenes "
            "de servicio registradas entre julio de 2024 y junio de 2026, con cobertura "
            "en seis ciudades de la región Caribe colombiana y 105 técnicos. La pregunta "
            "de investigación, tomada del menú académico de la guía, es: "
            "<b>¿cómo afecta la demora en llegar a la satisfacción del cliente y cuál "
            "sería un tiempo de respuesta máximo comprometible?</b> Las variables "
            "centrales son <i>Tiempo_respuesta_horas</i>, <i>Satisfaccion</i> y "
            "<i>Reproceso</i>.",
            styles["body"],
        )
    )
    story.append(
        _p(
            "El objetivo del documento es diagnosticar con datos limpios la relación "
            "entre demora y satisfacción, proponer un umbral operativo calculado desde "
            "la evidencia y formular un plan de acción con responsables, plazos e "
            "impacto estimado. El procesamiento se realizó con Python y la librería "
            "pandas (The pandas development team, 2026), y las visualizaciones con "
            "matplotlib y seaborn (Hunter, 2007; Waskom, 2021).",
            styles["body"],
        )
    )

    # ----- 3. ANÁLISIS TEMÁTICO -----
    story.append(_p("2. Análisis temático y reflexivo", styles["h1"]))

    story.append(_p("2.1. Fundamentación teórica", styles["h2"]))
    story.append(
        _p(
            "Un <b>dato</b> es un valor aislado (por ejemplo, 45.1 horas); se vuelve "
            "<b>información</b> cuando se contextualiza (tiempo de respuesta de una orden "
            "en Montería); y se convierte en <b>conocimiento</b> cuando orienta una "
            "decisión (definir un compromiso máximo de atención). Las variables del "
            "caso son cualitativas nominales (ciudad, canal, tipo de servicio), "
            "ordinales (satisfacción 1–5) y cuantitativas (tiempos, costos).",
            styles["body"],
        )
    )
    story.append(
        _p(
            "El ciclo de vida del análisis exige limpiar antes de explorar: nulos, "
            "duplicados, texto en columnas numéricas, valores imposibles, categorías "
            "inconsistentes, fechas mezcladas y espacios invisibles distorsionan "
            "cualquier promedio. En estadística descriptiva, la media puede mentir "
            "cuando existen extremos —como el valor sentinela 999 en tiempos de "
            "respuesta—, mientras la mediana describe mejor el caso típico. Los "
            "percentiles permiten fijar umbrales operativos, y la correlación mide "
            "si dos variables se mueven juntas, sin demostrar por sí sola causalidad "
            "(McKinney, 2022).",
            styles["body"],
        )
    )

    story.append(_p("2.2. Análisis crítico", styles["h2"]))
    story.append(
        _p(
            "Cuando una organización de servicios decide por intuición —por ejemplo, "
            "asumir que “el cliente se queja por el precio” sin mirar demoras—, interviene "
            "el síntoma equivocado y gasta recursos sin mejorar el indicador que "
            "realmente se deteriora. En este dataset, si no se hubieran tratado los "
            "valores 999, la relación entre demora y satisfacción habría quedado "
            "enmascarada: el mismo tipo de error que en clase hizo acusar al turno "
            "equivocado de producción.",
            styles["body"],
        )
    )
    story.append(
        _p(
            "Analizar información sin limpiarla es un riesgo profesional concreto: "
            "duplicados inflan volúmenes, tipografías de ciudad crean “ciudades fantasma” "
            "y un texto como «sin dato» convierte una columna numérica en texto, "
            "impidiendo correlaciones. En un sector de atención a domicilio, ese error "
            "se traduce en SLA mal calibrados, incentivos torcidos para técnicos y "
            "pérdida de confianza del cliente. La calidad del dato no es un trámite "
            "previo: es condición de validez de la decisión.",
            styles["body"],
        )
    )

    story.append(_p("2.3. Contrastación profesional", styles["h2"]))
    story.append(
        _p(
            "Excel sigue siendo útil para exploración puntual, pero frente a 15.587 "
            "registros con reglas repetibles de limpieza, el código en Python gana en "
            "volumen, auditoría y reproducción: cada transformación queda escrita y "
            "puede reejecutarse cuando lleguen nuevos meses de operación (McKinney, "
            "2022). Esa trazabilidad es exactamente lo que piden perfiles como analista "
            "de datos, analista de operaciones, business intelligence o quality "
            "analyst en empresas de field service y utilities.",
            styles["body"],
        )
    )
    story.append(
        _p(
            "En la práctica profesional del sector de servicios técnicos, combinar "
            "pandas para el diagnóstico con una capa posterior de almacenamiento y "
            "API —aunque este trabajo prioriza el análisis académico— permite que el "
            "mismo hallazgo alimente tableros y alertas. Lo esencial, sin embargo, "
            "no es la herramienta: es demostrar el problema con números y proponer "
            "una acción medible.",
            styles["body"],
        )
    )

    # ----- 4. DIAGNÓSTICO -----
    story.append(_p("3. Diagnóstico y aplicabilidad práctica", styles["h1"]))

    story.append(_p("3.1. Identificación del problema", styles["h2"]))
    story.append(
        _p(
            "En la operación simulada de servicios técnicos a domicilio (instalación, "
            "reparación, mantenimiento y garantías) se observa variabilidad fuerte en "
            "el tiempo entre la solicitud y la atención en sitio. La pregunta de "
            "negocio es concreta: <b>¿cómo afecta esa demora a la satisfacción del "
            "cliente y qué tiempo máximo de respuesta puede comprometer la empresa "
            "sin degradar el CSAT?</b> El ámbito es la base Opción B del diplomado "
            "(julio 2024 – junio 2026), con énfasis en "
            "<i>Tiempo_respuesta_horas</i>, <i>Satisfaccion</i> y <i>Reproceso</i>.",
            styles["body"],
        )
    )

    story.append(_p("3.2. Análisis del problema", styles["h2"]))
    story.append(
        _p(
            f"Se partió de <b>{r['rows_raw']:,}</b> registros crudos. Tras el diagnóstico "
            f"(info, nulos, duplicados y value_counts) se aplicó el botiquín de limpieza "
            f"de la clase 3: se eliminaron <b>{r['duplicates_removed']}</b> filas "
            f"duplicadas exactas; se unificaron fechas ISO y DD/MM/YYYY; se "
            f"normalizaron categorías de ciudad, tipo, canal y estado (strip + mapa "
            f"canónico); el texto «sin dato» y «pendiente» se convirtió a nulo con "
            f"<i>to_numeric(errors='coerce')</i>; y los valores imposibles se pasaron "
            f"a vacío —en particular <b>53</b> tiempos iguales a 999, <b>42</b> "
            f"satisfacciones fuera de 1–5, antigüedades negativas y valores de "
            f"servicio negativos. No se imputaron la demora ni la satisfacción porque "
            f"son variables clave del análisis: inventarlas sesgaría el hallazgo. El "
            f"dataset limpio quedó en <b>{r['rows_clean']:,}</b> filas; para la pregunta "
            f"de investigación se trabajó con <b>{n_an:,}</b> órdenes que tenían demora "
            f"y satisfacción válidas (periodo {r['period'][0]} a {r['period'][1]}).",
            styles["body"],
        )
    )
    story.append(
        _p(
            f"La demora media fue de <b>{r['tiempo_mean']:.1f} horas</b> y la mediana "
            f"de <b>{r['tiempo_median']:.1f} horas</b> (percentil 90 = "
            f"{r['tiempo_p90']:.1f} h). Por ventanas de tiempo se observa una caída "
            f"clara del CSAT. La correlación entre "
            f"<i>Tiempo_respuesta_horas</i> y <i>Satisfaccion</i> fue de "
            f"<b>r = {corr:.2f}</b>: relación negativa moderada-fuerte. Esta "
            f"correlación es una pista de causa probable, no una prueba de causalidad.",
            styles["body"],
        )
    )
    story.append(
        _p(
            "La Figura 1 muestra el hallazgo central: la satisfacción media pasa de "
            "4.53 en atenciones ≤12 h a 3.00 en la ventana 48–72 h, y el primer "
            "intervalo que cae por debajo del umbral CSAT 4.0 es 24–36 h. Por eso, "
            "el <b>tiempo máximo comprometible calculado desde los datos es 24 horas</b>: "
            f"límite superior del último bucket con satisfacción media ≥ 4.0. Por "
            f"debajo de ese compromiso el CSAT medio es <b>{sat_below:.2f}</b>; por "
            f"encima, <b>{sat_above:.2f}</b>. Aproximadamente el "
            f"<b>{pct_over:.1f}%</b> de las órdenes analizadas supera hoy las 24 h.",
            styles["body"],
        )
    )
    story.extend(
        _figure(
            FIGURES / "01_satisfaccion_por_demora.png",
            "Figura 1. ¿Qué ocurre con la satisfacción cuando aumenta la demora?",
            styles,
        )
    )
    story.append(
        _p(
            "La Figura 2 localiza el problema geográficamente: Montería concentra la "
            "mayor demora media (39.6 h) con CSAT 3.52, mientras el resto de ciudades "
            "se sitúa cerca de 19 h con CSAT en torno a 4.2. La Figura 3 refuerza el "
            f"vínculo numérico (r = {corr:.2f}) y marca el compromiso de {hours} h. "
            "El reproceso global del subconjunto analizado se mantiene cercano al 8% "
            "a ambos lados del umbral, lo que sugiere que la demora impacta primero "
            "la percepción (CSAT) y no necesariamente la tasa de reingreso en la "
            "misma magnitud.",
            styles["body"],
        )
    )
    story.extend(
        _figure(
            FIGURES / "02_demora_por_ciudad.png",
            "Figura 2. ¿Dónde se concentra la demora que más castiga el CSAT?",
            styles,
        )
    )
    story.extend(
        _figure(
            FIGURES / "03_correlacion_demora_satisfaccion.png",
            "Figura 3. ¿Por qué proponer 24 h? Relación demora–satisfacción y umbral.",
            styles,
        )
    )

    story.append(_p("3.3. Propuesta de solución", styles["h2"]))
    story.append(
        _p(
            "Con base en el umbral de 24 h y en el rezago de Montería, se propone el "
            "siguiente plan de acción:",
            styles["body"],
        )
    )
    story.append(
        ListFlowable(
            [
                ListItem(
                    _p(
                        "<b>Acción 1 — SLA de respuesta ≤ 24 horas.</b> Publicar y "
                        "monitorear un compromiso máximo de 24 h entre solicitud y "
                        "atención en sitio. <b>Responsable:</b> Jefatura de Operaciones. "
                        "<b>Plazo:</b> 30 días. <b>Impacto esperado:</b> alinear el "
                        f"{pct_over:.1f}% de órdenes que hoy superan 24 h hacia el "
                        f"CSAT medio de {sat_below:.2f} observado bajo el umbral.",
                        styles["body"],
                    )
                ),
                ListItem(
                    _p(
                        "<b>Acción 2 — Plan de capacidad en Montería.</b> Revisar "
                        "agenda, densidad de técnicos y ruteo en Montería hasta "
                        "acercar su demora media (~39.6 h) al rango de ~19 h del "
                        "resto de ciudades. <b>Responsable:</b> Coordinación regional "
                        "Caribe. <b>Plazo:</b> 45 días. <b>Impacto esperado:</b> "
                        "elevar el CSAT local desde 3.52 hacia valores cercanos a 4.2, "
                        "reduciendo la brecha que hoy explica gran parte del "
                        "deterioro territorial.",
                        styles["body"],
                    )
                ),
                ListItem(
                    _p(
                        "<b>Acción 3 — Tablero semanal demora × CSAT.</b> Publicar "
                        "un tablero con satisfacción media por ventana de tiempo y "
                        "alerta cuando el percentil 90 de demora supere 38.2 h "
                        "(valor observado en los datos). <b>Responsable:</b> Analista "
                        "de Calidad / Datos. <b>Plazo:</b> arranque en 15 días; "
                        "operación permanente. <b>Impacto esperado:</b> detectar "
                        "desviaciones antes de que el CSAT mensual caiga bajo 4.0.",
                        styles["body"],
                    )
                ),
            ],
            bulletType="1",
            start=1,
        )
    )

    # ----- 5. CONCLUSIONES -----
    story.append(_p("4. Conclusiones", styles["h1"]))
    story.append(
        _p(
            "El trabajo permitió pasar de una sospecha operativa (“la demora molesta”) "
            "a una evidencia cuantificada: tras limpiar 15.587 órdenes y analizar "
            f"{n_an:,} casos válidos, la satisfacción cae de forma consistente a "
            f"medida que aumenta el tiempo de respuesta (r = {corr:.2f}), y los "
            f"datos sostienen un compromiso máximo de <b>{hours} horas</b>. "
            "Montería aparece como el foco territorial prioritario.",
            styles["body"],
        )
    )
    story.append(
        _p(
            "Como profesional de Ingeniería Informática, el mayor aprendizaje no fue "
            "solo usar pandas o graficar con seaborn, sino disciplinar el ciclo "
            "recolectar–limpiar–explorar–visualizar–decidir: documentar cada "
            "transformación, desconfiar del promedio cuando hay sentinelas, y "
            "traducir un hallazgo en acciones con responsable, plazo e impacto. "
            "Esa competencia es transferible a cualquier sistema de servicio donde "
            "la experiencia del cliente dependa del tiempo de atención.",
            styles["body"],
        )
    )

    story.append(PageBreak())

    # ----- 6. REFERENCIAS -----
    story.append(_p("Referencias", styles["h1"]))
    refs = [
        "Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. "
        "<i>Computing in Science &amp; Engineering, 9</i>(3), 90–95. "
        "https://doi.org/10.1109/MCSE.2007.55",
        "McKinney, W. (2022). <i>Python for data analysis</i> (3.ª ed.). O’Reilly Media.",
        "The pandas development team. (2026). <i>pandas documentation</i>. "
        "https://pandas.pydata.org/docs/",
        "Waskom, M. L. (2021). Seaborn: Statistical data visualization. "
        "<i>Journal of Open Source Software, 6</i>(60), 3021. "
        "https://doi.org/10.21105/joss.03021",
    ]
    for ref in refs:
        story.append(_p(ref, styles["ref"]))

    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story)
    return OUT_PDF


if __name__ == "__main__":
    path = build_pdf()
    print(f"PDF generado: {path}")
