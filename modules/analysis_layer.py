# analysis_layer.py
import pandas as pd
#from utilities import print_colored, Colors
from .utilities import print_colored, Colors, log_error
from .config import TAKE_PROFIT, PRICE_DEVIATION

def generate_trading_signals(df: pd.DataFrame, active_positions: list) -> dict:
    """
    Evalúa indicadores técnicos para generar señales de compra (1) o venta (-1).
    """
    try:
        if df.empty or len(df) < 26:
            print_colored("Insufficient data for signals", Colors.RED)
            return {'signal': 0, 'conditions': {}}
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['close']
        signals['signal'] = 0.0

        # Condiciones para compra
        macd_bullish = (df['MACD'] > df['MACD_signal'])
        ema_trend = (df['close'] > df['EMA_9'] * 0.995)
        rsi_conditions = (df['RSI'] < 55)
        bb_conditions = (df['close'] < df['BB_middle'])

        # Condiciones para venta
        macd_bearish = (df['MACD'] < df['MACD_signal'])
        ema_downtrend = (df['close'] < df['EMA_9'] * 1.005)

        # Asignamos señales
        signals.loc[macd_bullish & ema_trend & rsi_conditions & bb_conditions, 'signal'] = 1.0
        signals.loc[macd_bearish & ema_downtrend, 'signal'] = -1.0

        current = signals.iloc[-1]
        conditions = {
            'MACD > Signal': bool(macd_bullish.iloc[-1]),
            'EMA Trend': bool(ema_trend.iloc[-1]),
            'RSI < 55': bool(rsi_conditions.iloc[-1]),
            'BB Condition': bool(bb_conditions.iloc[-1])
        }

        final_signal = 0
        if not active_positions and current['signal'] == 1.0:
            final_signal = 1
            print_colored("Buy signal detected", Colors.GREEN)
        elif active_positions and current['signal'] == -1.0:
            final_signal = -1
            print_colored("Sell signal detected", Colors.RED)

        return {
            'signal': final_signal,
            'conditions': conditions,
            'price': current['price'],
            'signals_data': {
                'buy_signals': (signals['signal'] == 1.0).sum(),
                'sell_signals': (signals['signal'] == -1.0).sum()
            }
        }
    except Exception as e:
        print_colored(f"Error generating signals: {str(e)}", Colors.RED)
        return {'signal': 0, 'conditions': {}}
# Al final de data_layer.py (y de los demás módulos)
def run_module():
    return "Data Layer ejecutado (dummy)"
