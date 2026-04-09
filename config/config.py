from dataclasses import dataclass

@dataclass(frozen=True)
class TradingConfig:
    # --- ŚCIEŻKA DO TERMINALA MT5 ---
    MT5_PATH: str = r"C:\Program Files\MetaTrader 5 fibodi\terminal64.exe"
    
    # --- GŁÓWNE PARAMETRY ---
    SYMBOL: str = "XAUUSDs"
    TIMEFRAME: int = 15  # M15
    MAGIC_NUMBER: int = 777777
    DEVIATION: int = 20
    VOLUME: float = 0.1
    
    # --- Parametry strategii Fibodi + SMC ---
    FIBO_LEVEL: float = 0.786
    TP1_LEVEL: float = 0.500
    OB_LOOKBACK: int = 50  # Zasięg szukania Order Blocków
    
    # --- Parametry Impulse MACD ---
    IMACD_FLAT_VARIANCE_THRESHOLD: float = 0.0001
    IMACD_OS_LEVEL: float = -0.005
    IMACD_OB_LEVEL: float = 0.005
    
config = TradingConfig()