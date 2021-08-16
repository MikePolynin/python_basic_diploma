from hotel import Hotel
from dotenv import load_dotenv
import os
import requests

load_dotenv()

url = 'https://hotels4.p.rapidapi.com/locations/search'

headers = {
    'x-rapidapi-key': os.getenv('X_RAPIDAPI_KEY'),
    'x-rapidapi-host': 'hotels4.p.rapidapi.com'
}


def example():
    """Выводит результат тестового запроса через API hotels.com"""

    querystring = {'query': 'new york', 'locale': 'en_US'}

    response = requests.request('GET', url, headers=headers, params=querystring)

    return response


class RequestsAPI:
    hotel = Hotel()
    pass
