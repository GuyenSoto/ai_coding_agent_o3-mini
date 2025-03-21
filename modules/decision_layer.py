from .utilities import print_colored, Colors
from .config import TAKE_PROFIT, PRICE_DEVIATION
# decision_layer.py
def decision_integration(signal_data: dict, active_positions: list, current_price: float) -> int:
    """
    Integra los resultados de la capa de análisis y determina la acción final:
    1 para compra, -1 para venta o 0 para mantener.
    """
    final_signal = 0
    if not active_positions and signal_data['signal'] == 1:
        final_signal = 1
    elif active_positions and signal_data['signal'] == -1:
        final_signal = -1
    print_colored(f"Final decision signal: {final_signal}", Colors.BLUE)
    return final_signal
# Al final de data_layer.py (y de los demás módulos)
def run_module():
    return "Data Layer ejecutado (dummy)"
