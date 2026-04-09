import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from config.config import config

class FibodiSMCEngine:
    """Warstwa domenowa obliczająca setupy SMC + Fibodi + Impulse MACD."""
    
    def __init__(self):
        self.pivot_window = 5 # Ilość świec po lewej i prawej do detekcji swingu

    @staticmethod
    def calculate_impulse_macd(df: pd.DataFrame) -> pd.DataFrame:
        """Wektoryzowane obliczanie Impulse MACD (LazyBear logic)."""
        df['ema_fast'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=26, adjust=False).mean()
        df['imacd'] = df['ema_fast'] - df['ema_slow']
        df['signal'] = df['imacd'].ewm(span=9, adjust=False).mean()
        df['imacd_hist'] = df['imacd'] - df['signal']
        return df

    def _find_pivots(self, df: pd.DataFrame) -> pd.DataFrame:
        """Wykrywa lokalne ekstrema (Swing High / Swing Low) przy użyciu SciPy."""
        # argrelextrema zwraca indeksy dla których warunek jest spełniony
        local_max = argrelextrema(df['high'].values, np.greater, order=self.pivot_window)[0]
        local_min = argrelextrema(df['low'].values, np.less, order=self.pivot_window)[0]
        
        df['is_pivot_high'] = False
        df['is_pivot_low'] = False
        
        df.loc[df.index[local_max], 'is_pivot_high'] = True
        df.loc[df.index[local_min], 'is_pivot_low'] = True
        
        return df

    def _find_bullish_order_block(self, df: pd.DataFrame, start_idx: int, end_idx: int):
        """Szuka ostatniej świecy spadkowej przed impulsem wzrostowym (Byczy OB)."""
        # Wycinamy fragment przedziału od Pivot Low (lub nieco przed) do Pivot High
        search_area = df.iloc[max(0, start_idx - 10) : end_idx]
        
        # Filtrujemy tylko świece spadkowe (Close < Open)
        bearish_candles = search_area[search_area['close'] < search_area['open']]
        
        if bearish_candles.empty:
            return None
            
        # Ostatnia spadkowa świeca przed silnym ruchem to nasz OB
        ob_candle = bearish_candles.iloc[-1]
        
        return {
            'top': ob_candle['high'],
            'bottom': ob_candle['low'],
            'index': ob_candle.name
        }

    def evaluate_long_setup(self, df: pd.DataFrame) -> dict | None:
        """
        Główna maszyna stanu dla Long (Kupno).
        Zwraca parametry egzekucji (SL, TP), jeśli konfluencja jest pełna.
        """
        if len(df) < 50:
            return None

        # 1. Obliczenie wskaźników i pivotów
        df = self.calculate_impulse_macd(df)
        df = self._find_pivots(df)
        
        # 2. Filtr płaskiego rynku (Bramka zmienności)
        recent_variance = df['imacd_hist'].tail(15).var()
        if recent_variance < config.IMACD_FLAT_VARIANCE_THRESHOLD:
            return None # Rynek w konsolidacji - blokada

        # 3. Analiza Ostatniego Impulsu (Szukamy sekwencji: Pivot Low -> Pivot High)
        pivot_lows = df[df['is_pivot_low']]
        pivot_highs = df[df['is_pivot_high']]
        
        if pivot_lows.empty or pivot_highs.empty:
            return None
            
        last_low_idx = pivot_lows.index[-1]
        last_high_idx = pivot_highs.index[-1]
        
        # Upewniamy się, że szczyt wystąpił PO dołku (trend impulsywny w górę)
        if last_high_idx <= last_low_idx:
            return None 

        P_L = df.loc[last_low_idx, 'low']
        P_H = df.loc[last_high_idx, 'high']
        delta = P_H - P_L
        
        if delta <= 0:
            return None

        # 4. Matematyka Fibo
        L_0786 = P_H - (config.FIBO_LEVEL * delta)
        TP1 = P_L + (config.TP1_LEVEL * delta)
        TP2 = P_H # TP na ostatnim szczycie
        
        current_price = df['close'].iloc[-1]
        
        # 5. Detekcja Order Blocka
        ob = self._find_bullish_order_block(df, start_idx=last_low_idx, end_idx=last_high_idx)
        if not ob:
            return None
            
        # 6. WERYFIKACJA KONFLUENCJI (SMC + Fibo + Price Action + MACD)
        
        # Konfluencja A: Czy poziom 0.786 przecina się z Order Blockiem? (Margines błędu 20%)
        ob_height = ob['top'] - ob['bottom']
        valid_zone_top = ob['top'] + (ob_height * 0.2)
        valid_zone_bottom = ob['bottom'] - (ob_height * 0.2)
        
        fibo_in_ob = valid_zone_bottom <= L_0786 <= valid_zone_top
        
        # Konfluencja B: Czy obecna cena jest w strefie rażenia (Deep Discount)?
        price_in_zone = ob['bottom'] <= current_price <= ob['top']
        
        # Konfluencja C: Impulse MACD Trigger (Odrzucenie z wyprzedania)
        imacd_cross_up = (df['imacd'].iloc[-2] < df['signal'].iloc[-2]) and (df['imacd'].iloc[-1] > df['signal'].iloc[-1])
        imacd_oversold = df['imacd'].iloc[-1] < config.IMACD_OS_LEVEL
        
        if fibo_in_ob and price_in_zone and imacd_cross_up and imacd_oversold:
            # Obliczanie bezpiecznego SL pod OB
            atr_buffer = (df['high'].tail(14).max() - df['low'].tail(14).min()) * 0.05
            sl_price = ob['bottom'] - atr_buffer
            
            return {
                "action": "BUY",
                "entry": current_price,
                "sl": round(sl_price, 2),
                "tp1": round(TP1, 2),
                "tp2": round(TP2, 2),
                "ob_level": ob['top']
            }
            
        return None