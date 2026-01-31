import os
import time

# Ścieżka do logów
log_path = os.path.expandvars(r'%LOCALAPPDATA%\FortniteGame\Saved\Logs\FortniteGame.log')

def start_logger():
    print("----WARMUP LOGGER----")
    print(f"MONITORING: {log_path}")
    print("WAITING FOR LOG 'LogBattleRoyaleGamePhaseLogic'...\n")

    if not os.path.exists(log_path):
        print("ERROR: NO LOG FILE FOUND")
        return

    # Otwieramy plik w trybie binarnym z podglądem na koniec
    with open(log_path, 'rb') as f:
        f.seek(0, 2)  # Skocz na koniec pliku
        
        try:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                
                # Dekodujemy linię i czyścimy białe znaki
                row = line.decode('utf-8', errors='ignore').strip()

                # Szukamy Twojej frazy (bez względu na wielkość liter)
                if "LogBattleRoyaleGamePhaseLogic" in row:
                    print("-" * 50)
                    print(f"🔔 FOUND LOG")
                    print(row) # Wyświetla całą treść linii z loga
                    print("-" * 50)

        except KeyboardInterrupt:
            print("\n----LOGGER STOPPED----")

if __name__ == "__main__":
    start_logger()