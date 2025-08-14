# LunarPhasesForexAnalysis

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-311/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Análisis de la influencia de las fases lunares en los retornos y la volatilidad del par EUR/USD en el mercado Forex, segmentado en períodos pre-pandemia, pandemia y pos-pandemia. Este proyecto utiliza datos M1 (1 minuto) y la librería Swiss Ephemeris para calcular fases lunares, generando estadísticas descriptivas, pruebas estadísticas y visualizaciones. Los resultados están disponibles en CSVs y gráficos PNG, ideales para traders e investigadores financieros interesados en explorar factores emocionales en el trading.

## Tabla de Contenidos
- [Descripción](#descripción)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Archivos Generados](#archivos-generados)
- [Contribuir](#contribuir)
- [Licencia](#licencia)
- [Agradecimientos](#agradecimientos)

## Descripción
¿Pueden las fases lunares influir en las decisiones de los traders y, por ende, en los mercados financieros? Inspirado en estudios como Bikhchandani y Sharma (2000) sobre comportamiento gregario y en referencias a métodos no convencionales en *L'argent ne dort jamais* (1999), este proyecto analiza si las fases lunares afectan los retornos y la volatilidad del par EUR/USD. Usamos datos M1 de 2018 a 2024, segmentados en:
- **Pre-pandemia**: Antes de marzo de 2020.
- **Pandemia**: Marzo de 2020 a diciembre de 2021.
- **Pos-pandemia**: Enero de 2022 a 2024.

Calculamos retornos logarítmicos y volatilidad diaria, realizamos pruebas estadísticas (ANOVA de Welch, Kruskal-Wallis) y generamos boxplots y gráficos de tendencia. Los resultados sugieren que las fases lunares tienen un impacto insignificante, pero los patrones descriptivos son un punto de partida para explorar factores emocionales en el trading. El código es reproducible y está diseñado para la comunidad financiera.

## Requisitos
- **Sistema Operativo**: Windows, macOS o Linux.
- **Python**: Versión 3.11.
- **Dependencias** (ver `requirements.txt`):
  - `pandas==2.2.2`
  - `numpy==1.26.4`
  - `pyswisseph==2.10.3.2`
  - `python-dotenv==1.0.1`
  - `pytz==2024.1`
  - `seaborn==0.13.2`
  - `matplotlib==3.9.2`
  - `scipy==1.13.1`
- **Datos**: Archivos CSV de precios M1 (frecuencia un minuto) de EUR/USD.
- **Swiss Ephemeris**:
  - Para **Windows**: Los archivos `libswe.dll`, `semo_18.se1` y `sepl_18.se1` están incluidos en `data/lunar_data/swisseph_dll/`.
  - Para **Linux/macOS**: Descarga los archivos de efemérides (`semo_18.se1`, `sepl_18.se1`) desde [astro.com](https://www.astro.com/swisseph/) y colócalos en `data/lunar_data/swisseph_dll/`. Asegúrate de que la librería `libswe.so` (Linux) o `libswe.dylib` (macOS) esté disponible.

## Instalación
1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/SaturnTrader/LunarPhasesForexAnalysis.git
   cd LunarPhasesForexAnalysis
   ```

2. **Crea un entorno virtual**:
   ```bash
   python -m venv venv311
   source venv311/bin/activate  # Linux/macOS
   .\venv311\Scripts\activate   # Windows
   ```

3. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las efemérides de Swiss Ephemeris**:
   - Para **Windows**: Los archivos necesarios (`libswe.dll`, `semo_18.se1`, `sepl_18.se1`) ya están en `data/lunar_data/swisseph_dll/`.
   - Para **Linux/macOS**: Descarga `semo_18.se1` y `sepl_18.se1` desde [astro.com](https://www.astro.com/swisseph/) y colócalos en `data/lunar_data/swisseph_dll/`. Asegúrate de que `libswe.so` (Linux) o `libswe.dylib` (macOS) esté instalado o disponible en el sistema.
   - Verifica que `EPHE_PATH` y `DLL_PATH` en `.env` apunten a `data/lunar_data/swisseph_dll/`.

5. **Configura el archivo `.env`**:
   - Copia `.env.example` a `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edita `.env` para especificar:
     - `FINANCIAL_CSV`: Nombre del archivo CSV de datos M1 (por ejemplo, `eur_usd_m1.csv`).
     - `FINANCIAL_DATA_PATH`: Ruta a los datos (por ejemplo, `data/financial_data`).
     - `FINANCIAL_DATA_TIMEZONE`: Zona horaria de los datos (por ejemplo, `UTC`).

6. **Descarga los datos**:
   - Obtén datos M1 de EUR/USD (2018-2024).
   - Coloca los archivos CSV en `data/financial_data/` (por ejemplo, `data/financial_data/eur_usd_m1.csv`).


## Uso
1. **Preprocesa los datos**:
   ```bash
   python scripts/calculate_lunar_phases.py
   ```
   - Combina los CSVs de `data/financial_data/` y calcula las fases lunares, generando `data/processed/combined_data.csv`.

2. **Ejecuta el análisis**:
   ```bash
   python scripts/analyze_lunar_phases.py
   ```
   - Genera estadísticas (`data/processed/statistics_by_phase_period.csv`), pruebas estadísticas (`data/processed/statistical_tests.csv`) y gráficos (`data/processed/plots/`).


## Estructura del Proyecto
```
LunarPhasesForexAnalysis/
├── data/
│   ├── financial_data/         # Datos M1 de EUR/USD (CSVs)
│   ├── lunar_data/             # Archivos de efemérides (swisseph_dll/)
│   │   ├── swisseph_dll/       # Incluye libswe.dll, semo_18.se1, sepl_18.se1 (Windows)
│   ├── processed/              # Datos procesados y resultados
│   │   ├── combined_data.csv
│   │   ├── statistics_by_phase_period.csv
│   │   ├── statistical_tests.csv
│   │   ├── plots/              # Gráficos PNG
│   │   │   ├── returns_boxplot_<period>.png
│   │   │   ├── volatility_boxplot_<period>.png
│   │   │   └── mean_returns_trend.png
├── scripts/
│   ├── calculate_lunar_phases.py # Calcula fases lunares y combina datos
│   ├── analyze_lunar_phases.py   # Genera estadísticas y gráficos
├── lunar_phases_report.tex       # Informe en LaTeX
├── .env.example                  # Ejemplo de configuración
├── requirements.txt              # Dependencias
├── README.md                     # Este archivo
```

## Archivos Generados
- **`data/processed/combined_data.csv`**: Datos M1 con columnas de precios, volumen, fase lunar y período.
- **`data/processed/statistics_by_phase_period.csv`**: Estadísticas descriptivas (retornos medios, volatilidad, etc.) por fase y período.
- **`data/processed/statistical_tests.csv`**: Resultados de pruebas estadísticas (ANOVA de Welch, Kruskal-Wallis).
- **`data/processed/plots/`**:
  - `returns_boxplot_<period>.png`: Boxplots de retornos por fase.
  - `volatility_boxplot_<period>.png`: Boxplots de volatilidad por fase.
  - `mean_returns_trend.png`: Tendencia de retornos medios.
- **`lunar_phases_report.pdf`**: Informe final en PDF (tras compilar LaTeX).

## Contribuir
¡Bienvenidos los aportes de la comunidad financiera! Para contribuir:
1. Haz un fork del repositorio.
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -m "Añadir nueva funcionalidad"`).
4. Envía un pull request con una descripción clara.

Sugerencias de mejoras:
- Analizar otros pares de divisas (por ejemplo, GBP/USD).

## Licencia
Este proyecto está bajo la [Licencia MIT](https://opensource.org/licenses/MIT). Consulta el archivo [LICENSE](LICENSE) para más detalles.

## Agradecimientos
- A la comunidad de [Rankia](https://www.rankia.com/) por inspirar este análisis.
- A los autores de `pyswisseph`, `pandas`, y otras librerías utilizadas.
- A Bikhchandani y Sharma (2000) y Yuan et al. (2006) por sus estudios.

---

**¡Únete al debate!** ¿Crees que las fases lunares afectan tus decisiones de trading? Prueba el código, revisa los resultados y comparte tus experiencias en [Rankia](https://www.rankia.com/) o en los issues de este repositorio.