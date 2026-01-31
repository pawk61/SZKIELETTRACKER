import requests
import json

API_KEY = "33d0ca22-d9533891-149061be-7b029919"
NICK = "Dmytro_159" # Wpisz swój nick

def pobierz_wszystko_z_api_io(nick):
    headers = {"Authorization": API_KEY}
    
    # KROK 1: Lookup (pobieramy świeże ID i budzimy API)
    lookup_url = f"https://fortniteapi.io/v1/lookup?username={nick}"
    l_res = requests.get(lookup_url, headers=headers).json()
    
    if not l_res.get("result"):
        return print(f"❌ Nie znaleziono gracza o nicku: {nick}")
    
    uid = l_res.get("account_id")
    print(f"✅ Znaleziono ID: {uid}")

    # KROK 2: Pobieramy WSZYSTKO (pełny zrzut zgodnie z dokumentacją)
    # Używamy adresu dokładnie ze strony: /v1/stats?account=ID
    stats_url = f"https://fortniteapi.io/v1/stats?account={uid}"
    response = requests.get(stats_url, headers=headers)

    if response.status_code == 200:
        if response.text.strip():
            data = response.json()
            print("\n📦 PEŁNY ZRZUT DANYCH:")
            print(json.dumps(data, indent=4))
        else:
            print("❌ Serwer odpowiedział 200, ale przysłał pusty tekst (profil nadal niewidoczny).")
    else:
        print(f"❌ Błąd serwera: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    pobierz_wszystko_z_api_io(NICK)