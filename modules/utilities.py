# utilities.py
import logging
from datetime import datetime
import time

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(message: str, color: str) -> None:
    """Imprime el mensaje en color en la consola."""
    print(f"{color}{message}{Colors.END}")

def setup_logging(log_file: str) -> None:
    """Configura el logging para archivo y consola."""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)

def log_trade(action: str, price: float, amount: float, profit: float = None) -> None:
    msg = f"{action}: {amount:.8f} @ {price:.8f}"
    if profit:
        msg += f" | Profit: {profit:.2f}%"
    logging.info(msg)

def log_signal(signal_type: str, conditions: dict) -> None:
    logging.info(f"Señal: {signal_type} | Condiciones: {conditions}")

def log_error(error: Exception, context: str = "") -> None:
    logging.error(f"{context}: {str(error)}")