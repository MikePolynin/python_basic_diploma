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
    querystring = {'query': '{0}'.format(city), 'locale': 'ru_RU'}
    response = requests.request('GET', url, headers=headers, params=querystring).json()
    result = response['suggestions'][0]['entities'][0]['destinationId']
    return result


def make_request(params: dict, result: list = None) -> list:
    """Функция запроса данных об отелях"""
    if result is None:
        result = list()
    current_date = datetime.datetime.now().date()
    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {'destinationId': params['city_id'],
                   'pageNumber': "1",
                   'pageSize': params['results_quantity'],
                   'checkIn': current_date,
                   'checkOut': current_date + datetime.timedelta(days=7),
                   'adults1': params['adults_quantity']}
    if params['user_command'] == '/lowprice':
        querystring['sortOrder'] = 'PRICE'
    elif params['user_command'] == '/highprice':
        querystring['sortOrder'] = 'PRICE_HIGHEST_FIRST'
    elif params['user_command'] == '/bestdeal':
        querystring['sortOrder'] = 'DISTANCE_FROM_LANDMARK'
        querystring['priceMin'] = params['min_price']
        querystring['priceMax'] = params['max_price']
        querystring['landmarkIds'] = 'City center'
        querystring['pageNumber'] = str(params['page_number'])
    response = requests.request('GET', url, headers=headers, params=querystring).json()
    search_results = response['data']['body']['searchResults']['results']
    if len(search_results) == 0:
        return ['No suitable results']
    if params['user_command'] == '/bestdeal':
        if float((search_results[0]['landmarks'][0]['distance'].split(' '))[0]) < \
                params['min_distance']:  # Выбор результатов, подходящих по расстоянию
            if float((search_results[params['results_quantity'] - 1]['landmarks'][0]['distance'].split(' '))[0]) < \
                    params['min_distance']:  # Проверка результатов со следующей страницы
                params['page_number'] += 1
                make_request(params)
            else:
                for i in range(len(search_results)):
                    if params['min_distance'] <= float((search_results[i]['landmarks'][0]['distance'].split(' '))[0]) \
                            <= params['max_distance']:
                        result.append(search_results[i])
                        params['page_number'] += 1
                        make_request(params, result)
        else:
            while len(result) < params['results_quantity']:
                for i in range(len(search_results)):
                    if search_results[i] not in result:
                        result.append(search_results[i])
                break
        sorted_results = sorted(result, key=lambda price: (price['ratePlan']['price']['exactCurrent']))
        return hotel.hotel_view(sorted_results, params)
    else:
        return hotel.hotel_view(search_results, params)


def get_photo(hotel_id: int) -> requests.Response:
    """Функция получения фотографий отеля по ID"""
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {'id': hotel_id}
    response = requests.request('GET', url, headers=headers, params=querystring)
    return response
