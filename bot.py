import telebot
from texts import *
from EqSolution import * 
from mysql import connector
from random import choice

# for shitgenerator
from swift import words
from random import choice
from string import punctuation
import numpy as np

words = np.array(words, dtype='<U32')


def generatetext(previous):
    my_arr = np.where(words == previous)[0]

    my_arr += 1
    chosen_ind = np.random.choice(my_arr)
    return words[chosen_ind]


def cleverJoin(smth):
    ans = smth[0]
    for i in smth[1:]:
        if i in punctuation:
            ans += i
        else:
            ans = ans + ' ' + i
    return ans


def shitMain(n):
    first = choice(words)
    ans = [first.capitalize()]
    for _ in range(n - 1):
        flag = True
        while flag:
            try:
                first = generatetext(first)
                ans.append(first)
                flag = False
            except IndexError:
                pass
            except ValueError:
                pass

    return cleverJoin(ans)

# to do list: recursion in questions, hole test system, code apperience, web-hooks, texts grammar and style

# https://habr.com/ru/post/350648/ time when i will need to wait for answer will come and then...

bot = telebot.TeleBot(token)

# ______________databases init section______________

# mysql://b50331da36c2ee:ea3c19f4@eu-cdbr-west-02.cleardb.net/heroku_f26f7c5be56f7dc?reconnect=true
mydb = connector.connect(
    host='eu-cdbr-west-02.cleardb.net',  # ?????
    user='b50331da36c2ee',  # "b3e60dc561c36c",
    passwd='ea3c19f4',
    database='heroku_f26f7c5be56f7dc'
)

cursorDB = mydb.cursor()

# cursorDB.execute('SELECT * FROM usersMain')
# print(list(cursorDB))

cursorDB.execute("CREATE TABLE IF NOT EXISTS usersMain (\
                username VARCHAR(255), \
                sinceLast TINYINT(255), \
                medium FLOAT(10, 2),\
                testON BOOLEAN,\
                askTest INT)")

# locals
cursorDB.execute("SHOW TABLES")
usersList = set([i[0] for i in cursorDB if i[0].lower() != 'usersmain'])
print(usersList)  # so that i could know when the show begins
answer = ''
isRunning = False


# ______________keyboards init section______________
keyboardMain = telebot.types.ReplyKeyboardMarkup(True)
keyboardMain.row('проверить знание', 'познать таинство', 'ничего не понял')
keyboardMain.row('нашел ошибку', 'дополнительно')

keyboardYesNoNever = telebot.types.ReplyKeyboardMarkup(True)
keyboardYesNoNever.row('да', 'нет', 'никогда не спрашивать')

keyboardYesNo = telebot.types.ReplyKeyboardMarkup(True)
keyboardYesNo.row('да', 'нет')

keyboardSettings = telebot.types.ReplyKeyboardMarkup(True)  # reply to main
keyboardSettings.row('очистить мою историю', 'настройки теста')
keyboardSettings.row('показать мою статистику', 'обратно')  # pass show statistics

keyboardTestSettings = telebot.types.ReplyKeyboardMarkup(True)  # reply to settings
keyboardTestSettings.row('изменить частоту вопроса о тесте', 'провести тест сейчас')
keyboardTestSettings.row(
    'отключить/включить опцию автоматический предлагать провести тест'
    )
keyboardTestSettings.row('обратно!')


def createEnviromentForNewUser(nickname):
    cursorDB.execute(f'INSERT INTO usersMain \
                    (username, sinceLast, medium, testON, askTest)\
                    VALUES ("{nickname}", 0, 6.0, 1, 15)')

    cursorDB.execute(f"CREATE TABLE IF NOT EXISTS {nickname} (\
                    id INT AUTO_INCREMENT PRIMARY KEY,\
                    task VARCHAR(255),\
                    mark INT(255), \
                    date DATE)")
    usersList.add(nickname.lower())
    mydb.commit()


def askTest(message):
    global answer, isRunning
    answer = message.text

    if answer.lower() == 'да':
        msg = bot.send_message(
            message.chat.id,
            'отлично, начинаем (тест)'
            )
        test()
        isRunning = False

    elif answer.lower() == 'нет':
        msg = bot.send_message(
            message.chat.id, 
            'ладно, как хочешь', 
            reply_markup=keyboardMain
            )
        isRunning = False

    elif answer.lower() == 'никогда не спрашивать':
        cursorDB.execute(
            f'UPDATE usersMain SET testON=0\
                WHERE username="{message.from_user.username}"'
            )
        msg = bot.send_message(
            message.chat.id, wontBotherText, 
            reply_markup=keyboardMain
            )
        isRunning = False

    else:
        bot.send_message(
            message.chat.id, 
            'вы неправильно ответили(придумать что нибудь здесь)',
            reply_markup=keyboardTestSettings
            )
        isRunning = False  # yeah, i know i am such an idiot


def test():
    pass


def askDelete(message):
    global answer, isRunning
    answer = message.text
    if answer.lower() == 'да':
        nickname = message.from_user.username
        msg = bot.send_message(
            message.chat.id,
            'удаляю, пожалуйста подождите...'
            )
        cursorDB.execute(f'DROP TABLE {nickname}')
        cursorDB.execute(
            f"DELETE FROM usersMain WHERE username='{nickname}'"
            )
        usersList.discard(nickname.lower())
        bot.send_message(message.chat.id,
                        'Ваша история была удалена',
                        reply_markup=keyboardMain
                        )
        isRunning = False

    elif answer.lower() == 'нет':
        msg = bot.send_message(
            message.chat.id,
            'ладно, тогда продолжаем', 
            reply_markup=keyboardMain
            )
        isRunning = False

    else:
        bot.send_message(
            message.chat.id,
            'вы неправильно ответили(придумать что нибудь здесь)', 
            reply_markup=keyboardTestSettings
            )
        isRunning = False  # shouldnt be here, add recursion, idiot!


def clearHistory(message):
    global isRunning
    msg = bot.send_message(
        message.chat.id, deleteHistoryQuestion, 
        reply_markup=keyboardYesNoNever
        )
    bot.register_next_step_handler(msg, askDelete)
    isRunning = True


def changeTestRegularity(message):
    global isRunning
    answer = message.text.lower()

    if answer.isdigit() and int(answer) > 0 and int(answer) < 2000000000:
        cursorDB.execute(
            f'UPDATE usersMain SET askTest={int(answer)}\
                WHERE username="{message.from_user.username}"')
        bot.send_message(
            message.chat.id, 
            f'Теперь я буду предлагать вам пройти тест раз в {answer} раз', 
            reply_markup=keyboardTestSettings
            )
        isRunning = False

    elif answer == 'q':
        bot.send_message(
            message.chat.id, 
            'Ладно, продолжаем', 
            reply_markup=keyboardTestSettings
            )
        isRunning = False

    else:
        bot.send_message(
            message.chat.id, 
            'Вы неправильно ввели число', 
            reply_markup=keyboardTestSettings
            )
        isRunning = False  # idiot!!! when ar knot going to make working system?!


def turnOnOffTest(message):
    nickname = message.from_user.username
    cursorDB.execute(
        f'SELECT testON FROM usersMain\
        WHERE username="{nickname.lower()}"'
        )
    testON = list(cursorDB)[0][0]
    cursorDB.execute(
        f'UPDATE usersMain SET testON={abs(testON - 1)}\
        WHERE username="{message.from_user.username}"'
        )

    if testON:
        bot.send_message(
            message.chat.id, 
            wontBotherSettingsText, 
            reply_markup=keyboardTestSettings
            )
    else:
        bot.send_message(
            message.chat.id, 
            willbotherSettingsText, 
            reply_markup=keyboardTestSettings
            )


def showInfo(message):  # for hacker mode
    cursorDB.execute('SELECT * FROM usersMain')
    ListPeople = '\n'.join(' '.join(str(j) for j in i) for i in list(cursorDB)) + '\n'
    cursorDB.execute('SHOW TABLES')
    ListPeople = '-В usersMain: \n' + ListPeople + '-ЛИЧНЫЕ ТАБЛИЦЫ: ' + '\n'
    ListPeople += '\n'.join(str(i) for i in list(cursorDB)) + '\n'
    ListPeople += '-ЛОКАЛЬНЫЙ СПИСОК: \n' + '\n'.join(i for i in usersList)
    bot.send_message(message.chat.id, ListPeople)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, greeting, reply_markup=keyboardMain)


@bot.message_handler(content_types=['text'])
def send_text(message):
    global isRunning
    ms = message.text.lower()
    if ms == 'привет':
        bot.send_message(message.chat.id, 'Привет, брооо')
    
    elif ' ' in ms and ms[:ms.index(' ')] == 'сосиска':
        wordsAmount = ms[ms.index(' ') + 1:]
        if wordsAmount.isdigit():
            bot.send_message(message.chat.id, shitMain(int(wordsAmount)))
        else:
            bot.send_message(message.chat.id, specialForVeronika)

    elif ms == 'проверить знание':
        bot.send_message(message.chat.id, checkKnowledge)

    elif ms == 'ничего не понял':
        bot.send_message(message.chat.id, understoodNothing)

    elif ms == 'нашел ошибку':
        bot.send_message(message.chat.id, foundMistake)

    elif ms == 'познать таинство':
        bot.send_message(message.chat.id, theoryText)
    
    elif ms in ['дополнительно', 'обратно!']:
        bot.send_message(message.chat.id, settingsText,
                        reply_markup=keyboardSettings)
    
    elif ms == 'очистить мою историю':
        clearHistory(message)
    
    elif ms == 'изменить частоту вопроса о тесте':
        msg = bot.send_message(message.chat.id, enterNumberOrQ)
        bot.register_next_step_handler(msg, changeTestRegularity)
        isRunning = True
    
    elif ms == 'провести тест сейчас':
        isRunning = True
        test()
        isRunning = False

    elif ms == 'настройки теста':
        bot.send_message(message.chat.id, 'Это насройки теста!',
                        reply_markup=keyboardTestSettings)
    
    elif ms == 'отключить/включить опцию автоматический предлагать провести тест':
        turnOnOffTest(message)
    
    elif ms == 'обратно':
        bot.send_message(message.chat.id, 'как хочешь',
                        reply_markup=keyboardMain)

    elif ms == 'я тебя люблю':  # secret unexpected message
        bot.send_sticker(message.chat.id, 'CAADAgADZgkAAnlc4gmfCor5YbYYRAI')

    elif 'check' in ms:
        bot.send_message(message.chat.id, main(ms))

    elif ms == 'список':
        showInfo(message)

    else:
        bot.reply_to(message, 'Таких иероглифов нет в моих писаньях')
    
    # database checking for updates section
    nickname = message.from_user.username
    if nickname.lower() not in usersList:  # new user to the bot
        createEnviromentForNewUser(nickname)

    elif not(isRunning):  # count all users actions and insert into a table 
        cursorDB.execute(
            f'SELECT testON FROM usersMain WHERE username="{nickname.lower()}"'
            )
        testON = list(cursorDB)
        print('testON: ', testON[0][0])

        if testON[0][0]:
            cursorDB.execute(
                f'SELECT sinceLast, askTest FROM usersMain WHERE username="{nickname}"'
                )
            info = list(cursorDB)
            previousCounter = info[0][0]
            testRegularity = info[0][1]
            print('previous counter: ', previousCounter)

            if previousCounter >= testRegularity:  # by defaut 15
                msg = bot.send_message(
                    message.chat.id, testQuestion, reply_markup=keyboardYesNoNever
                    )
                cursorDB.execute(
                    f'UPDATE usersMain SET sinceLast=0 WHERE username="{nickname}"'
                    )
                mydb.commit()

                bot.register_next_step_handler(msg, askTest)
                isRunning = True
            else:
                cursorDB.execute(
                    f'UPDATE usersMain SET sinceLast={previousCounter + 1}\
                        WHERE username="{nickname}"'
                        )
            mydb.commit()


bot.polling(none_stop=True)