#!/usr/bin/env python3
import logging
import random
import time

from aiogram import types

from algebrach import config
from algebrach.data.models import GifResponse, ImageResponse, StickerResponse, TextResponse, VoiceResponse
from algebrach.utils import my_bot, user_action_log


async def my_kek(message: types.Message):
    """
    открывает соответствующие файл и папку, кидает рандомную строчку из файла, или рандомную картинку или гифку из папки
    :param message:
    :return:
    """
    if not hasattr(my_kek, 'kek_bang'):
        my_kek.kek_bang = time.time()
    if not hasattr(my_kek, 'kek_crunch'):
        my_kek.kek_crunch = my_kek.kek_bang + 60 * 60
    if not hasattr(my_kek, 'kek_enable'):
        my_kek.kek_enable = True
    if not hasattr(my_kek, 'kek_counter'):
        my_kek.kek_counter = 0

    kek_init = True

    if message.chat.id == int(config.mm_chat):
        if my_kek.kek_counter == 0:
            my_kek.kek_bang = time.time()
            my_kek.kek_crunch = my_kek.kek_bang + 60 * 60
            my_kek.kek_counter += 1
            kek_init = True
        elif (my_kek.kek_counter >= config.limit_kek
              and time.time() <= my_kek.kek_crunch):
            kek_init = False
        elif time.time() > my_kek.kek_crunch:
            my_kek.kek_counter = -1
            kek_init = True

    if not (kek_init and my_kek.kek_enable):
        return
    if message.chat.id == config.mm_chat:
        my_kek.kek_counter += 1
    your_destiny = random.randint(1, 30)  # если при вызове не повезло, то кикаем из чата
    if your_destiny == 13 and str(message.chat.id) == config.mm_chat:
        await message.reply('Предупреждал же, что кикну. Если не предупреждал, то')
        await message.reply_document(config.gif_links[0])
        try:
            if int(message.from_user.id) in config.admin_ids:
                await message.reply('... Но против хозяев не восстану.')
                user_action_log(message, 'can\'t be kicked out')
            else:
                # кикаем кекуна из чата (можно ещё добавить условие,
                # что если один юзер прокекал больше числа n за время t,
                # то тоже в бан)
                await my_bot.kick_chat_member(message.chat.id,
                                              message.from_user.id)
                user_action_log(message, 'has been kicked out')
                await my_bot.unban_chat_member(message.chat.id,
                                               message.from_user.id)
                # тут же снимаем бан, чтобы смог по ссылке к нам вернуться
                user_action_log(message, 'has been unbanned')
        except Exception as ex:
            logging.exception(ex)
            pass
    else:
        type_of_kek = random.randint(1, 33)
        # Image route
        if type_of_kek == 33:
            random_kek_image = ImageResponse.get_random_by_type('kek')
            if random_kek_image:
                await message.reply_photo(random_kek_image.content)

        # Gif route
        elif type_of_kek == 32:
            random_kek_gif = GifResponse.get_random_by_type('kek')
            if random_kek_gif:
                await message.reply_document(('kek.gif', random_kek_gif.content))

        # Retarded gif route
        elif type_of_kek == 31:
            await message.reply_document(random.choice(config.gif_links))

        elif type_of_kek < 5:
            kek_sticker = StickerResponse.get_random_by_type('kek')
            if kek_sticker:
                await message.reply_sticker(kek_sticker.content)

        elif 5 < type_of_kek < 7:
            voice_id = VoiceResponse.get_random_by_type('kek')
            if voice_id:
                await message.reply_voice(voice_id.content)

        else:
            kek_text = TextResponse.get_random_by_type('kek')
            if kek_text:
                await message.reply(kek_text.content)

    if my_kek.kek_counter == config.limit_kek - 10:
        time_remaining = divmod(int(my_kek.kek_crunch) - int(time.time()), 60)
        # TODO: fix this notification
        await message.reply('<b>Внимание!</b>\nЭтот чат может покекать '
                            'ещё не более {0} раз до истечения кекочаса '
                            '(через {1} мин. {2} сек.).\n'
                            'По истечению кекочаса '
                            'счётчик благополучно сбросится.'.format(config.limit_kek - my_kek.kek_counter,
                                                                     time_remaining[0], time_remaining[1]),
                            parse_mode='HTML')
    if my_kek.kek_counter == config.limit_kek - 1:
        time_remaining = divmod(int(my_kek.kek_crunch) - int(time.time()), 60)
        # TODO: fix this notification
        await message.reply('<b>EL-FIN!</b>\nТеперь вы сможете кекать только через {0} мин. {1} сек.'
                            .format(time_remaining[0], time_remaining[1]),
                            parse_mode='HTML')
    my_kek.kek_counter += 1
