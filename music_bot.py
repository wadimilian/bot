import os
import telebot
from pytube import YouTube

bot_token = '5898259885:AAGXE1goXG-4uD_XU9w3JyzhI2d9aVZNuUs'
bot = telebot.TeleBot(bot_token)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Перевірка, чи є посилання на YouTube у повідомленні
    if 'youtube.com' in message.text or 'youtu.be' in message.text:
        try:
            # Створення об'єкту YouTube з посиланням
            yt = YouTube(message.text)

            # Отримання першого аудіопотоку з відео
            audio_stream = yt.streams.filter(only_audio=True).first()

            # Завантаження аудіопотоку як файл mp4
            audio_stream.download(filename='audio.mp4')

            # Відправка аудіофайлу користувачеві
            audio_file = open('audio.mp4', 'rb')
            bot.send_audio(message.chat.id, audio_file)

            # Видалення аудіофайлу з локального сховища
            os.remove('audio.mp4')

        except Exception as e:
            print(f"Помилка: {e}")

    else:
        bot.reply_to(message, "Будь ласка, надішліть посилання на YouTube відео.")

bot.polling()
