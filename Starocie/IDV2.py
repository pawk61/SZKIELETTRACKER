import requests

API_KEY = "#######################"
NICK = "Dmytro_159"

# Jedna linia na zapytanie i wyciągnięcie ID
data = requests.get(f"https://fortnite-api.com/v2/stats/br/v2?name={NICK}", headers={"Authorization": API_KEY}).json()
account_id = data.get('data', {}).get('account', {}).get('id')

print(account_id)