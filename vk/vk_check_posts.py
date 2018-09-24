#/usr/bin/env python3
import aiohttp
import asyncio
import logging

import config
import tokens
from utils import my_bot, action_log


# Checks for updates and calls vk_prepare() once there are
async def vk_check(session, vkgroup_id, date_last_post):
    ### vkgroup_id = '-41437811'
    # Try to address VK's API
    # except bad token
    try:
        # Get 2 (1st may be pinned) last posts
        # TODO: organize the query stings
        query_wall_get = 'https://api.vk.com/method/wall.get?access_token={0}&owner_id={1}&count={2}&offset={3}&v={4}'.format(
                            tokens.vk, vkgroup_id, 2, 0, config.vk_ver)
        async with session.get(query_wall_get) as response:
            # Create a json object
            posts = (await response.json())['response']['items']
            # Check which post is more recent
            post = posts[0] if posts[0]['date'] >= posts[1]['date'] else posts[1]
            # If date is larger than the recorded one we write the new date to file
            # and preparing the post
            # else return default to quit vk_main()
            if post['date'] > date_last_post:
                logging.info('We have a new post in VK group!')
                with open(config.file_location['vk_last_post'], 'w') as file:
                    file.write(str(post['date']))
                return (await vk_prepare(session, post))
            else:
                return 0
    except KeyError as ex:
        if (await response.json()['error']['error_code']) == 5:
            # Alert the admins about an invalid token
            await my_bot.send_message(mm_chat_debug, 'Что-то не так с токеном у ВК! Проверка новых постов приостановлена.\nФиксики приде, порядок наведе!')
            action_log('KeyError exception. Most likely there\'s invalid token.')
        return 0


# Prepares new VK post for sending to Telegram
async def vk_prepare(session, post):
    # Init
    post_hair = ''
    post_head = ''
    post_body = ''
    post_attach = ''
    urls_photo = []
    urls_gif = []
    post_complete = ''

    ### print(post)
    # We assume that it's an original post by default
    post_head = 'Пост '

    # If it's a repost we get everything that's added by a reposter,
    # change post_head
    # and operate with original post as if it wasn't reposted
    if 'copy_history' in post:
        post_hair = '{0}\n\n'.format(post['text'])
        post_head = '<a href="https://vk.com/wall{0}_{1}">Репост</a> '.format(post['from_id'], post['id'])
        post = post['copy_history'][0]

    # If owner_id < 0 then it was posted by a group,
    # if          > 0 -- by a user.
    # Updating post_head respectively
    if post['owner_id'] < 0:
        query_groups_getbyid = 'https://api.vk.com/method/groups.getById?access_token={0}&group_ids={1}&v={2}'.format(
                                tokens.vk, -post['owner_id'], config.vk_ver)
        async with session.get(query_groups_getbyid) as response:
            op_name = (await response.json())['response'][0]['name']
            op_screenname = (await response.json())['response'][0]['screen_name']
        post_head += 'из группы <a href="https://vk.com/{0}">{1}</a>:'.format(op_screenname, op_name)
    else:
        query_usersget = 'https://api.vk.com/method/users.get?access_token={0}&user_id={1}&v={2}'.format(
            tokens.vk, post['owner_id'], config.vk_ver)
        async with session,get(query_usersget) as response:
            op_name = '{0} {1}'.format((await response.json())['response'][0]['first_name'],
                                        (await response.json())['response'][0]['last_name'])
            op_screenname = (await response.json())['response'][0]['id']
        post_head += 'пользователя <a href="https://vk.com/id{0}">{1}</a>'.format(op_screenname, op_name)

    # Get the text part of the post
    post_body = post['text']
    
    # If the posts contains any attachments, we need to extract all of them
    if 'attachments' in post:
        # Call an extractor function
        post_attach_list = await vk_attachments(post, post_attach, urls_photo, urls_gif)
        post_attach = post_attach_list[0]
        urls_photo = post_attach_list[1]
        urls_gif = post_attach_list[2]
        
    
    post_complete = '{0}{1}\n{2}\n\n{3}'.format(post_hair, post_head, post_body, post_attach)

    return [post_complete, urls_photo, urls_gif]


# Extracts of post's attachments
async def vk_attachments(post, post_attach, urls_photo, urls_gif):
    # Scans for different types of attachment in post,
    # returns a list for different types of bot send
    # TODO: check for more types (audio/video/polls/etc.), add them all to post_attach
    for attachment in post['attachments']:
        try:
            # If an attachment is a photo then choose the highest quality possible.
            # Add it to urls_photo for my_bot.send_photo()
            if attachment['type'] == 'photo':
                for size in ['photo_1280', 'photo_807', 'photo_604', 'photo_130', 'photo_75']:
                    if size in attachment['photo']:
                        attach_url = attachment['photo'][size]
                        urls_photo.append(attach_url)
                        logging.info('Successfully extracted an URL (Photo)')
                        break
            
            # If an attachment is a link.
            # Add it to post_attach, so it may be posted as HTML
            elif attachment['type'] == 'link':
                post_attach += '<a href="{0}">{1}</a>\n'.format(attachment['link']['url'], attachment['link']['title'])
                logging.info('Successfully extracted an URL (Link)')

            # If an attachment is a GIF.
            # Add it to urls_gif for my_bot.send_document()
            if attachment['doc']['ext'] in ['gif']:
                urls_gif.append(attachment['doc']['url'])
                logging.info('Successfully extracted an URL (GIF)')

            # If an attachment is a PDF.
            # Add it to post_attach, so it may be posted as HTML            
            elif attachment['type'] in ['doc', 'pdf']:
                post_attach += '<a href="{0}">{1}</a>\n'.format(attachment['doc']['url'], attachment['doc']['title'])
                logging.info('Successfully extracted an URL (DOC)')
        except KeyError:
            logging.info('KeyError while scanning VK Post\'s attachments')

    return [post_attach, urls_photo, urls_gif]


# Posts to Telegram if there's an update
async def vk_main(dp):
    # Init
    post_text = ''
    post_imgs = []
    post_gifs = []

    # Try to get last date from a file
    # TODO: export to a DB
    try:
        with open(config.file_location['vk_last_post'], 'r') as file:
            date_last_post = int(file.read())
    except (OSError, TypeError, ValueError):
        date_last_post = 0

    # Start the main checker
    async with aiohttp.ClientSession(loop=dp.loop) as session:
        # Getting the last post
        post_new = await vk_check(session, config.mm_vk_group, date_last_post)
        # If it returns default then quit vk_main()
        if post_new == 0:
            return
        
        # Else get data for different types of bot send
        post_text = post_new[0]
        post_imgs = post_new[1]
        post_gifs = post_new[2]

        # Send the text portion of the post
        await my_bot.send_message(config.mm_chat, post_text, parse_mode='HTML',
                                     disable_web_page_preview=True)

        # Send all images and GIFs found in the attachments
        for url in post_imgs:
            async with session.get(url) as response:
                pic = await response.content.read()
            await my_bot.send_photo(config.mm_chat, pic)
        for url in post_gifs:
            async with session.get(url) as response:
                gif = await response.content.read()
            await my_bot.send_document(config.mm_chat, ('File.gif', gif))



async def schedule_vk(dp):
    while True:
        # Start vk_main() check for new VK posts every minute
        await vk_main(dp)
        await asyncio.sleep(60)
