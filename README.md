# LunarPhasesForexAnalysis


Análisis de la influencia de las fases lunares en los retornos y la volatilidad del par EUR/USD en el mercado Forex, segmentado en períodos pre-pandemia, pandemia y pos-pandemia. Este proyecto utiliza datos M1 (1 minuto) y la librería Swiss Ephemeris para calcular fases lunares, generando estadísticas descriptivas, pruebas estadísticas, y visualizaciones. Los resultados están disponibles en CSVs y gráficos PNG, ideales para traders e investigadores financieros interesados en explorar factores emocionales en el trading.

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

Calculamos retornos logarítmicos y volatilidad diaria, realizamos pruebas estadísticas (ANOVA de Welch, Kruskal-Wallis), y generamos boxplots y gráficos de tendencia. Los resultados sugieren que las fases lunares tienen un impacto insignificante, pero los patrones descriptivos son un punto de partida para explorar factores emocionales en el trading. El código es reproducible y está diseñado para la comunidad financiera.

## Requisitos
- **Sistema Operativo**: Windows, macOS, o Linux.
- **Python**: Versión 3.11.
- **Dependencias**:
  - `pandas`
  - `numpy`
  - `pyswisseph`
  - `scipy`
  - `seaborn`
  - `matplotlib`
  - `tabulate`
- **Datos**: Archivos CSV de precios M1 de EUR/USD (por ejemplo, de [HistData.com](http://www.histdata.com/)).
- **Opcional**: TeX Live o MikTeX para compilar el informe en LaTeX.

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
   pip install pandas numpy pyswisseph scipy seaborn matplotlib tabulate
   ```

4. **Descarga los datos**:
   - Obtén datos M1 de EUR/USD (2018-2024) desde [HistData.com](http://www.histdata.com/) o tu plataforma de trading.
   - Coloca los archivos CSV en `data/raw/` (por ejemplo, `data/raw/EURUSD_M1_2018.csv`, `data/raw/EURUSD_M1_2019.csv`, etc.).

5. **(Opcional) Instala LaTeX**:
   - Para compilar el informe en PDF, instala [TeX Live](https://tug.org/texlive/) o [MikTeX](https://miktex.org/download).
   - Alternativamente, usa [Overleaf](https://www.overleaf.com/) para compilar `lunar_phases_report.tex`.

## Uso
1. **Preprocesa los datos**:
   ```bash
   python scripts/preprocess_data.py
   ```
   - Combina los CSVs de `data/raw/` en `data/processed/eurusd_with_phases.csv`, añadiendo las fases lunares con Swiss Ephemeris.

2. **Ejecuta el análisis**:
   ```bash
   python scripts/analyze_lunar_phases.py
   ```
   - Genera estadísticas (`data/processed/statistics_by_phase_period.csv`), pruebas estadísticas (`data/processed/statistical_tests.csv`), y gráficos (`data/processed/plots/`).

3. **Genera el resumen**:
   ```bash
   python scripts/summarize_results_for_analysis.py
   ```
   - Crea un resumen consolidado en `data/processed/results_summary_for_analysis.md`.

4. **(Opcional) Genera el informe en PDF**:
   ```bash
   latexmk -pdf lunar_phases_report.tex
   ```
   - Produce `lunar_phases_report.pdf` con los resultados completos.

## Estructura del Proyecto
```
LunarPhasesForexAnalysis/
├── data/
│   ├── raw/                    # Datos M1 de EUR/USD (CSVs)
│   ├── processed/              # Datos procesados y resultados
│   │   ├── eurusd_with_phases.csv
│   │   ├── statistics_by_phase_period.csv
│   │   ├── statistical_tests.csv
│   │   ├── results_summary_for_analysis.md
│   │   ├── plots/              # Gráficos PNG
│   │   │   ├── returns_boxplot_<period>.png
│   │   │   ├── volatility_boxplot_<period>.png
│   │   │   └── mean_returns_trend.png
├── scripts/
│   ├── preprocess_data.py      # Combina datos y calcula fases lunares
│   ├── analyze_lunar_phases.py # Genera estadísticas y gráficos
│   ├── summarize_results_for_analysis.py # Crea resumen consolidado
├── lunar_phases_report.tex     # Informe en LaTeX
├── README.md                   # Este archivo
└── requirements.txt            # Dependencias
```

## Archivos Generados
- **`data/processed/eurusd_with_phases.csv`**: Datos M1 con columnas de precios y fase lunar.
- **`data/processed/statistics_by_phase_period.csv`**: Estadísticas descriptivas por fase y período.
- **`data/processed/statistical_tests.csv`**: Resultados de pruebas estadísticas (ANOVA, Kruskal-Wallis).
- **`data/processed/plots/`**:
  - `returns_boxplot_<period>.png`: Boxplots de retornos por fase.
  - `volatility_boxplot_<period>.png`: Boxplots de volatilidad por fase.
  - `mean_returns_trend.png`: Tendencia de retornos medios.
- **`data/processed/results_summary_for_analysis.md`**: Resumen consolidado de resultados.
- **`lunar_phases_report.pdf`**: Informe final en PDF (tras compilar LaTeX).

## Contribuir
¡Bienvenidos los aportes de la comunidad financiera! Para contribuir:
1. Haz un fork del repositorio.
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -m "Añadir nueva funcionalidad"`).
4. Envía un pull request con una descripción clara.

Sugerencias de mejoras:
- Añadir análisis para otros pares de divisas (por ejemplo, GBP/USD).
- Usar datos diarios en lugar de M1 para reducir ruido.
- Integrar análisis de sentimientos en redes sociales.

Por favor, sigue el [Código de Conducta](https://github.com/SaturnTrader/LunarPhasesForexAnalysis/blob/main/CODE_OF_CONDUCT.md).

## Licencia
Este proyecto está bajo la [Licencia MIT](https://opensource.org/licenses/MIT). Consulta el archivo [LICENSE](LICENSE) para más detalles.

## Agradecimientos
- A la comunidad de [Rankia](https://www.rankia.com/) por inspirar este análisis.
- A los autores de `pyswisseph`, `pandas`, y otras librerías utilizadas.
- A Bikhchandani y Sharma (2000) y Yuan et al. (2006) por sus estudios sobre comportamiento y fases lunares.

---

**¡Únete al debate!** ¿Crees que las fases lunares afectan tus decisiones de trading? Prueba el código, revisa los resultados, y comparte tus experiencias en [Rankia](https://www.rankia.com/) o en los issues de este repositorio.