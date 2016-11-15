#!/usr/bin/env bash
sudo yum install -y git redis python-pip python-simplejson python-requests MySQL-python
sudo pip install --upgrade pip
sudo pip install -r requirements.txt

service redis start

mkdir -p /data

cd /data
git clone git://github.com/xiaomatech/falcon.git


#ip2location
#wget 'http://ipfile.galaxyclouds.cn/mydata4vipday2.datx'  --http-user=backend --http-password=yuchengzhen -O vendors/ip.datx

#ip2location backup
#wget 'http://user.ipip.net/download.php?type=datx&token=d92cbe6ba7906664ac1050494120a96b055a9670' -O vendors/ip.datx
