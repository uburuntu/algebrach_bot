#/usr/bin/env python3
import aiohttp
import asyncio
import facebook
import logging
import re
from aiogram.types.input_media import InputMediaPhoto

import config
import tokens
from utils import my_bot, action_log
from vk.vk_utils import VkPost


async def vk_check(session, vkgroup_id, date_last_post, count):
    '''
    Checks for a new post
    If new post is found, calls VkPost() class to extract data for TG and FB
    Returns all required types of data
    '''

    disable_wp = True
    # count parameter is useful for /vk_last command
    if count < 1:
        return

    if count == 1:
        count = 2
        offset = 0
    else:
        offset = 1

    # Tries to contact VK's API
    # excepts bad token
    vkgroup_id = '-84875903'
    try:
        # Gets 2 (1st may be pinned) last posts
        # TODO: organize the query stings
        query_wall_get = 'https://api.vk.com/method/wall.get?access_token={0}&owner_id={1}&count={2}&offset={3}&v={4}'.format(
                            tokens.vk, vkgroup_id, count, offset, config.vk_ver)
        async with session.get(query_wall_get) as response:
            # Creates a json object
            posts = (await response.json())['response']['items']
            # Checks which post is more recent
            post = posts[0] if posts[0]['date'] >= posts[1]['date'] else posts[1]
            # If date is larger than the recorded one, records the new date to file
            # and calls VkPost() to prepare the post
            # else, returns None to quit vk_main()
            if post['date'] > date_last_post:
                logging.info('We have a new post in VK group!')
                with open(config.file_location['vk_last_post'], 'w') as file:
                    file.write(str(post['date']))

                my_new_post = VkPost(session, post)
                await my_new_post.post_prepare()

                post_tg_text = my_new_post.post_tg_text
                post_fb_text = my_new_post.post_fb_text
                disable_wp = not bool(my_new_post.link_preview)
                post_images = my_new_post.post_images
                post_gifs = my_new_post.post_gifs
                fb_link = my_new_post.fb_link

                '''
                print(post_tg_text)
                print(post_fb_text)
                print(disable_wp)
                print(post_images)
                print(post_gifs)
                '''
                return post_tg_text, post_fb_text, disable_wp, post_images, post_gifs, fb_link
            else:
                return
    except KeyError as ex:
        if (await response.json()['error']['error_code']) == 5:
            # Alert the admins about an invalid token
            await my_bot.send_message(mm_chat_debug, 'Что-то не так с токеном у ВК! Проверка новых постов приостановлена.\nФиксики приде, порядок наведе!')
            action_log('KeyError exception. Most likely there\'s invalid token.')
        return 0


async def send_tg(session, text, disable_wp, images, gifs):
    '''
    Sends all gathered data to TG
    '''

    # Sends the text portion of the post
    # If it's longer than 4000 characters, sends it in chunks
    while len(text) > 4000:
        await my_bot.send_message(config.mm_chat, text[:4000], parse_mode='HTML',
                                     disable_web_page_preview=disable_wp)
        text = text[4000:]
    await my_bot.send_message(config.mm_chat, text, parse_mode='HTML',
                                 disable_web_page_preview=disable_wp)

    # Sends all images and GIFs found in the post's attachments
    if len(images) > 0:
        await my_bot.send_media_group(config.mm_chat, [InputMediaPhoto(url) for url in images])

    for url in gifs:
        async with session.get(url) as response:
            gif = await response.content.read()
        await my_bot.send_document(config.mm_chat, ('File.gif', gif))


async def send_fb(session, text, images, gifs, link):
    '''
    Sends all gathered data to FB
    '''

    api = facebook.GraphAPI(tokens.fb)

    if len(images) > 1:
        async with session.get(images[0]) as response:
            pic = await response.content.read()
        status = api.put_photo(image=pic, message=text)
        for url in images:
            async with session.get(url) as response:
                pic = await response.content.read()
            status = api.put_photo(image=pic, album_path=config.mm_fb_album + '/photos')
        return

    elif len(images) == 1:
        async with session.get(images[0]) as response:
            pic = await response.content.read()
        status = api.put_photo(image=pic, message=text)
        return

    if len(gifs) > 0:
        status = api.put_object(
            parent_object='me', connection_name='feed',
            message=text,
            link=gifs[0])

    else:
        status = api.put_object(
            parent_object='me', connection_name='feed',
            message=text,
            link=link)



async def vk_main(dp):
    '''
    Performs checks and resends final post to TG and FB on an update
    '''

    # Tries to get last date from a file
    # TODO: export to a DB
    try:
        with open(config.file_location['vk_last_post'], 'r') as file:
            date_last_post = int(file.read())
    except (OSError, TypeError, ValueError):
        date_last_post = 0

    # Starts the main checker
    async with aiohttp.ClientSession(loop=dp.loop) as session:
        # Gets the last post
        post_new = await vk_check(session, config.mm_vk_group, date_last_post, 1)
        # If it returns default then quit vk_main()
        if post_new == None:
            return
        
        # Else, gets data for different types of bot send and reposts it to TG and FB
        post_tg_text, post_fb_text, disable_wp, post_images, post_gifs, fb_link = post_new

        await send_tg(session, post_tg_text, disable_wp, post_images, post_gifs)
        logging.info('Successfully reposted VK post to Telegram')

        await send_fb(session, post_fb_text, post_images, post_gifs, fb_link)
        logging.info('Successfully reposted VK post to Facebook')


async def schedule_vk(dp):
    '''
    Checks for new VK post every minute
    '''

    while True:
        await vk_main(dp)
        await asyncio.sleep(60)
