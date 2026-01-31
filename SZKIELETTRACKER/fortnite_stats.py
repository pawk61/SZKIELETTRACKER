import requests
import dotenv
import os

dotenv.load_dotenv(dotenv_path="api.env")
API_KEY = os.getenv("FORTNITE_API_KEY")

def sprawdz_staty_gracza(nick):
    url = "https://fortnite-api.com/v2/stats/br/v2"
    headers = {"Authorization": API_KEY}
    params = {"name": nick.strip(), "timeWindow": "lifetime"}

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()['data']
            
            acc_id = data['account']['id']
            name = data['account']['name']
            bp_level = data.get('battlePass', {}).get('level', 0)
            overall = data.get('stats', {}).get('all', {}).get('overall', {})
            
            print(f"\n✅ ZNALEZIONO: {name}")
            print(f"🆔 ID: {acc_id}")
            print(f"🎖️ BP Level: {bp_level} | ⏳ Grał: {round(overall.get('minutesPlayed', 0) / 60, 1)}h")
            
            # Liczenie K/D dla KBM i Pada
            def get_avg_kd(input_type):
                device = data.get('stats', {}).get(input_type, {})
                if not device: return "Brak"
                s = device.get('solo', {}).get('kd', 0)
                d = device.get('duo', {}).get('kd', 0)
                sq = device.get('squad', {}).get('kd', 0)
                return round((s + d + sq) / 3, 2)

            print(f"⌨️  K/D KBM: {get_avg_kd('keyboardMouse')} | 🎮 K/D PAD: {get_avg_kd('gamepad')}")
            
            return acc_id  # Przekazuje ID do managera
        else:
            print(f"❌ Błąd {response.status_code}: Profil prywatny lub zły nick.")
            return None
    except Exception as e:
        print(f"🚨 Błąd fortnite_stats: {e}")
        return None