import pandas as pd
import numpy as np
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Iniciando análisis estadístico de fases lunares...")

# Cargar variables de entorno
load_dotenv()
PRE_PANDEMIC_END = os.getenv('PRE_PANDEMIC_END', '2020-03-01')
PANDEMIC_END = os.getenv('PANDEMIC_END', '2021-12-31')

# Convertir fechas a datetime
try:
    pre_pandemic_end = pd.to_datetime(PRE_PANDEMIC_END).tz_localize('UTC')
    pandemic_end = pd.to_datetime(PANDEMIC_END).tz_localize('UTC')
except ValueError as e:
    logging.error(f"Error en el formato de fechas en .env: {e}")
    raise

def load_data():
    """Carga los datos combinados."""
    input_path = 'data/processed/combined_data.csv'
    if not os.path.exists(input_path):
        logging.error(f"Archivo no encontrado: {input_path}")
        raise FileNotFoundError(f"Archivo no encontrado: {input_path}")
    df = pd.read_csv(input_path, parse_dates=['timestamp'])
    logging.info(f"Datos cargados desde {input_path}")
    return df

def calculate_metrics(df):
    """Calcula retornos, volatilidad y rango diario."""
    # Calcular retornos logarítmicos
    df['return'] = np.log(df['close'] / df['close'].shift(1))
    
    # Agrupar por día, fase lunar y período
    df['date'] = df['timestamp'].dt.date
    daily_metrics = df.groupby(['date', 'lunar_phase', 'period']).agg({
        'return': ['mean', 'std'],
        'high': 'max',
        'low': 'min',
        'timestamp': 'count'
    }).reset_index()
    
    # Renombrar columnas
    daily_metrics.columns = ['date', 'lunar_phase', 'period', 'mean_return', 'volatility', 'high', 'low', 'count']
    daily_metrics['range'] = daily_metrics['high'] - daily_metrics['low']
    
    return daily_metrics

def descriptive_statistics(daily_metrics):
    """Calcula estadísticas descriptivas por fase lunar y período."""
    stats_df = daily_metrics.groupby(['lunar_phase', 'period']).agg({
        'mean_return': ['mean', 'median', 'std', lambda x: np.percentile(x.dropna(), 25), lambda x: np.percentile(x.dropna(), 75)],
        'volatility': ['mean'],
        'count': 'sum'
    }).reset_index()
    
    stats_df.columns = ['lunar_phase', 'period', 'mean_return', 'median_return', 'std_return', 'return_p25', 'return_p75', 'mean_volatility', 'count_days']
    
    output_dir = 'data/processed'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'statistics_by_phase_period.csv')
    stats_df.to_csv(output_path, index=False)
    logging.info(f"Estadísticas descriptivas guardadas en {output_path}")
    return stats_df

def statistical_tests(daily_metrics):
    """Realiza pruebas ANOVA de Welch y Kruskal-Wallis."""
    test_results = []
    metrics = ['mean_return', 'volatility']
    
    for period in daily_metrics['period'].unique():
        period_data = daily_metrics[daily_metrics['period'] == period]
        for metric in metrics:
            # Agrupar datos por fase lunar
            groups = [period_data[period_data['lunar_phase'] == phase][metric].dropna() 
                      for phase in period_data['lunar_phase'].unique()]
            
            # ANOVA de Welch
            try:
                f_stat, p_value = stats.f_oneway(*groups)
                test_results.append({
                    'metric': metric,
                    'period': period,
                    'test': 'ANOVA_Welch',
                    'p_value': p_value,
                    'significant': p_value < 0.05
                })
            except Exception as e:
                logging.warning(f"Error en ANOVA para {metric} en {period}: {e}")
            
            # Kruskal-Wallis
            try:
                stat, p_value = stats.kruskal(*groups)
                test_results.append({
                    'metric': metric,
                    'period': period,
                    'test': 'Kruskal-Wallis',
                    'p_value': p_value,
                    'significant': p_value < 0.05
                })
            except Exception as e:
                logging.warning(f"Error en Kruskal-Wallis para {metric} en {period}: {e}")
    
    test_df = pd.DataFrame(test_results)
    output_path = 'data/processed/statistical_tests.csv'
    test_df.to_csv(output_path, index=False)
    logging.info(f"Resultados de pruebas estadísticas guardados en {output_path}")
    return test_df

def generate_boxplots(daily_metrics):
    """Genera boxplots para retornos y volatilidad."""
    output_dir = 'data/processed/plots'
    os.makedirs(output_dir, exist_ok=True)
    
    sns.set_style("whitegrid")
    palette = sns.color_palette("deep", 8)
    
    for period in daily_metrics['period'].unique():
        period_data = daily_metrics[daily_metrics['period'] == period]
        
        # Boxplot para retornos
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='lunar_phase', y='mean_return', data=period_data, palette=palette)
        plt.title(f'Retornos por Fase Lunar - {period.capitalize()}')
        plt.xlabel('Fase Lunar')
        plt.ylabel('Retorno Logarítmico Medio Diario')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'returns_boxplot_{period}.png'))
        plt.close()
        
        # Boxplot para volatilidad
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='lunar_phase', y='volatility', data=period_data, palette=palette)
        plt.title(f'Volatilidad por Fase Lunar - {period.capitalize()}')
        plt.xlabel('Fase Lunar')
        plt.ylabel('Volatilidad (Desviación Estándar Diaria)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'volatility_boxplot_{period}.png'))
        plt.close()
    
    # Gráfico de líneas para tendencia de retornos
    trend_data = daily_metrics.groupby(['lunar_phase', 'period'])['mean_return'].mean().unstack()
    plt.figure(figsize=(12, 6))
    for period in trend_data.columns:
        plt.plot(trend_data.index, trend_data[period], marker='o', label=period.capitalize())
    plt.title('Tendencia de Retornos Medios por Fase Lunar')
    plt.xlabel('Fase Lunar')
    plt.ylabel('Retorno Logarítmico Medio')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mean_returns_trend.png'))
    plt.close()
    
    logging.info(f"Gráficos guardados en {output_dir}")

def main():
    """Función principal."""
    df = load_data()
    daily_metrics = calculate_metrics(df)
    stats_df = descriptive_statistics(daily_metrics)
    test_df = statistical_tests(daily_metrics)
    generate_boxplots(daily_metrics)

if __name__ == "__main__":
    main()