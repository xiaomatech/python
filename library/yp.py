# -*- coding:utf-8 -*-
from yunpian.SmsOperator import SmsOperator
from yunpian.VoiceOperator import VoiceOperator
from yunpian.TplOperator import TplOperator
from yunpian.UserOperator import UserOperator
from yunpian.FlowOperator import FlowOperator
from yunpian.Tea import Tea
from yunpian.DES import DES

import simplejson as json
from configs import yunpain_config

class YP:
    # 单条短信发送
    APIKEY=yunpain_config.get('APIKEY')
    API_SECRET=yunpain_config.get('API_SECRET')
    smsOperator = SmsOperator(APIKEY)
    result = smsOperator.single_send({'mobile': '13000000000', 'text': '【yunpian】您的验证码是4444'})
    print json.dumps(result.content, ensure_ascii=False)

    #
    # TEA加密短信发送
    mobile = Tea.encrypt_yunpian('13000000009', API_SECRET)
    text = Tea.encrypt_yunpian('【yunpian】您的验证码是4444', API_SECRET)
    result = smsOperator.single_send(
        {'mobile': mobile, 'text': text, 'encrypt': Tea.encrypt_name})
    print json.dumps(result.content, ensure_ascii=False)

    # DES加密短信发送
    mobile = DES.encrypt_yunpian('13000000011', API_SECRET)
    text = DES.encrypt_yunpian('【yunpian】您的验证码是4444', API_SECRET)
    result = smsOperator.single_send(
        {'mobile': mobile, 'text': text, 'encrypt': DES.encrypt_name})
    print json.dumps(result.content, ensure_ascii=False)

    #
    # 批量短信发送
    print json.dumps(smsOperator.batch_send({'mobile': '13000000001,13000000002', 'text': '【yunpian】您的验证码是0000'}).content,
                     ensure_ascii=False)
    # 个性化短信发送
    print json.dumps(smsOperator.multi_send(
        {'mobile': '13000000003,13000000004', 'text': '【yunpian】您的验证码是4442,【yunpian】您的验证码是4441'}).content,
                     ensure_ascii=False)

    # 获取账号信息
    userOperator = UserOperator()
    result = userOperator.get()
    print json.dumps(result.content,ensure_ascii=False)

    # 短信模板
    tplOperator = TplOperator()
    result = tplOperator.get()
    print json.dumps(result.content,ensure_ascii=False)
    print json.dumps(tplOperator.get_default({'tpl_id': '2'}).content, ensure_ascii=False)

    # 流量
    flowOperator = FlowOperator()
    print json.dumps(flowOperator.recharge({'mobile': '18720085991', 'sn': '1008601'}).content, ensure_ascii=False)

    # 语音
    voiceOperator = VoiceOperator()
    print json.dumps(voiceOperator.send({'mobile': '18720085991', 'code': '0012'}).content, ensure_ascii=False)
