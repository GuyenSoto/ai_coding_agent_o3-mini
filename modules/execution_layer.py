# execution_layer.py
import asyncio
from .utilities import print_colored, Colors, log_error
from .config import TRADING_PAIR, BASE_ORDER_SIZE, ORDER_MULTIPLIER, MIN_NOTIONAL, MAX_RETRIES, MIN_ORDER_SIZE

def round_to_precision(value: float, precision: int = 8) -> float:
    """Redondea un valor a la precisión indicada."""
    return round(value, precision)

async def execute_order_with_retries(exchange, order_type: str, params: dict):
    """
    Ejecuta una orden (compra o venta) con reintentos.
    """
    attempt = 0
    last_error = None
    while attempt < MAX_RETRIES:
        attempt += 1
        try:
            if order_type == 'buy':
                ticker = exchange.fetch_ticker(params['symbol'])
                current_price = ticker['last']
                base_amount = params['quote_amount'] / current_price
                base_amount = round_to_precision(max(base_amount, MIN_ORDER_SIZE))
                limit_price = round_to_precision(current_price * 0.9999, 2)
                print_colored(f"Placing limit buy order at {limit_price}", Colors.YELLOW)
                order = exchange.create_limit_buy_order(
                    symbol=params['symbol'],
                    amount=base_amount,
                    price=limit_price
                )
                await asyncio.sleep(1)
                return order
            else:
                ticker = exchange.fetch_ticker(params['symbol'])
                current_price = ticker['last']
                amount = round_to_precision(float(params['amount']))
                limit_price = round_to_precision(current_price * 1.0001, 2)
                print_colored(f"Placing limit sell order at {limit_price}", Colors.YELLOW)
                order = exchange.create_limit_sell_order(
                    symbol=params['symbol'],
                    amount=amount,
                    price=limit_price
                )
                await asyncio.sleep(1)
                return order
        except Exception as e:
            last_error = e
            print_colored(f"Order attempt {attempt} failed: {str(e)}", Colors.RED)
            await asyncio.sleep(1)
    raise Exception(f"Order failed after {MAX_RETRIES} attempts: {last_error}")

async def process_trading_signals(exchange, signal: int, data: dict, active_positions: list):
    """
    Según la señal final decide ejecutar una compra (incluyendo DCA) o venta.
    """
    if signal == 0:
        return
    try:
        base_currency, quote_currency = TRADING_PAIR.split('/')
        current_price = float(data['close'])
        if signal == 1:  # Señal de compra
            if len(active_positions) >= 4:
                print_colored("Max DCA orders reached", Colors.YELLOW)
                return
            if active_positions:
                last_entry = active_positions[-1]['entry_price']
                price_drop = (last_entry - current_price) / last_entry
                if price_drop < PRICE_DEVIATION:
                    print_colored("Price drop not enough for additional DCA", Colors.YELLOW)
                    return
            quote_amount = BASE_ORDER_SIZE * (ORDER_MULTIPLIER ** len(active_positions))
            if quote_amount < MIN_NOTIONAL:
                print_colored("Insufficient order amount", Colors.RED)
                return
            base_amount = round_to_precision(quote_amount / current_price)
            print_colored("Executing BUY order", Colors.GREEN)
            order = await execute_order_with_retries(exchange, 'buy', {'symbol': TRADING_PAIR, 'quote_amount': quote_amount})
            active_positions.append({
                'entry_price': current_price,
                'base_amount': base_amount,
                'quote_amount': quote_amount
            })
        elif signal == -1 and active_positions:  # Señal de venta
            print_colored("Executing SELL order", Colors.GREEN)
            total_base = sum(pos['base_amount'] for pos in active_positions)
            order = await execute_order_with_retries(exchange, 'sell', {'symbol': TRADING_PAIR, 'amount': total_base})
            active_positions.clear()
    except Exception as e:
        log_error(e, "Trade execution error")
        print_colored(f"Trade execution error: {str(e)}", Colors.RED)

# Al final de data_layer.py (y de los demás módulos)
def run_module():
    return "Data Execution Layer ejecutado (dummy)"
