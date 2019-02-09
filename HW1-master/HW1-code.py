''' выкачивает посты со стены и комментарии к ним.
Обязательное условие: со стены больше, чем 100 постов, и больше, чем 100 комментариев к посту
Кроме выкачивания нужно сделать следующее:
        Посчитайте питоном длину каждого поста и каждого комментария в словах.
        Создайте график, описывающий, как длина поста соотносится со средней длиной комментариев.
        Помимо выкачивания постов и комментариев, программа должна смотреть в профиль пользователя,
    который написал пост или сделал комментарий, : возраст и город (если они указаны).
    Для города достаточно id (то есть название не обязательно, хотя это можно сделать средствами API, а возраст уметь вычислять.
        Для каждого возраста нужно вычислить среднюю длину поста и комментария, нарисовать график, отражающий эту информацию.
        Аналогичные графики нужно нарисовать для каждого города.
Выложить скачанные тексты, построенные графики и сам код.'''

#https://vk.com/natgeoru  24565142


import urllib.request  # импортируем модуль
import requests
import json
import re
import matplotlib
import matplotlib.pyplot as plt
from collections import Counter

from matplotlib import style
style.use('ggplot')


def vk_api(method, **kwargs):
    api_request = 'https://api.vk.com/method/'+method + '?'
    api_request += '&'.join(['{}={}'.format(key, kwargs[key]) for key in kwargs])
    return json.loads(requests.get(api_request).text)

def file_write(data_to_write, name_file):  #функция которая записывает файлы
    file = open(name_file, 'w', encoding='utf-8')
    file.write(data_to_write)
    file.close()

def word_counter(wordes):        #возможно стоит избавляться от ссылок
    words = str(wordes)
    #print(words)
    #words = re.sub('(([a-zA-Z0-9])*?|[./]*?)+?', ' ', words)
    words = words.replace('.', ' ')
    words = words.replace(',', ' ')
    words = words.replace('«', ' ')
    words = words.replace(':', ' ')
    words = words.replace('»', ' ')
    words = words.replace('–', ' ')
    #print(words)
    words = re.sub( '\s+', ' ', words)       #.strip()
    #print(words)
    word_counting = len(words.split())
    return word_counting

def get_posts():        #here P get 200 posts
    posts = []
    counter_posts = 200
    posts_api = vk_api('wall.get', owner_id = '-24565142', v = '5.63')
    posts += posts_api["response"]["items"]
    while len(posts) < counter_posts:
        posts_api = vk_api('wall.get', owner_id='-24565142', v='5.63', count = counter_posts) #офсет нужно ли
        posts += posts_api["response"]["items"]
    return posts

def get_comments(posts): #хаха кажется эта функция не работает
    posts_and_comments = []
    i = 0
    #counter_posts = 200
    for post in posts:
        #print('p in ps')
        post_author = ["from_id"]
        the_post_id = ["id"]
        comment_text = ['']
        #print(len(posts))
        while i <= len(posts):
            #print('len counter and so on')
            comments_of_the_post = vk_api('wall.getComments', post_id = the_post_id, owner_id = post_author, v='5.63') #'''text = comment_text,''',
            i += 1
            #print(comments_of_the_post)
            #result1 = comments_of_the_post.json()['response']
            '''for element in comments_of_the_post['response']:
                print('element in ')
                if type(element) == dict:
                    print('type dict')
                    comment_text.append(element)

            print(comment_text, '1')'''
        posts_and_comments.append(post)
    #print(posts_and_comments)

    file_write(str(posts_and_comments), 'pAc.txt')
    return posts_and_comments

def posts_comments_relation(posts_and_comments):
    posts_text = ''                 #для записи в файл текста постов. (если вдруг нужно отдельно)
    posts_and_comments_text = ''    #для записи в файл комментов и постов
    posts_length = []               #массив с длинами постов
    comments_av_length = []         #массив со средними длинами постов
    p_avC_length = {}               #словарь где будет совмещено длина поста и средняя длина коммента
    for post in posts_and_comments:
        c_av_length = []            #средняя длина коммента для конкретного поста
        post_text = post['text']
        posts_text = posts_text + post_text + '\n' + '\n' + '\n'
        posts_and_comments_text = posts_and_comments_text + 'текст поста: \n' + post_text + 'текст его комментариев \n'
        if post_text == '':
            p_length = 0
        else:
            p_length = word_counter(post_text)
            #print(p_length)
        posts_length.append(p_length)
        #print(posts_length)
        comment_text = ['']

    file_write(posts_text, 'poststext.txt')
    #записи отделены тройными \n, потому что в одной записи может встретится двойной перенос строки



#def socio_info():
 #   city = []
  #  age = []
   # for comment in comments:



def main():
    posts = get_posts()
    posts_and_comments = get_comments(posts)
    val1 = posts_comments_relation(posts_and_comments)


main()