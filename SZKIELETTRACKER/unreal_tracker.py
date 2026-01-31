import requests

def pobierz_unreal_data(user_id):
    try:
        url = f"https://olitracker.com/api/stats/{user_id}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            rb = data.get('ranked_stats', {}).get('ranked-br', {})
            
            ranga = rb.get('division_name', 'Brak danych')
            miejsce = rb.get('unreal_placement', 'Brak') if ranga == "Unreal" else "N/A"
            
            return {"ranga": ranga, "miejsce": miejsce}
        return {"ranga": "Nieznana", "miejsce": "N/A"}
    except Exception as e:
        return {"ranga": f"Błąd: {e}", "miejsce": "N/A"}