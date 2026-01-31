import os
import time
import json
import fortnite_stats
import unreal_tracker

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
    print(f"---- SZKIELETTRACKER ----")
    
    if not os.path.exists(log_path):
        print("ERROR: NO LOG FILE ")
        return

    history = load_history()
    game_counter = len(history) + 1
    current_game_players = [] 
    known_nicks = set()
    in_warmup = False

    print(f"🚀 WAITING FOR WARMUP LOG (Gra {game_counter})...")

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
                    if in_warmup and len(current_game_players) >= 3:
                        game_key = f"Gra {game_counter}"
                        history[game_key] = current_game_players
                        save_history(history)
                        game_counter += 1

                    in_warmup = True
                    current_game_players = [] 
                    known_nicks = set()
                    print(f"\n🏝️  [WARMUP PHASE] {game_counter}")

                # 2. ZLICZANIE GRACZY + API CALLS
                if in_warmup and "LogPawnBoombox" in row and "song 'None'" in row:
                    parts = row.split("'")
                    if len(parts) > 1:
                        p_name = parts[1]
                        if p_name and p_name not in BOSS_BLACKLIST and p_name not in known_nicks:
                            known_nicks.add(p_name)
                            
                            # --- LOGIKA API ---
                            acc_id = fortnite_stats.sprawdz_staty_gracza(p_name)
                            ranga_info = {"ranga": "N/A", "miejsce": "N/A"}
                            
                            if acc_id:
                                ranga_info = unreal_tracker.pobierz_unreal_data(acc_id)
                            
                            p_data = {
                                "nick": p_name,
                                "id": acc_id if acc_id else "Prywatny",
                                "ranga": ranga_info.get('ranga', 'N/A'),
                                "miejsce": ranga_info.get('miejsce', 'N/A')
                            }
                            current_game_players.append(p_data)
                            
                            # --- WYŚWIETLANIE W KONSOLI ---
                            # Sprawdzamy czy ranga to Unreal (małe/duże litery)
                            ranga_str = str(p_data['ranga'])
                            miejsce_str = str(p_data['miejsce'])
                            
                            msg = f"👤 [G{game_counter}] {p_name} | {ranga_str}"
                            
                            if ranga_str.lower() == "unreal" and miejsce_str not in ["N/A", "Brak", "None"]:
                                msg += f" (Miejsce: #{miejsce_str})"
                            
                            print(msg)
                            # --- KONIEC LOGIKI API ---

                # 3. WYKRYCIE KONCA MECZU
                if "LogFort: Display: Plugin" in row and "is skipped" in row:
                    if in_warmup:
                        if len(current_game_players) >= 3:
                            game_key = f"Game {game_counter}"
                            history[game_key] = current_game_players
                            save_history(history)
                            print(f"\n💾 Saved: {game_key} ({len(current_game_players)} Players)")
                            game_counter += 1
                        
                        in_warmup = False
                        current_game_players = []
                        known_nicks = set()
                        print(f"⌛ MECZ ENDED, WAITING FOR NEW MATCH...")

        except KeyboardInterrupt:
            if current_game_players:
                save_history(history)
            print("\n----SZKIELETTRACKER STOPPED----")

if __name__ == "__main__":
    start_tracker()