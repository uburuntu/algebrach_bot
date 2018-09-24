#/usr/bin/env python3
import aiohttp
import asyncio
import logging
import re

import config
import tokens


class VkPost():
    '''
    Prepares a post for TG and FB repost
    '''

    def __init__(self, session_in, post_in):
        self.post = post_in  # our new post
        self.post_tg_text = 'VkPost Init text for Telegram.'  # full text for Telegram's message
        self.post_fb_text = 'VkPost Init text for Facebook.'  # full text for Facebook's post
        self.link_preview = ''  # parameter for TG's disable_web_page_preview
        self.post_images = []  # URLs of images
        self.post_gifs = []  # URLs of gifs
        self.is_repost = False  # determines which emoji to insert at the start of post_tg_header string
        self.fb_link = ''  # required link for FB's post
        self.session = session_in  # our aiohttp client session


    async def post_prepare(self):
        # Prepares the text portion of the post
        post_preheader = ''
        post_tg_header = '<a href="https://vk.com/wall{0}_{1}">Пост</a> '.format(self.post['from_id'], self.post['id'])
        post_fb_header = 'Пост '
        post_body = ''
        attachments_tg = ''
        attachments_fb = ''
        self.fb_link = 'https://vk.com/wall{0}_{1}'.format(self.post['from_id'], self.post['id'])
        
        # print(self.post)

        # Checks if the post is a repost
        if 'copy_history' in self.post:
            post_preheader = self.post['text']
            post_tg_header = '<a href="https://vk.com/wall{0}_{1}">Репост</a> '.format(self.post['from_id'], self.post['id'])
            post_fb_header =  'Репост '
            self.is_repost = True
            self.post = self.post['copy_history'][0]

        # If owner_id < 0 then it was posted by a group,
        # if          > 0 -- by a user
        # Updates headers respectively
        if self.post['owner_id'] < 0:
            query_groups_getbyid = 'https://api.vk.com/method/groups.getById?access_token={0}&group_ids={1}&v={2}'.format(tokens.vk, -self.post['owner_id'], config.vk_ver)
            async with self.session.get(query_groups_getbyid) as response:
                op_name = (await response.json())['response'][0]['name']
                op_screenname = (await response.json())['response'][0]['screen_name']
            post_tg_header += 'из группы <a href="https://vk.com/{0}">{1}</a>:'.format(op_screenname, op_name)
            post_fb_header += 'из группы {0} (https://vk.com/{1}):'.format(op_name, op_screenname)
        else:
            query_usersget = 'https://api.vk.com/method/users.get?access_token={0}&user_id={1}&v={2}'.format(tokens.vk, self.post['owner_id'], config.vk_ver)
            async with self.session.get(query_usersget) as response:
                op_name = '{0} {1}'.format((await response.json())['response'][0]['first_name'],
                                        (await response.json())['response'][0]['last_name'])
                op_screenname = (await response.json())['response'][0]['id']
            post_tg_header += 'пользователя <a href="https://vk.com/id{0}">{1}</a>:'.format(op_screenname, op_name)
            post_fb_header += 'пользователя {0} (https://vk.com/id{1}):'.format(op_name, op_screenname)

        # Gets main body of the post's text
        post_body = self.post['text']
    
        # If the posts contains any attachments, calls attach_prepare() to extract all of them
        if 'attachments' in self.post:
            attachments_tg, attachments_fb = self.attach_prepare()

        # Inserts an emoji-link depending on self.is_repost
        post_tg_header = '<a href="{0}">📢</a>'.format(self.link_preview)+post_tg_header if self.is_repost else '<a href="{0}">📋</a>'.format(self.link_preview)+post_tg_header

        # Replaces wiki-links for TG message and FB post respectively
        post_tg_preheader = self.replace_wikis(post_preheader)
        post_tg_body = self.replace_wikis(post_body)
        post_fb_preheader = self.replace_wikis(post_preheader, True)
        post_fb_body = self.replace_wikis(post_body, True)

        # Final text part for TG and FB
        self.post_tg_text = '{0}\n\n{1}\n{2}\n{3}'.format(post_tg_preheader, post_tg_header, post_tg_body, attachments_tg)
        self.post_fb_text = '{0}\n\n{1}\n{2}\n{3}'.format(post_fb_preheader, post_fb_header, post_fb_body, attachments_fb)


    def attach_prepare(self):
        '''
        Scans self.post['attachments'] to extract every attachment
        and prepares it for both TG and FB
        Returns prepared text parts of attachments for TG and FB
        '''

        attach_tg_albums = ''
        attach_fb_albums = ''
        attach_tg_audios = ''
        attach_fb_audios = ''
        attach_tg_docs = ''
        attach_fb_docs = ''
        attach_tg_links = ''
        attach_fb_links = ''
        attach_tg_notes = ''
        attach_fb_notes = ''
        attach_tg_pages = ''
        attach_fb_pages = ''
        attach_tg_polls = ''
        attach_fb_polls = ''
        attach_tg_videos = ''
        attach_fb_videos = ''

        try:
            for attachment in self.post['attachments']:
                if attachment['type'] in ['app', 'graffiti', 'photo', 'posted_photo']:
                    for size in ['photo_1280', 'photo_807', 'photo_604', 'photo_130', 'photo_75']:
                        if size in attachment[attachment['type']]:
                            image_url = attachment['photo'][size]
                            self.post_images.append(image_url)
                            logging.info('Successfully extracted an URL ({})'.format(attachment['type']))
                            break

                if attachment['type'] == 'album':
                    attach_tg_albums = attach_fb_albums = self.attach_naming(attach_tg_albums, '\n— Альбом:')
                    album_count = attachment['album']['size']
                    album_title = attachment['album']['title']
                    attach_tg_albums += '{0}, {1} фото\n'.format(album_title, album_count)
                    attach_fb_albums += '{0}, {1} фото\n'.format(album_title, album_count)
                    logging.info('Successfully extracted an album')

                if attachment['type'] == 'audio':
                    audio_url = attachment['audio']['url']
                    audio_title = '{0} - {1}'.format(attachment['audio']['artist'], attachment['audio']['title'])
                    attach_tg_audios = attach_fb_audios = self.attach_naming(attach_tg_audios, '\n— Аудио:')
                    if not (audio_url in ['', 'https://vk.com/mp3/audio_api_unavailable.mp3']):
                        attach_tg_audios += '<a href="{0}">{1}</a>\n'.format(audio_url, audio_title)
                        attach_fb_audios += '{0}: {1}\n'.format(audio_title, audio_url)
                        logging.info('Successfully extracted an URL (AUDIO)')
                    else:
                        attach_tg_audios += '{0}\n'.format(audio_title)
                        attach_fb_audios += '{0}\n'.format(audio_title)
                        logging.info('Successfully extracted audio\'s name')

                if attachment['type'] in ['doc', 'pdf']:
                    if attachment['doc']['ext'] in ['gif']:
                        gif_url = attachment['doc']['url']
                        self.post_gifs.append(gif_url)
                        logging.info('Successfully extracted an URL (GIF)')
                    else:
                        attach_tg_docs = attach_fb_docs = self.attach_naming(attach_tg_docs, '\n— Приложения:')
                        doc_url = attachment['doc']['url']
                        doc_title = attachment['doc']['title']
                        doc_size = ((int(attachment['doc']['size']))/1024)/1024
                        attach_tg_docs += '<a href="{0}">{1}</a>  ({2:.2f} Мб)\n'.format(doc_url, doc_title, doc_size)
                        attach_fb_docs += '{0}: {1}  ({2:.2f} Мб)\n'.format(doc_title, doc_url, doc_size)
                        logging.info('Successfully extracted an URL (DOC)')

                if attachment['type'] == 'link':
                    attach_tg_links = attach_fb_links = self.attach_naming(attach_tg_links, '\n— Ссылки:')
                    link_url = attachment['link']['url']
                    link_title = attachment['link']['title']
                    attach_tg_links += '<a href="{0}">{1}</a>\n'.format(link_url, link_title)
                    attach_fb_links += '{0}: {1}\n'.format(link_title, link_url)
                    if attachment['link'].get('photo') and not self.link_preview:
                        self.link_preview = self.fb_link = link_url
                    logging.info('Successfully extracted an URL (Link)')

                if attachment['type'] == 'page':
                    attach_tg_pages = attach_fb_pages = self.attach_naming(attach_tg_pages, '\n— Вики-страницы:')
                    page_url = attachment['note']['view_url']
                    page_title = attachment['note']['title']
                    attach_tg_pages += '<a href="{0}">{1}</a>\n'.format(page_url, page_title)
                    attach_fb_pages += '{0}: {1}\n'.format(page_title, page_url)
                    logging.info('Successfully extracted a wiki-page')

                if attachment['type'] == 'poll':
                    attach_tg_polls = attach_fb_polls = self.attach_naming(attach_tg_polls, '\n— Опрос:')
                    poll_question = attachment['poll']['question']
                    poll_answers = ''
                    for answer in attachment['poll']['answers']:
                        poll_answers += '{0} - проголосовало {1}  ({2}%)\n'.format(answer['text'], answer['votes'], answer['rate'])
                    attach_tg_polls += '{0}\n{1}\n'.format(poll_question, poll_answers)
                    attach_fb_polls += '{0}\n{1}\n'.format(poll_question, poll_answers)
                    logging.info('Successfully extracted a poll')

                if attachment['type'] == 'note':
                    attach_tg_notes = attach_fb_notes = self.attach_naming(attach_tg_notes, '\n— Заметки:')
                    note_url = attachment['note']['view_url']
                    note_title = attachment['note']['title']
                    attach_tg_notes += '<a href="{0}">{1}</a>\n'.format(note_url, note_title)
                    attach_fb_notes += '{0}: {1}\n'.format(note_title, note_url)
                    logging.info('Successfully extracted a note')

                if attachment['type'] == 'video':
                    attach_tg_videos = attach_fb_videos = self.attach_naming(attach_tg_videos, '\n— Видео:')
                    if 'platform' in attachment['video']:
                        video_title = attachment['video']['title']
                        attach_tg_videos += '{0}\n'.format(video_title)
                        attach_fb_videos += '{0}\n'.format(video_title)
                        logging.info('Successfully extracted video\'s name')
                    else:
                        video_owner = attachment['video']['owner_id']
                        video_id = attachment['video']['id']
                        video_url = 'https://vk.com/video{0}_{1}'.format(video_owner, video_id)
                        video_title = attachment['video']['title']
                        attach_tg_videos += '<a href="{0}">{1}</a>\n'.format(video_url, video_title)
                        attach_fb_videos += '{0}: {1}\n'.format(video_title, video_url)
                        logging.info('Successfully extracted video\'s link')
        except KeyError:
            logging.info('KeyError while scanning VK Post\'s attachments')

        tg = attach_tg_albums+attach_tg_audios+attach_tg_docs+attach_tg_links+attach_tg_notes+attach_tg_pages+attach_tg_polls+attach_tg_videos
        fb = attach_fb_albums+attach_fb_audios+attach_fb_docs+attach_fb_links+attach_fb_notes+attach_fb_pages+attach_fb_polls+attach_fb_videos
        return tg, fb


    def attach_naming(self, attach_string, name):
        '''
        Attaches a name of an attachment if it's the first one of it's kind
        '''

        if attach_string == '':
            attach_string = '{0}\n'.format(name)
        return attach_string


    def replace_wikis(self, text, raw_link=False):
        '''
        Switches from wiki-links like '[user_id|link_text]' to HTML for TG
        If raw_link=True, switches to FB format
        '''

        link_format = '{1} (https://vk.com/{0})' if raw_link else '<a href="https://vk.com/{0}">{1}</a>'
        pattern = re.compile(r'\[([^|]+)\|([^|]+)\]', re.U)
        results = pattern.findall(text, re.U)
        for i in results:
            user_id = i[0]
            link_text = i[1]
            before = "[{0}|{1}]".format(user_id, link_text)
            after = link_format.format(user_id, link_text)
            text = text.replace(before, after)
        return text