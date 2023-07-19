import os
import telebot
import youtube_dl
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

def delete_channel_id(chat_id):
    # Видалити ідентифікатор каналу з бази даних або файлової системи
    # Приклад: видалення зі словника user_channels
    user_channels.pop(chat_id, None)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привіт, я бот для конвертування відео з YouTube в аудіофайли! Для початку Вам потрібно добавити мене в свій телеграм канал у якості адміністратора та дати мені всі можливі дозволи, щоб я міг відразу розміщувати музику =)  Нажміть '/register' для реєстрації вашого каналу через '@ідентифікатор', якщо бажаєте відписати канал нажміть '/unregister'.")

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
    if message.text.startswith('https://www.youtube.com/') or message.text.startswith('https://youtu.be/'):
        # Отримати ідентифікатор відео з посилання
        video_id = message.text.split('/')[-1]
        if 'youtu.be' in video_id:
            video_id = video_id.split('/')[-1]

        # Створити посилання на відео
        youtube_link = f'https://www.youtube.com/watch?v={video_id}'

        # Створити об'єкт YouTubeDL з опціями для завантаження аудіофайлу у форматі mp3
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'audio.mp3',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        ydl = youtube_dl.YoutubeDL(ydl_opts)

        try:
            # Завантажити аудіофайл з YouTube
            ydl.download([youtube_link])
        except Exception as e:
            bot.reply_to(message, f"Помилка при завантаженні аудіофайлу: {e}")
            return

        chat_id = message.chat.id
        channel_id = get_channel_id(chat_id)
        if channel_id:
            # Перевірити, чи бот є адміністратором каналу
            try:
                chat_member = bot.get_chat_member(channel_id, bot.get_me().id)
                if chat_member and chat_member.status == 'administrator':
                    # Відправити аудіофайл на канал
                    bot.send_audio(channel_id, open('audio.mp3', 'rb'), title=ydl.extract_info(youtube_link, download=False)['title'])
                    bot.reply_to(message, "Аудіофайл успішно відправлено на ваш канал!")
                else:
                    bot.reply_to(message, "Бот повинен бути адміністратором каналу для відправки файлів.")
            except ApiTelegramException as e:
                bot.reply_to(message, f"Помилка при отриманні інформації про канал: {e}")
        else:
            # Відправити аудіофайл користувачеві
            bot.send_audio(chat_id, open('audio.mp3', 'rb'), title=ydl.extract_info(youtube_link, download=False)['title'])
            bot.reply_to(message, "Аудіофайл успішно конвертовано і відправлено вам!")
        
        # Видалити аудіофайл з локального сховища
        if os.path.exists('audio.mp3'):
            os.remove('audio.mp3')
    else:
        # Відправити повідомлення про помилку
        bot.reply_to(message, "Будь ласка, надішліть посилання на YouTube.")


bot.polling()
