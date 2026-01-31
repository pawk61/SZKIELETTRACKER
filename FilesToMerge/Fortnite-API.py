import requests

API_KEY = "###########################"

def sprawdz_staty_gracza(nick):
    url = "https://fortnite-api.com/v2/stats/br/v2"
    headers = {"Authorization": API_KEY}
    params = {"name": nick.strip(), "timeWindow": "lifetime"}

    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()['data']
            
            # Podstawowe informacje
            acc_id = data['account']['id']
            name = data['account']['name']
            bp_level = data.get('battlePass', {}).get('level', 0)
            
            # Statystyki ogólne (overall)
            overall = data.get('stats', {}).get('all', {}).get('overall', {})
            wins = overall.get('wins', 0)
            matches = overall.get('matches', 0)
            winrate = overall.get('winRate', 0)
            hours = round(overall.get('minutesPlayed', 0) / 60, 1)

            print(f"\n✅ ZNALEZIONO GRACZA: {name}")
            print(f"🆔 ID: {acc_id}")
            print(f"🎖️ BattlePass Level: {bp_level}")
            print(f"📊 Wins: {wins} | Matches: {matches} | WinRate: {winrate}%")
            print(f"⏳ Czas w grze: {hours}h")
            print("-" * 45)

            # Funkcja do liczenia średniej K/D (Solo + Duo + Squad) / 3
            def get_avg_kd(input_type):
                device = data.get('stats', {}).get(input_type, {})
                if not device: return None
                
                s = device.get('solo', {}).get('kd', 0)
                d = device.get('duo', {}).get('kd', 0)
                sq = device.get('squad', {}).get('kd', 0)
                
                return round((s + d + sq) / 3, 2)

            # Wyświetlanie statystyk dla urządzeń
            kbm_kd = get_avg_kd('keyboardMouse')
            pad_kd = get_avg_kd('gamepad')

            if kbm_kd is not None:
                print(f"⌨️  Średnie K/D (Solo/Duo/Squad) KBM: {kbm_kd}")
            if pad_kd is not None:
                print(f"🎮 Średnie K/D (Solo/Duo/Squad) PAD: {pad_kd}")

        else:
            print(f"❌ Błąd {response.status_code}: Nie znaleziono gracza lub profil prywatny.")

    except Exception as e:
        print(f"🚨 Problem: {e}")

if __name__ == "__main__":
    sprawdz_staty_gracza("MRSZKIELET2010PL")