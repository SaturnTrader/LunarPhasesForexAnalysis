import subprocess
import logging
import os
import sys
from datetime import datetime

# 1. Configurar el sistema de logging maestro
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_dir, f"MASTER_PIPELINE_{timestamp}.log")

# Configurar el formato del log para consola y archivo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 2. Definir el orden estricto de ejecución
# Ajusta "src/" si tus archivos están en la raíz u otra carpeta
pipeline_scripts = [
    # Fase 1: Datos Base y Calendario Astronómico (Automatizado por lista .env)
    "src/merge_histdata_csvs.py",
    "src/generate_lunar_phases_only.py",
    
    # Fase 2, 3 y 4: Etiquetado, Análisis Estadístico y Resumen (Orquestador principal)
    "src/process_all_currencies.py",
    
    # Fase 5 y 6: Consolidación Macro y Reporte Final
    "src/summarize_across_pairs.py",
    # "src/merge_all_pairs.py", # Comentado si no es necesario por defecto o falla
    "src/generate_internal_md.py"
]

def run_pipeline():
    logging.info("==================================================")
    logging.info("INICIANDO EJECUCIÓN MAESTRA DEL PIPELINE (ALPHA EXÓGENO)")
    logging.info("==================================================")

    for script in pipeline_scripts:
        # Verificar que el script exista antes de intentar ejecutarlo
        if not os.path.exists(script):
            # Intentar buscar en el directorio actual si no usa la carpeta 'src/'
            alt_script = os.path.basename(script)
            if os.path.exists(alt_script):
                script = alt_script
            else:
                logging.error(f"FATAL: No se encuentra el script '{script}'. Verifica la ruta.")
                return False

        logging.info(f"--- [ EJECUTANDO ] {script} ---")
        
        try:
            # Ejecutar el subproceso usando el Python del entorno virtual activo
            result = subprocess.run(
                [sys.executable, script],
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'  # Previene cuelgues por caracteres especiales en Windows
            )
            
            if result.stdout:
                for line in result.stdout.strip().split('\\n'):
                    logging.info(f"[{script}] {line}")
            
            logging.info(f"[ ÉXITO ] {script} finalizó correctamente.")
            
        except subprocess.CalledProcessError as e:
            logging.error("==================================================")
            logging.error(f"¡FALLO CRÍTICO DETECTADO EN: {script}!")
            logging.error("==================================================")
            if e.stdout:
                logging.error("--- SALIDA ESTÁNDAR (STDOUT) ---")
                for line in e.stdout.strip().split('\\n'):
                    logging.error(line)
            logging.error("--- DETALLE DEL ERROR (TRACEBACK / STDERR) ---")
            if e.stderr:
                for line in e.stderr.strip().split('\\n'):
                    logging.error(line)
            else:
                logging.error("Sin salida de error capturada.")
            logging.error("==================================================")
            logging.error("EJECUCIÓN INTERRUMPIDA: Por favor, corrige este script antes de continuar.")
            return False

    logging.info("==================================================")
    logging.info("PIPELINE COMPLETADO CON ÉXITO. DATOS LISTOS PARA PUBLICACIÓN.")
    logging.info("==================================================")
    return True

if __name__ == "__main__":
    run_pipeline()