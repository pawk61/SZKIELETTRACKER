import os
import time
import json

# Ścieżki
log_path = os.path.expandvars(r'%LOCALAPPDATA%\FortniteGame\Saved\Logs\FortniteGame.log')
db_path = "historia_gier.json"

BOSS_BLACKLIST = [
    "Cisza", "Plażowy Brutus", "Człowiek Ziutek", 
    "None", "NONE", "Anonymous", "Player"
]

def load_history():
    if os.path.exists(db_path):
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def save_history(history):
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def start_tracker():
    print(f"--- FORTNITE PHASE TRACKER (Warmup Edition) ---")
    
    if not os.path.exists(log_path):
        print("BŁĄD: Nie znaleziono pliku logów!")
        return

    history = load_history()
    game_counter = len(history) + 1
    current_game_players = set()
    in_warmup = False

    print(f"🚀 Gotowy. Czekam na fazę 'Warmup' (Gra {game_counter})...")

    with open(log_path, 'rb') as f:
        f.seek(0, 2)
        
        try:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.01)
                    continue
                
                row = line.decode('utf-8', errors='ignore').strip()

             # 1. WYKRYCIE STARTU WYSPY (Warmup)
                if "NewPhase = EAthenaGamePhase::Warmup" in row:
                    # Jeśli jakimś cudem flaga była już True, a my znów widzimy Warmup,
                    # oznacza to nową grę bez poprawnego zamknięcia poprzedniej.
                    if in_warmup and len(current_game_players) >= 3:
                        game_key = f"Gra {game_counter}"
                        history[game_key] = sorted(list(current_game_players))
                        save_history(history)
                        game_counter += 1

                    in_warmup = True
                    current_game_players = set() 
                    print(f"\n🏝️  [FAZA WARMUP] Start Gry {game_counter}")

                # 2. ZLICZANIE GRACZY (Tylko gdy in_warmup jest True!)
                if in_warmup and "LogPawnBoombox" in row and "song 'None'" in row:
                    parts = row.split("'")
                    if len(parts) > 1:
                        p_name = parts[1]
                        # Ignorujemy "NONE" i puste nicki
                        if p_name and p_name not in BOSS_BLACKLIST and p_name not in current_game_players:
                            current_game_players.add(p_name)
                            print(f"👤 [G{game_counter}] {p_name}")

                # 3. WYKRYCIE KONCA MECZU (Pluginy / Wyjście)
                if "LogFort: Display: Plugin" in row and "is skipped" in row:
                    if in_warmup:
                        if len(current_game_players) >= 3:
                            game_key = f"Gra {game_counter}"
                            history[game_key] = sorted(list(current_game_players))
                            save_history(history)
                            print(f"\n💾 ZAPISANO: {game_key} ({len(current_game_players)} graczy)")
                            game_counter += 1
                        
                        in_warmup = False
                        current_game_players = set()
                        print(f"⌛ Mecz zakończony. Czekam na nową fazę Setup -> Warmup...")

        except KeyboardInterrupt:
            if current_game_players:
                save_history(history)
            print("\n--- Tracker wyłączony ---")

if __name__ == "__main__":
    start_tracker()