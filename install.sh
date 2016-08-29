#!/usr/bin/env bash
sudo yum install -y git redis python-pip python-simplejson python-requests MySQL-python
sudo pip install --upgrade pip
sudo pip install -r requirements.txt

service redis start

mkdir -p /data

cd /data
git clone git://github.com/xiaomatech/falcon.git

