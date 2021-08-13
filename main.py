import requests
import telebot
from telebot.types import Message

bot = telebot.TeleBot('1948694899:AAHljPZ9B4-EP98eFDVyGMFvtOjHjuQKw1A')

url = 'https://hotels4.p.rapidapi.com/locations/search'

headers = {
    'x-rapidapi-key': '79e4d2058cmsh961ab2d335b0dbcp19d6b6jsn096e1f1fdf24',
    'x-rapidapi-host': 'hotels4.p.rapidapi.com'
}

if __name__ == '__main__':

    def example():

        """Выводит результат тестового запроса через API hotels.com"""

        querystring = {'query': 'new york', 'locale': 'en_US'}

        response = requests.request('GET', url, headers=headers, params=querystring)

        return response


    @bot.message_handler(content_types=['text'])
    def get_text_messages(message: Message) -> None:

        """Обработчик входящих сообщений
        На 'Привет' и '/hello-world' отвечает приветствием'
        /example выводит результат тестового запроса через API hotels.com
        /help выводит список возможных команд
        При некорректном вводе печатается сообщение об ошибке"""

        if message.text == 'Привет':
            bot.send_message(message.from_user.id, 'Привет!\n'
                                                   'Я - Telegram-bot с API Hotels.com на python\n'
                                                   'Помогу найти подходящее размещение\n'
                                                   'Список команд доступен по /help')
        elif message.text == 'hello-world':
            bot.send_message(message.from_user.id, 'Привет!\n'
                                                   'Я - Telegram-bot с API Hotels.com на python\n'
                                                   'Помогу найти подходящее размещение\n'
                                                   'Список команд доступен по /help')
        elif message.text == '/help':
            bot.send_message(message.from_user.id, 'Привет!\n'
                                                   'Я - Telegram-bot с API Hotels.com на python\n'
                                                   'Помогу найти подходящее размещение\n'
                                                   'Список доступных команд:\n'
                                                   'Привет и /hello-world - выводят приветствие\n'
                                                   '/example выводит результат тестового запроса через API hotels.com'
                                                   '/help - список возможных команд')
        elif message.text == '/example':
            bot.send_message(message.from_user.id, example())
        else:
            bot.send_message(message.from_user.id, 'Что-то не так с вводом. Список команд доступен по /help')


    bot.polling(none_stop=True, interval=0)
