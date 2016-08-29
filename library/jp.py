# -*- coding:utf-8 -*-
import jpush as jpush
from jpush import common
from configs import jpush_config

class jp:
    _jpush = jpush.JPush(jpush_config.get('app_key'), jpush_config.get('master_secret'))
    _jpush.set_logging("DEBUG")
    device = _jpush.create_device()
    alias = "alias1"
    platform = "android,ios"
    device.get_aliasuser(alias, platform)
    reg_id = '090c1f59f89'
    entity = jpush.device_tag("")
    device.set_deviceinfo(reg_id, entity)
    reg_id = '090c1f59f89'
    device.get_deviceinfo(reg_id)
    device.delete_alias(alias, platform)
    tag = "ddd"
    device.delete_tag(tag, platform)
    device.get_taglist()
    registration_id = '090c1f59f89'
    device.check_taguserexist(tag, registration_id)
    entity = jpush.device_regid(jpush.add("090c1f59f89"))
    device.update_tagusers(tag, entity)
    entity = jpush.device_tag(jpush.add("ddd", "tageee"))
    result=device.set_devicemobile(reg_id, entity)
    entity = jpush.device_mobile("18588232140")
    device.set_devicemobile(reg_id, entity)


    push = _jpush.create_push()
    push.audience = jpush.all_
    push.notification = jpush.notification(alert="hello python jpush api")
    push.platform = jpush.all_
    try:
        response=push.send()
    except common.Unauthorized:
        raise common.Unauthorized("Unauthorized")
    except common.APIConnectionException:
        raise common.APIConnectionException("conn")
    except common.JPushFailure:
        print ("JPushFailure")
    except:
        print ("Exception")

    push.audience = jpush.audience(
        jpush.tag("tag1", "tag2"),
        jpush.alias("alias1", "alias2")
    )
    push.notification = jpush.notification(alert="Hello world with audience!")
    push.platform = jpush.all_
    print (push.payload)
    push.options = {"time_to_live":86400, "sendno":12345,"apns_production":True}
    push.send()

    ios_msg = jpush.ios(alert="Hello, IOS JPush!", badge="+1", sound="a.caf", extras={'k1':'v1'})
    android_msg = jpush.android(alert="Hello, android msg")
    push.notification = jpush.notification(alert="Hello, JPush!", android=android_msg, ios=ios_msg)
    push.platform = jpush.all_
    push.send()

    ios_msg = jpush.ios(alert="Hello, IOS JPush!", badge="+1", extras={'k1':'v1'}, sound_disable=True)
    android_msg = jpush.android(alert="Hello, android msg")
    push.notification = jpush.notification(alert="Hello, JPush!", android=android_msg, ios=ios_msg)
    push.platform = jpush.all_
    push.send()

    push.notification = jpush.notification(alert="a sms message from python jpush api")
    push.platform = jpush.all_
    push.smsmessage=jpush.smsmessage("a sms message from python jpush api",0)
    print (push.payload)
    push.send()

    push.notification = jpush.notification(alert="Hello, world!")
    push.platform = jpush.all_
    push.send_validate()

    report=_jpush.create_report();
    report.get_messages("3289406737")
    report.get_received("3289406737")
    report.get_users("DAY","2016-04-10","3")

    schedule = _jpush.create_schedule()
    schedule.delete_schedule("e9c553d0-0850-11e6-b6d4-0021f652c102")
    schedule.get_schedule_by_id("e9c553d0-0850-11e6-b6d4-0021f652c102")
    schedule.get_schedule_list("1")
    schedule = _jpush.create_schedule()

    push=push.payload
    trigger=jpush.schedulepayload.trigger("2016-07-17 12:00:00")
    schedulepayload=jpush.schedulepayload.schedulepayload("name",True,trigger,push)
    result=schedule.post_schedule(schedulepayload)
    print (result.status_code)

    push=push.payload
    trigger=jpush.schedulepayload.trigger("2016-05-17 12:00:00")
    schedulepayload=jpush.schedulepayload.schedulepayload("update a new name", True, trigger, push)
    schedule.put_schedule(schedulepayload,"17349f00-0852-11e6-91b1-0021f653c902")



