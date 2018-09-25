#!/usr/bin/env python3
import logging

from algebrach.utils import user_action_log


# Команда /me
# TODO: из-за parse_mode="Markdown" не проходят запросы типа
#       "/me вызывает @rm_bk."
# TODO: отрефакторить говнокод
async def me_message(message):
    # В ЛС бот не может удалять сообщения пользователя
    """
    try:
        my_bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception:
        logging.exception("message")
    """
    # Если у пользователя есть юзернэйм, то берём его как your_name
    if message.from_user.username is not None:
        your_name = '[@{}](tg://user?id={})'.format(message.from_user.username, message.from_user.id)
    # Иначе, берём имя пользователя, которое есть всегда
    else:
        your_name = '[{}](tg://user?id={})'.format(message.from_user.first_name, message.from_user.id)
    # Если /me непусто, берём всё, что после '/me '
    if len(message.text.split()) < 2:
        return
    your_message = message.text.split(maxsplit=1)[1]
    your_me = "{} {}".format(your_name, your_message)
    try:
        # Если /me было ответом на какое-то сообщение, то посылаем запрос как ответ
        # TODO: расширить эту фичу на все команды
        if getattr(message, 'reply_to_message') is not None:
            await message.reply_to_message.reply(your_me, parse_mode="Markdown", disable_notification=True)
        else:
            await message.reply(your_me, parse_mode="Markdown", disable_notification=True, reply=False)
    except Exception:
        logging.exception("message")
    try:
        await message.delete()
    except Exception:
        logging.exception("message")
    user_action_log(message, "called the me:\n{}".format(your_me))
