#!/bin/env python
# -*- coding: utf-8 -*-
'''
testdav.py - tool to test WebDAV servers: make right and wrong requests - and saves responces.
./testdav.py http://localhost:8000/dav/ test
python testdav.py http://localhost/dasarchive/dav/ test
'''
# 1. system
import os, sys, pprint

# 2. 3rd parties
import requests, tidy

reload(sys)
sys.setdefaultencoding('utf-8')

def prepare(path):
    '''
    Prepare outdir and realpath to work:
    * Remove all
    * Create rw, ro and hidden dirs.
    * Create rw, ro and hidden files.
    '''
    pass

def __save_response(no, outdir, rtype, url, headers=None, data=None):
    '''
    Make request and save response to file
    @param no: test number
    @param outdir
    '''
    outfile = open(os.path.join(outdir, '%s.%02d' % (rtype, no)), 'wb')
    # 1. print request
    outfile.write('%s %s HTTP/1.1\n' % (rtype, url))
    if (headers):
        for k, v in headers.iteritems():
            outfile.write('%s: %s\n' % (k, v))
    if (data):
        outfile.write(data)
    outfile.write('\n====\n\n')
    # 2. print response
    r = requests.request(rtype, url, headers=headers, data=data)
    tosave = ''
    tosave += 'HTTP/1.1 %s %s\n' % (r.status_code, r.raw.reason)
    for k, v in r.headers.iteritems():
        tosave += '%s: %s\n' % (k, v)
    outfile.write(tosave)
    if (r.content):
        if (r.status_code == 207):
            #xml = etree.fromstring(r.content)
            content = str(tidy.parseString(r.content, **{'output_xml':1, 'indent':1, 'input_xml':1}))
        else:
            content = r.content
        outfile.write(content)
    outfile.close()

def chk_options(url, outdir):
    paths = (
        # ok
        '',
        '00000005',
        '00000005/wsgi.py',
        '0000000A/',
        '0000000A/Астера-банк.doc',
        # bad
        '0000000B',
        '0000000X',             # unreal
    )
    for i, path in enumerate(paths):
        __save_response(i, outdir, 'OPTIONS', url+path)

def chk_get(url, outdir):
    paths = (
        # ok
        '00000005',
        '00000005/wsgi.py',
        '0000000A/Астера-банк.doc',
        # bad
        '00000005/qwerty',
        '0000000X',
        '0000000X/querty',
    )
    for i, path in enumerate(paths):
        __save_response(i, outdir, 'GET', url+path)

def chk_put(url, outdir):
    data = 'lkju'
    headers = {
        'Content-Type': 'text/plain',
        'Content-Length': str(len(data)),
    }
    paths = (
        # ok
        '00000001/qwerty',           # not main, ascii, new
        '00000001/qwerty',           # not main, ascii, update
        '00000002/йцукенг',          # not main, cyr, new
        '00000002/йцукенг',          # not main, cyr, update
        '00000005/wsgi.py',         # main, ascii
        '0000000A/Астера-банк.doc', # main, cyr
        # bad
        'zxcv',                     # root
        '00000001',                 # dir
        '00000003/asdf/querty',     # subdir
    )
    for i, path in enumerate(paths):
        __save_response(i, outdir, 'PUT', url+path, headers=headers, data=data)

def chk_delete(url, outdir):
    paths = (
        # ok
        '00000001/qwerty',          # not main, ascii   ok
        '00000002/йцукенг',         # not main, cyr     ok
        # bad
        '00000001',                 # dir
        '00000005/wsgi.py',         # main, ascii
        '0000000A/Астера-банк.doc', # main, cyr
        'zxcv',                     # not exists
        '00000002/asdf',            # dir
        '00000003/asdf/querty',     # subdir
    )
    for i, path in enumerate(paths):
        __save_response(i, outdir, 'DELETE', url+path)


def chk_propfind(url, outdir):
    paths = (
        # ok
        '',
        '00000001',
        '0000000A',
        '00000005/wsgi.py',         # main, ascii
        '0000000A/Астера-банк.doc', # main, cyr
        # bad
        'zxcv',                     # not exists
        '00000002/asdf',            # dir
        '00000003/asdf/querty',     # subdir
    )
    for i, path in enumerate(paths):
        for depth in (0, 1):
            __save_response(i*2+depth, outdir, 'PROPFIND', url+path, headers={'Depth': str(depth)})

def chk_mkcol(url, outdir):
    paths = (
        # ok
        # bad
        '',
        '00000001',
        '00000002/qwer',
        '00000003/йцукеннг',
        '00000004/asdf/querty',
    )
    for i, path in enumerate(paths):
        __save_response(i, outdir, 'MKCOL', url+path)

def chk_copy(url, outdir):
    '''
    Ascii/Cyr (2)
    From main/notmain / to main/notmain (4)
    In same dir / between dirs (?)
    Dir/file
    '''
    paths = (
        # ok
        # - not destruct
        ('00000005/wsgi.py', '00000005/qwerty'),                # main > notmain
        ('00000005/qwerty', '00000005/asdfg'),                  # notmain > notmain
        ('0000000A/Астера-банк.doc', '0000000A/Сбер-банк.doc'), # main cyr > notmain cyr
        # - destruct (notmain > main)
        ('00000005/qwerty', '00000005/wsgi.py'),                # main > notmain
        # bad
        ('00000005/wsgi.py', 'wsgi.py'),                        # to root
        ('00000005/qwerty', '00000005/qwerty'),                 # src==dst
        ('00000005/wsgi.py', '00000006/wsgi.py'),               # between dirs
        ('00000005/wsgi.py', '00000005/aaa/wsgitest.py'),               # to subdir
    )
    for i, path in enumerate(paths):
        for j, over in enumerate(('F', 'T')):
            __save_response(i*2+j, outdir, 'COPY', url+path[0], headers={'Destination': url+path[1], 'Overwrite': over})

def chk_move(url, outdir):
    '''
    Ascii/Cyr (2)
    From main/notmain / to main/notmain (4)
    In same dir / between dirs (?)
    Dir/file
    '''
    paths = (
        # ok
        # - not destruct
        ('00000005/qwerty', '00000005/asdfg'),                  # notmain > notmain (ascii)
        ('0000000A/Сбер-банк.doc', '0000000A/Мастер-банк.doc'), # notmain > notmain (cyr)
        # - destruct (notmain > main)
        ('00000005/asdfg', '00000005/wsgi.py'),                  # notmain > main (ascii)
        ('0000000A/Мастер-банк.doc', '0000000A/Астера-банк.doc'), # notmain > main (cyr)
        # bad
        ('00000005/wsgi.py', '00000005/tratata'),               # main > notmain (ascii)
        ('0000000A/Астера-банк.doc', '0000000A/Сбер-банк.doc'), # main > notmain (cyr)
        ('00000005/asdfg', 'asdfg'),                              # to root
        ('00000005/asdfg', '00000005/asdfg'),                   # src==dst
        ('00000005/asdfg', '00000006/asdfg'),                   # between dirs
        ('00000005/asdfg', '00000005/aaa/asdfg'),               # to subdir
    )
    for i, path in enumerate(paths):
        for j, over in enumerate(('F', 'T')):
            __save_response(i*2+j, outdir, 'MOVE', url+path[0], headers={'Destination': url+path[1], 'Overwrite': over})

def main(url, outdir, realpath=None):
    if (realpath):
        prepare(realpath)
    # HTTP
    #chk_options(url, outdir)    # ok
    #chk_get(url, outdir)        # ok
    #chk_put(url, outdir)        # ok
    #chk_delete(url, outdir)     # ok
    # WebDAV
    #chk_propfind(url, outdir)   # ok
    #chk_mkcol(url, outdir)      # ok
    #chk_copy(url, outdir)       # ok
    #chk_move(url, outdir)
    # check MSO hack
    dir = '00000001'
    src = dir+'/eggwm-0.2.tar.gz'
    dst = dir+'/qwerty'
    __save_response(0, outdir, 'PROPFIND', url+dir, headers={'Depth': '1'})
    #__save_response(1, outdir, 'COPY', url+src, headers={'Destination': url+dst, 'Overwrite': 'T'})
    #__save_response(2, outdir, 'PROPFIND', url+dir, headers={'Depth': '1'})
    __save_response(3, outdir, 'DELETE', url+src)
    __save_response(4, outdir, 'PROPFIND', url+dir, headers={'Depth': '1'})
    #__save_response(5, outdir, 'MOVE', url+dst, headers={'Destination': url+src, 'Overwrite': 'T'})
    #__save_response(6, outdir, 'PROPFIND', url+dir, headers={'Depth': '1'})

if (__name__ == '__main__'):
    argc = len(sys.argv)
    if ((argc < 3) or (argc > 4)):
        print 'Usage: %s <url> <outdir> [<realpath>]' % sys.argv[0]
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3] if (argc > 3) else None)
