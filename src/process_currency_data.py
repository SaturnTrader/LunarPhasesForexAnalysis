import swisseph as swe
import pandas as pd
from datetime import datetime, timedelta, timezone
import logging
import os
from dotenv import load_dotenv
import pytz

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/process_currency_{}.log'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))),
        logging.StreamHandler()
    ]
)
logging.info("Iniciando procesamiento de datos financieros...")

# Cargar variables de entorno desde .env
load_dotenv()
EPHE_PATH = os.getenv('EPHE_PATH', 'data/lunar_data/swisseph_dll')
DLL_PATH = os.path.abspath(os.getenv('DLL_PATH', 'data/lunar_data/swisseph_dll'))
START_DATE = os.getenv('START_DATE', '2018-01-01')
END_DATE = os.getenv('END_DATE', '2024-12-31')
FINANCIAL_DATA_TIMEZONE = os.getenv('FINANCIAL_DATA_TIMEZONE', 'EST')
PRE_PANDEMIC_END = os.getenv('PRE_PANDEMIC_END', '2020-03-01')
PANDEMIC_END = os.getenv('PANDEMIC_END', '2021-12-31')
CLIP_OUTLIERS = os.getenv('CLIP_OUTLIERS', 'True').lower() == 'true'
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'data/output')

# Convertir fechas a objetos datetime en UTC
try:
    start_date = datetime.strptime(START_DATE, '%Y-%m-%d').replace(tzinfo=timezone.utc, hour=0, minute=0, second=0, microsecond=0)
    end_date = datetime.strptime(END_DATE, '%Y-%m-%d').replace(tzinfo=timezone.utc, hour=23, minute=59, second=59, microsecond=999999)
    pre_pandemic_end = datetime.strptime(PRE_PANDEMIC_END, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    pandemic_end = datetime.strptime(PANDEMIC_END, '%Y-%m-%d').replace(tzinfo=timezone.utc)
except ValueError as e:
    logging.error(f"Error en el formato de las fechas en .env: {e}")
    raise

# Verificar y configurar rutas de Swiss Ephemeris
if not os.path.exists(EPHE_PATH):
    logging.error(f"Directorio de efemérides no encontrado: {EPHE_PATH}")
    raise FileNotFoundError(f"Directorio de efemérides no encontrado: {EPHE_PATH}")
if not os.path.exists(DLL_PATH):
    logging.error(f"Directorio de DLL no encontrado: {DLL_PATH}")
    raise FileNotFoundError(f"Directorio de DLL no encontrado: {DLL_PATH}")
swe.set_ephe_path(EPHE_PATH)
if os.name == 'nt':  # Windows
    os.add_dll_directory(DLL_PATH)
logging.info(f"Rutas de Swiss Ephemeris configuradas: {EPHE_PATH}, {DLL_PATH}")

# Definir las 8 fases lunares
NUM_PHASES = 8
ANGLE_PER_PHASE = 360.0 / NUM_PHASES
PHASE_NAMES_ES = [
    "Luna Nueva",
    "Creciente Cóncava",
    "Cuarto Creciente",
    "Creciente Gibosa",
    "Luna Llena",
    "Menguante Gibosa",
    "Cuarto Menguante",
    "Menguante Cóncava"
]

def get_phase_data(dt_utc):
    """Calcula el ángulo de fase para un datetime UTC."""
    try:
        jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
        sun_pos = swe.calc_ut(jd_ut, swe.SUN)[0][0]
        moon_pos = swe.calc_ut(jd_ut, swe.MOON)[0][0]
        angle = (moon_pos - sun_pos) % 360
        return angle
    except Exception as e:
        logging.error(f"Error al calcular el ángulo de fase para {dt_utc}: {e}")
        raise

def find_next_phase_change(start_dt_utc, current_phase_num):
    """Encuentra el momento exacto del próximo cambio de fase."""
    target_phase_num = (current_phase_num + 1) % NUM_PHASES
    target_angle = target_phase_num * ANGLE_PER_PHASE
    current_dt = start_dt_utc
    step = timedelta(hours=6)
    max_steps = 5000
    step_count = 0

    while current_dt < end_date and step_count < max_steps:
        current_angle = get_phase_data(current_dt)
        current_phase_num_check = int((current_angle % 360) / ANGLE_PER_PHASE) % NUM_PHASES
        if current_phase_num_check == target_phase_num:
            fine_dt = current_dt
            fine_step = timedelta(minutes=1)
            while True:
                fine_dt -= fine_step
                prev_angle = get_phase_data(fine_dt)
                prev_phase_num = int((prev_angle % 360) / ANGLE_PER_PHASE) % NUM_PHASES
                if prev_phase_num != target_phase_num:
                    return fine_dt + fine_step
                if fine_dt < start_date:
                    logging.warning(f"No se encontró cambio de fase para {target_phase_num} desde {start_dt_utc}")
                    return current_dt
            break
        current_dt += step
        step_count += 1

    if step_count >= max_steps:
        logging.error(f"Bucle infinito detectado buscando la fase {target_phase_num} desde {start_dt_utc}")
        raise RuntimeError(f"No se pudo encontrar la fase {target_phase_num}")
    if current_dt >= end_date:
        logging.warning(f"Fecha límite alcanzada: {current_dt}")
        return end_date
    return current_dt

def generate_lunar_phase_changes():
    """Genera un DataFrame con los momentos exactos de cambio de fase."""
    logging.info(f"Calculando cambios de fase desde {START_DATE} hasta {END_DATE}")
    phase_changes = []
    current_dt = start_date
    last_phase_num = None

    while current_dt < end_date:
        angle = get_phase_data(current_dt)
        phase_num = int((angle % 360) / ANGLE_PER_PHASE) % NUM_PHASES
        if last_phase_num is None or phase_num != last_phase_num:
            phase_changes.append({
                'TimestampUTC': current_dt,
                'PhaseName': PHASE_NAMES_ES[phase_num]
            })
            logging.info(f"Inicio de {PHASE_NAMES_ES[phase_num]} a las {current_dt}")
            last_phase_num = phase_num
        current_dt = find_next_phase_change(current_dt, phase_num)

    df = pd.DataFrame(phase_changes)
    output_dir = 'data/lunar_data'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'lunar_phase_changes.csv')
    df.to_csv(output_path, index=False)
    logging.info(f"Cambios de fase guardados en {output_path}")
    return df

def check_lunar_phases():
    """Chequea si lunar_phase_changes.csv existe y coincide con las fechas."""
    phase_path = 'data/lunar_data/lunar_phase_changes.csv'
    if not os.path.exists(phase_path):
        logging.warning(f"No se encontró {phase_path}. Generando fases lunares...")
        return generate_lunar_phase_changes()
    
    df_phases = pd.read_csv(phase_path, parse_dates=['TimestampUTC'])
    min_date = df_phases['TimestampUTC'].min()
    max_date = df_phases['TimestampUTC'].max()
    
    if min_date > start_date or max_date < end_date - timedelta(days=1):
        logging.warning(f"Fechas en {phase_path} no cubren el rango [{START_DATE}, {END_DATE}]. Regenerando...")
        return generate_lunar_phase_changes()
    
    logging.info(f"Usando fases lunares existentes en {phase_path}")
    return df_phases

def combine_financial_data(csv_path, pair):
    """Combina datos financieros M1 con fases lunares y períodos."""
    logging.info(f"Procesando datos financieros para {pair} desde {csv_path}")

    # Leer CSV financiero
    if not os.path.exists(csv_path):
        logging.error(f"Archivo financiero no encontrado: {csv_path}")
        raise FileNotFoundError(f"Archivo financiero no encontrado: {csv_path}")

    try:
        # Intentar leer con header=0 (para CSVs con headers)
        df_financial = pd.read_csv(csv_path, header=0, low_memory=False)
        columns = df_financial.columns.str.lower()
        required_cols = ['date', 'time', 'open', 'high', 'low', 'close', 'volume']
        if all(col in columns for col in required_cols):
            logging.info("CSV detectado con headers ('date', 'time').")
        elif 'timestamp' in df_financial.columns:
            logging.info("CSV detectado con 'timestamp' pre-creado (formato merged).")
            # Parsear timestamp como datetime
            df_financial['timestamp'] = pd.to_datetime(df_financial['timestamp'], errors='coerce')
            df_financial = df_financial.dropna(subset=['timestamp'])  # Drop inválidos
            logging.info(f"Timestamp parseado: {df_financial['timestamp'].dtype} (filas después de parse: {len(df_financial)})")
            # Seleccionar columnas
            df_financial = df_financial[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        else:
            # Fallback a header=None
            logging.warning("Nombres de columnas no coinciden. Intentando sin headers...")
            df_financial = pd.read_csv(csv_path, header=None, names=required_cols, low_memory=False)
            if df_financial.shape[1] != 7:
                logging.error(f"El archivo '{csv_path}' no tiene 7 columnas. Requiere: date, time, open, high, low, close, volume.")
                raise ValueError(f"Formato de CSV inválido: {csv_path}")
    except Exception as e:
        logging.error(f"Error al leer el archivo financiero: {e}")
        raise

    # Convertir OHLC y volume a numérico con coerción
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    initial_len = len(df_financial)
    for col in numeric_cols:
        if col in df_financial.columns:
            df_financial[col] = pd.to_numeric(df_financial[col], errors='coerce')
            nan_count = df_financial[col].isna().sum()
            if nan_count > 0:
                logging.warning(f"Convertidos {nan_count} valores inválidos a NaN en '{col}' (eliminados).")
    df_financial = df_financial.dropna(subset=numeric_cols)
    dropped = initial_len - len(df_financial)
    if dropped > 0:
        logging.info(f"Eliminadas {dropped} filas con valores inválidos en OHLC/volume ({dropped/initial_len*100:.2f}%).")
    if len(df_financial) == 0:
        raise ValueError(f"No hay datos válidos para {pair} después de limpieza.")

    # Validar datos numéricos (después de coerción)
    for col in ['open', 'high', 'low', 'close']:
        if not df_financial[col].notnull().all():
            logging.error(f"Aún hay valores inválidos en '{col}' después de limpieza.")
            raise ValueError(f"Valores inválidos en '{col}' después de coerción.")
        if (df_financial[col] < 0).any():
            logging.error(f"Valores negativos en '{col}'.")
            raise ValueError(f"Valores negativos en '{col}'.")

    # Manejar timestamp (si no fue parseado antes)
    if 'timestamp' not in df_financial.columns or not pd.api.types.is_datetime64_any_dtype(df_financial['timestamp']):
        # Crear desde date + time
        try:
            df_financial['timestamp'] = pd.to_datetime(df_financial['date'] + ' ' + df_financial['time'], format='%Y.%m.%d %H:%M', errors='coerce')
            df_financial = df_financial.dropna(subset=['timestamp'])
            logging.info(f"Timestamp creado desde date+time: {df_financial['timestamp'].dtype} (filas después: {len(df_financial)})")
        except Exception as e:
            logging.error(f"Error al procesar fechas en el CSV financiero: {e}")
            raise
    else:
        # Ya tiene timestamp; asumir UTC si no tiene tz
        if df_financial['timestamp'].dt.tz is None:
            df_financial['timestamp'] = df_financial['timestamp'].dt.tz_localize('UTC')
        logging.info("Usando 'timestamp' pre-creado (asumiendo UTC).")

    # Validar rango de fechas
    min_timestamp = df_financial['timestamp'].min()
    max_timestamp = df_financial['timestamp'].max()
    if min_timestamp > start_date or max_timestamp < end_date - timedelta(days=1):
        logging.warning(f"Fechas en {csv_path} ({min_timestamp} a {max_timestamp}) no cubren completamente [{START_DATE}, {END_DATE}]")

    # Validar calidad de datos
    total_rows = len(df_financial)
    df_financial = df_financial[(df_financial['timestamp'] >= start_date) & (df_financial['timestamp'] <= end_date)]
    filtered_rows = len(df_financial)
    logging.info(f"{pair}: {total_rows} filas totales, {filtered_rows} en rango [{START_DATE}, {END_DATE}]")
    if filtered_rows == 0:
        logging.error(f"No hay datos válidos para {pair} en el rango especificado")
        raise ValueError(f"No hay datos válidos para {pair}")

    # Cargar fases lunares
    df_phases = check_lunar_phases()

    # Asignar fases lunares
    df_financial['lunar_phase'] = None
    for i in range(len(df_phases) - 1):
        start_time = df_phases['TimestampUTC'].iloc[i]
        end_time = df_phases['TimestampUTC'].iloc[i + 1]
        phase = df_phases['PhaseName'].iloc[i]
        mask = (df_financial['timestamp'] >= start_time) & (df_financial['timestamp'] < end_time)
        df_financial.loc[mask, 'lunar_phase'] = phase
    df_financial.loc[df_financial['timestamp'] >= df_phases['TimestampUTC'].iloc[-1], 'lunar_phase'] = df_phases['PhaseName'].iloc[-1]

    # Asignar períodos
    def assign_period(timestamp):
        if timestamp < pre_pandemic_end:
            return 'prepandemia'
        elif timestamp <= pandemic_end:
            return 'pandemia'
        else:
            return 'pospandemia'
    df_financial['period'] = df_financial['timestamp'].apply(assign_period)

    # Seleccionar columnas de salida
    output_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'lunar_phase', 'period']
    df_financial = df_financial[output_cols]

    # Guardar resultado
    output_dir = f'{OUTPUT_DIR}/{pair}'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'combined_data.csv')
    df_financial.to_csv(output_path, index=False)
    logging.info(f"Datos combinados guardados en {output_path}")

    # Guardar calidad de datos
    quality_data = {
        'pair': pair,
        'total_rows': total_rows,
        'filtered_rows': filtered_rows,
        'min_timestamp': min_timestamp,
        'max_timestamp': max_timestamp,
        'coverage': filtered_rows / total_rows if total_rows > 0 else 0,
        'dropped_invalid': dropped
    }
    quality_df = pd.DataFrame([quality_data])
    quality_path = f'{OUTPUT_DIR}/data_quality_summary.csv'
    if os.path.exists(quality_path):
        quality_df.to_csv(quality_path, mode='a', header=False, index=False)
    else:
        quality_df.to_csv(quality_path, index=False)
    logging.info(f"Calidad de datos registrada para {pair}")

    return df_financial

def main(csv_path, pair):
    """Función principal."""
    combine_financial_data(csv_path, pair)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        logging.error("Uso: python process_currency_data.py <csv_path> <pair>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])