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
            
        # Pobieramy ostatnie 100 świec z zadanego interwału
        df = self.broker.get_historical_data(mt5.TIMEFRAME_M15, 100)
        if df.empty:
            return
            
        signal = self.strategy.evaluate_long_setup(df)
        
        if signal and signal['action'] == "BUY":
            print(f"[ACTION] Wykryto setup SMC+Fibodi! Egzekucja LONG. SL: {signal['sl']}, TP: {signal['tp']}")
            self.broker.execute_market_order(
                order_type=mt5.ORDER_TYPE_BUY,
                volume=config.VOLUME,
                sl_price=signal['sl'],
                tp_price=signal['tp']
            )