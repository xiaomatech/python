#!/usr/bin/env bash

celery worker -A app.celery --beat --schedule=/var/run/celerybeat-schedule --event --workdir=/data/workers --loglevel=WARNING --logfile=/data/logs/%n.celery.log
    -Ofair --without-gossip --pidfile=/var/run/%n.celery.pid -P gevent --concurrency=32 --autoscale=256,32

