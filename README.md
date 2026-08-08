# Análisis de servicios técnicos a domicilio

Proyecto del **Diplomado en Análisis de Datos** — Corporación Universitaria Reformada (UNIREFORMADA). Opción B (base del diplomado).

## 1. Problema

**Pregunta de investigación:** ¿Cómo afecta la demora en llegar a la satisfacción del cliente y cuál sería un tiempo de respuesta máximo comprometible?

Variables centrales:

- `Tiempo_respuesta_horas`
- `Satisfaccion`
- `Reproceso`

Ciclo aplicado: recolectar → limpiar → explorar → visualizar → decidir.

## 2. Dataset

Archivo en el repo (para que el profesor pueda clonar y probar):

`data/datos_proyecto_final_servicios_tecnicos.xlsx`

| Detalle | Valor |
|--------|--------|
| Archivo | `datos_proyecto_final_servicios_tecnicos.xlsx` |
| Hoja de análisis | `servicios` (también incluye `diccionario` y `contexto`) |
| Registros crudos | 15.587 órdenes |
| Periodo | julio 2024 – junio 2026 |
| Cobertura | 6 ciudades del Caribe colombiano, 105 técnicos |
| Columnas | 14 (nombres exactos del Excel; no se inventan campos) |

El pipeline busca el Excel en este orden:

1. `data/datos_proyecto_final_servicios_tecnicos.xlsx` (dentro del proyecto — ruta recomendada)
2. `../datos_proyecto_final_servicios_tecnicos.xlsx` (carpeta padre, opcional)

### Aviso importante (buena práctica de Git)

**Este tipo de archivos (Excel, CSV grandes, dumps, datos sensibles) no deberían subirse a un repositorio en un proyecto real.** Inflan el historial, dificultan el clonado y pueden exponer información. Lo habitual es:

- dejarlos fuera de Git (`.gitignore`);
- documentar cómo obtenerlos;
- o usar almacenamiento externo / LFS si hace falta compartirlos.

Aquí el Excel **sí está en el repo solo por motivo académico**: facilitar que el profesor clone el proyecto y ejecute `python -m src.pipeline` sin pasos extra. No tomarlo como práctica recomendada de producción o portafolio profesional.

## 3. Arquitectura

```text
data/datos_proyecto_final_servicios_tecnicos.xlsx
        │
        ▼
src/ingestion.py          # Carga hoja servicios
        │
        ▼
src/cleaning.py           # Botiquín Clase 3 + receta de fechas de la guía
        │
        ▼
src/validation.py         # Dominios, tipos, cero duplicados
        │
        ├─► data/servicios_limpios.csv
        ├─► data/cleaning_log.txt
        │
        ▼
src/analysis.py           # Stats, correlación, umbral comprometible
src/visualize.py          # Figuras con título = hallazgo
        │
        ├─► reports/figures/*.png
        ├─► data/analysis_summary.json
        │
        ▼
scripts/generate_pdf.py   # Trabajo final académico (PDF)
        │
        └─► reports/Trabajo_Final_Sergio_Martinez.pdf
```

Orquestación: `python -m src.pipeline`.

## 4. Instalación

Requisito: Python 3.10+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

En Git Bash / Linux / macOS:

```bash
python -m venv .venv
source .venv/Scripts/activate   # en Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Tras clonar, el Excel ya debe estar en `data/` (incluido en este repo académico). Ver sección Dataset.

## 5. Ejecución

Desde la raíz del repositorio (con el venv activo):

```bash
# Pipeline completo: limpiar, analizar y generar gráficos
python -m src.pipeline

# PDF del trabajo final
python scripts/generate_pdf.py

# Tests de limpieza
python -m pytest
```

Este proyecto **no levanta un servidor web** en su entrega académica. “Ejecutar” significa correr el pipeline de datos anterior.

## 6. Pipeline de datos

Reglas aplicadas en [`src/cleaning.py`](src/cleaning.py) (alineadas a la Clase 3 y a la guía):

1. Diagnóstico previo (`info`, nulos, duplicados, `value_counts`).
2. Categorías: `.str.strip()` + mapa canónico (ciudad, tipo, canal, estado).
3. `drop_duplicates()` — en este dataset se eliminan **295** filas idénticas.
4. Fechas mixtas: primero `%Y-%m-%d`, luego `%d/%m/%Y` (receta de la guía).
5. Texto en números → `pd.to_numeric(..., errors="coerce")` (`sin dato`, `pendiente`).
6. Imposibles → `NaN`: `Tiempo_respuesta_horas == 999`, `Satisfaccion` ∉ {1..5}, antigüedad &lt; 0, valor &lt; 0.
7. **No se imputan** `Tiempo_respuesta_horas` ni `Satisfaccion` (variables clave); se filtran en el análisis.

Tras limpieza: **15.292** filas. Subconjunto de análisis (demora + satisfacción válidas): **14.512** órdenes.

## 7. Análisis y resultados

| Indicador | Valor (datos reales) |
|-----------|----------------------|
| Correlación demora vs satisfacción | **r ≈ -0.54** |
| Tiempo máximo comprometible | **24 horas** (último bucket con CSAT medio ≥ 4.0) |
| CSAT si respuesta ≤ 24 h | **4.34** |
| CSAT si respuesta &gt; 24 h | **3.68** |
| Demora media / mediana | 21.3 h / 18.8 h |
| Peor ciudad | **Montería** (~39.6 h, CSAT ~3.52) |

Gráficos (título = hallazgo):

- [`reports/figures/01_satisfaccion_por_demora.png`](reports/figures/01_satisfaccion_por_demora.png) — ¿qué?
- [`reports/figures/02_demora_por_ciudad.png`](reports/figures/02_demora_por_ciudad.png) — ¿dónde?
- [`reports/figures/03_correlacion_demora_satisfaccion.png`](reports/figures/03_correlacion_demora_satisfaccion.png) — ¿por qué?
- [`reports/figures/04_heatmap_ciudad_demora.png`](reports/figures/04_heatmap_ciudad_demora.png) — cruce ciudad × ventana

**Entrega final académica:** [`reports/Trabajo_Final_Sergio_Martinez.pdf`](reports/Trabajo_Final_Sergio_Martinez.pdf)  
*(versión corregida v2: título “Cuando esperar cuesta…”, no-causalidad explícita, Figura 2 con CSAT legible por ciudad. Es la fuente de verdad del informe; no regenerar desde `scripts/generate_pdf.py` sin revisión.)*

## 8. Entregables generados

| Archivo | Descripción |
|---------|-------------|
| `data/servicios_limpios.csv` | Dataset limpio |
| `data/cleaning_log.txt` | Conteos antes/después de la limpieza |
| `data/analysis_summary.json` | Resumen numérico del análisis |
| `reports/figures/*.png` | Figuras del diagnóstico |
| `reports/Trabajo_Final_Sergio_Martinez.pdf` | **PDF final corregido** (entrega académica) |

## 9. Extensión futura (no requerida para la nota)

`requirements.txt` incluye SQLAlchemy, PostgreSQL (`psycopg`), FastAPI y uvicorn. Quedan como extensión profesional (API + base de datos + deploy). **No forman parte de la entrega académica actual.**

## 10. Seguridad

- Credenciales solo en `.env` (ignorado por Git).
- Plantilla: [`.env.example`](.env.example).
- No hardcodear `DATABASE_URL`, passwords ni API keys.
