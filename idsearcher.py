import re
import os

log_path = os.path.expandvars(r'%LOCALAPPDATA%\FortniteGame\Saved\Logs\FortniteGame.log')

def wyciagnij_pelne_id():
    # Szukamy ciągu 32 znaków (hex), który nie ma w środku kropek
    # Typowe ID Epic to znaki 0-9 i a-f
    id_pattern = re.compile(r"([a-f0-9]{32})")
    
    found_ids = set()

    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Szukamy w liniach sieciowych (LogNet), tam nie skracają ID
            if "LogNet" in line or "Registering" in line:
                matches = id_pattern.findall(line.lower())
                for match in matches:
                    found_ids.add(match)

    print(f"✅ Znaleziono {len(found_ids)} pełnych identyfikatorów ID:")
    for player_id in found_ids:
        print(f"🆔 {player_id}")

if __name__ == "__main__":
    wyciagnij_pelne_id()