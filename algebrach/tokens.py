#!/usr/bin/env python3
import os


bot_default = ''
bot = os.getenv('ALGEBRACH_BOT_TOKEN_TELEGRAM', bot_default)
bot_test = os.getenv('ALGEBRACH_BOT_TOKEN_TEST_TELEGRAM', bot_default)

vk_default = ''
vk = os.getenv('MM_BOT_VK_TOKEN', vk_default)

wolfram_default = ''
wolfram = os.getenv('ALGEBRACH_BOT_TOKEN_WOLFRAM', wolfram_default)

fb_default = ''
fb = os.getenv('ALGEBRACH_BOT_TOKEN_FACEBOOK', fb_default)


socks5_url_default = ''
socks5_url = os.getenv('ALGEBRACH_BOT_SOCKS5_URL', socks5_url_default)

socks5_login_default = ''
socks5_login = os.getenv('ALGEBRACH_BOT_SOCKS5_LOGIN', socks5_login_default)

socks5_password_default = ''
socks5_password = os.getenv('ALGEBRACH_BOT_SOCKS5_PASSWORD', socks5_password_default)
