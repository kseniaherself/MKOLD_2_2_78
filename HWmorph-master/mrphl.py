'''Написать программу-бота, с которой можно разговаривать:
пользователь пишет ей реплику, а она отвечает предложением,
в котором все слова заменены на какие-то случайные другие слова
той же части речи и с теми же грамматическими характеристиками.
Предложение-ответ должно быть согласованным.
Например, на фразу "Мама мыла раму" программа может ответить "Девочка пела песню".
Для такой программы вам понадобится большой список русских слов:
можно взять просто любой большой текст, вытащить из него слова и использовать их. – DONE

Из этого списка вам нужен только список разных лемм разных частей речи,
и затем нужно будет использовать функции !parse и !inflect.'''

import re
import random
from pymorphy2 import MorphAnalyzer
morph = MorphAnalyzer()

# очищает текст и делает из него строку слов
def clean_text(text1_file):
    #text1_file.lower()
    print(text1_file)
    regex = re.compile('\W+')
    res = regex.sub(' ', text1_file).strip()
    #print(res)
    return res

# открывает и очищает текст из файла исходного: ВЫСТАКИВАЕМ СЛОВА В СТРОЧКУ ДЛЯ ДАЛЬНЕЙШЕГО ИСПОЛЬЗОВАНИЯ
def open_and_read(file1_name):
    text1_file = open(file1_name)
    text1 = text1_file.read()
    #print(text1)
    text2 = clean_text(text1)
    #print(text2)
    text1_file.close()
    return text2

# разбор слова. Использование PARSE. ВСЕ СЛОВА ИЗ ТЕКСТА
def inflexion(text1):
    text_arr = text1.split()
    tags1 = []
    nrmlzd_words = []
    for elem in text_arr:
        elem1 = morph.parse(elem)[0]
        tag1 = elem1.tag
        tags1.append(tag1)
        #print(tags1)
        nrmlzd_w = elem1.normalized
        nrmlzd_t = nrmlzd_w.tag
        nrmlzd_words.append(nrmlzd_t) # очищенные слова
        #print(nrmlzd_words)
    return nrmlzd_words, tags1

def inflexion_v2(nrmlzd_words):
    wed1 = input('введите ваш текст: ')
    response = []
    wed2 = clean_text(wed1.lower())
    wed2.lower()
    wed2.split()
    print(wed2)
    nrmlzd_NEW, GRAMMAR = inflexion(wed2)
    print(nrmlzd_NEW)
    for elem, element in zip(nrmlzd_NEW, GRAMMAR):
        tag = re.sub(' ', ',', str(element))
        tags = frozenset(tag.split(','))
        prog = morph.parse(elem)[0]
        prog = prog.inflect(tags)
        response.append(prog.word)
    print(response)



def main():
    var1 = open_and_read('text_G_crop.txt')
    var2, var3 = inflexion(var1)
    var4 = inflexion_v2(var2)


main()