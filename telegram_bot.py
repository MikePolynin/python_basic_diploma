import datetime

from telebot import TeleBot
from dotenv import load_dotenv
import API_requests
import os
import telebot

load_dotenv()


class TelegramBot(TeleBot):
    params = {}
    command_history = []

    def help_func(self, message):
        bot.send_message(message.from_user.id,
                         'Что я могу:\n'
                         '/start - приветствие\n'
                         '/lowprice - самых дешевые отели в городе\n'
                         '/highprice - самые дорогие отели в городе\n'
                         '/bestdeal - список отелей, наиболее подходящих по цене и расстоянию от центра\n'
                         '/history - история поиска отелей\n'
                         '/help - меню команд'.format(
                             message.from_user.first_name))

    def parse_command(self, message: telebot.types.Message) -> None:
        """Обработчик входящих сообщений
            На '/start' отвечает приветствием
            /help выводит список возможных команд
            /lowprice - самые дешевые отели в городе
            /highprice - самые дорогие отели в городе
            /bestdeal - список отелей, наиболее подходящих по цене и расстоянию от центра
            /history - история поиска отелей
            При некорректном вводе печатается сообщение об ошибке"""
        if message.text == '/start':
            bot.send_message(message.chat.id,
                             'Привет, {0}!\n'
                             'Я - Telegram-bot с API Hotels.com\n'
                             'Помогу найти подходящее размещение\n'
                             'Что я умею? Нажмите /help'.format(message.from_user.first_name))
        elif message.text == '/help':
            bot.help_func(message)
        elif message.text == '/lowprice' or message.text == '/highprice' or message.text == '/bestdeal':
            bot.params.clear()
            start_search(message)
        elif message.text == '/history':
            history(message)
        else:
            bot.send_message(message.from_user.id,
                             'Некорректный ввод. Список команд доступен по /help')


bot = TelegramBot(os.getenv('BOT_TOKEN'))


@bot.message_handler(content_types=['text'])
def get_text_messages(message: telebot.types.Message) -> None:
    """Обработчик входящих сообщений"""
    bot.parse_command(message)


def start_search(message: telebot.types.Message) -> None:
    """Функция запроса локации для поиска"""
    bot.params['user_command'] = message.text
    bot.send_message(message.from_user.id,
                     'В каком городе ищем?')
    bot.register_next_step_handler(message, get_city)


def incorrect_city(message: telebot.types.Message) -> None:
    """Функция повторного запроса локации для поиска"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id,
                     'Ищем в другом месте?', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call: telebot.types.CallbackQuery) -> None:
        """Обработчик выбранного ответа"""
        if call.data == 'yes':
            bot.send_message(message.from_user.id,
                             'В каком городе ищем?')
            bot.register_next_step_handler(message, get_city)
        elif call.data == 'no':
            bot.help_func(message)


def get_city(message: telebot.types.Message) -> None:
    """Функция получения ID введенной локации.
    При некорректном вводе предлагает повторить запрос"""
    bot.params['city'] = message.text
    while True:
        try:
            city_id = API_requests.get_city_id(message.text)
            bot.params['record'] = ['Запрос от ' + datetime.datetime.strftime(datetime.datetime.now(),
                                                                              '%Y.%m.%d %H:%M:%S')]
            bot.params['city_id'] = city_id
            bot.send_message(message.from_user.id,
                             'Сколько взрослых гостей?')
            bot.register_next_step_handler(message, get_adults_quantity)
            break
        except IndexError:
            bot.send_message(message.from_user.id,
                             'Такого города не найдено')
            incorrect_city(message)
            break


def get_adults_quantity(message: telebot.types.Message) -> None:
    """Функция запроса количества взрослых гостей"""
    while True:
        try:
            adults_quantity = int(message.text)
            if adults_quantity <= 0:
                bot.send_message(message.from_user.id,
                                 'Число взрослых гостей должно быть больше 0')
                incorrect_adults_quantity(message)
                break
            else:
                bot.params['adults_quantity'] = int(message.text)
                if bot.params['user_command'] == '/bestdeal' and 'min_price' not in bot.params.keys():
                    bot.params['page_number'] = 1
                    bot.send_message(message.from_user.id,
                                     'Какая минимальная цена?')
                    bot.register_next_step_handler(message, get_min_price)
                    break
                bot.send_message(message.from_user.id,
                                 'Сколько отелей показать?')
                bot.register_next_step_handler(message, city_quantity)
                break
        except ValueError:
            bot.send_message(message.from_user.id,
                             'Используйте цифры')
            incorrect_adults_quantity(message)
            break


def incorrect_adults_quantity(message: telebot.types.Message) -> None:
    """Функция повторного запроса количества взрослых гостей"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id,
                     'Ввести количество взрослых гостей снова?', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call: telebot.types.CallbackQuery) -> None:
        """Обработчик выбранного ответа"""
        if call.data == 'yes':
            bot.send_message(message.from_user.id,
                             'Сколько взрослых гостей?')
            bot.register_next_step_handler(message, get_adults_quantity)
        elif call.data == 'no':
            bot.help_func(message)


def get_min_price(message: telebot.types.Message) -> None:
    """Функция определения минимальной цены.
    При некорректном вводе предлагает повторить запрос"""
    while True:
        try:
            min_price = int(message.text)
            if min_price <= 0:
                bot.send_message(message.from_user.id,
                                 'Цена должна быть больше 0')
                incorrect_min_price(message)
                break
            else:
                bot.params['min_price'] = int(message.text)
                bot.send_message(message.from_user.id,
                                 'Какая максимальная цена?')
                bot.register_next_step_handler(message, get_max_price)
                break
        except ValueError:
            bot.send_message(message.from_user.id,
                             'Используйте цифры')
            incorrect_min_price(message)
            break


def incorrect_min_price(message: telebot.types.Message) -> None:
    """Функция повторного запроса минимальной цены"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id,
                     'Ввести минимальную цену снова?', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call: telebot.types.CallbackQuery) -> None:
        """Обработчик выбранного ответа"""
        if call.data == 'yes':
            bot.send_message(message.from_user.id,
                             'Какая минимальная цена?')
            bot.register_next_step_handler(message, get_min_price)
        elif call.data == 'no':
            bot.help_func(message)


def get_max_price(message: telebot.types.Message) -> None:
    """Функция определения максимальной цены.
    При некорректном вводе предлагает повторить запрос"""
    while True:
        try:
            max_price = int(message.text)
            if max_price <= 0:
                bot.send_message(message.from_user.id,
                                 'Цена должна быть больше 0')
                incorrect_max_price(message)
                break
            elif max_price <= bot.params['min_price']:
                bot.send_message(message.from_user.id,
                                 'Цена должна быть больше минимальной')
                incorrect_max_price(message)
                break
            else:
                bot.params['max_price'] = int(message.text)
                bot.send_message(message.from_user.id,
                                 'Какое минимальное расстояние от центра?')
                bot.register_next_step_handler(message, get_min_distance)
                break
        except ValueError:
            bot.send_message(message.from_user.id,
                             'Используйте цифры')
            incorrect_min_price(message)
            break


def incorrect_max_price(message: telebot.types.Message) -> None:
    """Функция повторного запроса максимальной цены"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id,
                     'Ввести максимальную цену снова?', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call: telebot.types.CallbackQuery) -> None:
        """Обработчик выбранного ответа"""
        if call.data == 'yes':
            bot.send_message(message.from_user.id,
                             'Какая максимальная цена?')
            bot.register_next_step_handler(message, get_max_price)
        elif call.data == 'no':
            bot.help_func(message)


def get_min_distance(message: telebot.types.Message) -> None:
    """Функция определения минимального расстояния от центра.
    При некорректном вводе предлагает повторить запрос"""
    while True:
        try:
            min_distance = float(message.text)
            if min_distance <= 0:
                bot.send_message(message.from_user.id,
                                 'Расстояние должно быть больше 0')
                incorrect_min_distance(message)
                break
            else:
                bot.params['min_distance'] = float(message.text)
                bot.send_message(message.from_user.id,
                                 'Какое максимальное расстояние от центра?')
                bot.register_next_step_handler(message, get_max_distance)
                break
        except ValueError:
            bot.send_message(message.from_user.id,
                             'Используйте цифры')
            incorrect_min_distance(message)
            break


def incorrect_min_distance(message: telebot.types.Message) -> None:
    """Функция повторного запроса минимального расстояния от центра"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id,
                     'Ввести максимальное расстояние от центра снова?', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call: telebot.types.CallbackQuery) -> None:
        """Обработчик выбранного ответа"""
        if call.data == 'yes':
            bot.send_message(message.from_user.id,
                             'Какое максимальное расстояние от центра?')
            bot.register_next_step_handler(message, get_min_distance)
        elif call.data == 'no':
            bot.help_func(message)


def get_max_distance(message: telebot.types.Message) -> None:
    """Функция определения максимального расстояния от центра.
    При некорректном вводе предлагает повторить запрос"""
    while True:
        try:
            max_distance = float(message.text)
            if max_distance <= 0:
                bot.send_message(message.from_user.id,
                                 'Расстояние должно быть больше 0')
                incorrect_max_distance(message)
                break
            elif max_distance <= bot.params['min_distance']:
                bot.send_message(message.from_user.id,
                                 'Расстояние должно быть больше минимального')
                incorrect_max_distance(message)
                break
            else:
                bot.params['max_distance'] = float(message.text)
                bot.send_message(message.from_user.id,
                                 'Сколько отелей показать?')
                bot.register_next_step_handler(message, city_quantity)
                break
        except ValueError:
            bot.send_message(message.from_user.id,
                             'Используйте цифры')
            incorrect_min_price(message)
            break


def incorrect_max_distance(message: telebot.types.Message) -> None:
    """Функция повторного запроса максимального расстояния от центра"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id,
                     'Ввести максимальное расстояния от центра снова?', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call: telebot.types.CallbackQuery) -> None:
        """Обработчик выбранного ответа"""
        if call.data == 'yes':
            bot.send_message(message.from_user.id,
                             'Какая максимальная цена?')
            bot.register_next_step_handler(message, get_max_price)
        elif call.data == 'no':
            bot.help_func(message)


def incorrect_results_quantity(message: telebot.types.Message) -> None:
    """Функция повторного запроса количества результатов.
    При некорректном вводе предлагает повторить запрос"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id,
                     'Ввести количество снова?', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call: telebot.types.CallbackQuery) -> None:
        """Обработчик выбранного ответа"""
        if call.data == 'yes':
            bot.send_message(message.from_user.id,
                             'Сколько отелей показать?')
            bot.register_next_step_handler(message, city_quantity)
        elif call.data == 'no':
            bot.help_func(message)


def city_quantity(message: telebot.types.Message) -> None:
    """Функция запроса количества результатов.
    При некорректном вводе предлагает повторить запрос"""
    while True:
        max_result_quantity = 15
        try:
            quantity = int(message.text)
            if quantity <= 0:
                bot.send_message(message.from_user.id,
                                 'Количество должно быть больше 0')
                incorrect_results_quantity(message)
                break
            elif quantity > max_result_quantity:
                bot.send_message(message.from_user.id,
                                 'Количество должно быть не больше {0}'.format(max_result_quantity))
                incorrect_results_quantity(message)
                break
            else:
                bot.params['results_quantity'] = int(message.text)
                needs_photo(message)
                break
        except ValueError:
            bot.send_message(message.from_user.id,
                             'Используйте цифры')
            incorrect_results_quantity(message)
            break


def needs_photo(message: telebot.types.Message) -> None:
    """Функция запроса необходимости фотографий результатов"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id,
                     'Показать фото?', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call: telebot.types.CallbackQuery) -> None:
        """Обработчик выбранного ответа"""
        if call.data == 'yes':
            bot.params['needs_photo'] = 1
            bot.send_message(message.from_user.id,
                             'Сколько фото показать?')
            bot.register_next_step_handler(message, photo_quantity)
        elif call.data == 'no':
            bot.params['needs_photo'] = 0
            response = API_requests.make_request(bot.params)
            if bot.params['user_command'] == '/bestdeal':
                answer = 'Результаты поиска в "{0}" для {1} гостей по цене "{2} - {3}" ' \
                         'и на расстоянии от центра "{4} - {5}"\n'. \
                    format(bot.params['city'],
                           bot.params['adults_quantity'],
                           bot.params['min_price'],
                           bot.params['max_price'],
                           bot.params['min_distance'],
                           bot.params['max_distance'])
                bot.params['record'].append(0)
                bot.params['record'].append(answer)
                bot.send_message(message.from_user.id, answer)
            else:
                answer = 'Результаты поиска в "{0}" для {1} гостей по запросу "{2}"\n'. \
                    format(bot.params['city'],
                           bot.params['adults_quantity'],
                           bot.params['user_command'][1:])
                bot.params['record'].append(0)
                bot.params['record'].append(answer)
                bot.send_message(message.from_user.id, answer)
            for i in range(len(response)):
                bot.send_message(message.from_user.id, str(response[i]))
                bot.params['record'].append(str(response[i]))
            bot.command_history.append(bot.params['record'])


def incorrect_photo_quantity(message: telebot.types.Message) -> None:
    """Функция повторного запроса количества фотографий результатов.
    При некорректном вводе предлагает повторить запрос"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id,
                     'Ввести количество снова?', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call: telebot.types.CallbackQuery) -> None:
        """Обработчик выбранного ответа"""
        if call.data == 'yes':
            bot.send_message(message.from_user.id,
                             'Сколько фото показать?')
            bot.register_next_step_handler(message, photo_quantity)
        elif call.data == 'no':
            bot.help_func(message)


def photo_quantity(message: telebot.types.Message) -> None:
    """Функция запроса количества фотографий результатов.
    При некорректном вводе предлагает повторить запрос"""
    while True:
        max_result_quantity = 3
        try:
            quantity = int(message.text)
            if quantity <= 0:
                bot.send_message(message.from_user.id,
                                 'Количество должно быть больше 0')
                incorrect_photo_quantity(message)
                break
            elif quantity > max_result_quantity:
                bot.send_message(message.from_user.id,
                                 'Количество должно быть не больше {0}'.format(max_result_quantity))
                incorrect_photo_quantity(message)
                break
            else:
                bot.params['photo_quantity'] = int(message.text)
                response = API_requests.make_request(bot.params)
                if bot.params['user_command'] == '/bestdeal':
                    answer = 'Результаты поиска в "{0}" для {1} гостей по цене "{2} - {3}" ' \
                             'и на расстоянии от центра "{4} - {5}"\n'. \
                        format(bot.params['city'],
                               bot.params['adults_quantity'],
                               bot.params['min_price'],
                               bot.params['max_price'],
                               bot.params['min_distance'],
                               bot.params['max_distance'])
                    bot.params['record'].append(1)
                    bot.params['record'].append(answer)
                    bot.send_message(message.from_user.id, answer)
                else:
                    answer = 'Результаты поиска в "{0}" для {1} гостей по запросу "{2}"\n'. \
                        format(bot.params['city'],
                               bot.params['adults_quantity'],
                               bot.params['user_command'][1:])
                    bot.params['record'].append(1)
                    bot.params['record'].append(answer)
                    bot.send_message(message.from_user.id, answer)
                for i in range(len(response)):
                    photos = []
                    bot.send_message(message.from_user.id, str(response[i]))
                    bot.params['record'].append(str(response[i]))
                    for j in range(len(response[i].photos)):
                        bot.send_photo(message.from_user.id, response[i].photos[j])
                        photos.append(response[i].photos[j])
                    bot.params['record'].append(photos)
                bot.command_history.append(bot.params['record'])
                break
        except ValueError:
            bot.send_message(message.from_user.id,
                             'Используйте цифры')
            incorrect_photo_quantity(message)
            break


def history(message: telebot.types.Message) -> None:
    """Функция просмотра истории поиска отелей"""
    bot.send_message(message.from_user.id, 'История запросов')
    for i in range(len(bot.command_history)):
        bot.send_message(message.from_user.id, bot.command_history[i][0])
        bot.send_message(message.from_user.id, bot.command_history[i][2])
        if bot.command_history[i][1] == 0:
            for j in range(3, len(bot.command_history[i])):
                bot.send_message(message.from_user.id, bot.command_history[i][j])
        else:
            for j in range(3, len(bot.command_history[i]) - 1, 2):
                bot.send_message(message.from_user.id, bot.command_history[i][j])
                for k in range(len(bot.command_history[i][j + 1])):
                    bot.send_photo(message.from_user.id, bot.command_history[i][j + 1][k])
