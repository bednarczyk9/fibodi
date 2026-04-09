from libraries.mt5_broker import MT5Broker
from libraries.strategy_engine import FibodiSMCEngine
import MetaTrader5 as mt5
from config.config import config

class TradingFlow:
    def __init__(self):
        self.broker = MT5Broker()
        self.strategy = FibodiSMCEngine()
        
def run_market_scan(self):
        """Główny przepływ: Pobranie danych -> Analiza -> Egzekucja"""
        if not self.broker.connect():
            return
            
        df = self.broker.get_historical_data(mt5.TIMEFRAME_M15, 100)
        if df.empty:
            return
            
        # Sprawdzamy oba kierunki
        long_setup = self.strategy.evaluate_long_setup(df)
        short_setup = self.strategy.evaluate_short_setup(df)
        
        if long_setup and long_setup['action'] == "BUY":
            print(f"[ACTION] Wykryto setup LONG (SMC+Fibo)! SL: {long_setup['sl']}, TP1: {long_setup['tp1']}")
            self.broker.execute_market_order(
                order_type=mt5.ORDER_TYPE_BUY,
                volume=config.VOLUME,
                sl_price=long_setup['sl'],
                tp_price=long_setup['tp1']
            )
            
        elif short_setup and short_setup['action'] == "SELL":
            print(f"[ACTION] Wykryto setup SHORT (SMC+Fibo)! SL: {short_setup['sl']}, TP1: {short_setup['tp1']}")
            self.broker.execute_market_order(
                order_type=mt5.ORDER_TYPE_SELL,
                volume=config.VOLUME,
                sl_price=short_setup['sl'],
                tp_price=short_setup['tp1']
            )