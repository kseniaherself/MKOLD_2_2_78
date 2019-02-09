'''Телеграм-бот:
бот спрашивает у пользователя анкету по типологии признака "старый"
(http://lextyp.org/anketas/) на русском языке
(вопросы на русском, а для какого языка отвечает пользователь, надо уточнить)
и записывает полученные данные, сводная информация по ответам показывается по специальной команде.. '''

import flask
import telebot
import conf
import re
#import random
#import copy


# создаём массив с вопросами.
# потом создаётся словарь пользователь+его ответы, где каждый новый пользователь, заполнивший анкету – ключ в словаре

WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.TOKEN)

bot = telebot.TeleBot(conf.TOKEN, threaded=False)

bot.remove_webhook()

bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)

app = flask.Flask(__name__)

#функция возвращает массив с вопросами, создаёт и записывает в файл про результаты. возвращает массив с вопросами
def questionnaire_arr():
    fl = open('/home/xenja1ks/mysite/old_questions.txt', 'r') #
    questions = ['старт']
    f = open('/home/xenja1ks/mysite/results.csv', 'a')  #
    f.write('id \t')
    for line in fl:
        line = re.sub('\n', '', line)
        f.write(line + '\t')
        questions.append(line)
    f.write('\n')
    f.close()
    fl.close()
    return questions

questions = questionnaire_arr() # переменная с вопросами
q_len = len(questions) + 1

ids_collection_d = {} # словарь куда потом всё будет записываться


# функция которая записывает ответы в файл
def write_in_file(us_dict, uset_id):
    f = open('/home/xenja1ks/mysite/results.csv', 'a') #   # файл открыт на дозапись результатов в процессе опроса
    answer = str(uset_id) + '\t'
    for i in range(0, q_len):
        a = us_dict[i]
        if a != '':
            if a == '/start':
                print('брынь брынь')
            else:
                answer += str(a) + '\t'
        else:
            answer += '---' + '\t'
    f.write(answer + '\n')
    f.close()


# команда приветствует и проверяет участвовал ли человек в опросе. Если не участвовал, предлагает команду для опроса
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "привет! это анкета собирает информацию о значении 'старый'. \r\n ВНИМАНИЕ! Анкету рекомендуется заполнять только один раз (если хотите пройти опрос ещё раз: /start). \r\n чтобы узнать больше: /info. \r\n получить файл: /getfile. \r\n получить ответы в распечатанном виде: /getanswers . \r\n \r\n предложения будут появляться на русском языке, переводите их на ваш родной язык, но сначала напишите Ваш язык") # \r\n Для начала опроса вызовите /askme")
    user_id = message.chat.id
    lang = message.text
    ids_collection_d[user_id] = {0: lang}


# команда даёт информацию и ссылку на лекстип
@bot.message_handler(commands=['info'])
def info_command(message):
    bot.send_message(message.chat.id, "этот бот собирает анкету типологического признака 'старый'. \r\n Подробней: http://lextyp.org/anketas/ ")


# команда проводит анкетирование
@bot.message_handler(commands=['askme'])    #, func=lambda m: True)
def get_answers(message):
    user_id = message.chat.id
    if len(ids_collection_d[user_id]) != q_len:
        ques = questions[len(ids_collection_d[user_id])]
        bot.send_message(message.chat.id, ques)


@bot.message_handler(content_types=['text'])    #, func=lambda m: True)
def get_answers2(message):
    user_id = message.chat.id
    use_len = len(ids_collection_d[user_id]) #- 1        # {user_id: {1: ответ, 2: ответ, 3: ответ, ...}}
    if use_len == q_len:
        bot.send_message(message.chat.id, "вопросы закончились!")
    else:
        ids_collection_d[user_id][use_len] = message.text
        use_len += 1
        if use_len < q_len:
            ques = questions[use_len]
            bot.send_message(message.chat.id, ques)
            #ids_collection_d[user_id][use_len] = message.text
        else:
            bot.send_message(message.chat.id, "спасибо, ответы записаны")
            us_dict = ids_collection_d[user_id]     # словарь ответов одного пользователя {1: ответ, 2: ответ, 3: ответ, ...}
            bot.send_message(message.chat.id) # , str(us_dict))
            write_in_file(us_dict, user_id)         # us_dict – ответы этого пользователя, user_id – id пользователя
            # записать в файл ids_collection_d[user_id[use_len]]


# выдаёт файл
@bot.message_handler(commands=['getfile'])
def get_file(message):
    f = open('/home/xenja1ks/mysite/results.csv', 'rb')
    bot.send_document(message.chat.id, f)
    #bot.send_document(message.chat.id, document=open('/home/xenja1ks/mysite/results.csv', 'rb'))


def langs(ods_collection_d):
    langs_list = []
    langs_dict = {}
    for e in ods_collection_d:
        langs_list.append(ods_collection_d[e][1])
    for el in langs_list:
        if el not in langs_dict:
            langs_dict[el] = [el]
        else:
            langs_dict[el].append(el)
    for elem in langs_dict:
        langs_dict[elem] = len(langs_dict[elem])
    return langs_dict


# в распечатанном виде выдаёт данные файла с результатами
@bot.message_handler(commands=['getanswers'])
def send_answers(message, ods_collection_d):
    answers = langs(ods_collection_d)
    st = ''

    for element in answers:
        st += element + 'представлен ' + str(langs[element]) + 'носитель(ями)' '\r\n'

    participants = len(ods_collection_d)
    bot.send_message(message.chat.id, "Участиников всего: {}".format(participants))

    #bot.send_message(message.chat.id, answers, "бряк")


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
