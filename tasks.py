from robocorp.tasks import task
from keywords.trading_keywords import TradingFlow
import time

@task
def run_trading_bot():
    """
    Główna pętla asynchroniczna systemu.
    Działa jako daemon skanujący rynek w poszukiwaniu konfluencji SMC.
    """
    print("--- Uruchamianie maszyny analitycznej: Fibodi + SMC ---")
    flow = TradingFlow()
    
    # Pętla nasłuchująca (State Machine)
    # W środowisku produkcyjnym Robocorp Control Room, 
    # może to być uruchamiane np. cronem co 15 minut.
    try:
        while True:
            flow.run_market_scan()
            time.sleep(10) # Przerwa między skanami wektorowymi
    except KeyboardInterrupt:
        print("[SYSTEM] Zatrzymywanie bota...")