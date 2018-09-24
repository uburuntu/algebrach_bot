#!/usr/bin/env python3

import random

import wikipedia
from langdetect import detect

from algebrach.utils import user_action_log


async def my_wiki(message):
    wiki_title = ''
    if len(message.text.split()) == 1:
        wikipedia.set_lang(random.choice(['en','ru']))
        wiki_query = wikipedia.random(pages=1)
    else:
        wiki_query = ' '.join(message.text.split()[1:])
        user_action_log(message,
                        'entered this query for /wiki:\n{0}'.format(wiki_query))
        if all(ord(x) < 127 or not x.isalpha() for x in wiki_query):
                wikipedia.set_lang('en')
        # TODO: a bit dirty condition
        elif all(ord(x) < 127 or (ord('Ё') <= ord(x) <= ord('ё')) or not x.isalpha() for x in wiki_query):
            wikipedia.set_lang('ru')
        else:
            wikipedia.set_lang(detect(wiki_query))

    try:
        wiki_page = wikipedia.page(title=wiki_query)
        wiki_title = wiki_page.title
        wiki_url = wiki_page.url
        wiki_fact = wikipedia.summary(wiki_query, sentences=5)
        if '\n  \n' in str(wiki_fact):
            wiki_fact = '{}...\n\n' \
                        '<i>В данной статье имеется математическая вёрстка.\n' \
                        'Для удобства чтения перейди по ссылке:</i>'.format(str(wiki_fact).split('\n  \n', 1)[0])
        await message.reply('<b>{0}.</b>\n{1}\n{2}'.format(wiki_title, wiki_fact, wiki_url), parse_mode='HTML')
    except wikipedia.exceptions.DisambiguationError as e:
        wiki_list = '\n'.join(map(str, e.options))
        wiki_fact = ''
        await message.reply('Пожалуйста, уточни запрос.\n' \
                            'Выбери, что из перечисленного имелось в виду, и вызови /wiki ещё раз.\n{0}'.format(wiki_list))
    except wikipedia.exceptions.PageError:
        await message.reply('Запрос не найден.')
    user_action_log(message, "got Wikipedia article\n{0}".format(wiki_title))
