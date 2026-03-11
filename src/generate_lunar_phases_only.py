import swisseph as swe
import pandas as pd
from datetime import datetime, timedelta, timezone
import logging
import os
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/lunar_phases_{}.log'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))),
        logging.StreamHandler()
    ]
)
logging.info("Iniciando generación de fases lunares...")

# Cargar variables de entorno desde .env
load_dotenv()
EPHE_PATH = os.getenv('EPHE_PATH', 'data/lunar_data/swisseph_dll')
DLL_PATH = os.path.abspath(os.getenv('DLL_PATH', 'data/lunar_data/swisseph_dll'))
START_DATE = os.getenv('START_DATE', '2018-01-01')
END_DATE = os.getenv('END_DATE', '2024-12-31')

# Convertir fechas a objetos datetime en UTC
try:
    start_date = datetime.strptime(START_DATE, '%Y-%m-%d').replace(tzinfo=timezone.utc, hour=0, minute=0, second=0, microsecond=0)
    end_date = datetime.strptime(END_DATE, '%Y-%m-%d').replace(tzinfo=timezone.utc, hour=23, minute=59, second=59, microsecond=999999)
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

def main():
    """Función principal."""
    generate_lunar_phase_changes()

if __name__ == "__main__":
    main()