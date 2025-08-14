# Resumen Consolidado de Resultados para Análisis

Este archivo contiene un resumen de los resultados generados por `analyze_lunar_phases.py`, incluyendo estadísticas descriptivas, pruebas estadísticas, y patrones numéricos de los gráficos.

## 1. Estadísticas Descriptivas

**Archivo**: `data/processed/statistics_by_phase_period.csv`

Contiene estadísticas de retornos y volatilidad por fase lunar y período.

| lunar_phase       | period       |   mean_return |   median_return |   std_return |   return_p25 |   return_p75 |   mean_volatility |   count_days |
|:------------------|:-------------|--------------:|----------------:|-------------:|-------------:|-------------:|------------------:|-------------:|
| Creciente Cóncava | pandemia     |        -0     |          -0     |        4e-06 |       -2e-06 |        3e-06 |          0.000108 |        85703 |
| Creciente Cóncava | pos-pandemia |        -1e-06 |           0     |        7e-06 |       -3e-06 |        2e-06 |          0.000127 |       135224 |
| Creciente Cóncava | pre-pandemia |         0     |           0     |        3e-06 |       -2e-06 |        2e-06 |          0.000102 |       100469 |
| Creciente Gibosa  | pandemia     |        -1e-06 |          -0     |        5e-06 |       -3e-06 |        2e-06 |          0.000116 |        84463 |
| Creciente Gibosa  | pos-pandemia |         0     |           0     |        5e-06 |       -3e-06 |        3e-06 |          0.000127 |       130837 |
| Creciente Gibosa  | pre-pandemia |        -0     |          -1e-06 |        4e-06 |       -2e-06 |        1e-06 |          9.6e-05  |       100338 |
| Cuarto Creciente  | pandemia     |         0     |          -0     |        3e-06 |       -1e-06 |        2e-06 |          0.000103 |        84612 |
| Cuarto Creciente  | pos-pandemia |        -0     |          -0     |        5e-06 |       -3e-06 |        2e-06 |          0.000124 |       134791 |
| Cuarto Creciente  | pre-pandemia |         0     |           0     |        3e-06 |       -2e-06 |        2e-06 |          9.7e-05  |        98575 |
| Cuarto Menguante  | pandemia     |        -1e-06 |           0     |        4e-06 |       -3e-06 |        2e-06 |          0.000112 |        90865 |
| Cuarto Menguante  | pos-pandemia |         0     |           0     |        5e-06 |       -2e-06 |        3e-06 |          0.000126 |       135149 |
| Cuarto Menguante  | pre-pandemia |         0     |           0     |        5e-06 |       -2e-06 |        2e-06 |          9.7e-05  |       100152 |
| Luna Llena        | pandemia     |        -0     |          -0     |        4e-06 |       -2e-06 |        2e-06 |          0.000108 |        84532 |
| Luna Llena        | pos-pandemia |         0     |          -0     |        5e-06 |       -3e-06 |        3e-06 |          0.000125 |       130307 |
| Luna Llena        | pre-pandemia |        -1e-06 |           0     |        7e-06 |       -1e-06 |        2e-06 |          0.000102 |       100386 |
| Luna Nueva        | pandemia     |         1e-06 |           0     |        4e-06 |       -1e-06 |        3e-06 |          0.000101 |        79595 |
| Luna Nueva        | pos-pandemia |        -0     |          -0     |        5e-06 |       -3e-06 |        2e-06 |          0.000126 |       133230 |
| Luna Nueva        | pre-pandemia |        -0     |          -0     |        4e-06 |       -2e-06 |        3e-06 |          0.000102 |       100483 |
| Menguante Cóncava | pandemia     |         0     |           0     |        4e-06 |       -2e-06 |        2e-06 |          0.000111 |        84181 |
| Menguante Cóncava | pos-pandemia |        -0     |           0     |        5e-06 |       -2e-06 |        2e-06 |          0.00013  |       136017 |
| Menguante Cóncava | pre-pandemia |        -0     |          -0     |        3e-06 |       -2e-06 |        1e-06 |          9.5e-05  |       100679 |
| Menguante Gibosa  | pandemia     |         1e-06 |           0     |        5e-06 |       -2e-06 |        2e-06 |          0.000115 |        86519 |
| Menguante Gibosa  | pos-pandemia |         0     |          -0     |        5e-06 |       -3e-06 |        2e-06 |          0.000124 |       133336 |
| Menguante Gibosa  | pre-pandemia |        -0     |          -0     |        3e-06 |       -2e-06 |        2e-06 |          9.5e-05  |       104413 |

**Observaciones**:
- **Pandemia**:
  - Mayor retorno medio: Luna Nueva (0.000001)
  - Menor retorno medio: Creciente Gibosa (-0.000001)
  - Mayor volatilidad: Creciente Gibosa (0.000116)
  - Menor volatilidad: Luna Nueva (0.000101)
- **Pos-pandemia**:
  - Mayor retorno medio: Creciente Gibosa (0.000000)
  - Menor retorno medio: Creciente Cóncava (-0.000001)
  - Mayor volatilidad: Menguante Cóncava (0.000130)
  - Menor volatilidad: Cuarto Creciente (0.000124)
- **Pre-pandemia**:
  - Mayor retorno medio: Creciente Cóncava (-0.000000)
  - Menor retorno medio: Luna Llena (-0.000001)
  - Mayor volatilidad: Creciente Cóncava (0.000102)
  - Menor volatilidad: Menguante Cóncava (0.000095)

## 2. Pruebas Estadísticas

**Archivo**: `data/processed/statistical_tests.csv`

Resultados de ANOVA de Welch y Kruskal-Wallis para determinar diferencias significativas (p < 0.05).

| metric      | period       | test           |   p_value | significant   |
|:------------|:-------------|:---------------|----------:|:--------------|
| mean_return | pre-pandemia | ANOVA_Welch    |    0.5981 | False         |
| mean_return | pre-pandemia | Kruskal-Wallis |    0.8216 | False         |
| volatility  | pre-pandemia | ANOVA_Welch    |    0.5539 | False         |
| volatility  | pre-pandemia | Kruskal-Wallis |    0.5689 | False         |
| mean_return | pandemia     | ANOVA_Welch    |    0.1117 | False         |
| mean_return | pandemia     | Kruskal-Wallis |    0.4958 | False         |
| volatility  | pandemia     | ANOVA_Welch    |    0.5378 | False         |
| volatility  | pandemia     | Kruskal-Wallis |    0.4148 | False         |
| mean_return | pos-pandemia | ANOVA_Welch    |    0.228  | False         |
| mean_return | pos-pandemia | Kruskal-Wallis |    0.6715 | False         |
| volatility  | pos-pandemia | ANOVA_Welch    |    0.9916 | False         |
| volatility  | pos-pandemia | Kruskal-Wallis |    0.9895 | False         |

**Observaciones**:
- No se encontraron diferencias significativas (p > 0.05)

## 3. Patrones de Boxplots

Resumen numérico de los patrones en los boxplots (`returns_boxplot_<period>.png`, `volatility_boxplot_<period>.png`).

| metric          | period       | max_iqr_phase     | min_iqr_phase     | max_value_phase   | min_value_phase   | mean_return   | mean_volatility   |
|:----------------|:-------------|:------------------|:------------------|:------------------|:------------------|:--------------|:------------------|
| mean_return     | pandemia     | Cuarto Menguante  | Menguante Cóncava | Menguante Gibosa  | Creciente Gibosa  |               |                   |
| mean_volatility | pandemia     | Creciente Gibosa  | Cuarto Creciente  | Creciente Gibosa  | Luna Nueva        |               |                   |
| mean_return     | pos-pandemia | Luna Llena        | Menguante Cóncava | Cuarto Menguante  | Creciente Cóncava |               |                   |
| mean_volatility | pos-pandemia | Creciente Cóncava | Cuarto Menguante  | Menguante Cóncava | Cuarto Creciente  |               |                   |
| mean_return     | pre-pandemia | Luna Nueva        | Luna Llena        | Cuarto Menguante  | Luna Llena        |               |                   |
| mean_volatility | pre-pandemia | Luna Llena        | Creciente Cóncava | Luna Llena        | Menguante Gibosa  |               |                   |

**Observaciones**:
- **mean_return en pandemia**:
  - Mayor dispersión (IQR): Cuarto Menguante
  - Menor dispersión (IQR): Menguante Cóncava
  - Mayor valor: Menguante Gibosa
  - Menor valor: Creciente Gibosa
- **mean_volatility en pandemia**:
  - Mayor dispersión (IQR): Creciente Gibosa
  - Menor dispersión (IQR): Cuarto Creciente
  - Mayor valor: Creciente Gibosa
  - Menor valor: Luna Nueva
- **mean_return en pos-pandemia**:
  - Mayor dispersión (IQR): Luna Llena
  - Menor dispersión (IQR): Menguante Cóncava
  - Mayor valor: Cuarto Menguante
  - Menor valor: Creciente Cóncava
- **mean_volatility en pos-pandemia**:
  - Mayor dispersión (IQR): Creciente Cóncava
  - Menor dispersión (IQR): Cuarto Menguante
  - Mayor valor: Menguante Cóncava
  - Menor valor: Cuarto Creciente
- **mean_return en pre-pandemia**:
  - Mayor dispersión (IQR): Luna Nueva
  - Menor dispersión (IQR): Luna Llena
  - Mayor valor: Cuarto Menguante
  - Menor valor: Luna Llena
- **mean_volatility en pre-pandemia**:
  - Mayor dispersión (IQR): Luna Llena
  - Menor dispersión (IQR): Creciente Cóncava
  - Mayor valor: Luna Llena
  - Menor valor: Menguante Gibosa

## 4. Patrones de Tendencia

Resumen numérico del gráfico de tendencia (`mean_returns_trend.png`).

| lunar_phase       | trend_type   |   pre_pandemia_return |   pandemia_return |   pos_pandemia_return |
|:------------------|:-------------|----------------------:|------------------:|----------------------:|
| Creciente Cóncava | Variable     |                 0     |            -0     |                -1e-06 |
| Creciente Gibosa  | Variable     |                -0     |            -1e-06 |                 0     |
| Cuarto Creciente  | Variable     |                 0     |             0     |                -0     |
| Cuarto Menguante  | Creciente    |                 0     |            -1e-06 |                 0     |
| Luna Llena        | Variable     |                -1e-06 |            -0     |                 0     |
| Luna Nueva        | Variable     |                -0     |             1e-06 |                -0     |
| Menguante Cóncava | Decreciente  |                -0     |             0     |                -0     |
| Menguante Gibosa  | Decreciente  |                -0     |             1e-06 |                 0     |

**Observaciones**:
- **Creciente Cóncava**: Tendencia variable en retornos medios (Pre-pandemia: 0.0, Pandemia: -0.0, Pos-pandemia: -1e-06)
- **Creciente Gibosa**: Tendencia variable en retornos medios (Pre-pandemia: -0.0, Pandemia: -1e-06, Pos-pandemia: 0.0)
- **Cuarto Creciente**: Tendencia variable en retornos medios (Pre-pandemia: 0.0, Pandemia: 0.0, Pos-pandemia: -0.0)
- **Cuarto Menguante**: Tendencia creciente en retornos medios (Pre-pandemia: 0.0, Pandemia: -1e-06, Pos-pandemia: 0.0)
- **Luna Llena**: Tendencia variable en retornos medios (Pre-pandemia: -1e-06, Pandemia: -0.0, Pos-pandemia: 0.0)
- **Luna Nueva**: Tendencia variable en retornos medios (Pre-pandemia: -0.0, Pandemia: 1e-06, Pos-pandemia: -0.0)
- **Menguante Cóncava**: Tendencia decreciente en retornos medios (Pre-pandemia: -0.0, Pandemia: 0.0, Pos-pandemia: -0.0)
- **Menguante Gibosa**: Tendencia decreciente en retornos medios (Pre-pandemia: -0.0, Pandemia: 1e-06, Pos-pandemia: 0.0)
