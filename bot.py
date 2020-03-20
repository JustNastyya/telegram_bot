import telebot
# from stuff import *
from mysql import connector


# https://habr.com/ru/post/350648/ time when i will need to wait for answer will come and then...

bot = telebot.TeleBot('700325444:AAHrC3QgLOXWATmDmbIUq8n4XCjo0MC4bx0')

# ______________databases init section______________
answer = ''

# mysql://b3e60dc561c36c:9d3e7e2b@eu-cdbr-west-02.cleardb.net/heroku_8e1964d3a4dc12f?reconnect=true

mydb = connector.connect(
    host='us-cdbr-gcp-east-01.cleardb.net',  # ?????
    user='b6a98ca53090be',  # "b3e60dc561c36c",
    passwd='aa2d7024',
    database='gcp_7c9c726b38df1d89673f'
)

cursorDB = mydb.cursor()
#cursorDB.execute('SELECT * FROM usersMain')
#print(list(cursorDB))

# non official zone

#cursorDB.execute("SHOW DATABASES")
#print([i for i in cursorDB])

#cursorDB.execute('DROP TABLE justnastyaa')
#cursorDB.execute('SELECT * FROM usersMain')
#print([i for i in cursorDB])

# bot.send_message()
'''
cursorDB.execute("GRANT ALL PRIVILEGES ON Growth.* TO 'b6a98ca53090be'@'%' WITH GRANT OPTION")
cursorDB.execute("FLUSH PRIVILEGES")

'''
# cursorDB.execute('CREATE DATABASE Growth')
cursorDB.execute("SHOW TABLES")
usersList = [i[0] for i in cursorDB if i[0].lower() != 'usersmain'] # change to []

cursorDB.execute("CREATE TABLE IF NOT EXISTS usersMain (\
                username VARCHAR(255), \
                sinceLast TINYINT(255), \
                medium FLOAT(10, 2),\
                testON BOOLEAN)")


keyboardMain = telebot.types.ReplyKeyboardMarkup(True)
keyboardMain.row('проверить знание', 'познать таинство', 'ничего не понял', 'нашел ошибку')

keyboardYesOrNo = telebot.types.ReplyKeyboardMarkup(True)
keyboardYesOrNo.row('да', 'нет', 'никогда не спрашивать')


def askTest(message):
    global answer
    answer = message.text
    if answer.lower() == 'да':
        msg = bot.send_message(message.chat.id, 'отлично, начинаем (тест)')
    elif answer.lower() == 'нет':
        msg = bot.send_message(message.chat.id, 'ладно, как хочешь', reply_markup=keyboardMain)
    else:
        msg = bot.send_message(message.chat.id, 'хорошо, не буду мешать, можешь исправить это в настройках',reply_markup=keyboardMain)


def test():
    pass


@bot.message_handler(commands = ['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Приветствую, я помогу тебе познать таинство схемы Горнера. Хочешь ли ты получить бесценные знания или проверить свои?', reply_markup=keyboardMain)


@bot.message_handler(content_types = ['text'])
def send_text(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет, брооо')
    elif message.text.lower() == 'список':
        cursorDB.execute('SELECT * FROM usersMain')
        bot.send_message(message.chat.id, [i for i in cursorDB])
    else:
        bot.reply_to(message, 'Таких иероглифов нет в моих писаньях')
    
    nickname = message.from_user.username
    if message.from_user.username.lower() not in usersList:
        cursorDB.execute(f'INSERT INTO usersMain (username, sinceLast, medium, testON) VALUES ("{nickname}", 0, 6.0, 1)')

        cursorDB.execute(f"CREATE TABLE IF NOT EXISTS {nickname} (\
                                        id INT AUTO_INCREMENT PRIMARY KEY,\
                                        task VARCHAR(255),\
                                        mark INT(255), \
                                        date DATE)")
        usersList.append(message.from_user.username)


    else:
        cursorDB.execute(f'SELECT testON FROM usersMain WHERE username="{nickname.lower()}"')
        oy = list(cursorDB)
        # print(oy[0][0])  # i need this!!!
        if oy[0][0]:
            cursorDB.execute(f'SELECT sinceLast FROM usersMain WHERE username="{nickname}"')
            previousCounter = list(cursorDB)[0][0]
            # print(previousCounter)

            if previousCounter >= 6:  # change to 15
                msg = bot.send_message(message.chat.id, 'вы накопили какое то кол-во знаний, не хотите ли себя испытать?', reply_markup=keyboardYesOrNo)
                cursorDB.execute(f'UPDATE usersMain SET sinceLast=0 WHERE username="{nickname}"')
                mydb.commit()

                bot.register_next_step_handler(msg, askTest)
                if answer.lower() == 'да':
                    test()
                elif answer.lower() == 'никогда не спрашивать':
                    cursorDB.execute(f'UPDATE usersMain SET testON=0 WHERE username="{nickname}"')
            else:
                cursorDB.execute(f'UPDATE usersMain SET sinceLast={previousCounter + 1} WHERE username="{nickname}"')
    mydb.commit()


bot.polling(none_stop=True)