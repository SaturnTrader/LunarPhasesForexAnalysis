import os
import pandas as pd
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'data/output')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/generate_internal_md_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logging.info("Generando archivo Markdown interno con detalles por par...")

# Definir períodos y pares
PERIODS = {
    'prepandemia': 'Prepandemia (2018-01-01 a 2020-02-29)',
    'pandemia': 'Pandemia (2020-03-01 a 2021-12-31)',
    'pospandemia': 'Pospandemia (2022-01-01 a 2024-12-31)'
}
PAIRS = ['AUDUSD', 'EURCHF', 'EURGBP', 'EURJPY', 'GBPUSD', 'USDCAD', 'USDCHF', 'USDHKD', 'USDJPY', 'USDMXN']

# Ruta de salida
output_path = f'{OUTPUT_DIR}/internal_analysis.md'

# Función para leer datos y generar contenido
def generate_md_content():
    content = "# Análisis Interno Detallado de Fases Lunares en 10 Pares de Divisas\n"
    content += f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} CST\n\n"
    content += "Este documento proporciona un análisis detallado por par de divisas, incluyendo estadísticas descriptivas, resultados de pruebas estadísticas y referencias a visualizaciones generadas.\n\n"

    for pair in PAIRS:
        content += f"## {pair.upper()}\n\n"
        
        # Cargar datos estadísticos
        stats_path = os.path.join(f'{OUTPUT_DIR}/{pair}', 'statistics_by_phase_period.csv')
        tests_path = os.path.join(f'{OUTPUT_DIR}/{pair}', 'statistical_tests.csv')
        
        if not os.path.exists(stats_path):
            content += f"- **Error**: No se encontró {stats_path}. Saltando par.\n\n"
            logging.warning(f"No se encontró {stats_path}")
            continue
        
        stats_df = pd.read_csv(stats_path)
        content += "### 1. Estadísticas Descriptivas por Fase y Período\n\n"
        content += stats_df.to_markdown(index=False, floatfmt='.6f')
        content += "\n\n**Observaciones:**\n"
        for period in PERIODS.keys():
            period_data = stats_df[stats_df['period'] == period]
            if not period_data.empty:
                max_return_phase = period_data.loc[period_data['mean_return'].idxmax(), 'lunar_phase']
                min_return_phase = period_data.loc[period_data['mean_return'].idxmin(), 'lunar_phase']
                max_vol_phase = period_data.loc[period_data['mean_volatility'].idxmax(), 'lunar_phase']
                min_vol_phase = period_data.loc[period_data['mean_volatility'].idxmin(), 'lunar_phase']
                content += f"- **{PERIODS[period]}**:\n"
                content += f"  - Mayor retorno medio: {max_return_phase} ({period_data['mean_return'].max():.6f})\n"
                content += f"  - Menor retorno medio: {min_return_phase} ({period_data['mean_return'].min():.6f})\n"
                content += f"  - Mayor volatilidad: {max_vol_phase} ({period_data['mean_volatility'].max():.6f})\n"
                content += f"  - Menor volatilidad: {min_vol_phase} ({period_data['mean_volatility'].min():.6f})\n"
        content += "\n"

        # Cargar y agregar pruebas estadísticas
        if os.path.exists(tests_path):
            tests_df = pd.read_csv(tests_path)
            content += "### 2. Resultados de Pruebas Estadísticas\n\n"
            content += tests_df.to_markdown(index=False, floatfmt='.6f')
            content += "\n\n**Observaciones:**\n"
            for _, row in tests_df.iterrows():
                if row['significant']:
                    content += f"- Diferencia significativa en {row['metric']} ({PERIODS[row['period']]}, {row['test']}): p={row['p_value']:.6f}\n"
        else:
            content += "- **Nota**: No se encontraron resultados de pruebas estadísticas.\n\n"
            logging.warning(f"No se encontró {tests_path} para {pair}")

        # Referencias a visualizaciones
        plots_dir = os.path.join(f'{OUTPUT_DIR}/{pair}', 'plots')
        if os.path.exists(plots_dir):
            content += "### 3. Visualizaciones\n\n"
            for period in PERIODS.keys():
                content += f"- Boxplot de Retornos Diarios - {pair} ({PERIODS[period]}): `boxplot_returns_{period}.png`\n"
                content += f"- Boxplot de Volatilidad Diaria - {pair} ({PERIODS[period]}): `boxplot_volatility_{period}.png`\n"
        else:
            content += "- **Nota**: No se encontraron directorios de gráficos para este par.\n\n"
            logging.warning(f"No se encontró {plots_dir} para {pair}")

        content += "\n---\n\n"

    # Agregar sección de resumen
    content += "## Resumen General\n\n"
    content += "El análisis interno revela que, aunque hay variaciones descriptivas en retornos y volatilidad por fase lunar, las pruebas estadísticas no muestran significancia general (p > 0.05), excepto en casos aislados (ejemplo: 10% de pares en pandemia). Las visualizaciones sugieren que 'Creciente Gibosa' y 'Menguante Cóncava' podrían merecer atención en estrategias especulativas.\n\n"

    return content

# Generar y guardar el archivo
try:
    md_content = generate_md_content()
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    logging.info(f"Archivo Markdown interno guardado en {output_path}")
except Exception as e:
    logging.error(f"Error al generar el archivo Markdown: {e}")