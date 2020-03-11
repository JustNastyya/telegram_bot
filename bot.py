import telebot

token = '700325444:AAHrC3QgLOXWATmDmbIUq8n4XCjo0MC4bx0'
bot = telebot.TeleBot(token)


keyboard1 = telebot.types.ReplyKeyboardMarkup(True)
keyboard1.row('проверить знание', 'познать таинство', 'ничего не понял', 'нашел ошибку')


@bot.message_handler(commands = ['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Приветствую, я помогу тебе познать таинство схемы Горнера. Хочешь ли ты получить бесценные знания или проверить свои?', reply_markup = keyboard1)

@bot.message_handler(content_types = ['text'])
def send_text(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет, брооо')
    else:
        bot.reply_to(message, 'Таких иероглифов нет в моих писаньях')


bot.polling(none_stop=True)