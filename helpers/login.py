#!/usr/bin/env python
# -*- coding:utf8 -*-

import requests
from bs4 import BeautifulSoup
import time
import hashlib
import re
import base64
import rsa
import binascii
import random
from urllib import quote_plus


class Weibo():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
        headers = {'User-Agent': self.agent}
        self.session = requests.session()
        index_url = "http://weibo.com/login.php"
        try:
            self.session.get(index_url, headers=headers, timeout=2)
        except:
            self.session.get(index_url, headers=headers)

    def get_su(self):
        """
        对 email 地址和手机号码 先 javascript 中 encodeURIComponent
        然后在 base64 加密后decode
        """
        username_quote = quote_plus(self.username)
        username_base64 = base64.b64encode(username_quote.encode("utf-8"))
        return username_base64.decode("utf-8")

    # 预登陆获得 servertime, nonce, pubkey, rsakv
    def get_server_data(self, su):
        pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="
        pre_url = pre_url + su + "&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_="
        pre_url = pre_url + str(int(time.time() * 1000))
        pre_data_res = self.session.get(pre_url, headers=self.headers)
        sever_data = eval(
            pre_data_res.content.decode("utf-8").replace(
                "sinaSSOController.preloginCallBack", ''))
        return sever_data

    def get_password(self, servertime, nonce, pubkey):
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(
            self.password)  # 拼接明文js加密文件中得到
        message = message.encode("utf-8")
        passwd = rsa.encrypt(message, key)  # 加密
        passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
        return passwd

    def get_cha(self, pcid):
        cha_url = "http://login.sina.com.cn/cgi/pin.php?r="
        cha_url = cha_url + str(int(random.random() * 100000000)) + "&s=0&p="
        cha_url = cha_url + pcid
        cha_page = self.session.get(cha_url, headers=self.headers)
        with open("cha.jpg", 'wb') as f:
            f.write(cha_page.content)
            f.close()
            print(u"请到当前目录下，找到验证码后输入")

    def login(self):
        # su 是加密后的用户名
        su = self.get_su()
        sever_data = self.get_server_data(su)
        servertime = sever_data["servertime"]
        nonce = sever_data['nonce']
        rsakv = sever_data["rsakv"]
        pubkey = sever_data["pubkey"]
        showpin = sever_data["showpin"]
        password_secret = self.get_password(servertime, nonce, pubkey)

        postdata = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'useticket': '1',
            'pagerefer':
            "http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl",
            'vsnf': '1',
            'su': su,
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'rsakv': rsakv,
            'sp': password_secret,
            'sr': '1366*768',
            'encoding': 'UTF-8',
            'prelt': '115',
            'url':
            'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        if showpin == 0:
            login_page = self.session.post(
                login_url, data=postdata, headers=self.headers)
        else:
            pcid = sever_data["pcid"]
            self.get_cha(pcid)
            postdata['door'] = input(u"请输入验证码")
            login_page = self.session.post(
                login_url, data=postdata, headers=self.headers)
        login_loop = (login_page.content.decode("GBK"))
        pa = r'location\.replace\([\'"](.*?)[\'"]\)'
        loop_url = re.findall(pa, login_loop)[0]
        login_index = self.session.get(loop_url, headers=self.headers)
        uuid = login_index.text
        uuid_pa = r'"uniqueid":"(.*?)"'
        uuid_res = re.findall(uuid_pa, uuid, re.S)[0]
        web_weibo_url = "http://weibo.com/%s/profile?topnav=1&wvr=6&is_all=1" % uuid_res
        weibo_page = self.session.get(web_weibo_url, headers=self.headers)
        weibo_pa = r'<title>(.*?)</title>'
        self.user_id = re.findall(weibo_pa, weibo_page.content.decode(
            "utf-8", 'ignore'), re.S)[0]
        return self.user_id


class Xueqiu():
    def __init__(self, telephone, password):
        self.telephone = telephone
        self.password = password
        self.agent = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        self.headers = {
            'User-Agent': self.agent,
            'Host': "xueqiu.com",
            "Accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch, br",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.6",
            "Connection": "keep-alive"
        }
        self.session = requests.session()
    # 密码的 md5 加密
    def get_md5(self):
        md5 = hashlib.md5()
        md5.update(self.password.encode())
        return md5.hexdigest().upper()

    def login(self):
        url = 'https://xueqiu.com/'
        self.session.get(url, headers=self.headers)
        self.headers['Referer'] = "https://xueqiu.com/"
        login_url_api = "https://xueqiu.com/service/csrf?api=%2Fuser%2Flogin"
        self.session.get(login_url_api, headers=self.headers)
        login_url = "https://xueqiu.com/user/login"
        postdata = {
            "areacode": "86",
            "password": self.get_md5(self.password),
            "remember_me": "on",
            "telephone": self.telephone
        }
        log = self.session.post(login_url, data=postdata, headers=self.headers)
        log = self.session.get("https://xueqiu.com/setting/user",
                               headers=self.headers)
        pa = r'"profile":"/(.*?)","screen_name":"(.*?)"'
        res = re.findall(pa, log.text)
        if res == []:
            raise Exception('fail')
        else:
            return res[0]


class JingDong():
    def __init__(self, un, pw):
        self.headers = {
            'User-Agent':
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
        }
        self.session = requests.session()
        self.login_url = "http://passport.jd.com/uc/login"
        self.post_url = "http://passport.jd.com/uc/loginService"
        self.auth_url = "https://passport.jd.com/uc/showAuthCode"
        self.un = un
        self.pw = pw

    def get_authcode(self, url):
        self.headers['Host'] = 'authcode.jd.com'
        self.headers['Referer'] = 'https://passport.jd.com/uc/login'
        response = self.session.get(url, headers=self.headers)
        with open('authcode.jpg', 'wb') as f:
            f.write(response.content)
        authcode = input("plz enter authcode:")
        return authcode

    def get_info(self):
        '''获取登录相关参数'''
        try:
            page = self.session.get(self.login_url, headers=self.headers)
            soup = BeautifulSoup(page.text)
            input_list = soup.select('.form input')

            data = {}
            data['uuid'] = input_list[0]['value']
            data['eid'] = input_list[4]['value']
            data['fp'] = input_list[5]['value']
            data['_t'] = input_list[6]['value']
            rstr = input_list[7]['name']
            data[rstr] = input_list[7]['value']
            acRequired = self.session.post(
                self.auth_url, data={'loginName': self.un}).text

            if 'true' in acRequired:
                print('need authcode, plz find it and fill in ')
                acUrl = soup.select('.form img')[0]['src2']
                acUrl = 'http:{}&yys={}'.format(acUrl,
                                                str(int(time.time() * 1000)))
                authcode = self.get_authcode(acUrl)
                data['authcode'] = authcode
            else:
                data['authcode'] = ''
            return data
        except Exception as e:
            raise e

    def login(self):
        postdata = self.get_info()
        postdata['loginname'] = self.un
        postdata['nloginpwd'] = self.pw
        postdata['loginpwd'] = self.pw
        try:
            self.headers['Host'] = 'passport.jd.com'
            self.headers['Origin'] = 'https://passport.jd.com'
            self.headers['X-Requested-With'] = 'XMLHttpRequest'
            login_page = self.session.post(
                self.post_url, data=postdata, headers=self.headers)
            return login_page.text
        except Exception as e:
            raise e
