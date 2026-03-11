import pandas as pd
import os
import glob
import logging
from datetime import datetime
# from dotenv import load_dotenv

# Configurar logging base (solo consola inicialmente)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def load_dotenv():
    """Carga .env si existe."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

def merge_csvs(pair, raw_dir='data/financial_data/raw', output_dir='data/interim/financial', use_subdirs=False):
    """
    Mergea CSVs anuales de histdata.com para un par de divisas.
    
    Args:
        pair (str): Nombre del par (ej: 'USDJPY').
        raw_dir (str): Carpeta con archivos raw por año.
        output_dir (str): Carpeta de salida para el CSV merged.
        use_subdirs (bool): Si True, busca CSVs en raw_dir/{pair.lower()}/.
    
    Returns:
        str: Path al archivo merged.
    """
    load_dotenv()
    raw_base_dir = os.getenv('HISTDATA_RAW_PATH', raw_dir)
    output_dir = os.getenv('FINANCIAL_DATA_PATH', output_dir)
    
    # Configurar directorio de CSVs según use_subdirs
    if use_subdirs:
        raw_dir = os.path.join(raw_base_dir, pair.lower())
    else:
        raw_dir = raw_base_dir
    
    # Crear directorios si no existen
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs('logs', exist_ok=True)  # Crear logs/
    
    # Configurar logging específico para este par
    log_file = f'logs/merge_histdata_{pair}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    log_handler = logging.FileHandler(log_file)
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger()
    logger.handlers = [logging.StreamHandler(), log_handler]
    
    start_date_str = os.getenv('START_DATE', '2018-01-01')
    end_date_str = os.getenv('END_DATE', '2024-12-31')
    start_year = int(start_date_str.split('-')[0])
    end_year = int(end_date_str.split('-')[0])
    
    logging.info(f"Iniciando merge para {pair} (años {start_year}-{end_year}) desde {raw_dir}")
    
    years = list(range(start_year, end_year + 1))
    dfs = []
    total_rows = 0
    for year in years:
        pattern = os.path.join(raw_dir, f'DAT_MT_{pair}_M1_{year}.csv')
        files = glob.glob(pattern)
        if not files:
            logging.warning(f"No se encontró {pattern}. Saltando año {year}.")
            continue
        
        file_path = files[0]
        logging.info(f"Cargando {file_path}")
        
        try:
            df = pd.read_csv(file_path, header=None, names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='%Y.%m.%d %H:%M')
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df = df[df['timestamp'].dt.year == year]
            dfs.append(df)
            rows_this_year = len(df)
            total_rows += rows_this_year
            logging.info(f"Año {year}: {rows_this_year} filas cargadas")
        except Exception as e:
            logging.error(f"Error al cargar {file_path}: {e}")
            continue
    
    if not dfs:
        raise ValueError(f"No se pudieron cargar datos para {pair}. Verifica archivos en {raw_dir}.")
    
    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df = merged_df.sort_values('timestamp').reset_index(drop=True)
    
    initial_len = len(merged_df)
    merged_df = merged_df.drop_duplicates(subset=['timestamp'], keep='first')
    duplicates_removed = initial_len - len(merged_df)
    if duplicates_removed > 0:
        logging.warning(f"Eliminados {duplicates_removed} duplicados por timestamp.")
    
    min_date = merged_df['timestamp'].min().date()
    max_date = merged_df['timestamp'].max().date()
    expected_min = pd.to_datetime(start_date_str).date()
    expected_max = pd.to_datetime(end_date_str).date()
    if min_date > expected_min or max_date < expected_max:
        logging.warning(f"Rango de fechas: {min_date} a {max_date} (esperado: {expected_min} a {expected_max})")
    
    gaps = merged_df['timestamp'].diff().dt.total_seconds() > 60
    gap_count = gaps.sum()
    gap_percentage = (gap_count / len(merged_df)) * 100
    logging.info(f"Total filas merged: {len(merged_df)}")
    logging.info(f"Gaps detectados (>1min): {gap_count} ({gap_percentage:.2f}%)")
    
    output_filename = f"{pair.lower()}_m1.csv"
    output_path = os.path.join(output_dir, output_filename)
    merged_df.to_csv(output_path, index=False)
    
    logging.info(f"CSV merged guardado en {output_path}")
    return output_path

def main():
    """Función principal para CLI."""
    import sys
    load_dotenv()
    
    # Si se pasa un argumento, procesa solo ese par
    if len(sys.argv) > 1 and sys.argv[1] != '--all':
        pairs = [sys.argv[1]]
        use_subdirs = '--subdirs' in sys.argv
    else:
        # Si no hay argumentos o se usa --all, procesa la lista PAIRS del .env
        pairs_str = os.getenv('PAIRS', 'AUDUSD,EURCHF,EURGBP,EURJPY,GBPUSD,USDCAD,USDCHF,USDHKD,USDJPY,USDMXN')
        pairs = [p.strip() for p in pairs_str.split(',')]
        use_subdirs = True  # Asume subdirs cuando procesa en lote (ej. raw/audusd/)
        
    logging.info(f"Iniciando consolidación para los pares: {pairs}")
    
    procesados = []
    for pair in pairs:
        try:
            output_path = merge_csvs(pair, use_subdirs=use_subdirs)
            logging.info(f"¡Merge completado! Archivo sobrescrito exitosamente: {output_path}")
            procesados.append(pair)
        except Exception as e:
            logging.error(f"Error en merge_csvs para {pair}: {e}")
            print(f"Error procesando {pair}: {e}")
            
    logging.info(f"Proceso finalizado. {len(procesados)}/{len(pairs)} pares consolidados exitosamente.")

if __name__ == "__main__":
    main()