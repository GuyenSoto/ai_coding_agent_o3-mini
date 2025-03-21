# main.py
import asyncio
import pandas as pd
from modules.data_layer import create_exchange, get_historical_data, binance_websocket
from modules.processing_layer import calculate_technical_indicators
from modules.analysis_layer import generate_trading_signals
from modules.decision_layer import decision_integration
from modules.execution_layer import process_trading_signals
from modules.utilities import setup_logging, print_colored, Colors, log_error
from modules.config import TRADING_PAIR, LOG_FILE
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "modules"))

async def main():
    setup_logging(LOG_FILE)
    exchange = create_exchange()
    if exchange is None:
        print_colored("Exchange initialization failed", Colors.RED)
        return
    active_positions = []
    symbol = TRADING_PAIR.replace('/','').lower()
    historical_data = get_historical_data(exchange, TRADING_PAIR, limit=50)
    if not historical_data:
        print_colored("Failed to obtain historical data", Colors.RED)
        return
    print_colored("Historical data loaded", Colors.GREEN)
    async for data in binance_websocket(symbol, historical_data):
        try:
            if data.get('confirmadas', False):
                df = pd.DataFrame(data['ohlcv'], columns=['timestamp','open','high','low','close','volume'])
                df.set_index('timestamp', inplace=True)
                df.index = pd.to_datetime(df.index, unit='ms', utc=True)
                df = calculate_technical_indicators(df)
                if 'MACD' in df.columns:
                    signal_data = generate_trading_signals(df, active_positions)
                    final_signal = decision_integration(signal_data, active_positions, float(data['close']))
                    if final_signal != 0:
                        await process_trading_signals(exchange, final_signal, data, active_positions)
        except Exception as e:
            log_error(e, "Main loop error")
            print_colored(f"Main loop error: {str(e)}", Colors.RED)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
