import API_requests


class Hotel:
    """Класс для создания и форматирования вывода информации об отеле"""

    def __init__(self, name: str, address: str, center_distance: str, price: str, photos: list = None) -> None:
        """Функция определения свойств отеля"""
        if photos is None:
            photos = list()
        self.name = name
        self.address = address
        self.center_distance = center_distance
        self.price = price
        self.photos = photos

    def __str__(self) -> str:
        """Функция переопределения метода для преобразования класса отеля в строку"""
        result = '\nHotel name: {0}\n' \
                 'Hotel address: {1}\n' \
                 'Distance from center: {2}\n' \
                 'Price: {3}\n'.format(self.name,
                                       self.address,
                                       self.center_distance,
                                       self.price)
        return result


def hotel_view(result: list, params: dict) -> list:
    """Функция представления данных об отеле"""
    hotels = []
    for i in range(len(result)):
        hotel_photos = []
        hotels.append(Hotel(result[i]['name'],
                            result[i]['address']['streetAddress'],
                            result[i]['landmarks'][0]['distance'],
                            result[i]['ratePlan']['price']['current'],
                            hotel_photos))
        if params['needs_photo'] == 1:
            hotel_photos.clear()
            response = API_requests.get_photo(result[i]['id']).json()  # Запрос фотографий
            for j in range(params['photo_quantity']):
                photo_link = response['hotelImages'][j]['baseUrl']
                size_suffix = response['hotelImages'][j]['sizes'][0]['suffix']  # Выбор размера фотографий
                photo = photo_link.replace('{size}', size_suffix)
                hotel_photos.append(photo)
    return hotels
