# -*- coding:utf8 -*-
import time
import json
import requests
import logging
log = logging.getLogger(__name__)


class QQFriends():
    def __init__(self):
        self.f = {}  # friends list
        self.g = {}  # group list
        self.d = {}  # discus group list
        self.r = {}  # recent list
        self.c = []
        self.group_info = {}
        self.user_info = {}

    def parse_friends(self, j):
        j = j['result']
        # category,  uin & flag
        for e in j['friends']:
            self.f[e['uin']] = {}
            self.f[e['uin']]['category'] = e['categories']
            self.f[e['uin']]['flag'] = e['flag']

        # marknames
        for e in j['marknames']:
            self.f[e['uin']]['markname'] = e['markname']
            #  self.f[e['uin']]['mType'] = e['type']

            # vipinfo
        for e in j['vipinfo']:
            self.f[e['u']]['vip'] = e['is_vip'] and e['vip_level']

        # user info
        for e in j['info']:
            self.f[e['uin']]['nickname'] = e['nick']
            self.f[e['uin']]['face'] = e['face']
            self.f[e['uin']]['flag'] = e['flag']

        # categories
        for e in j['categories']:
            self.c.append(e['name'])

    def parse_groups(self, j):
        j = j['result']
        self.g = {e['gid']: e for e in j['gnamelist']}
        for e in self.g.values():
            del (e['gid'])

    def parse_discus(self, j):
        j = j['result']
        self.d = {e['did']: e for e in j['dnamelist']}
        for e in self.d.values():
            del (e['did'])

    def parse_recent(self, j):
        j = j['result']
        self.r[0] = []
        self.r[1] = []
        self.r[2] = []
        for b in j:
            self.r[b['type']].append(b['uin'])

    def parse_online_buddies(self, j):
        pass

    def get_group_info(self, gid):
        return self.group_info.get(gid)

    def parse_group_info(self, j):
        j = j['result']
        g = j['ginfo']
        g['members'] = {m['muin']: {} for m in g['members']}  # ignore mflags
        for m in j['stats']:
            g['members'][m['uin']].update(m)
        for m in j['minfo']:
            g['members'][m['uin']].update(m)
        for m in j['cards']:
            g['members'][m['muin']].update(m)
        for m in j['vipinfo']:
            g['members'][m['u']]['vip_level'] = (m['is_vip'] and
                                                 m['vip_level'])
        for m in g['members'].values():
            m.pop('uin', None)
            m.pop('muin', None)
            m.pop('u', None)
        self.group_info[g['gid']] = g
        return g

    def get_user_info(self, uin):
        return self.user_info.get(uin)

    def parse_user_info(self, j):
        self.user_info[j['result']['uin']] = j['result']
        return j['result']


class QQClient():
    default_headers = dict(
        Referer='http://s.web2.qq.com/proxy.html',
        User_Agent=(
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/'
            '537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36'))
    poll_headers = dict(
        Origin='http://d1.web2.qq.com',
        Referer='http://d1.web2.qq.com/proxy.html',
        User_Agent=(
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/'
            '537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36'))

    def __init__(self):
        self.friend_list = QQFriends()
        self.msg_id = 50500000
        self.requests_sess = requests.session()

    def _parse_arg(self, js_str):
        js_str = js_str[js_str.index('(') + 1:len(js_str) - 2]
        return list(map(lambda x: x.strip().strip("'"), js_str.split(',')))

    def get_qq_hash(self):
        # rewritten from an javascript function
        # see mq_private.js for original version
        if not hasattr(self, '_qhash'):
            x = int(self.uin)
            I = self.ptwebqq
            N = [0, 0, 0, 0]
            i = 0
            while i < len(I):
                N[i % 4] ^= ord(I[i])
                i += 1
            V = []
            V.append(x >> 24 & 255 ^ ord('E'))
            V.append(x >> 16 & 255 ^ ord('C'))
            V.append(x >> 8 & 255 ^ ord('O'))
            V.append(x & 255 ^ ord('K'))
            U = []
            for T in range(8):
                if T % 2 == 0:
                    U.append(N[T >> 1])
                else:
                    U.append(V[T >> 1])
            N = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B",
                 "C", "D", "E", "F"]
            V = ""
            for T in range(len(U)):
                V += N[U[T] >> 4 & 15]
                V += N[U[T] & 15]
            self._qhash = V
        return self._qhash

    def QR_veri(self):
        tag = 'verify'
        # --------------necessary urls--------------
        url_get_QR_image = "https://ssl.ptlogin2.qq.com/ptqrshow?" \
                           "appid=501004106&e=0&l=M&s=5&d=72&v=4&t=0.5"
        url_check_QR_state = (
            "https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&"
            "remember_uin=1&login2qq=1&aid=501004106&u1="
            "http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type"
            "%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&"
            "dumy=&fp=loginerroralert&action=0-0-{timer}&mibao_css=m_webqq&"
            "t=undefined&g=1&js_type=0&js_ver=10139&login_sig=&pt_randsalt=0")
        # ------------end necessary urls------------

        # check QR verification state
        t = int(time.clock() * 10000) + 10000  # default clock
        prev = -1
        while True:
            time.sleep(1)
            t += int(time.clock() * 10000)
            res = self._parse_arg(requests.post(url_check_QR_state.format(
                timer=t)).text).decode('utf-8').strip()
            if prev != res[0]:
                if res[0] == '65':
                    log.info(tag + 'QR code expired.')
                elif res[0] == '66':
                    log.info(tag +
                             'Please scan the QRCode shown on your screen.')
                elif res[0] == '67':
                    log.info(tag + 'Please press confirm on your phone.')
                elif res[0] == '0':
                    # QR code verification completed
                    log.info(tag + res[-2])
                    self.username = res[-1]
                    log.info(tag + 'User name: ' + self.username)
                    break
                prev = res[0]

        # first step login
        requests.post(res[2])

        # cookie proxy
        self.requests_sess.cookies.set_cookie(
            'p_skey',
            self.requests_sess.cookies.get_dict('.web2.qq.com')['p_skey'],
            'w.qq.com')
        self.requests_sess.cookies.set_cookie(
            'p_uin',
            self.requests_sess.cookies.get_dict('.web2.qq.com')['p_uin'],
            'w.qq.com')

    def login(self, get_info=True, save_veri=False, filename=None):
        tag = 'login'
        # --------necessary urls & data--------
        url_get_vfwebqq = "http://s.web2.qq.com/api/getvfwebqq?" \
                          "ptwebqq={ptwebqq}&psessionid=&t=1456633306528"
        url_login2 = "http://d1.web2.qq.com/channel/login2"
        post_login2 = {'clientid': 53999199,
                       'pssessionid': '',
                       'status': 'online'}
        # ------end necessary urls & data------

        # get ptwebqq
        self.ptwebqq = self.requests_sess.cookies.get_dict('.qq.com')[
            'ptwebqq']
        # get vfwebqq
        self.vfwebqq = requests.post(
            url_get_vfwebqq.format(ptwebqq=self.ptwebqq),
            headers=self.default_headers).json()['result']['vfwebqq']

        # second step login
        post_login2['ptwebqq'] = self.ptwebqq
        j2 = requests.post(url_login2,
                           data={'r': json.dumps(post_login2)}).json()

        self.uin = j2['result']['uin']
        self.psessionid = j2['result']['psessionid']
        self.status = j2['result']['status']
        self.get_qq_hash()
        if get_info:
            self.get_user_friends()
            self.get_group_list()
            self.get_discus_list()
        if save_veri:
            log.info(tag + 'Verification saved @ ' + self.save_veri(filename))
        self.get_online_buddies()
        self.get_recent_list()

    def save_veri(self, filename=None):
        if filename is None:
            filename = './' + str(self.uin) + '.veri'

        with open(filename, 'w') as f:
            # save all cookies
            f.write('{"cookies":')
            json.dump(self.requests_sess.cookies, f)
            # save username
            f.write(',\n"username":"%s"' % self.username)
            # save user friends, groups and discus groups
            f.write(',\n"friends":')
            json.dump(self.friend_list.f, f)
            f.write(',\n"groups":')
            json.dump(self.friend_list.g, f)
            f.write(',\n"discus_groups":')
            json.dump(self.friend_list.d, f)
            f.write('}')

        return filename

    def load_veri(self, filename):
        tag = 'verify'
        with open(filename, 'r') as f:
            v = json.load(f)
        for domain, cookies in v['cookies'].items():
            for name, value in cookies.items():
                self.requests_sess.cookies.set(name, value, domain)
        self.username = v['username']
        self.friend_list.f = {
            int(id): value
            for id, value in v['friends'].items()
        }
        self.friend_list.g = {
            int(id): value
            for id, value in v['groups'].items()
        }
        self.friend_list.d = {
            int(id): value
            for id, value in v['discus_groups'].items()
        }
        log.info(tag + 'Verification loaded from ' + filename)
        log.info(tag + 'Username: ' + self.username)

    def poll_message(self):
        url_poll2 = 'http://d1.web2.qq.com/channel/poll2'
        d = {'r': json.dumps({
            "ptwebqq": self.ptwebqq,
            "clientid": 53999199,
            "psessionid": self.psessionid,
            "key": ""
        })}
        return requests.post(
            url_poll2, data=d, headers=self.poll_headers).json()

    def get_user_friends(self):
        self.friend_list.parse_friends(requests.get(
            'http://s.web2.qq.com/api/get_user_friends2',
            data={'r': json.dumps({
                'hash': self.get_qq_hash(),
                'vfwebqq': self.vfwebqq
            })},
            headers=self.default_headers).json())
        log.info('list' + 'Finished getting friend list.')

    def get_group_list(self):
        self.friend_list.parse_groups(requests.get(
            'http://s.web2.qq.com/api/get_group_name_list_mask2',
            data={'r': json.dumps({
                'hash': self.get_qq_hash(),
                'vfwebqq': self.vfwebqq
            })},
            headers=self.default_headers).json())
        log.info('list' + 'Group list fetched.')

    def get_discus_list(self):
        self.friend_list.parse_discus(requests.get(
            'http://s.web2.qq.com/api/get_discus_list',
            data={'clientid': 53999199,
                  'psessionid': self.psessionid,
                  'vfwebqq': self.vfwebqq,
                  't': int(time.time())},
            headers=self.default_headers).json())
        log.info('list' + 'Discus group list fetched.')

    def get_online_buddies(self):
        # method is GET
        url_get_online = ('http://d1.web2.qq.com/channel/get_online_buddies2?'
                          'vfwebqq={}&clientid={}&psessionid={}&t={}').format(
                              self.vfwebqq, 53999199, self.psessionid,
                              time.time())
        self.friend_list.parse_online_buddies(requests.get(
            url_get_online, headers=self.poll_headers).json())
        log.info('list' + 'Online buddies list fetched.')

    def get_recent_list(self):
        self.friend_list.parse_recent(requests.post(
            'http://d1.web2.qq.com/channel/get_recent_list2',
            data={'r': json.dumps({
                'vfwebqq': self.vfwebqq,
                'clientid': 53999199,
                'psessionid': self.psessionid
            })},
            headers=self.poll_headers).json())
        log.info('list' + 'Recent list fetched.')

    def get_self_info(self):
        # method is GET
        if not hasattr(self, 'info'):
            r = requests.get(
                'http://s.web2.qq.com/api/get_self_info2?t' + str(time.time()),
                headers=self.default_headers).json()
            if r['retcode'] == 0:
                self.info = r['result']
            else:
                log.e('info', 'User self info fetching failed.')
        return self.info

    def get_user_info(self, uin):
        # method is GET
        r = self.friend_list.get_user_info(uin)
        if r is not None:
            return r
        else:
            url_get_user_info = (
                'http://s.web2.qq.com/api/get_friend_info2?'
                'tuin={}&vfwebqq={}&clientid=53999199&psessionid={}&'
                't={}').format(uin, self.vfwebqq, self.psessionid, time.time())
            j = requests.get(url_get_user_info,
                             headers=self.default_headers).json()
            return self.friend_list.parse_user_info(j)

    def get_recent_contact_list(self, vfwebqq="", psessionid="", clientid=0):
        rsp_json = requests.post(
            url='http://d1.web2.qq.com/channel/get_recent_list2',
            data={
                "vfwebqq": vfwebqq if vfwebqq else self.vfwebqq,
                "clientid": clientid if clientid else self.clientid,
                "psessionid": psessionid if psessionid else self.psessionid
            },
            headers=self.default_headers).json()

        if 'result' in rsp_json:  # 成功收到信息
            return rsp_json['result']
        else:
            return False  # 其他错误

    def get_discuss_info(self, did, vfwebqq="", clientid=0, psessionid=""):
        rsp_json = requests.get(
            url='http://d1.web2.qq.com/channel/get_discu_info',
            data={
                'did': did,
                'vfwebqq': vfwebqq if vfwebqq else self.vfwebqq,
                'clientid': clientid if clientid else self.clientid,
                'psessionid': psessionid if psessionid else self.psessionid,
                't': int(time()),  # unix time
            },
            headers=self.default_headers).json()
        return rsp_json['result']['info']

    def get_group_info(self, gid):
        # method is GET
        r = self.friend_list.get_group_info(gid)
        if r is not None:
            return r
        else:
            url_get_group_info = (
                'http://s.web2.qq.com/api/get_group_info_ext2?'
                'gcode={}&vfwebqq={}&t={}').format(
                    self.friend_list.g[gid]['code'], self.vfwebqq, time.time())
            print(url_get_group_info)
            j = requests.get(url_get_group_info,
                             headers=self.default_headers).json()
            return self.friend_list.parse_group_info(j)

    def send_buddy_message(self,
                           uin,
                           content,
                           font="宋体",
                           size=10,
                           color='000000'):
        self.msg_id += 1
        c = json.dumps([
            content, ["font", {"name": font,
                               "size": size,
                               "style": [0, 0, 0],
                               "color": color}]
        ])
        requests.post('http://d1.web2.qq.com/channel/send_buddy_msg2',
                      data={'r': json.dumps({
                          'to': uin,
                          'content': c,
                          'face': self.friend_list.f[uin]['face'],
                          'clientid': 53999199,
                          'msg_id': self.msg_id,
                          'psessionid': self.psessionid
                      })},
                      headers=self.poll_headers)

    def send_group_message(self,
                           gid,
                           content,
                           font="宋体",
                           size=10,
                           color='000000'):
        self.msg_id += 1
        c = json.dumps([
            content, ["font", {"name": font,
                               "size": size,
                               "style": [0, 0, 0],
                               "color": color}]
        ])
        requests.post('http://d1.web2.qq.com/channel/send_qun_msg2',
                      data={'r': json.dumps({
                          'group_uin': gid,
                          'content': c,
                          'face': 0,  # TODO figure out what `face` is
                          'clientid': 53999199,
                          'msg_id': self.msg_id,
                          'psessionid': self.psessionid
                      })},
                      headers=self.poll_headers)

    def get_real_uin(self, tuin):
        """Get user's real uin by tuin
        WebQQ protocol itself uses `tuin` which is not the original uin,
        getting the real uin requires an API request, which is exactly
        what this method does.
        Returns user's real uin.
        Client.get_real_uin(tuin) -> int
        """
        # method is GET
        j = requests.get(
            ('http://s.web2.qq.com/api/get_friend_uin2?tuin={}&type=1&'
             'vfwebqq={}&t={}').format(tuin, self.vfwebqq, time.time()),
            headers=self.default_headers).json()
        if j['retcode'] != 0:
            raise RuntimeError('get_real_uin failed: illegal arguments.')
        else:
            return j['result']['account']
