# -*- coding: utf-8 -*-
'''
utils.py
'''

import hashlib, sys, logging

# 3. 3rd parties
import magic

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
__ch = logging.StreamHandler()
__ch.setLevel(logging.DEBUG)  # will be in /var/log/httpd/error_log
logger.addHandler(__ch)
LOG = logger.debug     #: logging function

mime = magic.open(magic.MIME_TYPE)
mime.load()

def file_md5(file, block_size=1024*14):
    '''
    file_md5(file, use_system = False) -> md5sum of "file" as hexdigest string.
    "file" may be a file name or file object, opened for read.
    If "use_system" is True, if possible use system specific program. This ignore, if file object given.
    "block_size" -- size in bytes buffer for calc md5. Used with "use_system=False".
    '''
    if isinstance(file, basestring):
        file = open(file, 'rb')
    h = hashlib.md5()
    block = file.read(block_size)
    while block:
        h.update(block)
        block = file.read(block_size)
    return h.hexdigest()

def get_mime(path):
    # workround
    m = mime.file(path)
    if (m == 'application/msword'):
        e = path.rsplit('.', 1)
        if (len(e) > 1):
            e = e[1].lower()
            if (e == 'xls'):
                m = 'application/vnd.ms-excel'
            elif (e == 'ppt'):
                m = 'application/vnd.ms-powerpoint'
    return m
