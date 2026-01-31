import requests

# Twój klucz API wklejony bezpośrednio w nagłówek
API_KEY = "c372c472-eefb-46aa-ab69-d4739690c0f8"

def sprawdz_staty_gracza(nick):
    url = "https://fortnite-api.com/v2/stats/br/v2"
    
    headers = {
        "Authorization": API_KEY
    }
    
    # Parametry: szukamy po nicku, dane z całego konta (lifetime)
    params = {
        "name": nick.strip(),
        "timeWindow": "lifetime"
    }

    print(f"--- Sprawdzam gracza: {nick} ---")

    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()['data']
            
            # Wyciągamy dane
            
            
      
   
            print(f"⚠️ Błąd {response.status_code}: {response.text}")

    except Exception as e:
        print(f"🚨 Wystąpił problem z połączeniem: {e}")

# Możesz tutaj wpisać dowolny nick do sprawdzenia
if __name__ == "__main__":
    moj_nick = "Dmytro_159"
    sprawdz_staty_gracza(moj_nick)