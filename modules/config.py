# config.py
import os
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno (asegúrate de tener un archivo keys.env con tus credenciales)
load_dotenv("keys.env")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# Parámetros de trading y configuraciones globales
TIMEFRAME = 300  # 5 minutos
PRICE_DEVIATION = 0.02  # 2%
TAKE_PROFIT = 0.055  # 5.5%
STOP_LOSS = 0.25  # 25%
BASE_ORDER_SIZE = 10  # Monto base
ORDER_MULTIPLIER = 2.6  # Multiplicador para DCA
MAX_DCA_ORDERS = 4
TRADING_PAIR = "ETH/USDT"
COMMISSION = 0.001
MIN_NOTIONAL = 10
MAX_RETRIES = 3
MIN_ORDER_SIZE = 0.00001

# Para creación de archivos de log
LOG_FILE = f'trading_bot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

def run_module():
    # Retorna el contenido del archivo para ver qué hay en él
    with open(__file__, "r", encoding="utf-8") as f:
        return f.read()
