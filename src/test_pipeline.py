import pandas as pd
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import sys
import io

# Importa módulos del proyecto (ajusta path si es necesario)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.merge_histdata_csvs import merge_csvs
from src.process_currency_data import combine_financial_data
from src.analyze_lunar_phases import main as analyze_main
from src.summarize_results_for_analysis import main as summarize_main

class TestPipeline(unittest.TestCase):
    def setUp(self):
        # Crea dir temp para tests
        self.temp_dir = tempfile.mkdtemp()
        self.sample_pair = 'EURUSD'
        self.raw_dir = os.path.join(self.temp_dir, 'raw')
        self.output_dir = os.path.join(self.temp_dir, 'financial_data')
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Crea mini-CSV sample (1 mes fake, formato histdata MT)
        sample_data = [
            ['2018.01.01', '00:00', 1.2000, 1.2005, 1.1995, 1.2002, 1000],
            ['2018.01.01', '00:01', 1.2002, 1.2007, 1.2001, 1.2005, 1200],
            # ... más filas para simular
        ] * 100  # 200 filas
        sample_df = pd.DataFrame(sample_data, columns=['date', 'time', 'open', 'high', 'low', 'close', 'volume'])
        sample_path = os.path.join(self.raw_dir, 'DAT_MT_EURUSD_M1_2018.csv')
        sample_df.to_csv(sample_path, index=False, header=False)
        
        # Configurar environment variables
        os.environ['HISTDATA_RAW_PATH'] = self.raw_dir
        os.environ['FINANCIAL_DATA_PATH'] = self.output_dir
        os.environ['OUTPUT_DIR'] = os.path.join(self.temp_dir, 'output')
        os.environ['START_DATE'] = '2018-01-01'
        os.environ['END_DATE'] = '2018-01-31'
        os.environ['FINANCIAL_DATA_TIMEZONE'] = 'EST'
        
        # Sobreescribir constantes de módulo evaluadas antes del setup
        import src.process_currency_data
        src.process_currency_data.OUTPUT_DIR = os.environ['OUTPUT_DIR']
        import src.analyze_lunar_phases
        src.analyze_lunar_phases.OUTPUT_DIR = os.environ['OUTPUT_DIR']
        import src.summarize_results_for_analysis
        src.summarize_results_for_analysis.OUTPUT_DIR = os.environ['OUTPUT_DIR']

    def tearDown(self):
        # Limpia temp dir
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_merge_csvs(self):
        """Test merge de sample CSV."""
        output_path = merge_csvs(self.sample_pair, self.raw_dir, self.output_dir)
        self.assertTrue(os.path.exists(output_path))
        df = pd.read_csv(output_path, parse_dates=['timestamp'])
        self.assertGreater(len(df), 0)
        self.assertIn('timestamp', df.columns)
        self.assertEqual(df['timestamp'].min().year, 2018)
        print(f"Merge test OK: {len(df)} filas merged")

    @patch('src.process_currency_data.combine_financial_data')
    def test_combine_financial_data(self, mock_combine):
        """Test combine (mock para evitar Swiss Ephemeris)."""
        mock_combine.return_value = pd.DataFrame({'timestamp': pd.date_range('2018-01-01', periods=100)})
        # Simula llamada
        csv_path = os.path.join(self.output_dir, f"{self.sample_pair.lower()}_m1.csv")
        combine_financial_data(csv_path, self.sample_pair)
        mock_combine.assert_called_once()
        print("Combine test OK: Llamada simulada exitosa")

    def test_analyze_lunar_phases(self):
        """Test analyze (requiere combined_data.csv; usa sample)."""
        # Primero merge
        merge_csvs(self.sample_pair, self.raw_dir, self.output_dir)
        csv_path = os.path.join(self.output_dir, f"{self.sample_pair.lower()}_m1.csv")
        
        # Mock check_lunar_phases para evitar calc real y loop infinito
        with patch('src.process_currency_data.check_lunar_phases') as mock_phases:
            mock_phases.return_value = pd.DataFrame({
                'TimestampUTC': pd.date_range('2018-01-01', periods=10, freq='4D', tz='UTC'),
                'PhaseName': ['Luna Nueva', 'Cuarto Creciente', 'Luna Llena', 'Cuarto Menguante'] * 2 + ['Luna Nueva', 'Cuarto Creciente']
            })
            combine_financial_data(csv_path, self.sample_pair)
        
        # Test analyze
        analyze_main(self.sample_pair)
        stats_path = os.path.join(self.temp_dir, 'output', self.sample_pair, 'statistics_by_phase_period.csv')
        self.assertTrue(os.path.exists(stats_path))
        stats_df = pd.read_csv(stats_path)
        # Valida 6 decimales
        num_cols = ['mean_return', 'median_return', 'std_return', 'return_p25', 'return_p75', 'mean_volatility']
        for col in num_cols:
            if col in stats_df.columns:
                self.assertTrue((stats_df[col].round(6) == stats_df[col]).all())
        print(f"Analyze test OK: {len(stats_df)} stats generadas con 6 decimales")

    def test_summarize_results(self):
        """Test summarize (requiere analyze)."""
        # Run analyze primero
        self.test_analyze_lunar_phases()
        summarize_main(self.sample_pair)
        md_path = os.path.join(self.temp_dir, 'output', self.sample_pair, 'results_summary_for_analysis.md')
        self.assertTrue(os.path.exists(md_path))
        with open(md_path, 'r') as f:
            content = f.read()
            self.assertIn('Prepandemia', content)  # Valida labels
        print("Summarize test OK: MD generado con labels correctos")

if __name__ == '__main__':
    unittest.main(verbosity=2)