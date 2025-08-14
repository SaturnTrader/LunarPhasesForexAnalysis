import pandas as pd
import numpy as np
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Generando resumen consolidado de resultados para análisis...")

def load_results():
    """Carga los archivos de resultados."""
    stats_path = 'data/processed/statistics_by_phase_period.csv'
    tests_path = 'data/processed/statistical_tests.csv'
    
    if not os.path.exists(stats_path) or not os.path.exists(tests_path):
        logging.error("Archivos de resultados no encontrados")
        raise FileNotFoundError("Asegúrate de que statistics_by_phase_period.csv y statistical_tests.csv existan en data/processed/")
    
    stats_df = pd.read_csv(stats_path)
    tests_df = pd.read_csv(tests_path)
    logging.info("Archivos de resultados cargados correctamente")
    return stats_df, tests_df

def analyze_boxplot_patterns(stats_df):
    """Genera un resumen numérico de los patrones en los boxplots."""
    boxplot_summary = []
    metrics = ['mean_return', 'mean_volatility']
    
    for period in stats_df['period'].unique():
        # Crear una copia explícita para evitar SettingWithCopyWarning
        period_data = stats_df[stats_df['period'] == period].copy()
        for metric in metrics:
            if metric == 'mean_return':
                metric_col = 'mean_return'
                iqr_col = ['return_p25', 'return_p75']
            else:
                metric_col = 'mean_volatility'
                iqr_col = None  # No hay percentiles directos para volatilidad, usamos std_return como proxy
            
            # Calcular IQR usando .loc
            if iqr_col:
                period_data.loc[:, 'iqr'] = period_data[iqr_col[1]] - period_data[iqr_col[0]]
                max_iqr_phase = period_data.loc[period_data['iqr'].idxmax(), 'lunar_phase']
                min_iqr_phase = period_data.loc[period_data['iqr'].idxmin(), 'lunar_phase']
            else:
                max_iqr_phase = period_data.loc[period_data['std_return'].idxmax(), 'lunar_phase']
                min_iqr_phase = period_data.loc[period_data['std_return'].idxmin(), 'lunar_phase']
            
            # Fase con mayor y menor valor
            max_value_phase = period_data.loc[period_data[metric_col].idxmax(), 'lunar_phase']
            min_value_phase = period_data.loc[period_data[metric_col].idxmin(), 'lunar_phase']
            
            boxplot_summary.append({
                'metric': metric,
                'period': period,
                'max_iqr_phase': max_iqr_phase,
                'min_iqr_phase': min_iqr_phase,
                'max_value_phase': max_value_phase,
                'min_value_phase': min_value_phase
            })
    
    return pd.DataFrame(boxplot_summary)

def analyze_trend_patterns(stats_df):
    """Genera un resumen de la tendencia de retornos medios."""
    trend_summary = []
    trend_data = stats_df.groupby(['lunar_phase', 'period'])['mean_return'].mean().unstack()
    
    for phase in trend_data.index:
        phase_trend = trend_data.loc[phase]
        # Determinar si la tendencia es creciente, decreciente o estable
        trend_diff = phase_trend.diff().dropna()
        if all(trend_diff > 0):
            trend_type = 'Creciente'
        elif all(trend_diff < 0):
            trend_type = 'Decreciente'
        else:
            trend_type = 'Variable'
        
        trend_summary.append({
            'lunar_phase': phase,
            'trend_type': trend_type,
            'pre_pandemia_return': phase_trend.get('pre-pandemia', np.nan),
            'pandemia_return': phase_trend.get('pandemia', np.nan),
            'pos_pandemia_return': phase_trend.get('pos-pandemia', np.nan)
        })
    
    return pd.DataFrame(trend_summary)

def generate_markdown_summary(stats_df, tests_df, boxplot_summary, trend_summary):
    """Genera un resumen consolidado en Markdown."""
    output_dir = 'data/processed'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'results_summary_for_analysis.md')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Resumen Consolidado de Resultados para Análisis\n\n")
        f.write("Este archivo contiene un resumen de los resultados generados por `analyze_lunar_phases.py`, incluyendo estadísticas descriptivas, pruebas estadísticas, y patrones numéricos de los gráficos.\n\n")
        
        f.write("## 1. Estadísticas Descriptivas\n\n")
        f.write("**Archivo**: `data/processed/statistics_by_phase_period.csv`\n\n")
        f.write("Contiene estadísticas de retornos y volatilidad por fase lunar y período.\n\n")
        stats_df['mean_return'] = stats_df['mean_return'].round(6)
        stats_df['median_return'] = stats_df['median_return'].round(6)
        stats_df['std_return'] = stats_df['std_return'].round(6)
        stats_df['return_p25'] = stats_df['return_p25'].round(6)
        stats_df['return_p75'] = stats_df['return_p75'].round(6)
        stats_df['mean_volatility'] = stats_df['mean_volatility'].round(6)
        f.write(stats_df.to_markdown(index=False))
        f.write("\n\n")
        
        f.write("**Observaciones**:\n")
        for period in stats_df['period'].unique():
            period_data = stats_df[stats_df['period'] == period].copy()
            max_return_phase = period_data.loc[period_data['mean_return'].idxmax(), 'lunar_phase']
            min_return_phase = period_data.loc[period_data['mean_return'].idxmin(), 'lunar_phase']
            max_volatility_phase = period_data.loc[period_data['mean_volatility'].idxmax(), 'lunar_phase']
            min_volatility_phase = period_data.loc[period_data['mean_volatility'].idxmin(), 'lunar_phase']
            f.write(f"- **{period.capitalize()}**:\n")
            f.write(f"  - Mayor retorno medio: {max_return_phase} ({period_data['mean_return'].max():.6f})\n")
            f.write(f"  - Menor retorno medio: {min_return_phase} ({period_data['mean_return'].min():.6f})\n")
            f.write(f"  - Mayor volatilidad: {max_volatility_phase} ({period_data['mean_volatility'].max():.6f})\n")
            f.write(f"  - Menor volatilidad: {min_volatility_phase} ({period_data['mean_volatility'].min():.6f})\n")
        f.write("\n")
        
        f.write("## 2. Pruebas Estadísticas\n\n")
        f.write("**Archivo**: `data/processed/statistical_tests.csv`\n\n")
        f.write("Resultados de ANOVA de Welch y Kruskal-Wallis para determinar diferencias significativas (p < 0.05).\n\n")
        tests_df['p_value'] = tests_df['p_value'].round(4)
        f.write(tests_df.to_markdown(index=False))
        f.write("\n\n")
        
        f.write("**Observaciones**:\n")
        significant_tests = tests_df[tests_df['significant']]
        if not significant_tests.empty:
            for _, row in significant_tests.iterrows():
                f.write(f"- Diferencias significativas en {row['metric']} durante {row['period']} ({row['test']}, p={row['p_value']})\n")
        else:
            f.write("- No se encontraron diferencias significativas (p > 0.05)\n")
        f.write("\n")
        
        f.write("## 3. Patrones de Boxplots\n\n")
        f.write("Resumen numérico de los patrones en los boxplots (`returns_boxplot_<period>.png`, `volatility_boxplot_<period>.png`).\n\n")
        boxplot_summary['mean_return'] = boxplot_summary['mean_return'].round(6) if 'mean_return' in boxplot_summary else None
        boxplot_summary['mean_volatility'] = boxplot_summary['mean_volatility'].round(6) if 'mean_volatility' in boxplot_summary else None
        f.write(boxplot_summary.to_markdown(index=False))
        f.write("\n\n")
        
        f.write("**Observaciones**:\n")
        for _, row in boxplot_summary.iterrows():
            f.write(f"- **{row['metric']} en {row['period']}**:\n")
            f.write(f"  - Mayor dispersión (IQR): {row['max_iqr_phase']}\n")
            f.write(f"  - Menor dispersión (IQR): {row['min_iqr_phase']}\n")
            f.write(f"  - Mayor valor: {row['max_value_phase']}\n")
            f.write(f"  - Menor valor: {row['min_value_phase']}\n")
        f.write("\n")
        
        f.write("## 4. Patrones de Tendencia\n\n")
        f.write("Resumen numérico del gráfico de tendencia (`mean_returns_trend.png`).\n\n")
        trend_summary['pre_pandemia_return'] = trend_summary['pre_pandemia_return'].round(6)
        trend_summary['pandemia_return'] = trend_summary['pandemia_return'].round(6)
        trend_summary['pos_pandemia_return'] = trend_summary['pos_pandemia_return'].round(6)
        f.write(trend_summary.to_markdown(index=False))
        f.write("\n\n")
        
        f.write("**Observaciones**:\n")
        for _, row in trend_summary.iterrows():
            f.write(f"- **{row['lunar_phase']}**: Tendencia {row['trend_type'].lower()} en retornos medios (Pre-pandemia: {row['pre_pandemia_return']}, Pandemia: {row['pandemia_return']}, Pos-pandemia: {row['pos_pandemia_return']})\n")
    
    logging.info(f"Resumen consolidado guardado en {output_path}")
    return output_path

def main():
    """Función principal."""
    stats_df, tests_df = load_results()
    boxplot_summary = analyze_boxplot_patterns(stats_df)
    trend_summary = analyze_trend_patterns(stats_df)
    report_path = generate_markdown_summary(stats_df, tests_df, boxplot_summary, trend_summary)
    print(f"Resumen consolidado generado en: {report_path}")

if __name__ == "__main__":
    main()