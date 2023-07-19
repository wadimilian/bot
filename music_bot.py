import os
import telebot
from pytube import YouTube
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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

def delete_channel_id(chat_id):
    # Видалити ідентифікатор каналу з бази даних або файлової системи
    # Приклад: видалення зі словника user_channels
    user_channels.pop(chat_id, None)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.reply_to(message, "Привіт, я бот для конвертування відео з YouTube в аудіофайли! Для початку Вам потрібно добавити мене в свій телеграм канал у якості адміністратора та дати мені всі можливі дозволи, щоб я міг відразу розміщувати музику =)  Нажміть '/register' для реєстрації вашого каналу через '@ідентифікатор', якщо бажаєте відписати канал нажміть '/unregister' ")

    # Отримати ідентифікатор каналу
    channel_id = get_channel_id(chat_id)
    if channel_id:
        # Відправити кнопки підписки і відміни підписки разом з повідомленням
        keyboard = create_buttons(channel_id)
        bot.send_message(chat_id, "Ви можете підписатися на канал, натиснувши кнопку нижче:", reply_markup=keyboard)

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

@bot.message_handler(commands=['unregister'])
def unregister_channel(message):
    chat_id = message.chat.id
    channel_id = get_channel_id(chat_id)
    if channel_id:
        delete_channel_id(chat_id)
        bot.reply_to(message, "Канал видалено!")
    else:
        bot.reply_to(message, "Ви не маєте зареєстрованого каналу.")

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
            # Відправити аудіофайл користувачеві
            bot.send_audio(chat_id, open('audio.mp4', 'rb'), title=yt.title)
            bot.reply_to(message, "Аудіофайл успішно конвертовано і відправлено вам!")
        
        # Видалити аудіофайл з локального сховища
        os.remove('audio.mp4')
    else:
        # Відправити повідомлення про помилку
        bot.reply_to(message, "Будь ласка, надішліть посилання на YouTube.")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = call.data
    chat_id = call.message.chat.id
    channel_id = get_channel_id(chat_id)

    if data == 'subscribe':
        if not channel_id:
            bot.send_message(chat_id, "Будь ласка, введіть ідентифікатор вашого каналу:")
            bot.register_next_step_handler(call.message, save_channel)
        else:
            bot.send_message(chat_id, "Ви вже підписані на канал!")
    elif data == 'unsubscribe':
        if channel_id:
            delete_channel_id(chat_id)
            bot.send_message(chat_id, "Ви успішно відписалися від каналу.")
        else:
            bot.send_message(chat_id, "Ви не маєте зареєстрованого каналу.")

def create_buttons(channel_id):
    keyboard = InlineKeyboardMarkup()
    subscribe_button = InlineKeyboardButton(text='Підписатися', callback_data='subscribe')
    unsubscribe_button = InlineKeyboardButton(text='Відписатися', callback_data='unsubscribe')
    keyboard.row(subscribe_button, unsubscribe_button)
    return keyboard

bot.polling()

