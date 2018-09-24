#!/usr/bin/env python3
import logging
import random
import re

from aiogram.utils import executor
import pytz

import config
from commands import arxiv_queries, dice, me, morning_message, wiki, wolfram, kek
from utils import dp, command_with_delay, commands_handler, action_log, user_action_log, loop, my_bot
from vk import vk_check

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='algebrach.log')


@dp.message_handler(func=commands_handler(['/id']))
async def process_start_command(message):
    await message.reply('Algebrach Bot for Mechmath.\nNow on Aiogram!')


@dp.message_handler(func=commands_handler(['/start', '/help', '/links', '/wifi', '/chats', '/channels']))
async def my_new_data(message):
    command = message.text.lower().split()[0]
    command_raw = re.split("@+", command)[0]
    with open(config.file_location[command_raw], 'r', encoding='utf-8') as file:
        await message.reply(file.read(), parse_mode="HTML", disable_web_page_preview=True)
    user_action_log(message, "called that command: {}".format(command))


@dp.message_handler(func=commands_handler(['/rules']))
@command_with_delay(delay=3)
async def rules_command(message):
    if str(message.chat.id) == config.mm_chat:
        with open(config.file_location['/rules'], 'r', encoding='utf-8') as file:
            await message.reply(file.read(), parse_mode="HTML", disable_web_page_preview=True)
        user_action_log(message, "called rules")


@dp.message_handler(func=commands_handler(['/wiki']))
async def wolfram_solver(message):
    await wiki.my_wiki(message)


@dp.message_handler(func=commands_handler(['/wolfram', '/wf']))
async def wolfram_solver(message):
    await wolfram.wolfram_solver(message)


@dp.message_handler(func=commands_handler(['/arxiv']))
@command_with_delay(delay=10)
async def arxiv_checker(message):
    await arxiv_queries.arxiv_checker(message)


@dp.message_handler(func=commands_handler(['/truth']))
async def my_truth(message):
    answers = ["да", "нет", "это не важно", "да, хотя зря", "никогда", "100%", "1 из 100"]
    truth = random.choice(answers)
    await message.reply(truth)
    user_action_log(message, "has discovered the Truth:\n{0}".format(truth))


@dp.message_handler(func=commands_handler(['/roll']))
async def my_roll(message):
    rolled_number = random.randint(0, 100)
    await message.reply(str(rolled_number).zfill(2))
    user_action_log(message, "recieved {0}".format(rolled_number))


@dp.message_handler(func=commands_handler(['/d6']))
async def my_d6(message):
    await dice.my_d6(message)


@dp.message_handler(func=commands_handler(['/dn']))
async def my_dn(message):
    await dice.my_dn(message)


@dp.message_handler(func=commands_handler(['/gender']))
async def your_gender(message):
    with open(config.file_location['/gender'], 'r', encoding='utf-8') as file_gender:
        gender = random.choice(file_gender.readlines())
        await message.reply(gender)
    user_action_log(message, "has discovered his gender:\n{0}".format(str(gender).replace("<br>", "\n")))


@dp.message_handler(func=commands_handler(['/me']))
async def me_message(message):
    await me.me_message(message)


@dp.message_handler(func=commands_handler(['/or']))
@command_with_delay(delay=1)
async def command_or(message):
    user_action_log(message, 'called: ' + message.text)
    # Shitcode alert!
    or_lang = 'ru'
    if len(message.text.split()) < 4:
        return
    or_message = message.text.split(' ', 1)[1]
    if 'or' in message.text.split():
        make_choice = re.split(r'[ ](?:or)[, ]', or_message)
        or_lang = 'en'
    else:
        make_choice = re.split(r'[ ](?:или)[, ]', or_message)
    if len(make_choice) > 1 and not ((message.text.split()[1] == 'или') or (message.text.split()[1] == 'or')):
        choosen_answer = random.choice(make_choice)
        if or_lang == 'ru':
            choosen_answer = re.sub(r'(?i)\bя\b', 'ты', choosen_answer)
        else:
            choosen_answer = re.sub(r'(?i)\bi\b', 'you', choosen_answer)
        # more subs to come
        await message.reply(choosen_answer)


@dp.message_handler(func=commands_handler(['/kek']))
@command_with_delay(delay=1)
async def my_kek(message):
    await kek.my_kek(message)


if __name__ == '__main__':
    if config.debug_mode:
        action_log("Running bot in Debug mode!")
    else:
        action_log("Running bot!")

    dp.loop.create_task(morning_message.schedule_morning_messages())
    dp.loop.create_task(vk_check.schedule_vk(dp))
    executor.start_polling(dp, skip_updates=True)

