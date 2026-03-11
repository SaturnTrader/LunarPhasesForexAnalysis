import os
import glob
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from multiprocessing import Pool
from functools import partial
from process_currency_data import combine_financial_data
from analyze_lunar_phases import main as analyze_main
from summarize_results_for_analysis import main as summarize_main
import traceback

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(
            f'logs/process_all_currencies_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

# Cargar variables de entorno
load_dotenv()
FINANCIAL_DATA_PATH = os.getenv('FINANCIAL_DATA_PATH', 'data/financial_data')
START_DATE = os.getenv('START_DATE', '2018-01-01')
END_DATE = os.getenv('END_DATE', '2024-12-31')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'data/output')
pairs_str = os.getenv(
    'PAIRS', 'AUDUSD,EURCHF,EURGBP,EURJPY,GBPUSD,USDCAD,USDCHF,USDHKD,USDJPY,USDMXN')
PAIRS = [pair.strip() for pair in pairs_str.split(',')]


def get_pair_from_filename(filename):
    """Extrae el nombre del par desde el nombre del archivo."""
    base = os.path.basename(filename).replace('_m1.csv', '').upper()
    return base


def process_single_pair(args):
    """Procesa un par individual (para paralelismo)."""
    csv_path, pair = args
    try:
        # Verificar si outputs ya existen
        output_dir = f'{OUTPUT_DIR}/{pair}'
        stats_path = os.path.join(output_dir, 'statistics_by_phase_period.csv')
        plots_dir = os.path.join(output_dir, 'plots')
        summary_path = os.path.join(
            output_dir, 'results_summary_for_analysis.md')

        # Combine secuencial (I/O)
        combine_financial_data(csv_path, pair)

        # Analyze y summarize en paralelo (CPU)
        analyze_main(pair)

        '''
        # Verificar si outputs existen antes de summarize
        if not (os.path.exists(stats_path) and os.path.exists(plots_dir) and os.path.exists(summary_path)):
            summarize_main(pair)
        '''

        # Generar siempre el resumen para garantizar datos actualizados
        summarize_main(pair)

        logging.info(f"Completado procesamiento de {pair}")
        return pair
    except Exception as e:
        logging.error(f"Error al procesar {pair}: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        # El proceso falló realmente, no enmascarar el error
        return None
    '''    
    except Exception as e:
        logging.error(f"Error al procesar {pair}: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        # Marcar como exitoso si outputs existen
        if os.path.exists(stats_path) and os.path.exists(plots_dir) and os.path.exists(summary_path):
            logging.info(
                f"Outputs existen para {pair}, marcando como exitoso a pesar de error: {str(e)}")
            return pair
        return None
    
    '''
    

def main():
    """Procesa todos los CSVs en FINANCIAL_DATA_PATH."""
    start_time = time.time()
    logging.info(
        f"Buscando CSVs en {FINANCIAL_DATA_PATH} para {len(PAIRS)} pares: {PAIRS}")

    # Limpiar data_quality_summary.csv si existe
    quality_path = os.path.join(
        OUTPUT_DIR, 'data_quality_summary.csv')
    if os.path.exists(quality_path):
        os.remove(quality_path)
        logging.info(f"Eliminado {quality_path} para nueva ejecución")

    # Obtener lista de CSVs y pares
    csv_files = glob.glob(os.path.join(FINANCIAL_DATA_PATH, '*_m1.csv'))
    if not csv_files:
        logging.error(f"No se encontraron CSVs en {FINANCIAL_DATA_PATH}")
        raise FileNotFoundError(
            f"No se encontraron CSVs en {FINANCIAL_DATA_PATH}")

    pair_args = []
    for csv_path in csv_files:
        pair = get_pair_from_filename(csv_path)
        if pair in PAIRS:
            pair_args.append((csv_path, pair))

    if not pair_args:
        logging.error("No hay pares válidos encontrados")
        raise ValueError("No hay pares válidos encontrados")

    # Procesar secuencial para combine, paralelo para analyze/summarize
    processed_pairs = []
    with Pool(processes=os.cpu_count()) as pool:
        results = pool.map(process_single_pair, pair_args)
        processed_pairs = [p for p in results if p is not None]

    # Resumen final
    logging.info(
        f"Procesamiento completo. Pares procesados: {len(processed_pairs)}/{len(pair_args)}")
    logging.info(f"Tiempo total: {time.time() - start_time:.2f} segundos")
    if processed_pairs:
        logging.info(f"Pares exitosos: {processed_pairs}")


if __name__ == "__main__":
    main()
