import pandas as pd
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/summarize_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logging.info("Generando resumen consolidado de resultados para análisis...")

from dotenv import load_dotenv

load_dotenv()
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'data/output')

def generate_markdown_summary(pair):
    """Genera un resumen en Markdown para un par."""
    output_dir = f'{OUTPUT_DIR}/{pair}'
    stats_path = os.path.join(output_dir, 'statistics_by_phase_period.csv')
    tests_path = os.path.join(output_dir, 'statistical_tests.csv')
    
    try:
        stats_df = pd.read_csv(stats_path)
        tests_df = pd.read_csv(tests_path)
    except FileNotFoundError as e:
        logging.error(f"No se encontraron archivos de resultados para {pair}: {e}")
        raise
    except Exception as e:
        logging.error(f"Error al leer archivos para {pair}: {e}")
        raise
    
    # Verificar columnas esperadas
    expected_cols = ['lunar_phase', 'period', 'mean_return', 'std_return', 'count_return', 'mean_volatility', 'std_volatility', 'count_volatility']
    if not all(col in stats_df.columns for col in expected_cols):
        missing_cols = [col for col in expected_cols if col not in stats_df.columns]
        logging.error(f"Columnas faltantes en statistics_by_phase_period.csv para {pair}: {missing_cols}")
        raise ValueError(f"Columnas faltantes: {missing_cols}")
    
    # Mapeo de períodos para display
    period_map = {
        'prepandemia': 'Prepandemia',
        'pandemia': 'Pandemia',
        'pospandemia': 'Pospandemia'
    }
    stats_df['period'] = stats_df['period'].map(period_map)
    
    output_path = os.path.join(output_dir, 'results_summary_for_analysis.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Resumen de Análisis para {pair}\n\n")
        f.write(f"Este archivo contiene estadísticas y resultados de pruebas para {pair} segmentados por fase lunar y período.\n\n")
        
        f.write("## 1. Estadísticas por Fase y Período\n\n")
        f.write(stats_df.to_markdown(index=False, floatfmt='.6f'))
        f.write("\n\n")
        
        f.write("**Observaciones**:\n")
        for period in period_map.values():
            period_data = stats_df[stats_df['period'] == period]
            if period_data.empty:
                f.write(f"- {period}: No hay datos suficientes.\n")
                continue
            max_return_phase = period_data.loc[period_data['mean_return'].idxmax(), 'lunar_phase']
            min_return_phase = period_data.loc[period_data['mean_return'].idxmin(), 'lunar_phase']
            max_volatility_phase = period_data.loc[period_data['mean_volatility'].idxmax(), 'lunar_phase']
            min_volatility_phase = period_data.loc[period_data['mean_volatility'].idxmin(), 'lunar_phase']
            f.write(f"- **{period}**:\n")
            f.write(f"  - Mayor retorno medio: {max_return_phase} ({period_data['mean_return'].max():.6f})\n")
            f.write(f"  - Menor retorno medio: {min_return_phase} ({period_data['mean_return'].min():.6f})\n")
            f.write(f"  - Mayor volatilidad: {max_volatility_phase} ({period_data['mean_volatility'].max():.6f})\n")
            f.write(f"  - Menor volatilidad: {min_volatility_phase} ({period_data['mean_volatility'].min():.6f})\n")
        f.write("\n")
        
        f.write("## 2. Resultados de Pruebas Estadísticas\n\n")
        if tests_df.empty:
            f.write("No hay resultados de pruebas estadísticas.\n")
        else:
            tests_df['period'] = tests_df['period'].map(period_map)
            f.write(tests_df.to_markdown(index=False, floatfmt='.6f'))
            f.write("\n\n")
            f.write("**Observaciones**:\n")
            for _, row in tests_df.iterrows():
                if row['significant']:
                    f.write(f"- Diferencia significativa en {row['metric']} ({row['period']}, {row['test']}): p={row['p_value']:.6f}\n")
        
        f.write("## 3. Gráficos\n\n")
        f.write("Ver la carpeta `plots/` para boxplots de retornos y volatilidad por fase lunar y período.\n")
    
    logging.info(f"Resumen consolidado guardado en {output_path}")

def main(pair):
    """Función principal."""
    try:
        generate_markdown_summary(pair)
    except Exception as e:
        logging.error(f"Error al generar resumen para {pair}: {e}")
        raise

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        logging.error("Uso: python summarize_results_for_analysis.py <pair>")
        sys.exit(1)
    main(sys.argv[1])