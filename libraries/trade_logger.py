import csv
import os
from datetime import datetime

class TelemetryLogger:
    def __init__(self, trade_file="trade_telemetry.csv", market_file="market_telemetry.csv"):
        self.trade_file = trade_file
        self.market_file = market_file
        self._init_files()

    def _init_files(self):
        # 1. Plik transakcji (strzały snajpera)
        if not os.path.exists(self.trade_file):
            with open(self.trade_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Time", "Ticket_MT5", "Type", "Entry_Price", 
                    "Wick_Points", "Spread_Points", 
                    "Resistance_Level", "Support_Level", "Box_Width_Points"
                ])
                
        # 2. Plik rynku (tętno co 5 minut)
        if not os.path.exists(self.market_file):
            with open(self.market_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Candle_Time", "Close_Price", 
                    "Support_6M5", "Resistance_6M5", 
                    "Lower_Wick_Pts", "Upper_Wick_Pts", 
                    "Action_Taken"
                ])

    def log_trade(self, ticket, order_type, price, wick, spread, resistance, support, point_value):
        """Zapisuje fizycznie otwarte pozycje."""
        box_width = (resistance - support) / point_value
        direction = "BUY" if order_type == 0 else "SELL" # 0 to mt5.ORDER_TYPE_BUY
        
        with open(self.trade_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ticket, direction, price, 
                round(wick, 1), round(spread, 1), 
                round(resistance, 2), round(support, 2), round(box_width, 1)
            ])

    def log_market_candle(self, timestamp, close_price, support, resistance, lower_wick, upper_wick, action="NONE"):
        """Zapisuje stan rynku z zamkniętej świecy co 5 minut."""
        readable_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.market_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                readable_time, round(close_price, 2), 
                round(support, 2), round(resistance, 2),
                round(lower_wick, 1), round(upper_wick, 1), 
                action
            ])