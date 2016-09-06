#-*- coding: utf-8 -*-

import json
import time
import requests
import requests.packages.urllib3.util.ssl_
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'


def check_token(func):
    """check if the token is invalid
    """
    cache = {}

    def __wrapper__(**kwargs):
        """use cache token or create new"""
        if not cache.get('token',
                         '') or cache.get('expire', 0) + 7200 < time.time():
            resp = DingTalk.get_token(**kwargs)
            if resp['errcode'] != 0:
                raise Exception('HttpError: %s', resp['errmsg'])
            cache['token'] = resp['token']
            cache['expire'] = time.time()
        return cache['token']

    return __wrapper__


class DingTalk():
    def __init__(self, **kwargs):
        self.corpid = ''
        self.coresecret = ''
        self.access_token = None
        self.sender = "发送这ID"
        self.chat_id = '会话ID'

    def get_token(self):

        get_url = 'https://oapi.dingtalk.com/gettoken?corpid=%s&corpsecret=%s' % (
            self.corpid, self.coresecret)

        try:
            r = requests.get(get_url)
        except:
            raise Exception("DingTalk token获取失败!!!")

        data = json.loads(r.content)
        access_token = data['access_token']
        self.access_token = access_token
        return access_token

    def post_images(self, source_img, file_type='image'):
        if self.access_token is None:
            self.access_token = self.get_token()
        headers = {'content-type': 'application/json'}
        post_url = 'https://oapi.dingtalk.com/media/upload?access_token=' + self.access_token + '&type=%s' % file_type
        files = {'media': open(source_img, 'rb')}
        try:
            res = requests.post(post_url, files=files).json()
            media_id = res['media_id']
            templates = {"chatid": self.chat_id,
                         "sender": self.sender,
                         "msgtype": "image",
                         "image": {"media_id": media_id}}
            post_data = json.dumps(templates)
            r = requests.post(post_url, data=post_data, headers=headers)
            return r.json()
        except:
            raise Exception("DingTalk POST数据失败!!!")

    def get_img(self):
        get_url = 'https://oapi.dingtalk.com/media/get?'

    def post_msg(self, content):
        if self.access_token is None:
            self.access_token = self.get_token()
        headers = {'content-type': 'application/json'}
        post_url = 'https://oapi.dingtalk.com/chat/send?access_token=' + self.access_token
        templates = {"chatid": self.chat_id,
                     "sender": self.sender,
                     "msgtype": "text",
                     "text": {"content": content}}
        post_data = json.dumps(templates)
        try:
            r = requests.post(post_url, data=post_data, headers=headers)
            if json.loads(r.content)['errmsg'] != 'ok':
                raise Exception("发送者ID不存在(sender)")
        except:
            raise Exception("DingTalk POST数据失败!!!")

        return r.json()

    def send_link(self, title, text, pic_url, message_url):
        if self.access_token is None:
            self.access_token = self.get_token()

        headers = {'content-type': 'application/json'}
        post_url = 'https://oapi.dingtalk.com/chat/send?access_token=' + self.access_token
        templates = {"chatid": self.chat_id,
                     "sender": self.sender,
                     "msgtype": "link",
                     "link": {"title": title,
                              "text": text,
                              "pic_url": pic_url,
                              "message_url": message_url}}
        post_data = json.dumps(templates)
        try:
            r = requests.post(post_url, data=post_data, headers=headers)
            return r.json()
        except:
            raise Exception("DingTalk POST数据失败!!!")
