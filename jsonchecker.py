import json
import os
from collections import defaultdict

db_path = "historia_gier.json"

def analyze_players():
    if not os.path.exists(db_path):
        print("BŁĄD: Nie znaleziono pliku historia_gier.json!")
        return

    with open(db_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("BŁĄD: Plik JSON jest uszkodzony lub pusty.")
            return

    # Słownik: gracz -> lista gier, w których był
    player_map = defaultdict(list)
    all_unique_players = set()

    for game_id, players in data.items():
        for player in players:
            player_map[player].append(game_id)
            all_unique_players.add(player)

    # Filtrujemy tylko tych, którzy byli w więcej niż 1 grze
    duplicates = {name: games for name, games in player_map.items() if len(games) > 1}

    # --- NAGŁÓWEK RAPORTU ---
    print("\n" + "="*70)
    print(f"📊 PEŁNY RAPORT BAZY DANYCH")
    print(f"Liczba zapisanych meczów: {len(data)}")
    print(f"ŁĄCZNA LICZBA UNIKALNYCH GRACZY: {len(all_unique_players)}")
    print("="*70)

    # --- POWTÓRKI ---
    print(f"--- ANALIZA POWTÓREK ---")
    
    if not duplicates:
        print("Nie znaleziono żadnych powtarzających się graczy.")
    else:
        # Sortujemy od największej liczby wystąpień
        sorted_duplicates = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)

        print(f"{'GRACZ':<25} | {'SPOTKANIA':<10} | {'W GRACH'}")
        print("-" * 70)

        for name, games in sorted_duplicates:
            games_str = ", ".join(games)
            print(f"{name:<25} | {len(games):<10} | {games_str}")

        print("-" * 70)
        print(f"Znaleziono {len(duplicates)} osób spotkanych więcej niż raz.")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    analyze_players()