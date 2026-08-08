# Dataset de Servicios Técnicos a Domicilio — Proyecto de Diplomado

Este repositorio contiene la base de datos, diccionarios, scripts de procesamiento y análisis exploratorio del proyecto de diplomado enfocado en el procesamiento, limpieza y análisis de datos para una empresa de servicios técnicos a domicilio en la región Caribe colombiana.

---

## 1. Descripción General del Proyecto

El conjunto de datos (`datos_proyecto_final_servicios_tecnicos.xlsx`) simula la operación real de una compañía de soporte técnico a domicilio durante un período de 24 meses. El objetivo del proyecto es realizar el ciclo completo de datos: ingestión, limpieza/estandarización (ETL), análisis exploratorio (EDA), evaluación de KPIs operativos y generación de modelos o recomendaciones de negocio.

* **Empresa:** Empresa de servicios técnicos a domicilio (Caso práctico ficticio basado en patrones reales del sector).
* **Actividad:** Instalación, reparación, mantenimiento de equipos y atención de garantías.
* **Cobertura geográfica:** 6 ciudades de la región Caribe colombiana.
* **Periodo de análisis:** Julio de 2024 a junio de 2026 (24 meses).
* **Volumen:** 15,587 órdenes de servicio registradas.
* **Fuerza técnica:** 105 técnicos registrados con ingresos y rotación a lo largo del periodo.

---

## 2. Estructura del Archivo de Datos (`.xlsx`)

El libro de Excel contiene **3 pestañas**:

| Pestaña | Descripción | Registros / Filas |
| :--- | :--- | :--- |
| **`servicios`** | Tabla principal con el histórico de órdenes de servicio registradas por el sistema. | 15,587 registros |
| **`diccionario`** | Descripción técnica de las 14 variables/columnas presentes en la tabla de servicios. | 14 variables |
| **`contexto`** | Ficha técnica con el contexto del negocio, reglas y consideraciones de calidad de datos. | 8 campos clave |

---

## 3. Diccionario de Datos

| Columna | Tipo de Dato Esperado | Descripción / Significado | Ejemplo |
| :--- | :--- | :--- | :--- |
| **`ID_servicio`** | Texto | Identificador único de la orden de servicio | `S100000` |
| **`Fecha_solicitud`** | Fecha | Día en que el cliente solicitó el servicio | `2025-04-18` |
| **`Ciudad`** | Categoría | Ciudad donde se prestó el servicio (6 ciudades de la región Caribe) | `Barranquilla` |
| **`Tipo_servicio`** | Categoría | Tipo de atención: *Instalación*, *Reparación*, *Mantenimiento* o *Garantía* | `Reparación` |
| **`Canal`** | Categoría | Medio de entrada de la solicitud: *App*, *Call center*, *Web* o *Presencial* | `App` |
| **`Tecnico_id`** | Texto | Código del técnico asignado (105 técnicos en total) | `T017` |
| **`Antiguedad_tecnico_meses`** | Entero | Meses de antigüedad del técnico en la empresa al momento del servicio | `14` |
| **`Tiempo_respuesta_horas`** | Decimal | Horas transcurridas entre la solicitud y la atención en sitio | `19.5` |
| **`Duracion_servicio_min`** | Entero | Duración total de la atención presencial (en minutos) | `95` |
| **`Costo_repuestos`** | Decimal | Costo de repuestos utilizados (en COP `$`) | `74300` |
| **`Valor_servicio`** | Decimal | Valor cobrado al cliente (en COP `$`). Las garantías cobran `$0` | `180000` |
| **`Reproceso`** | Entero (0 o 1) | `1` si requirió reingreso/visita de corrección por falla previa; `0` de lo contrario | `0` |
| **`Satisfaccion`** | Entero (1 a 5) | Calificación del cliente al cierre (1 = muy insatisfecho, 5 = muy satisfecho) | `4` |
| **`Estado`** | Categoría | Estado del servicio: *Completado*, *Reprogramado* o *Cancelado* | `Completado` |

---

## 4. Retos y Desafíos de Calidad de Datos (Data Quality)

El dataset se entrega tal como proviene del sistema operacional (*raw data*) para simular los problemas habituales en entornos de producción:

* **Formatos de fecha inconsistentes:** Mezcla de estándares ISO (`YYYY-MM-DD`) y formato tradicional (`DD/MM/YYYY`).
* **Errores de digitación y tipográficos:** Inconsistencias en nombres de ciudades, tipos de servicio y canales.
* **Valores nulos / celdas vacías:** Omisiones en tiempos de respuesta, duración, nivel de satisfacción y costo de repuestos.
* **Registros duplicados:** Duplicación explícita de órdenes de servicio (`ID_servicio`).
* **Incongruencias y valores imposibles:** Registros con valores atípicos o no válidos que deben ser filtrados en la fase de limpieza.

---

## 5. Indicadores Clave de Negocio (KPIs a Evaluar)

1. **Eficiencia Operativa:** Tiempo promedio de respuesta (horas) y duración de servicio (minutos) por ciudad y tipo de servicio.
2. **Calidad de Servicio:** Tasa de reprocesos (`% Reproceso = 1`) e Índice de Satisfacción del Cliente (CSAT Promedio 1-5).
3. **Desempeño Técnico:** Rendimiento de técnicos según antigüedad, volumen de atenciones finalizadas y tasa de satisfacción.
4. **Análisis Financiero:** Ingresos por `Valor_servicio`, margen bruto descontando `Costo_repuestos` e impacto económico de las garantías.
5. **Comportamiento por Canal y Ciudad:** Distribución del volumen de solicitudes y efectividad según el canal de contacto (*App*, *Call center*, *Web*, *Presencial*).

---

## 6. Estructura del Repositorio

```text
analisis-servicios-tecnicos/
│
├── data/
│   └── datos_proyecto_final_servicios_tecnicos.xlsx   # Dataset fuente
│
├── notebooks/
│   └── 01_exploracion.ipynb                            # Análisis exploratorio (EDA)
│
├── src/
│   ├── __init__.py
│   ├── config.py                                       # Rutas y parámetros globales
│   ├── database.py                                     # Conexión a base de datos
│   ├── ingestion.py                                    # Carga e ingesta del archivo Excel
│   ├── cleaning.py                                     # Limpieza y estandarización de datos
│   └── analysis.py                                     # Cálculo de métricas e indicadores
│
├── api/
│   ├── __init__.py
│   └── main.py                                         # API REST (FastAPI)
│
├── tests/
│   └── test_cleaning.py                                # Pruebas unitarias para scripts de limpieza
│
├── sql/
│   └── schema.sql                                      # Modelo relacional / Tablas SQL
│
├── reports/
│   └── figures/                                        # Gráficas e imágenes generadas
│
├── .env.example                                        # Variables de entorno
├── .gitignore                                          # Archivos ignorados por Git
├── requirements.txt                                    # Dependencias del proyecto Python
├── README.md                                           # Documentación principal
└── Dockerfile                                          # Configuración de contenedor Docker
```
---

## 7. Instrucciones de Ejecución
Requisitos Previos
Python 3.10+

## Entorno virtual de Python (venv o conda)

### 1.Clonar el repositorio y acceder a la carpeta del proyecto:
´´´git clone <URL_DEL_REPOSITORIO>
cd analisis-servicios-tecnicos´´´

### 2.Crear y activar un entorno virtual:
´´´# En Linux / macOS / Git Bash
python -m venv venv
source venv/bin/activate

# En Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1´´´

### 3.Instalar las dependencias:
´´´pip install -r requirements.txt´´´

### 4.Ejecutar el pipeline de limpieza y procesamiento:
´´´python -m src.cleaning´´´