import requests

API_KEY = 'YOUR_USDA_API_KEY'

def search_food(query):
    url = f'https://api.nal.usda.gov/fdc/v1/foods/search?query={query}&api_key={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('foods', [])
    return []