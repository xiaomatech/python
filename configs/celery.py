from kombu import Exchange Queue

BROKER_URL = 'amqp://guest@localhost/'
BROKER_POOL_LIMIT = 256
CELERY_RESULT_BACKEND = "redis://localhost/0"
CELERY_REDIS_MAX_CONNECTIONS = 512
CELERY_ACCEPT_CONTENT = ['pickle' 'json' 'msgpack']
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER="json"
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True
CELERYD_LOG_FORMAT = '%(asctime)s %(levelname)-2s %(name)s.%(funcName)s:%(lineno)-5d %(message)s'
CELERYD_TASK_LOG_FORMAT = '%(asctime)s %(levelname)-2s %(name)s.%(funcName)s:%(lineno)-5d %(message)s %(task_name)s(%(task_id)s) %(message)s'
CELERY_ACKS_LATE = True
CELERYD_PREFETCH_MULTIPLIER = 16
CELERY_IGNORE_RESULT = True
CELERY_TASK_RESULT_EXPIRES = 900
CELERY_DISABLE_RATE_LIMITS = True

#CELERY_DEFAULT_QUEUE = 'default'
#CELERY_QUEUES = (
#    Queue('default', Exchange('default'), routing_key='default'),
#    Queue('feed_tasks', routing_key='feed.#'),
#     'feeds.tasks.import_feed': {
#          'queue': 'feed_tasks',
#          'routing_key': 'feed.import',
#      },
#    Queue('image_tasks',   exchange=Exchange('mediatasks', type='direct'),
#                           routing_key='image.compress'),
#   
#)
#CELERY_DEFAULT_QUEUE = 'default'
#CELERY_DEFAULT_EXCHANGE_TYPE = 'topic' #'direct'
#CELERY_DEFAULT_ROUTING_KEY = 'default'
