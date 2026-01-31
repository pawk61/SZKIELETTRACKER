import requests

def pobierz_unreal_data(user_id):
    url = f"https://olitracker.com/api/stats/{user_id}"
    data = requests.get(url).json()
    
    # Wyciągamy sekcję ranked-br
    rb = data.get('ranked_stats', {}).get('ranked-br', {})
    
    return {
        "ranga": rb.get('division_name'),
        
        "miejsce": rb.get('unreal_placement') if rb.get('division_name') == "Unreal" else "Brak"
    }

# Przykład użycia:
res = pobierz_unreal_data("e6ceece9d6a145aaae24f6b9fbc56091")
print(f"Ranga: {res['ranga']}\nMiejsce: {res['miejsce']}")