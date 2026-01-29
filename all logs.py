import os
import time

log_path = os.path.expandvars(r'%LOCALAPPDATA%\FortniteGame\Saved\Logs\FortniteGame.log')
output_file = "raw_dump.txt"

def grab_everything():
    print("🚀 Log Grabber URUCHOMIONY.")
    print(f"📂 Zapisuję wszystko do: {output_file}")
    print("---")
    print("INSTRUKCJA:")
    print("1. Wejdź do meczu/lobby.")
    print("2. Wyjdź z meczu do lobby głównego.")
    print("3. Odczekaj 5 sekund i wyłącz ten skrypt (Ctrl+C).")
    
    if not os.path.exists(log_path):
        print("BŁĄD: Brak pliku logów!")
        return

    with open(log_path, 'rb') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        # Skok na koniec, żeby nie kopiować starych śmieci sprzed uruchomienia
        f_in.seek(0, 2)
        
        try:
            while True:
                line = f_in.readline()
                if not line:
                    time.sleep(0.01)
                    continue
                
                # Dekodujemy i zapisujemy każdą linię do pliku
                row = line.decode('utf-8', errors='ignore')
                f_out.write(row)
                f_out.flush() # Natychmiastowy zapis na dysk
                
                # Opcjonalnie: podgląd w konsoli (żebyś widział, że żyje)
                if "Log" in row:
                    print(f"DEBUG: {row[:80]}...") 

        except KeyboardInterrupt:
            print(f"\n✅ ZAKOŃCZONO. Dane zapisane w {output_file}")

if __name__ == "__main__":
    grab_everything()