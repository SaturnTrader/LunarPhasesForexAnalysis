# LunarPhasesForexAnalysis

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-311/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Análisis de la influencia astronómica (fases lunares) en los retornos y la volatilidad del mercado Forex. Este proyecto procesa millones de filas de datos de alta frecuencia M1 (1 minuto) correspondientes a **10 pares de divisas** (AUDUSD, EURCHF, EURGBP, EURJPY, GBPUSD, USDCAD, USDCHF, USDHKD, USDJPY, USDMXN). 

El análisis se segmentó rigurosamente en períodos pre-pandemia (2018-2020), pandemia (2020-2021) y pos-pandemia (2022-2024), utilizando la librería [Swiss Ephemeris](https://www.astro.com/swisseph/) para la precisión astrométrica.

Implementa un **Pipeline Orquestado** que automatiza el cruce de datos financieros contra las efemérides astronómicas, calcula la rentabilidad logarítmica y la volatilidad, aplica limpieza de datos (clipping de outliers) y ejecuta pruebas estadísticas de significancia con **ANOVA de Welch** y **Kruskal-Wallis**.

## Tabla de Contenidos
- [Descripción](#descripción)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso: Master Pipeline](#uso-master-pipeline)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Documentación Final](#documentación-final)
- [Licencia](#licencia)

## Descripción
Inspirado en estudios sobre comportamiento gregario y factores emocionales en las finanzas, este proyecto busca validar estadísticamente si las diferentes fases de la luna alteran la oferta y la demanda de instrumentos. 

Con los 10 pares evaluados calculamos `Retorno Medio` y `Volatilidad` diarios. Tras contrastarlo con casi 25 millones de minutos de transacciones, los resultados prueban robustamente que la fase lunar tiene una significancia nula casi universal, a excepción de una llamativa anomalía estadística pospandémica en el **EURCHF**, fuertemente influenciada por intervenciones exógenas del Banco Nacional Suizo. 

Todo el proceso de validación es 100% reproducible.

## Requisitos
- **Sistema Operativo**: Windows (Recomendado debido al uso de DLLs), macOS o Linux.
- **Python**: Versión 3.11 o superior.
- **Datos (HistData)**: Descargar los CSVs crudos desde HistData para los 10 pares en formato genérico ASCII-CSV-M1 correspondientes a 2018-2024 y colocarlos dentro de `data/financial_data/raw/<PAR>/`.

## Instalación
1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/tu_usuario/LunarPhasesForexAnalysis.git
   cd LunarPhasesForexAnalysis
   ```

2. **Crea y activa un entorno virtual**:
   ```bash
   python -m venv lunar_phases
   .\lunar_phases\Scripts\activate   # En Windows
   ```

3. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Variables de Entorno**:
   Copia `.env.example` a `.env` (si existe) y asegúrate de que define los años de análisis y las rutas para las efemérides. Las variables clave ya deben venir configuradas por defecto:
   - `START_DATE="2018-01-01"`
   - `DLL_PATH="data/lunar_data/swisseph_dll/"`

## Uso: Master Pipeline
La modernización del código incluye un script centralizado tipo orquestador (`master_pipeline.py`) que ejecuta paso a paso (y pausas de seguridad) la carga, consolidación, cruce y testeo de todas las monedas, evitando cuellos de botella de VRAM o errores prematuros:

```bash
python src/master_pipeline.py
```
> **Nota:** La primera vez que el script combina los históricos crudos y extrae las lunas puede tomar varias horas dependiendo del hardware.

### Flujo Interno (Sub-scripts ejecutados automáticamente)
1. `src/merge_histdata_csvs.py`: Unifica los datos crudos en la carpeta `interim`.
2. `src/generate_lunar_phases_only.py`: Interroga la DLL de efemérides.
3. `src/process_all_currencies.py`: Une astronomía con los precios M1.
4. `src/analyze_lunar_phases.py`: Despliega las herramientas estadísticas (SciPy/Pandas).
5. `src/summarize_across_pairs.py`: Redacta reportes Markdown finales.

## Estructura del Proyecto
```text
LunarPhasesForexAnalysis/
├── .env                          # Configuración
├── README.md
├── src/                          # Código Fuente y Arquitectura
│   ├── master_pipeline.py        # 🚀 Entry point principal
│   ├── analyze_lunar_phases.py
│   ├── process_all_currencies.py
│   └── ...
├── data/
│   ├── lunar_data/swisseph_dll/  # 🌠 DLLs astronómicas de SWISS EPHEMERIS
│   ├── financial_data/raw/       # Data de terceros ignorada por el .gitignore
│   ├── interim/                  # CSVs consolidados intermedios
│   └── processed/                # 📊 Tablas, Gráficos y Reportes Generados
```

## Documentación Final
Al ejecutar la investigación, los resultados estadísticos reales se autodespliegan en un análisis Markdown compilado:

- **`data/processed/Fases_Lunares_v3_Corregido.md`** -> Contiene el texto de la Tesis con el marco teórico y la narrativa en base a los datos.
- **`data/processed/Anexos.md`** -> Anexos con valores p (P-Values), recuentos de volatilidad y datos puros para revisión de pares.

## Licencia
Licencia MIT (MIT). Consulta el archivo LICENSE para mayor información (si aplica). (El contenido astrométrico de the Swiss Ephemeris está sujeto a su propia licencia de Astrodienst).