import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/summarize_across_pairs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logging.info("Iniciando resumen consolidado de todos los pares...")

# Cargar variables de entorno
load_dotenv()
PAIRS_STR = os.getenv('PAIRS')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'data/output')
if not PAIRS_STR:
    logging.error("Variable PAIRS no definida en .env")
    raise ValueError("Variable PAIRS no definida en .env")
PAIRS = PAIRS_STR.split(',')
logging.info(f"Pares a procesar: {PAIRS}")

# Mapeo de períodos para display
PERIOD_MAP = {
    'prepandemia': 'Prepandemia',
    'pandemia': 'Pandemia',
    'pospandemia': 'Pospandemia'
}

def load_pair_data(pair):
    """Carga estadísticas y pruebas para un par."""
    stats_path = f'{OUTPUT_DIR}/{pair}/statistics_by_phase_period.csv'
    tests_path = f'{OUTPUT_DIR}/{pair}/statistical_tests.csv'
    
    if not os.path.exists(stats_path) or not os.path.exists(tests_path):
        logging.warning(f"Datos incompletos para {pair}. Saltando...")
        return None, None
    
    stats_df = pd.read_csv(stats_path)
    tests_df = pd.read_csv(tests_path)
    return stats_df, tests_df

def aggregate_statistics():
    """Calcula estadísticas agregadas de todos los pares."""
    all_stats = []
    for pair in PAIRS:
        stats_df, _ = load_pair_data(pair)
        if stats_df is None:
            continue
        stats_df['pair'] = pair
        all_stats.append(stats_df)
    
    if not all_stats:
        logging.error("No se encontraron datos válidos para ningún par")
        return None
    
    combined_stats = pd.concat(all_stats, ignore_index=True)
    
    # Calcular promedios y desviaciones estándar
    aggregated = combined_stats.groupby(['lunar_phase', 'period']).agg({
        'mean_return': ['mean', 'std'],
        'mean_volatility': ['mean', 'std']
    }).reset_index()
    
    aggregated.columns = ['lunar_phase', 'period', 'avg_mean_return', 'std_mean_return', 'avg_mean_volatility', 'std_mean_volatility']
    
    # Redondear a 6 decimales
    for col in ['avg_mean_return', 'std_mean_return', 'avg_mean_volatility', 'std_mean_volatility']:
        aggregated[col] = aggregated[col].apply(lambda x: 0.0 if abs(x) < 1e-8 else round(x, 6))
    
    return aggregated

def generate_heatmap():
    """Genera un heatmap de retornos medios por fase y par."""
    heatmap_data = []
    for pair in PAIRS:
        stats_df, _ = load_pair_data(pair)
        if stats_df is None:
            continue
        pivot = stats_df.pivot_table(values='mean_return', index='lunar_phase', columns='period', aggfunc='mean')
        pivot['pair'] = pair
        heatmap_data.append(pivot.reset_index())
    
    if not heatmap_data:
        logging.error("No hay datos para generar heatmap")
        return
    
    combined = pd.concat(heatmap_data, ignore_index=True)
    for period in combined.columns:
        if period not in ['lunar_phase', 'pair']:
            combined[period] = combined[period].apply(lambda x: 0.0 if abs(x) < 1e-8 else round(x, 6))
    
    output_dir = f'{OUTPUT_DIR}/summary_across_pairs'
    os.makedirs(output_dir, exist_ok=True)
    
    sns.set_style("whitegrid")
    plt.figure(figsize=(12, 8))
    pivot_table = combined.pivot(index='pair', columns='lunar_phase', values='pospandemia')
    sns.heatmap(pivot_table, annot=True, fmt='.6f', cmap='coolwarm', center=0)
    plt.title('Retornos Medios Pospandemia por Fase Lunar y Par de Divisas')
    plt.xlabel('Fase Lunar')
    plt.ylabel('Par de Divisas')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'heatmap_returns_pospandemia.png'))
    plt.close()
    logging.info(f"Heatmap guardado en {output_dir}/heatmap_returns_pospandemia.png")

def meta_analysis():
    """Realiza un meta-análisis de significancia estadística."""
    significant_counts = []
    for pair in PAIRS:
        _, tests_df = load_pair_data(pair)
        if tests_df is None:
            continue
        significant = tests_df[tests_df['significant']].groupby(['metric', 'period', 'test']).size().reset_index(name='count')
        significant['pair'] = pair
        significant_counts.append(significant)
    
    if not significant_counts:
        return pd.DataFrame(columns=['metric', 'period', 'test', 'count_significant', 'percentage'])
    
    combined = pd.concat(significant_counts, ignore_index=True)
    meta_results = combined.groupby(['metric', 'period', 'test']).agg({
        'count': 'sum'
    }).reset_index()
    meta_results['percentage'] = (meta_results['count'] / len(PAIRS) * 100).round(2)
    meta_results = meta_results.rename(columns={'count': 'count_significant'})
    return meta_results

def generate_markdown_summary(aggregated_stats, meta_results):
    """Genera un resumen consolidado en Markdown."""
    output_dir = f'{OUTPUT_DIR}/summary_across_pairs'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'results_summary_across_pairs.md')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Resumen Consolidado de Todos los Pares\n\n")
        f.write(f"Este archivo contiene un resumen de las estadísticas agregadas, patrones de retornos y significancia estadística de los {len(PAIRS)} pares de divisas.\n\n")
        
        f.write("## 1. Estadísticas Agregadas\n\n")
        f.write("Promedios y desviaciones estándar de retornos y volatilidad por fase lunar y período.\n\n")
        if aggregated_stats is not None:
            aggregated_stats['period'] = aggregated_stats['period'].map(PERIOD_MAP)
            f.write(aggregated_stats.to_markdown(index=False, floatfmt='.6f'))
        else:
            f.write("No hay datos disponibles.\n")
        f.write("\n\n")
        
        f.write("**Observaciones**:\n")
        if aggregated_stats is not None:
            for period in aggregated_stats['period'].unique():
                period_data = aggregated_stats[aggregated_stats['period'] == period]
                max_return_phase = period_data.loc[period_data['avg_mean_return'].idxmax(), 'lunar_phase']
                min_return_phase = period_data.loc[period_data['avg_mean_return'].idxmin(), 'lunar_phase']
                max_volatility_phase = period_data.loc[period_data['avg_mean_volatility'].idxmax(), 'lunar_phase']
                min_volatility_phase = period_data.loc[period_data['avg_mean_volatility'].idxmin(), 'lunar_phase']
                f.write(f"- **{period}**:\n")
                f.write(f"  - Mayor retorno medio: {max_return_phase} ({period_data['avg_mean_return'].max():.6f})\n")
                f.write(f"  - Menor retorno medio: {min_return_phase} ({period_data['avg_mean_return'].min():.6f})\n")
                f.write(f"  - Mayor volatilidad: {max_volatility_phase} ({period_data['avg_mean_volatility'].max():.6f})\n")
                f.write(f"  - Menor volatilidad: {min_volatility_phase} ({period_data['avg_mean_volatility'].min():.6f})\n")
        else:
            f.write("- No hay datos para observaciones.\n")
        f.write("\n")
        
        f.write("## 2. Heatmap de Retornos\n\n")
        f.write("Ver `heatmap_returns_pospandemia.png` para un mapa de calor de retornos medios pospandemia por par y fase lunar.\n\n")
        
        f.write("## 3. Meta-Análisis de Significancia\n\n")
        f.write("Porcentaje de pares con diferencias significativas (p < 0.05) en pruebas estadísticas.\n\n")
        meta_results['period'] = meta_results['period'].map(PERIOD_MAP)
        f.write(meta_results.to_markdown(index=False, floatfmt='.2f'))
        f.write("\n\n")
        
        f.write("**Observaciones**:\n")
        if not meta_results.empty:
            for _, row in meta_results.iterrows():
                f.write(f"- {row['metric']} en {row['period']} ({row['test']}): {row['count_significant']} pares significativos ({row['percentage']}%)\n")
        else:
            f.write("- No se encontraron resultados significativos.\n")
    
    logging.info(f"Resumen consolidado guardado en {output_path}")

def main():
    """Función principal."""
    aggregated_stats = aggregate_statistics()
    generate_heatmap()
    meta_results = meta_analysis()
    generate_markdown_summary(aggregated_stats, meta_results)

if __name__ == "__main__":
    main()