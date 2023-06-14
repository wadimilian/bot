from telegram.ext import Updater, CommandHandler

# Функція, яка буде виконуватися при отриманні команди /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привіт! Я бот привітання. Як справи?")

def main():
    # Створення екземпляру Updater з токеном вашого бота
    updater = Updater(token='5898259885:AAGXE1goXG-4uD_XU9w3JyzhI2d9aVZNuUs', use_context=True)
    dispatcher = updater.dispatcher

    # Реєстрація обробника команди /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Запуск бота
    updater.start_polling()

    # Зупинка бота при натисканні Ctrl + C
    updater.idle()

if __name__ == '__main__':
    main()
