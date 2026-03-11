import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
from datetime import datetime
import logging
from scipy import stats
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/analyze_lunar_phases_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logging.info("Iniciando análisis estadístico de fases lunares...")

# Cargar variables de entorno
load_dotenv()
START_DATE = os.getenv('START_DATE', '2018-01-01')
END_DATE = os.getenv('END_DATE', '2024-12-31')
PRE_PANDEMIC_END = os.getenv('PRE_PANDEMIC_END', '2020-03-01')
PANDEMIC_END = os.getenv('PANDEMIC_END', '2021-12-31')
CLIP_OUTLIERS = os.getenv('CLIP_OUTLIERS', 'True').lower() == 'true'
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'data/output')

# Definir períodos
PERIODS = {
    'prepandemia': (START_DATE, PRE_PANDEMIC_END),
    'pandemia': (PRE_PANDEMIC_END, PANDEMIC_END),
    'pospandemia': (PANDEMIC_END, END_DATE)
}

def load_data(pair):
    """Carga datos combinados para un par."""
    data_path = f'{OUTPUT_DIR}/{pair}/combined_data.csv'
    if not os.path.exists(data_path):
        logging.error(f"No se encontró {data_path}")
        raise FileNotFoundError(f"No se encontró {data_path}")
    
    df = pd.read_csv(data_path, parse_dates=['timestamp'])
    return df

def calculate_daily_metrics(df):
    """Calcula retornos y volatilidad diarios."""
    df['date'] = df['timestamp'].dt.date
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    daily_data = df.groupby(['date', 'lunar_phase', 'period']).agg({
        'log_return': 'sum',  # Retorno diario acumulado
        'high': 'max',
        'low': 'min'
    }).reset_index()
    
    daily_data['volatility'] = (daily_data['high'] - daily_data['low']) / daily_data['low']
    daily_data = daily_data.rename(columns={'log_return': 'mean_return'})
    
    if CLIP_OUTLIERS:
        for metric in ['mean_return', 'volatility']:
            q_low = daily_data[metric].quantile(0.01)
            q_high = daily_data[metric].quantile(0.99)
            initial_len = len(daily_data)
            daily_data = daily_data[(daily_data[metric] >= q_low) & (daily_data[metric] <= q_high)]
            logging.info(f"Eliminadas {initial_len - len(daily_data)} filas con outliers en {metric}")
    
    return daily_data

def statistical_tests(df, pair):
    """Realiza pruebas estadísticas por fase y período."""
    results = []
    for period in PERIODS.keys():
        period_data = df[df['period'] == period]
        for metric in ['mean_return', 'volatility']:
            grouped = [group[metric].dropna().values for _, group in period_data.groupby('lunar_phase')]
            if len(grouped) < 2 or any(len(g) < 2 for g in grouped):
                logging.warning(f"Datos insuficientes para pruebas en {pair}, {period}, {metric}")
                continue
            
            try:
                stat_welch, p_welch = stats.f_oneway(*grouped)
                results.append({
                    'pair': pair,
                    'period': period,
                    'metric': metric,
                    'test': 'Welch ANOVA',
                    'statistic': round(stat_welch, 4),
                    'p_value': round(p_welch, 6),
                    'significant': p_welch < 0.05
                })
            except Exception as e:
                logging.error(f"Error en Welch ANOVA para {pair}, {period}, {metric}: {e}")
            
            try:
                stat_kw, p_kw = stats.kruskal(*grouped)
                results.append({
                    'pair': pair,
                    'period': period,
                    'metric': metric,
                    'test': 'Kruskal-Wallis',
                    'statistic': round(stat_kw, 4),
                    'p_value': round(p_kw, 6),
                    'significant': p_kw < 0.05
                })
            except Exception as e:
                logging.error(f"Error en Kruskal-Wallis para {pair}, {period}, {metric}: {e}")
    
    return pd.DataFrame(results)

def generate_plots(df, pair):
    """Genera boxplots y líneas de tendencia."""
    output_dir = f'{OUTPUT_DIR}/{pair}/plots'
    os.makedirs(output_dir, exist_ok=True)
    
    sns.set_style("whitegrid")
    palette = sns.color_palette("husl", n_colors=len(df['lunar_phase'].unique()))
    
    for period in PERIODS.keys():
        period_data = df[df['period'] == period]
        if period_data.empty:
            logging.warning(f"No hay datos para {pair} en {period}")
            continue
        
        # Boxplot de retornos
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='lunar_phase', y='mean_return', hue='lunar_phase', data=period_data, palette=palette, legend=False)
        plt.title(f'Retornos Diarios por Fase Lunar ({pair} - {period.capitalize()})')
        plt.xlabel('Fase Lunar')
        plt.ylabel('Retorno Diario (Log)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'boxplot_returns_{period}.png'))
        plt.close()
        
        # Boxplot de volatilidad
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='lunar_phase', y='volatility', hue='lunar_phase', data=period_data, palette=palette, legend=False)
        plt.title(f'Volatilidad Diaria por Fase Lunar ({pair} - {period.capitalize()})')
        plt.xlabel('Fase Lunar')
        plt.ylabel('Volatilidad Diaria (High-Low/Low)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'boxplot_volatility_{period}.png'))
        plt.close()
    
    logging.info(f"Gráficos guardados en {output_dir}")

def generate_statistics(df, pair):
    """Genera estadísticas por fase y período."""
    stats = df.groupby(['lunar_phase', 'period']).agg({
        'mean_return': ['mean', 'std', 'count'],
        'volatility': ['mean', 'std', 'count']
    }).reset_index()
    
    stats.columns = [
        'lunar_phase', 'period',
        'mean_return', 'std_return', 'count_return',
        'mean_volatility', 'std_volatility', 'count_volatility'
    ]
    
    # Redondear a 6 decimales
    for col in ['mean_return', 'std_return', 'mean_volatility', 'std_volatility']:
        stats[col] = stats[col].apply(lambda x: 0.0 if abs(x) < 1e-8 else round(x, 6))
    
    output_path = f'{OUTPUT_DIR}/{pair}/statistics_by_phase_period.csv'
    stats.to_csv(output_path, index=False)
    logging.info(f"Estadísticas guardadas en {output_path}")
    return stats

def generate_markdown_summary(pair, stats_df, tests_df):
    """Genera un resumen en Markdown."""
    output_dir = f'{OUTPUT_DIR}/{pair}'
    output_path = os.path.join(output_dir, 'results_summary_for_analysis.md')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Resumen de Análisis para {pair}\n\n")
        f.write(f"Este archivo contiene estadísticas y resultados de pruebas para {pair} segmentados por fase lunar y período.\n\n")
        
        f.write("## 1. Estadísticas por Fase y Período\n\n")
        f.write(stats_df.to_markdown(index=False, floatfmt='.6f'))
        f.write("\n\n")
        
        f.write("**Observaciones**:\n")
        for period in PERIODS.keys():
            period_data = stats_df[stats_df['period'] == period]
            if period_data.empty:
                f.write(f"- {period.capitalize()}: No hay datos suficientes.\n")
                continue
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
        
        f.write("## 2. Resultados de Pruebas Estadísticas\n\n")
        if tests_df.empty:
            f.write("No hay resultados de pruebas estadísticas.\n")
        else:
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
    df = load_data(pair)
    daily_data = calculate_daily_metrics(df)
    stats_df = generate_statistics(daily_data, pair)
    tests_df = statistical_tests(daily_data, pair)
    
    # Save tests_df bugfix
    output_path = f'{OUTPUT_DIR}/{pair}/statistical_tests.csv'
    tests_df.to_csv(output_path, index=False)
    logging.info(f"Pruebas estadísticas guardadas en {output_path}")

    generate_plots(daily_data, pair)
    generate_markdown_summary(pair, stats_df, tests_df)
    logging.info(f"Archivos de resultados cargados para {pair}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        logging.error("Uso: python analyze_lunar_phases.py <pair>")
        sys.exit(1)
    main(sys.argv[1])