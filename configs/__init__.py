#!/usr/bin/env python
# -*- coding:utf8 -*-

autoloader_dir = ['controllers']  #['library','helpers','models','controllers']

redis_conf = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0,
    'max_connections': 600,
}

log_common = {
    'mode': 'a+',
    'maxBytes': 1073741824,  #1G
    'backupCount': 5
}

log_error_config = {'log_file': './logs/error.log'}

log_debug_config = {'log_file': './logs/debug.log'}

log_loader = {'log_file': './logs/loader.log'}

ssh_config = {
    'private_key_file': '',
    'port': 22,
    'user': 'ops',
    'password': 'feafoanohfd',
    'timeout': 15
}

jpush_config = {
    'app_key' : '6be9204c30b9473e87bad4dc',
    'master_secret' : '9349ad7c90292a603c512e92'
}

yunpain_config = {
    'APIKEY':'xxxxxx',
    'API_SECRET':'12345678'
}
