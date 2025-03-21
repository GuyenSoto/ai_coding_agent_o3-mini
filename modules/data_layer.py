# data_layer.py
import ccxt
import time
import requests
import os
import json
import asyncio
import websockets
from datetime import datetime
import pandas as pd
import pytz
from typing import Optional, Dict, Any, Generator
#from config import API_KEY, API_SECRET, TRADING_PAIR, TIMEFRAME
from .config import API_KEY, API_SECRET, TRADING_PAIR, TIMEFRAME
#from utilities import print_colored, Colors, log_error
from .utilities import print_colored, Colors, log_error


def get_server_time_offset() -> int:
    """
    Obtiene la diferencia entre el tiempo del servidor de Binance y el local.
    Retorna un offset en milisegundos o un valor conservador en caso de error.
    """
    try:
        response = requests.get('https://api.binance.us/api/v3/time')
        server_time = response.json()['serverTime']
        local_time = int(time.time() * 1000)
        return server_time - local_time
    except Exception as e:
        print_colored(f"Error obtaining server time: {str(e)}", Colors.YELLOW)
        return -2000

def create_exchange() -> Optional[ccxt.binanceus]:
    """
    Inicializa la conexión al exchange usando ccxt y las credenciales.
    """
    try:
        print_colored("\n=== INITIALIZING EXCHANGE ===", Colors.BLUE)
        if not os.path.exists("keys.env"):
            print_colored("keys.env not found", Colors.RED)
            return None
        if not API_KEY or not API_SECRET:
            print_colored("API credentials not found", Colors.RED)
            return None
        time_offset = get_server_time_offset()
        print_colored(f"Time offset (ms): {time_offset}", Colors.BLUE)
        exchange = ccxt.binanceus({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'timeout': 30000,
            'enableRateLimit': True,
            'options': {
                'recvWindow': 5000,
                'defaultType': 'spot',
                'adjustForTimeDifference': True
            },
            'nonce': lambda: int(time.time() * 1000) + time_offset - 500
        })
        exchange.load_markets()
        print_colored("Exchange connection successful", Colors.GREEN)
        return exchange
    except Exception as e:
        print_colored(f"Exchange error: {str(e)}", Colors.RED)
        log_error(e, "Exchange Connection Error")
        return None

def get_historical_data(exchange: ccxt.Exchange, symbol: str, timeframe: str = None, limit: int = 50) -> Optional[Dict[str, Any]]:
    """
    Solicita datos históricos (OHLCV) y los procesa.
    """
    if timeframe is None:
        timeframe = f'{int(TIMEFRAME/60)}m'
    try:
        print_colored("\n=== LOADING HISTORICAL DATA ===", Colors.BLUE)
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if not ohlcv:
            print_colored("No data received", Colors.RED)
            return None
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        et_tz = pytz.timezone('America/New_York')
        df['datetime_et'] = df['datetime'].dt.tz_convert(et_tz)
        now = datetime.now(et_tz)
        df = df[df['datetime_et'] <= now]
        return {
            'timestamp': df['timestamp'].iloc[-1],
            'close': df['close'].iloc[-1],
            'high': df['high'].iloc[-1],
            'low': df['low'].iloc[-1],
            'volume': df['volume'].iloc[-1],
            'ohlcv': df[['timestamp','open','high','low','close','volume']].values.tolist()
        }
    except Exception as e:
        print_colored(f"Error processing historical data: {str(e)}", Colors.RED)
        log_error(e, "Historical Data Error")
        return None

async def binance_websocket(symbol: str, historical_data: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Conecta al WebSocket de Binance para recibir velas y las emite.
    """
    timeframe_minutes = int(TIMEFRAME / 60)
    url = f"wss://stream.binance.us:9443/ws/{symbol.lower()}@kline_{timeframe_minutes}m"
    reconnect_delay = 5
    # Copiamos las velas históricas
    velas_confirmadas = historical_data['ohlcv'].copy()
    et_tz = pytz.timezone('America/New_York')
    last_processed_timestamp = None
    while True:
        try:
            print_colored(f"Connecting to WebSocket: {url}", Colors.BLUE)
            async with websockets.connect(url) as ws:
                print_colored("WebSocket connected", Colors.GREEN)
                data = {
                    'timestamp': historical_data['timestamp'],
                    'ohlcv': velas_confirmadas,
                    'close': historical_data['close'],
                    'high': historical_data['high'],
                    'low': historical_data['low'],
                    'volume': historical_data['volume'],
                    'confirmadas': True
                }
                last_processed_timestamp = data['timestamp']
                yield data
                while True:
                    try:
                        msg = await ws.recv()
                        parsed = json.loads(msg)
                        if 'k' not in parsed:
                            continue
                        kline = parsed['k']
                        if not kline.get('x', False):  # Procesar solo velas confirmadas
                            continue
                        new_timestamp = int(kline['t'])
                        if last_processed_timestamp is None or new_timestamp > last_processed_timestamp:
                            new_candle = [
                                new_timestamp,
                                float(kline['o']),
                                float(kline['h']),
                                float(kline['l']),
                                float(kline['c']),
                                float(kline['v'])
                            ]
                            if len(velas_confirmadas) >= 50:
                                velas_confirmadas.pop(0)
                            velas_confirmadas.append(new_candle)
                            data = {
                                'timestamp': new_timestamp,
                                'ohlcv': velas_confirmadas,
                                'close': float(kline['c']),
                                'high': float(kline['h']),
                                'low': float(kline['l']),
                                'volume': float(kline['v']),
                                'confirmadas': True
                            }
                            last_processed_timestamp = new_timestamp
                            yield data
                    except Exception as e:
                        print_colored(f"WebSocket message error: {str(e)}", Colors.RED)
                        continue
        except Exception as e:
            log_error(e, "WebSocket Error")
            print_colored(f"Reconnecting in {reconnect_delay} seconds...", Colors.YELLOW)
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 60)
# Al final de data_layer.py (y de los demás módulos)
def run_module():
    return "Data Layer ejecutado (dummy)"
