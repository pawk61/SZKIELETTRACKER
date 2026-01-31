import requests

API_KEY = "########################"
HEADERS = {"Authorization": API_KEY}

def pobierz_id_gracza(nick):
    url = f"https://fortniteapi.io/v1/lookup?username={nick}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            account_id = data.get("account_id")
            print(f"✅ {nick} -> {account_id}")
            return account_id
        else:
            print(f"❌ {nick}: Nie znaleziono lub błąd API.")
            return None
    except Exception as e:
        print(f"🚨 Błąd: {e}")
        return None

# TEST:
if __name__ == "__main__":
    lobby = ["Dmytro_159", "Mongraal", "MokryAreczek11"]
    for gracz in lobby:
        pobierz_id_gracza(gracz)