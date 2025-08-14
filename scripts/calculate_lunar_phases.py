import swisseph as swe
import pandas as pd
from datetime import datetime, timedelta, timezone
import logging
import os
from dotenv import load_dotenv
import pytz

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Iniciando script de cálculo de fases lunares...")

# Cargar variables de entorno desde .env
load_dotenv()
EPHE_PATH = os.getenv('EPHE_PATH', 'data/lunar_data/swisseph_dll')
DLL_PATH = os.path.abspath(os.getenv('DLL_PATH', 'data/lunar_data/swisseph_dll')) # Modificado por Cline
START_DATE = os.getenv('START_DATE', '2018-01-01')
END_DATE = os.getenv('END_DATE', '2024-12-31')
FINANCIAL_DATA_TIMEZONE = os.getenv('FINANCIAL_DATA_TIMEZONE', 'UTC')
PRE_PANDEMIC_END = os.getenv('PRE_PANDEMIC_END', '2020-03-01')
PANDEMIC_END = os.getenv('PANDEMIC_END', '2021-12-31')
FINANCIAL_CSV = os.getenv('FINANCIAL_CSV', 'eur_usd_m1.csv')
FINANCIAL_DATA_PATH = os.getenv('FINANCIAL_DATA_PATH', 'data/financial_data')

# Convertir fechas a objetos datetime en UTC
try:
    start_date = datetime.strptime(START_DATE, '%Y-%m-%d').replace(tzinfo=timezone.utc, hour=0, minute=0, second=0, microsecond=0)
    end_date = datetime.strptime(END_DATE, '%Y-%m-%d').replace(tzinfo=timezone.utc, hour=0, minute=0, second=0, microsecond=0)
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
ANGLE_PER_PHASE = 360.0 / NUM_PHASES  # 45° por fase
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

def combine_financial_data():
    """Combina datos financieros M1 con fases lunares y períodos."""
    logging.info(f"Combinando datos financieros desde {FINANCIAL_CSV}")

    # Cargar variables de entorno desde .env
    load_dotenv()
    
    # Leer CSV financiero
    financial_path = os.path.join(FINANCIAL_DATA_PATH, FINANCIAL_CSV)
    if not os.path.exists(financial_path):
        logging.error(f"Archivo financiero no encontrado: {financial_path}")
        raise FileNotFoundError(f"Archivo financiero no encontrado: {financial_path}")

    # Intentar leer con nombres de columnas
    try:
        df_financial = pd.read_csv(financial_path, header=0)
        columns = df_financial.columns.str.lower()
        required_cols = ['date', 'time', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in columns for col in required_cols):
            logging.warning("Nombres de columnas no coinciden. Intentando sin nombres...")
            df_financial = pd.read_csv(financial_path, header=None, names=required_cols)
            if df_financial.shape[1] != 7:
                logging.error(f"El archivo '{FINANCIAL_CSV}' no tiene nombres de columnas en la primera fila o no tiene exactamente 7 columnas. Por favor, añada una fila con los nombres: date, time, open, high, low, close, volume.")
                raise ValueError(f"Formato de CSV inválido: {FINANCIAL_CSV}")
    except Exception as e:
        logging.error(f"Error al leer el archivo financiero: {e}")
        raise

    # Validar datos financieros
    for col in ['open', 'high', 'low', 'close']:
        if not pd.to_numeric(df_financial[col], errors='coerce').notnull().all():
            logging.error(f"Valores inválidos en '{col}'. Asegúrese de que sean números no negativos.")
            raise ValueError(f"Valores inválidos en '{col}'")
    if df_financial[['date', 'time']].isnull().any().any():
        logging.error("Datos faltantes en 'date' o 'time'.")
        raise ValueError("Datos faltantes en 'date' o 'time'")

    # Convertir date y time a timestamp en UTC
    try:
        df_financial['timestamp'] = pd.to_datetime(df_financial['date'] + ' ' + df_financial['time'], format='%Y.%m.%d %H:%M')
        timezone = pytz.timezone(FINANCIAL_DATA_TIMEZONE) if FINANCIAL_DATA_TIMEZONE else pytz.UTC
        if not FINANCIAL_DATA_TIMEZONE:
            logging.warning("No se especificó FINANCIAL_DATA_TIMEZONE en .env. Asumiendo UTC para los datos financieros.")
        df_financial['timestamp'] = df_financial['timestamp'].dt.tz_localize(timezone).dt.tz_convert(pytz.UTC)
    except Exception as e:
        logging.error(f"Error al procesar fechas en el CSV financiero: {e}")
        raise

    # Validar rango de fechas
    logging.info(f"start_date: {start_date}, end_date: {end_date}")
    logging.info(f"df_financial['timestamp'].min(): {df_financial['timestamp'].min()}, df_financial['timestamp'].max(): {df_financial['timestamp'].max()}")
    min_timestamp = df_financial['timestamp'].min().replace(hour=0, minute=0, second=0, microsecond=0)
    max_timestamp = df_financial['timestamp'].max().replace(hour=0, minute=0, second=0, microsecond=0)
    if min_timestamp < start_date or max_timestamp > end_date:
        logging.error(f"Las fechas del CSV financiero están fuera del rango [{START_DATE}, {END_DATE}].")
        raise ValueError("Rango de fechas inválido")

    # Leer cambios de fase
    df_phases = generate_lunar_phase_changes()

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
            return 'pre-pandemia'
        elif timestamp <= pandemic_end:
            return 'pandemia'
        else:
            return 'pos-pandemia'
    df_financial['period'] = df_financial['timestamp'].apply(assign_period)

    # Seleccionar columnas de salida
    output_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'lunar_phase', 'period']
    df_financial = df_financial[output_cols]

    # Guardar resultado
    output_dir = 'data/processed'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'combined_data.csv')
    df_financial.to_csv(output_path, index=False)
    logging.info(f"Datos combinados guardados en {output_path}")

def main():
    """Función principal."""
    combine_financial_data()

if __name__ == "__main__":
    main()
