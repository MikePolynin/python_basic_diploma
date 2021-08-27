import datetime
import hotel
from dotenv import load_dotenv
import os
import requests

load_dotenv()

headers = {
    'x-rapidapi-key': os.getenv('X_RAPIDAPI_KEY'),
    'x-rapidapi-host': 'hotels4.p.rapidapi.com'
}


def get_city_id(city: str) -> str:
    """Функция запроса ID локации по переданному значению"""
    url = 'https://hotels4.p.rapidapi.com/locations/search'
    querystring = {'query': '{0}'.format(city)}
    response = requests.request('GET', url, headers=headers, params=querystring).json()
    result = response['suggestions'][0]['entities'][0]['destinationId']
    return result


def make_request(params: dict) -> list:
    """Функция запроса данных об отелях"""
    current_date = datetime.datetime.now().date()
    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {'destinationId': params['city_id'],
                   'pageNumber': "1",
                   'pageSize': params['results_quantity'],
                   'checkIn': current_date,
                   'checkOut': current_date + datetime.timedelta(days=7),
                   'adults1': '1',
                   'currency': 'USD'}
    if params['user_command'] == '/lowprice':
        querystring['sortOrder'] = 'PRICE'
    elif params['user_command'] == '/highprice':
        querystring['sortOrder'] = 'PRICE_HIGHEST_FIRST'
    elif params['user_command'] == '/bestdeal':
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11
        pass
    response = requests.request('GET', url, headers=headers, params=querystring).json()
    result = hotel.hotel_view(response, params)
    return result


def get_photo(hotel_id: int) -> requests.Response:
    """Функция получения фотографий отеля по ID"""
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {'id': hotel_id}
    response = requests.request('GET', url, headers=headers, params=querystring)
    return response
