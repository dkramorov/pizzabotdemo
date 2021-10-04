# -*- coding: utf-8 -*-
import json
import logging
import requests

logger = logging.getLogger(__name__)


class TelegramMessage:
    """Telegram message"""
    error = None
    chat_id = None
    text = None
    first_name = None
    last_name = None

    def __init__(self, body_bytes):
        """Receive raw message
           :param body_bytes: raw request.body data
        """
        try:
            json_obj = json.loads(body_bytes)
        except Exception as e:
            logger.error(e)
            self.error = e
            return

        message = json_obj['message']
        self.text = message.get('text')
        chat = message.get('chat', {})
        self.chat_id = chat.get('id')
        self.first_name = chat.get('first_name')
        self.last_name = chat.get('last_name')

class TelegramBot:
    """TelegramBot"""
    def __init__(self, token: str = None, proxy: str = None, chat_id: int = None):
        self.api_url = 'https://api.telegram.org/bot{}/'.format(token)
        proxies = None
        if proxy:
            proxies = {
                'http': proxy,
                'https': proxy,
            }
        self.token = token
        self.proxies = proxies
        self.chat_id = chat_id

    def get_emoji(self, code=None):
        """Get smile for fun
           :param code: smile code, for example 'rain'
        """
        emoji = {'thunderstorm': '\U0001F4A8',    # Code: 200's, 900, 901, 902, 905
                 'drizzle': '\U0001F4A7',         # Code: 300's
                 'rain': '\U00002614',            # Code: 500's
                 'snowflake': '\U00002744',       # Code: 600's snowflake
                 'snowman': '\U000026C4',         # Code: 600's snowman, 903, 906
                 'atmosphere': '\U0001F301',      # Code: 700's foogy
                 'clearSky': '\U00002600',        # Code: 800 clear sky
                 'fewClouds': '\U000026C5',       # Code: 801 sun behind clouds
                 'clouds': '\U00002601',          # Code: 802-803-804 clouds general
                 'hot': '\U0001F525',             # Code: 904
                 'defaultEmoji': '\U0001F300',    # default emojis
                }
        return emoji.get(code, emoji['defaultEmoji'])

    def do_request(self, method='getMe', kwargs=None):
        """Request to api
           :param method: method of endpoint
        """
        if not kwargs:
            kwargs = {}
        urla = "{}{}".format(self.api_url, method)
        resp = requests.get(urla, kwargs, proxies=self.proxies)
        return resp.json()

    # -------------------------------------------
    # Чтобы получить идентификатор чата,
    # сначала отправляем сообщение в чат с ботом,
    # затем снимаем данные этим методом
    # -------------------------------------------
    def get_updates(self, offset=None, timeout=30):
        """Get updates method for receive chat id of whatever
           :param offset: offset
           :param timeout: wait response before raise error
        """
        return self.do_request('getUpdates', {
            'timeout': timeout,
            'offset': offset
        })

    def send_message(self, text: str,
                     chat_id: int,
                     parse_mode: str = None,
                     disable_web_page_preview: bool = False,
                     timeout: int = 20):
        """Send text message"""
        params = {
            'chat_id': chat_id or self.chat_id,
            'text': text,
            'disable_web_page_preview': disable_web_page_preview,
        }
        if parse_mode:
            params['parse_mode'] = parse_mode
        try:
            resp = requests.post(
                "{}{}".format(self.api_url, 'sendMessage'),
                params,
                proxies = self.proxies,
                timeout = timeout
            )
            if not resp.status_code == 200:
                logger.error('Telegram response: %s' % (resp.text, ))
                return {}
            return resp.json()
        except Exception as e:
            logger.error('Telegram и медный таз встретились на раз! %s' % str(e))
        return {}

    def send_document(self, input_file, caption='', chat_id=None):
        """Send document"""
        self.send_file(input_file, caption=caption, chat_id=chat_id, file_type='doc')

    def send_photo(self, input_file, caption='', chat_id=None):
        """Send photo"""
        self.send_file(input_file, caption=caption, chat_id=chat_id, file_type='img')

    def send_file(self, input_file,
                  caption='',
                  file_type: str = 'doc',
                  timeout: int = 20):
        """Send file
           Usage:
               fname = '1.xlsx'
               with open(fname, 'rb') as f:
                   TelegramBot().send_document(f))
           :param input_file: opened descriptor of file
           :param caption: file caption
           :param chat_id: chat id
           :param file_type: type of file
        """
        params = {'caption': caption, 'chat_id': self.chat_id}
        method = 'sendDocument'
        files = {'document': input_file}
        if file_type == 'img':
            method = 'sendPhoto'
            files = {'photo': input_file}
        try:
            resp = requests.post(
                "{}{}".format(self.api_url, method),
                files=files,
                data=params,
                proxies=self.proxies,
                timeout = timeout
            )
            if not resp.status_code == 200:
                logger.error('Telegram response: %s' % (resp.text, ))
                return {}
            return resp.json()
        except Exception as e:
            logger.error('Telegram и медный таз встретились на раз! %s' % str(e))
        return {}

    def set_webhook(self, webhook_url: str):
        """Set webhook for bot
           :param webhook_url: url for webhook
        """
        params = {'url': webhook_url}
        result = self.do_request('setWebhook', params)
        logger.info(result)
        return result
