#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import json
import datetime
import requests
import codecs
import logging
import pandas

EVENTS = {}

umeng_config = {
    'email': 'abc@test.com',
    'password': '123456'
}


class Umeng(object):
    def __init__(self):
        self.baseurl = "http://api.umeng.com/"
        self.email = umeng_config.get('email')
        self.password = umeng_config.get('password')
        self.log = logging.getLogger(__name__)
        self.auth_token = self.auth()
        self.appkeys = self.get_apps()

    def post_api(self, url, data):
        headers = {'content-type': 'application/json'}
        res = requests.post(url, data=json.dumps(data), timeout=60, headers=headers)
        return res.json()

    def get_api(self, url, auth=None):
        headers = {'content-type': 'application/json'}
        time.sleep(1)
        res = requests.get(url, params=auth, timeout=60, headers=headers)
        return res.json()

    def auth(self):
        data = {
            "email": self.email,
            "password": self.password,
        }
        url = self.baseurl + 'authorize'
        res = self.post_api(url, data)
        if res.get("auth_token"):
            return res["auth_token"]
        else:
            self.log.error("user/password error")
            return None

    def get_apps(self):
        data = {"auth_token": self.auth_token}
        url = self.baseurl + 'apps'
        res = self.get_api(url, data)
        apps = {}
        for app in res:
            apps.update({app.get("appkey"): app.get("name")})
        return apps

    def getdates(self, start_date_str, end_date_str):
        datelist = []
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        temp_date = start_date
        while temp_date < end_date:
            datelist.append(temp_date.strftime("%Y-%m-%d"))
            temp_date = temp_date + datetime.timedelta(days=1)
            continue
        datelist.append(end_date_str)
        return datelist

    def getchannels(self):
        data = {"auth_token": self.auth_token, "per_page": 100}
        url = self.baseurl + 'channels'
        appchannel = {}
        for appkey, appname in self.appkeys.items():
            data.update({"appkey": appkey})
            res = self.get_api(url, data)
            channels = {}
            for channel in res:
                channelid = channel.get("id")
                channelname = channel.get("channel")
                channels.update({channelid: channelname})
            appchannel.update({appkey: channels})
        return appchannel

    def get_eventgroup(self, start_date='', end_date=''):
        appkey_groupids = {}
        data = {"auth_token": self.auth_token,
                "start_date": start_date,
                "end_date": end_date,
                "period_type": "daily"
                }
        url = self.baseurl + '/events/group_list'
        for app in self.appkeys.keys():
            groupid = []
            data.update({"appkey": app})
            res = self.get_api(url, data)
            for event_group in res:
                group_name = event_group.get("name")
                if group_name in EVENTS.keys():
                    groupid.append(event_group)
            appkey_groupids.update({app: groupid})
        return appkey_groupids

    def getchannelinstalls(self, start_date, end_date):
        data = {"auth_token": self.auth_token, "per_page": 100}
        url = self.baseurl + 'channels'
        datelist = self.getdates(start_date, end_date)
        f = codecs.open("channels.txt", "w", 'utf-8')
        f.write("appname" + "\t" + "channel" + "\t" + "installcount" + "\t" + "installdate" + "\n")
        for appkey, appname in self.appkeys.items():
            data.update({"appkey": appkey})
            for datestr in datelist:
                data.update({"date": datestr})
                res = self.get_api(url, data)
                channels = {}
                for channel in res:
                    channelid = channel.get("id")
                    channelname = channel.get("channel")
                    channels.update({channelid: channelname})
                    channelname = channel.get("channel")
                    install = channel.get("install")
                    installdate = channel.get("date")
                    f.write(appname + "\t" + channelname + "\t" + str(install) + "\t" + installdate + "\n")
        f.close()

    def get_users(self, start_date='', end_date=''):
        apppchannels = self.getchannels()
        events = self.get_eventgroup(start_date=start_date, end_date=end_date)
        data = {"type": "device",
                "start_date": start_date,
                "end_date": end_date,
                "period_type": "daily",
                "group_id": "",
                "channels": "",
                "appkey": "",
                "auth_token": self.auth_token}
        url = self.baseurl + 'events/daily_data'
        filename = "userdata.txt"
        f = codecs.open(filename, "w", 'utf-8')
        f.write("appname" + "\t" + "channelname" + "\t" + "display_name" + "\t"
                + "event_id" + "\t" + "date" + "\t" + "usercount" + "\n")

        for appkey, channels in apppchannels.items():
            data["appkey"] = appkey
            appname = self.appkeys.get(appkey)
            for channelid, channelname in channels.items():
                data["channels"] = channelid
                for group in events.get(appkey):
                    group_id = group.get("group_id")
                    data["group_id"] = group_id
                    res = self.get_api(url, data)
                    userdata = res.get("data")
                    dates = res.get("dates")
                    users = userdata.get("all")
                    for index, date in enumerate(dates):
                        tempdata = {"app": appname, "channel": channelname,
                                    "display_name": group.get("display_name"), "name": group.get("name")
                                    }
                        tempdata.update({"date": date, "usercount": users[index]})
                        f.write(appname + "\t" + channelname + "\t" + group.get("display_name") + "\t"
                                + group.get("name") + "\t" + date + "\t" + str(users[index]) + "\n")

        f.close()

    def get_events(self, start_date, end_date):
        data = {"start_date": start_date,
                "end_date": end_date,
                "period_type": "daily",
                "auth_token": self.auth_token}
        url = self.baseurl + '/events/event_list'
        event_groups = self.get_eventgroup()
        events = {}
        for app, groupids in event_groups.items():
            events_bygroup = []
            for groupid in groupids:
                data.update({"appkey": app,
                             "group_id": groupid
                             })
                res = self.get_api(url, data)
                for event in res:
                    event_id = event.get("event_id")
                    events_bygroup.append(event_id)
            events.update({app: events_bygroup})
        return events

    def get_retentions(self, start_date, end_date):
        data = {"start_date": start_date,
                "end_date": end_date,
                "period_type": "daily",
                "auth_token": self.auth_token}
        url = self.baseurl + '/retentions'
        retentions = {}
        for appkey, appname in self.appkeys.items():
            data.update({"appkey": appkey})
            res = self.get_api(url, data)
            retentions.update({appkey: res})
        return retentions

    def get_new_users(self, start_date, end_date):
        data = {"start_date": start_date,
                "end_date": end_date,
                "period_type": "daily",
                "auth_token": self.auth_token}
        url = self.baseurl + '/new_users'
        new_users = {}
        for appkey, appname in self.appkeys.items():
            data.update({"appkey": appkey})
            res = self.get_api(url, data)
            new_users.update({appkey: res})
        return new_users

    def get_active_users(self, start_date, end_date):
        data = {"start_date": start_date,
                "end_date": end_date,
                "period_type": "daily",
                "auth_token": self.auth_token}
        url = self.baseurl + '/active_users'
        active_users = {}
        for appkey, appname in self.appkeys.items():
            data.update({"appkey": appkey})
            res = self.get_api(url, data)
            active_users.update({appkey: res})
        return active_users

    def get_launches(self, start_date, end_date):
        data = {"start_date": start_date,
                "end_date": end_date,
                "period_type": "daily",
                "auth_token": self.auth_token}
        url = self.baseurl + '/launches'
        launches = {}
        for appkey, appname in self.appkeys.items():
            data.update({"appkey": appkey})
            res = self.get_api(url, data)
            launches.update({appkey: res})
        return launches
