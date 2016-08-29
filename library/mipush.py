# -*- coding: utf-8 -*-
import json
import requests

# import traceback


class Constants(object):

    reg_url = '/v3/message/regid'
    alias_url = '/v3/message/alias'
    user_account_url = '/v2/message/user_account'
    topic_url = '/v3/message/topic'
    multi_topic_url = '/v3/message/multi_topic'
    all_url = '/v3/message/all'
    multi_messages_regids_url = '/v2/multi_messages/regids'
    multi_messages_aliases_url = '/v2/multi_messages/aliases'
    multi_messages_user_accounts_url = '/v2/multi_messages/user_accounts'
    stats_url = '/v1/stats/message/counters'
    message_trace_url = '/v1/trace/message/status'
    messages_trace_url = '/v1/trace/messages/status'
    validation_regids_url = '/v1/validation/regids'
    subscribe_url = '/v2/topic/subscribe'
    unsubscribe_url = '/v2/topic/unsubscribe'
    subscribe_alias_url = '/v2/topic/subscribe/alias'
    unsubscribe_alias_url = '/v2/topic/unsubscribe/alias'
    delete_schedule_job = '/v2/schedule_job/delete'
    check_schedule_job_exist = '/v2/schedule_job/exist'
    get_all_aliases = '/v1/alias/all'
    get_all_topics = '/v1/topic/all'

    fetch_invalid_regids_url = 'https://feedback.xmpush.xiaomi.com/v1/feedback/fetch_invalid_regids'

    UNION = 'UNION'  # 并集
    INTERSECTION = 'INTERSECTION'  # 交集
    EXCEPT = 'EXCEPT'  # 差集


SuccessCode = 0


class MipushError(Exception):
    def __init__(self, result):
        self.status_code = result.status_code
        self.raw = result.raw


class Result(object):
    def __init__(self, req):
        self.status_code = req.status_code
        try:
            raw = json.loads(req.text)
            self.raw = raw
            self.errorCode = raw['code']
        except Exception:
            self.raw = req.text
            raise MipushError(self)


class MipushClient(object):
    def __init__(self, version, appsecret, retries=1, timeout=3):
        '''
        @params version 发布版本或者测试版本:release dev
        @params appsecret 注册后申请取得
        @params retries 因网络异常允许的重试次数,默认重试一次
        @params timeout 接口的请求超时时间,默认3秒
        '''
        self.appsecret = appsecret
        self.retries = retries
        self.timeout = timeout

        assert version in ['release', 'dev']
        if version == 'release':
            self.domain = 'https://api.xmpush.xiaomi.com'
        else:
            self.domain = 'https://sandbox.xmpush.xiaomi.com'

    def getResult(self, method, url, fields):
        '''发送请求，获取result，带重试'''
        r = self._getReq(method, url, fields)
        result = Result(r)
        if result.errorCode == SuccessCode:
            return result
        # 重试
        retries = self.retries
        while retries > 0:
            retries -= 1
            r = self._getReq(method, url, fields)
            result = Result(r)
            if result.errorCode == SuccessCode:
                return result
        raise MipushError(result)

    def _getReq(self, method, url, fields):
        '''发送请求'''
        headers = {
            'Authorization': 'key=%s' % self.appsecret,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        assert method in ['post', 'get']
        timeout = self.timeout
        if method == 'get':
            r = requests.get(url,
                             params=fields,
                             headers=headers,
                             timeout=timeout)
        elif method == 'post':
            r = requests.post(url,
                              params=fields,
                              headers=headers,
                              timeout=timeout)
        return r

    # ##### DevTools #####

    def getAliasesOf(self, packagename, regid):
        ''' 获取一个应用的某个用户目前设置的所有Alias '''
        url = self.domain + Constants.get_all_aliases
        fields = {'registration_id': regid,
                  'restricted_package_name': packagename}
        return self.getResult('get', url, fields)

    def getTopicsOf(self, packagename, regid):
        ''' 获取一个应用的某个用户目前订阅的所有Topic '''
        url = self.domain + Constants.get_all_topics
        fields = {'registration_id': regid,
                  'restricted_package_name': packagename}
        return self.getResult('get', url, fields)

    def getInvalidRegIds(self):
        '''
        获取失效的regId列表不需要传递任何HTTP参数。
        获取失效的regId列表，每次请求最多返回1000个regId。
        每次请求之后，成功返回的失效的regId将会从MiPush数据库删除。
        存在失效的regid
            {“result”:”ok”,”description”:”成功”,”data”:{“list”:["regid1","regid2","regid3"]},”code”:0}
        不存在失效的regid
            {“result”:”ok”,”description”:”成功”,”data”:{“list”:[]},”code”:0}
        '''
        url = Constants.fetch_invalid_regids_url
        fields = {}
        return self.getResult('get', url, fields)

    # ##### Sender #####

    def sendToId(self, message, regid_list):
        '''指定regId列表群发'''
        if not isinstance(regid_list, (list, tuple, set)):
            regid_list = [regid_list, ]  # 一个元素的list

        url = self.domain + Constants.reg_url
        fields = message.get_fields()
        fields['registration_id'] = ','.join([k for k in regid_list if k])
        return self.getResult('post', url, fields)

    def sendToAlias(self, message, alias_list):
        '''指定别名列表群发'''
        if not isinstance(alias_list, (list, tuple, set)):
            alias_list = [alias_list]

        url = self.domain + Constants.alias_url
        fields = message.get_fields()
        fields['alias'] = ','.join([k for k in alias_list if k])
        return self.getResult('post', url, fields)

    def sendToUserAccount(self, message, account_list):
        '''指定userAccount列表群发'''
        if not isinstance(account_list, (list, tuple, set)):
            account_list = [account_list]

        url = self.domain + Constants.user_account_url
        fields = message.get_fields()
        fields['user_account'] = ','.join([k for k in account_list if k])
        return self.getResult('post', url, fields)

    def broadcastTopic(self, message, topic):
        '''指定topic群发'''
        url = self.domain + Constants.topic_url
        fields = message.get_fields()
        fields['topic'] = topic
        return self.getResult('post', url, fields)

    def broadcastTopicList(self, message, topic_list, topic_op):
        '''广播消息，多个topic，支持topic间的交集、并集或差集'''
        if len(topic_list) == 1:
            return self.broadcastTopic(message, topic_list)
        url = self.domain + Constants.multi_topic_url
        fields = message.get_fields()
        fields['topics'] = u';$;'.join([k for k in topic_list if k])
        fields['topic_op'] = topic_op
        return self.getResult('post', url, fields)

    def broadcastAll(self, message):
        '''向所有设备发送消息'''
        url = self.domain + Constants.all_url
        fields = message.get_fields()
        return self.getResult('post', url, fields)

    def multiSend(self, targetMessage_list, ty, timeToSend=None):
        '''多条发送'''
        TARGET_TYPE_REGID = 1
        TARGET_TYPE_ALIAS = 2
        TARGET_TYPE_USER_ACCOUNT = 3
        url = {
            TARGET_TYPE_REGID:
            self.domain + Constants.multi_messages_regids_url,
            TARGET_TYPE_ALIAS:
            self.domain + Constants.multi_messages_aliases_url,
            TARGET_TYPE_USER_ACCOUNT:
            self.domain + Constants.multi_messages_user_accounts_url,
        }[ty]
        data_list = [t.get_fields() for t in targetMessage_list]
        fields = {}
        fields['messages'] = json.dumps(data_list)
        if timeToSend:
            fields['time_to_send'] = timeToSend
        return self.getResult('post', url, fields)

    def checkScheduleJobExist(self, msgid):
        '''检测定时任务是否存在'''
        url = self.domain + Constants.check_schedule_job_exist
        fields = {'job_id': msgid}
        return self.getResult('post', url, fields)

    def deleteScheduleJob(self, msgid):
        '''删除定时任务'''
        url = self.domain + Constants.delete_schedule_job
        fields = {'job_id': msgid}
        return self.getResult('post', url, fields)

    # #### Stats #####

    def getStats(self, packagename, startDate, endDate):
        '''
        @brief 获取消息的统计数据
        @params packagename IOS设备,传入App的Bundle Id;Android设备,传入App的包名
        @params startDate 表示开始日期,如20140214
        @params endDate 表示结束日期,如20140314
        '''
        url = self.domain + Constants.stats_url
        fields = {
            'start_date': startDate,
            'end_date': endDate,
            'restricted_package_name': packagename,
        }
        return self.getResult('get', url, fields)

    # #### Subscription #####

    def subscribeForRegid(self, regid_list, topic, packagename=None):
        ''' 订阅RegId的标签 '''
        if not isinstance(regid_list, (list, tuple, set)):
            regid_list = [regid_list]

        url = self.domain + Constants.subscribe_url
        fields = {'topic': topic}
        fields['registration_id'] = ','.join([k for k in regid_list if k])
        if packagename:
            fields['restricted_package_name'] = packagename
        return self.getResult('post', url, fields)

    def unsubscribeForRegid(self, regid_list, topic, packagename=None):
        ''' 取消订阅RegId的标签 '''
        if not isinstance(regid_list, (list, tuple, set)):
            regid_list = [regid_list]

        url = self.domain + Constants.unsubscribe_url
        fields = {'topic': topic}
        fields['registration_id'] = ','.join([k for k in regid_list if k])
        if packagename:
            fields['restricted_package_name'] = packagename
        return self.getResult('post', url, fields)

    def subscribeForAlias(self, alias_list, topic, packagename=None):
        ''' 订阅Alias的标签 '''
        if not isinstance(alias_list, (list, tuple, set)):
            alias_list = [alias_list]

        url = self.domain + Constants.subscribe_alias_url
        fields = {'topic': topic}
        fields['aliases'] = ','.join([k for k in alias_list if k])
        if packagename:
            fields['restricted_package_name'] = packagename
        return self.getResult('post', url, fields)

    def unsubscribeForAlias(self, alias_list, topic, packagename=None):
        ''' 取消订阅Alias的标签 '''
        if not isinstance(alias_list, (list, tuple, set)):
            alias_list = [alias_list]

        url = self.domain + Constants.unsubscribe_alias_url
        fields = {'topic': topic}
        fields['aliases'] = ','.join([k for k in alias_list if k])
        if packagename:
            fields['restricted_package_name'] = packagename
        return self.getResult('post', url, fields)

    # #### Trace #####

    def getMessageStatusById(self, msgid):
        '''
        @brief 通过Id追踪消息状态
        @params msgid 发送消息时返回的msgid
        '''
        url = self.domain + Constants.message_trace_url
        fields = {'msg_id': msgid}
        return self.getResult('get', url, fields)

    def getMessageStatusByJobKey(self, jobkey):
        '''
        @brief 通过JobKey追踪消息状态
        @params jobKey 发送消息时设置的jobKey
        '''
        url = self.domain + Constants.message_trace_url
        url = self.domain + Constants.message_trace_url
        fields = {'job_key': jobkey}
        return self.getResult('get', url, fields)

    def getMessagesStatusByTimeArea(self, beginTime, endTime):
        '''
        @brief 通过时间范围追踪消息状态
        @params beginTime 表示开始时间戳，单位ms
        @params endTime 表示结束时间戳，单位ms
        '''
        url = self.domain + Constants.message_trace_url
        fields = {'begin_time': beginTime, 'end_time': endTime}
        return self.getResult('get', url, fields)


class Message(object):
    def __init__(self):
        self._data = {}
        self._data['notify_id'] = 0
        self._data['notify_type'] = -1
        self._data['payload'] = ''

    def build(self,
              packagename,
              title,
              description,
              payload=None,
              pass_through=0,
              notify_type=-1,
              notify_id=0,
              time_to_live=None,
              time_to_send=None,
              extra=None):
        '''
        restricted_package_name  # 支持多包名
        payload  # payload是字符串
        title  # 在通知栏的标题，长度小于16
        description  # 在通知栏的描述，长度小于128
        pass_through  # 是否透传给app(1 透传 0 通知栏信息)
        notify_type  可以是DEFAULT_ALL或者以下其他几种的OR组合
            DEFAULT_ALL = -1;
            DEFAULT_SOUND  = 1;  // 使用默认提示音提示；
            DEFAULT_VIBRATE = 2;  // 使用默认震动提示；
            DEFAULT_LIGHTS = 4;   // 使用默认led灯光提示；
        notify_id  # 0-4同一个notifyId在通知栏只会保留一条
        time_to_live  # 可选项,long,当用户离线是，消息保留时间，默认两周，单位ms
        time_to_send  # 可选项,long,定时发送消息，用自1970年1月1日以来00:00:00.0 UTC时间表示（以毫秒为单位的时间）。
        extra  # 可选项，额外定义一些key value（字符不能超过1024，key不能超过10个）
        extra的一部分可选项:(不包括全部,更多查看文档)
            *locale  可以接收消息的设备的语言范围，用逗号分隔。
            *locale_not_in
            *model  model支持三种用法:机型、品牌、价格区间
            *model_not_in
            *app_version  可以接收消息的app版本号，用逗号分割。
            *app_version_not_in
            *connpt  指定在特定的网络环境下才能接收到消息;目前只支持指定wifi;
            *jobkey  设置消息的组ID
            *ticker  开启通知消息在状态栏滚动显示
            *sound_uri  自定义通知栏消息铃声
            *notify_foreground  预定义通知栏消息的点击行为,参考文档2.2.3
            *flow_control  控制是否需要进行平缓发送，1表示平缓，0否
            *notify_effect  指定点击行为
        '''

        if not isinstance(packagename, (list, tuple, set)):
            packagename = [packagename]
        self._data['restricted_package_name'] = ','.join(packagename)
        self._data['title'] = title
        self._data['description'] = description
        self._data['pass_through'] = pass_through
        self._data['notify_type'] = notify_type
        self._data['notify_id'] = notify_id
        if payload:
            self._data['payload'] = payload
        if time_to_live is not None:
            self._data['time_to_live'] = time_to_live
        if time_to_send is not None:
            self._data['time_to_send'] = time_to_send
        self.fields = {}
        self.json_infos = {}

        for k, v in self._data.iteritems():
            self.fields[k] = v
            self.json_infos[k] = v

        EXTRA_PREFIX = 'extra.'
        self.json_infos['extra'] = {}
        for k, v in (extra or {}).iteritems():
            self.fields[EXTRA_PREFIX + k] = v
            self.json_infos['extra'][k] = v

    def get_fields(self):
        return self.fields

    def getJSONInfos(self):
        return self.json_infos


if __name__ == '__main__':
    APPSECRET = 'your app secret'
    PACKAGE_ANDROID = 'Android设备,传入App的包名'
    PACKAGE_IOS = 'IOS设备,传入App的Bundle Id'

    # sandbox API只提供对IOS支持，不支持Android。
    client = MipushClient('release', APPSECRET, retries=1, timeout=3)
    message = Message()
    message.build(PACKAGE_ANDROID, u'标题', u'内容')
    # 向所有设备发送消息
    # result = client.broadcastAll(message)

    try:
        result = client.checkScheduleJobExist('not-exist-job')
        # result = client.getInvalidRegIds()
        print result.raw
    except MipushError as e:
        print 'error'
        print e.raw


