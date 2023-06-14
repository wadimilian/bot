import os
import telebot
from pytube import YouTube
from telebot.types import ChatMember
from telebot.apihelper import ApiTelegramException

bot = telebot.TeleBot('5898259885:AAGXE1goXG-4uD_XU9w3JyzhI2d9aVZNuUs')


# Приклад збереження ідентифікаторів каналів у словнику
user_channels = {}

def save_channel_id(chat_id, channel_id):
    # Зберегти ідентифікатор каналу у базі даних або файловій системі
    # Приклад: збереження у словнику user_channels
    user_channels[chat_id] = channel_id

def get_channel_id(chat_id):
    # Отримати ідентифікатор каналу з бази даних або файлової системи
    # Приклад: отримання зі словника user_channels
    return user_channels.get(chat_id)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привіт, я бот для конвертування відео з YouTube в аудіофайли! /n Введіть "/register" для реєстрації вашого каналу ")

@bot.message_handler(commands=['register'])
def register_channel(message):
    chat_id = message.chat.id
    bot.reply_to(message, "Будь ласка, введіть ідентифікатор вашого каналу:")
    if message.reply_to_message:
        bot.register_next_step_handler(message.reply_to_message, save_channel)
    else:
        bot.register_next_step_handler(message, save_channel)

def save_channel(message):
    chat_id = message.chat.id
    channel_id = message.text
    save_channel_id(chat_id, channel_id)
    bot.reply_to(message, "Канал зареєстровано!")

@bot.message_handler(func=lambda msg: True)
def convert_and_send(message):
    # Перевірити, чи є повідомлення посиланням на YouTube
    if message.text.startswith('https://www.youtube.com/'):
        # Створити об'єкт YouTube з посиланням
        yt = YouTube(message.text)
        # Отримати перший аудіопотік з відео
        audio_stream = yt.streams.filter(only_audio=True).first()
        # Завантажити аудіопотік як файл mp4
        audio_stream.download(filename='audio.mp4')

        chat_id = message.chat.id
        channel_id = get_channel_id(chat_id)
        if channel_id:
            # Перевірити, чи бот є адміністратором каналу
            try:
                chat_member = bot.get_chat_member(channel_id, bot.get_me().id)
                if chat_member and chat_member.status == 'administrator':
                    # Відправити аудіофайл на канал
                    bot.send_audio(channel_id, open('audio.mp4', 'rb'), title=yt.title)
                    bot.reply_to(message, "Аудіофайл успішно відправлено на ваш канал!")
                else:
                    bot.reply_to(message, "Бот повинен бути адміністратором каналу для відправки файлів.")
            except ApiTelegramException as e:
                bot.reply_to(message, f"Помилка при отриманні інформації про канал: {e}")
        else:
            bot.reply_to(message, "Будь ласка, зареєструйте свій канал за допомогою команди /register.")
        
        # Видалити аудіофайл з локального сховища
        os.remove('audio.mp4')
    else:
        # Відправити повідомлення про помилку
        bot.reply_to(message, "Будь ласка, надішліть посилання на YouTube.")


bot.polling()
