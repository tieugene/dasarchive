DEBUG = True
#DEBUG = False
#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': 'unix:/tmp/memcached.sock',
#    }
#}
#DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': '/mnt/shares/dasarchive/dasarchive.db'}}
#DATABASES = {'default': {'ENGINE': 'django.db.backends.mysql', 'NAME': 'dasarchive', 'USER': 'dasarchive', 'PASSWORD': 'dasarchive'}}
DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql_psycopg2', 'NAME': 'dasarchive', 'USER': 'dasarchive', 'PASSWORD': 'dasarchive'}}
#INBOX_ROOT = '/var/lib/trash'
#INBOX_URL = '/trash/'
#OUTBOX_ROOT = '/var/lib/dasarchive'
#OUTBOX_DRIVE = 'B'
#UASCACHE_ROOT = '/var/lib/uascache'
#HELP_TEMPLATE = 'help_formysite.html'
