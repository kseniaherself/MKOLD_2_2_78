'''Телеграм-бот:
бот спрашивает у пользователя анкету по типологии признака "старый"
(http://lextyp.org/anketas/) на русском языке
(вопросы на русском, а для какого языка отвечает пользователь, надо уточнить)
и записывает полученные данные, сводная информация по ответам показывается по специальной команде.. '''

import flask
import telebot
import conf
import re
import random
import copy


# создаём массив с вопросами.
# потом создаётся словарь пользователь+его ответы, где каждый новый пользователь, заполнивший анкету – ключ в словаре

WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.TOKEN)

bot = telebot.TeleBot(conf.TOKEN, threaded=False)

bot.remove_webhook()

bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)

app = flask.Flask(__name__)


# !!! функции заготовки для обработки запросов

#функция возвращает массив с вопросами
def questionnaire_arr():
    fl = open('old_questions.txt')
    questions = []
    for line in fl:
        line = re.sub('\n', '', line)
        questions.append(line)
    fl.close()
    return questions


data_dict = {}      # оставим эту переменную "глобальной"
# функция готовит словарь
def question_dict():
    questions = questionnaire_arr()
    questions_dict = {}
    i = 0
    for q in questions:
        questions_dict[q] = i
        i += 1
    return questions_dict


questions_dict = question_dict()
#questions_dict = {'q0':0, 'q1':1, 'q2':2, 'q3':3, 'q4':4}
dict_keys_and_values = {v: k for k, v in questions_dict.items()}
keys = list(dict_keys_and_values.keys())


def writing_ids(user_id):
    ids_dict = {}
    if user_id in ids_dict:
        return ids_dict[id_user]
    else:
        ids_dict[user_id] = []
        return ids_dict[user_id]


#функция даёт информацию (статистику) о языках
def languages():
    languages_list = []
    languages_dict = {}
    for el in data_dict:
        languages_list.append(data_dict[el][0])
    #филлер
    for i in languages_list:
        if i not in languages_dict:
            languages_dict[i] = [i]
        else:
            languages_dict[i].append(i)
    for elem in languages_dict:
        languages_dict[elem] = len(languages_dict[elem])
    return languages_dict


#функция подготавливает информацию для записи в файл
def make_data():
    questions = questionnaire_arr()
    data1 = copy.deepcopy(data_dict)
    for e in data1:
        for n in range(0,18):
            if n not in data1[e]:
                data1[e][n] = ''
    data2 = 'id\t'
    for elem in questions:
        data2 += elem + '\t'
    data2 += '\n'
    for el in data1:
        users = str(el) + '\t'
        for j in sorted(data1[el].keys()):
            users += data1[el][j] + '\t'
        data2 += users + '\n'
    print(data2)
    return data2



# собственно бот

# функция старт, создаёт значение нового пользователя и записывает к нему данные. иначе: отказывает в обработке
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "привет! это анкета собирает информацию о значении 'старый'. \r\n ВНИМАНИЕ! Анкету заполнить можно только один раз. \r\n вопросы будут задаваться на русском языке. ответьте на вопросы, которые будут появляться: ваш родной язык; далее, пожалуйста, переведите предложения на ваш родной язык. \r\n чтобы узать больше: /help. \r\n Для начала опроса вызовите /askme")
    if message.chat.id in data_dict:
        bot.send_message(message.chat.id, "Форма может быть заполнена только один раз! Вы уже отпрвили сови ответы")
    else:
        bot.send_message(message.chat.id, dict_keys_and_values[0])
        user_id = message.chat.id
        data_dict[user_id] = {0: ''}


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "этот бот собирает анкету типологического признака 'старый'. Подробней: http://lextyp.org/anketas/ ")


# функция запрашивает и записывает (распределяет) ответы
@bot.message_handler(commands=['askme'])
def get_answers_command(message):
    user_id = message.chat.id
    ids = writing_ids(user_id)

    if len(data_dict[user_id]) != 18:
        order_n = random.choice(keys)
        while order_n in data_dict[user_id]:
            order_n = random.choice(keys)
        if order_n not in data_dict[user_id]:
            ids.append(order_n)
            bot.send_message(message.chat.id, "{}/17. {}".format(len(ids),dict_keys_and_values[order_n]))
            answer = (message.text).lower()
            if len(data_dict[user_id]) == 1:
                data_dict[user_id][0] = answer
                data_dict[user_id][order_n] = ''
            else:
                data_dict[user_id][ids[-2]] = answer
                data_dict[user_id][order_n] = ''
        else:
            bot.send_message(message.chat.id, '~~error~~')
    else:
        bot.send_message(message.chat.id, 'ответы записаны, спасибо!')
        if data_dict[message.chat.id][ids[-1]] == '':
            ans = (message.text).lower()
            data_dict[user_id][ids[-1]] = ans


# функция выдаёт статистику и информацию
@bot.message_handler(commands=['info'])
def stats(message):
    langs = languages()
    st = ''
    ids = writing_ids(message.chat.id)

    for element in langs:
        st += element + 'представлен ' + str(langs[element]) + 'носитель(ями)' '\r\n'

    participants = len(data_dict)
    bot.send_message(message.chat.id, "Участиников всего: {}".format(participants))

    bot.send_message(message.chat.id, "чтобы получить файл со всей  нформацией, вызовите команду /file")

    if len(ids) != 0 and len(data_dict) != 0 and data_dict[message.chat.id][ids[-1]] == '':
        bot.send_message(message.chat.id, dict_keys_and_values[ids[-1]])
    elif len(ids) == 0 and len(data_dict) != 0:
        bot.send_message(message.chat.id, dict_keys_and_values[0])


# функция для получения файла со всеми данными
@bot.message_handler(commands=['file'])
def get_file(message):
    data2 = make_data()

    with open('/home/xenja1ks/mysite/old_field_data.csv', 'w', encoding='utf-8') as fle:
        fle.write(data2)
    f1 = open('/home/xenja1ks/mysite/old_field_data.csv', 'rb')
    bot.send_document(message.chat.id, f1)
    ids = writing_ids(message.chat.id)


# пустая главная страничка для проверки
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'oks'


# обрабатываем вызовы вебхука = функция, которая запускается, когда к нам постучался телеграм
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():

    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)
