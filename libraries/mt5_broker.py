import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
from config.config import config

class MT5Broker:
    """Klasa odpowiedzialna wyłącznie za komunikację z API MT5 (Infrastruktura)."""
    
    def __init__(self, symbol: str = config.SYMBOL):
        self.symbol = symbol

    def connect(self) -> bool:
        if not mt5.initialize():
            print(f"[FATAL] Inicjalizacja MT5 nie powiodła się: {mt5.last_error()}")
            return False
        if not mt5.symbol_select(self.symbol, True):
            print(f"[FATAL] Symbol {self.symbol} niedostępny.")
            return False
        print(f"[SYSTEM] Połączono z MT5. Symbol: {self.symbol}")
        return True

    def get_historical_data(self, timeframe: int, num_candles: int) -> pd.DataFrame:
        """Pobiera dane i formatuje do wektora Pandas dla analizy SMC."""
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, num_candles)
        if rates is None or len(rates) == 0:
            return pd.DataFrame()
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def execute_market_order(self, order_type: int, volume: float, sl_price: float, tp_price: float):
        """Wysyła zlecenie na rynek."""
        tick = mt5.symbol_info_tick(self.symbol)
        if not tick:
            return None

        price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": sl_price,
            "tp": tp_price,
            "deviation": config.DEVIATION,
            "magic": config.MAGIC_NUMBER,
            "comment": "Fibodi_SMC",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        return mt5.order_send(request)