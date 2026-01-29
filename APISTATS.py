import requests

# --- KONFIGURACJA ---
API_KEY = "######################### - won't show it here for security reasons"
NICK = "MRSZKIELET2010PL"
PLATFORM = "kbm" # kbm, gamepad, touch

def pobierz_staty_api_v2():
    # To jest oficjalny URL dla darmowych kluczy publicznych
    url = f"https://public-api.tracker.gg/v2/fortnite/standard/profile/{PLATFORM}/{NICK}"
    
    headers = {
        "TRN-Api-Key": API_KEY,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"📡 Próba połączenia z API...")

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # Wyciąganie statystyk
            segments = data['data']['segments'][0]['stats']
            
            print("\n" + "—"*40)
            print(f"✅ POŁĄCZONO POMYŚLNIE!")
            print(f"👤 GRACZ: {NICK}")
            print(f"📊 K/D:   {segments.get('kd', {}).get('displayValue', 'N/A')}")
            print(f"🏆 WINS:  {segments.get('wins', {}).get('displayValue', 'N/A')}")
            print("—"*40)
            
        elif response.status_code == 401:
            print("❌ Błąd 401: Klucz API jest nieprawidłowy lub nieaktywny.")
            print("Sprawdź czy na stronie Tracker.gg klucz nie ma statusu 'Pending' lub 'Disabled'.")
        elif response.status_code == 403:
            print("❌ Błąd 403: Masz klucz, ale nie masz uprawnień do tego profilu (Cloudflare).")
        else:
            print(f"❌ Błąd {response.status_code}: {response.text}")

    except Exception as e:
        print(f"❌ Błąd krytyczny: {e}")

if __name__ == "__main__":
    pobierz_staty_api_v2()