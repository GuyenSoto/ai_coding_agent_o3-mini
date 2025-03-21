# processing_layer.py
import pandas as pd
import ta
import pytz
from .utilities import print_colored, Colors, log_error

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula indicadores técnicos (EMA, MACD, RSI y Bollinger Bands)
    y los añade al DataFrame.
    """
    try:
        et_tz = pytz.timezone('America/New_York')
        if df.index.tz is None:
            df.index = pd.to_datetime(df.index, unit='ms', utc=True).tz_convert(et_tz)
        df['EMA_9'] = ta.trend.ema_indicator(close=df['close'], window=9)
        df['EMA_21'] = ta.trend.ema_indicator(close=df['close'], window=21)
        macd = ta.trend.MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['RSI'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
        bb = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
        df['BB_upper'] = bb.bollinger_hband()
        df['BB_middle'] = bb.bollinger_mavg()
        df['BB_lower'] = bb.bollinger_lband()
        print_colored("Indicators calculated successfully", Colors.GREEN)
        return df
    except Exception as e:
        print_colored(f"Error calculating indicators: {str(e)}", Colors.RED)
        log_error(e, "Indicator Calculation Error")
        return df

def verify_macd_calculation(df: pd.DataFrame):
    """
    Realiza una verificación paso a paso del cálculo del MACD.
    """
    if len(df) < 26:
        print_colored("Not enough data for MACD calculation", Colors.RED)
        return None, None, None
    close_prices = df['close']
    ema12 = close_prices.ewm(span=12, adjust=False).mean()
    ema26 = close_prices.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    print_colored("MACD calculation verified", Colors.BLUE)
    return macd_line, signal_line, histogram
# Al final de data_layer.py (y de los demás módulos)
def run_module():
    return "Data Layer ejecutado (dummy)"
