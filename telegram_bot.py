from dotenv import load_dotenv
from API_requests import example

import telebot as telebot
import os

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))


@bot.message_handler(content_types=['text'])


def get_text_messages(message: telebot.types.Message) -> None:
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


class TelegramBot:
    pass
