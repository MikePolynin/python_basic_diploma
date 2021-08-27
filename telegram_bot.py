from telebot import TeleBot
from dotenv import load_dotenv
import API_requests
import os
import telebot

load_dotenv()


class TelegramBot(TeleBot):
    params = {}

    def help_func(self, message):
        bot.send_message(message.from_user.id,
                         'Список доступных команд:\n'
                         '/start - вывод приветствия\n'
                         '/lowprice - вывод самых дешевых отелей в городе\n'
                         '/highprice - вывод самых дорогих отелей в городе\n'
                         '/help - список возможных команд'.format(
                             message.from_user.first_name))

    def parse_command(self, message: telebot.types.Message) -> None:
        """Обработчик входящих сообщений
            На '/start' отвечает приветствием
            /help выводит список возможных команд
            /lowprice - вывод самых дешевых отелей в городе
            /highprice - вывод самых дорогих отелей в городе
            При некорректном вводе печатается сообщение об ошибке"""
        if message.text == '/start':
            bot.send_message(message.chat.id,
                             'Привет, {0}!\n'
                             'Я - Telegram-bot с API Hotels.com на python\n'
                             'Помогу найти подходящее размещение\n'
                             'Список команд доступен по /help'.format(message.from_user.first_name))
        elif message.text == '/help':
            bot.help_func(message)
        elif message.text == '/lowprice' or message.text == '/highprice':
            bot.params.clear()
            start_search(message)
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
            bot.params['city_id'] = city_id
            if bot.params['user_command'] == '/bestdeal':
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11
                break
            else:
                bot.send_message(message.from_user.id,
                                 'Сколько результатов показать?')
                bot.register_next_step_handler(message, city_quantity)
                break
        except IndexError:
            bot.send_message(message.from_user.id,
                             'Такого города не найдено')
            incorrect_city(message)
            break


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
                             'Сколько результатов показать?')
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
                             'Количество должно быть числом')
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
                     'Фото нужны?', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call: telebot.types.CallbackQuery) -> None:
        """Обработчик выбранного ответа"""
        if call.data == 'yes':
            bot.params['needs_photo'] = 1
            bot.send_message(message.from_user.id,
                             'Сколько фотографий показать?')
            bot.register_next_step_handler(message, photo_quantity)
        elif call.data == 'no':
            bot.params['needs_photo'] = 0
            response = API_requests.make_request(bot.params)
            bot.send_message(message.from_user.id, 'Результаты поиска в "{0}" по запросу "{1}"\n'.
                             format(bot.params['city'],
                                    bot.params['user_command'][1:]))
            for i in range(len(response)):
                bot.send_message(message.from_user.id, str(response[i]))


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
                             'Сколько фотографий показать?')
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

                bot.send_message(message.from_user.id, 'Результаты поиска в "{0}" по запросу "{1}"\n'.
                                 format(bot.params['city'],
                                        bot.params['user_command'][1:]))

                for i in range(len(response)):
                    bot.send_message(message.from_user.id, str(response[i]))
                    for j in range(len(response[i].photos)):
                        bot.send_photo(message.from_user.id, response[i].photos[j])
                break
        except ValueError:
            bot.send_message(message.from_user.id,
                             'Количество должно быть числом')
            incorrect_photo_quantity(message)
            break
