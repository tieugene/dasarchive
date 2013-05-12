#!/bin/env python
# -*- coding: utf-8 -*-
'''
Tool to maintain DasArchive:
- check integrity (_chk) - current/yesterday/rollback
- backuping
TODO:
* Options (http://www.doughellmann.com/PyMOTW/optparse/index.html)
    - current check: full
    - yd check: full
    - backup: force
    - verbose (all)
    - timestamps
* exit codes
'''

# 1. system
import os, sys, re, datetime, shutil, hashlib, optparse, pprint
import settings

reload(sys)
sys.setdefaultencoding('utf-8')

DAY0 = datetime.datetime.fromtimestamp(0)

parser = None

# 0. helpers
def __init_parser():
    '''
    Init CLI options.
    '''
    parser = optparse.OptionParser(usage='usage: %prog [options]', version='%prog 1.0')
    parser.add_option('-c', '--full-current', action='store_true', dest='c', default=False, help='Full (md5) check of current')
    parser.add_option('-y', '--full-yesterday', action='store_true', dest='y', default=False, help='Full (md5) check of yesterday')
    parser.add_option('-b', '--force-backup', action='store_true', dest='b', default=False, help='Force write backups')
    parser.add_option('-v', '--verbose', action='store_true', dest='v', default=False, help='Verbose')
    parser.add_option('-t', '--timestamps', action='store_true', dest='t', default=False, help='Show timestamps')
    return parser

def __id2dir(id):
    iddir = '%08X' % id
    return '%s/%s/%s/%s' % (iddir[:2], iddir[2:4], iddir[4:6], iddir[6:])

def __dir2id(s):
    return long(s.replace('/', ''), 16)

def __fromunixtime(l):
    return datetime.datetime.fromtimestamp(long(l))

def __tounixtime(d):
    return long((d - DAY0).total_seconds())

def __mkpath(root, id, fname=''):
    return os.path.join(root, __id2dir(id), fname)

def __file_md5(file, block_size=1024*14):
    if isinstance(file, basestring):
        file = open(file.encode('utf-8'), 'rb')
    h = hashlib.md5()
    block = file.read(block_size)
    while block:
        h.update(block)
        block = file.read(block_size)
    return h.hexdigest()

def __open_db():
    dbengine = settings.DATABASES['default']['ENGINE']
    if (dbengine == 'django.db.backends.sqlite3'):
        import sqlite3
        return sqlite3.connect(settings.DATABASES['default']['NAME'])
    elif (dbengine == 'django.db.backends.mysql'):
        import MySQLdb
        retvalue = MySQLdb.connect(
            user =   settings.DATABASES['default']['USER'],
            passwd = settings.DATABASES['default']['PASSWORD'],
            db =     settings.DATABASES['default']['NAME'],
            use_unicode=True,
        )
        retvalue.set_character_set('utf8')
        return retvalue
    else:
        return None

# 1. Get data
def __get_fs(top):
    '''
    @return: {id: set(fnames)}
    @rtype: dict
    '''
    entries = dict()
    toplen = len(top)
    ISDIR = re.compile(top+'/[0-9A-F]{2}/[0-9A-F]{2}/[0-9A-F]{2}/[0-9A-F]{2}')
    for root, dirs, files in os.walk(top):
        #print root, len(dirs), len(files),
        if (ISDIR.match(root)):
            # hack
            tmp = list()
            for i in files:
                tmp.append(unicode(i, 'utf-8'))
            # /hack
            entries[__dir2id(root[toplen+1:])] = set(tmp)
    return entries

def __get_outbox_db():
    '''
    Get files in outbox (DB).
    ID: {fname, size, md5, mtime}
    '''
    entries = dict()
    db = __open_db()
    if (not db):
        print 'Unknown database engine'
        return None, None
    cur = db.cursor()
    cur.execute('SELECT id, fname, size, md5 FROM dasarchive_file ORDER BY id')
    for row in cur.fetchall() :
        entries[row[0]] = {
            'fname': row[1],
            'size': row[2],
            'md5': row[3],
            #'mtime': datetime.datetime.strptime(row[4][:19], '%Y-%m-%d %H:%M:%S'),
        }
    db.close()
    return entries

def __get_yesterday_db():
    '''
    Get files in yesterday (index.txt)
    '''
    entries = dict()
    for i in open(os.path.join(settings.YESTERDAY_ROOT, 'index.txt'), 'rt'):
        i = i.rstrip('\n').split('\t')
        id = __dir2id(i[2][:11])
        entries[id] = {
            'fname': unicode(i[2][12:]),
            'size': long(i[1]),
            'md5': i[0],
            #'mtime': __fromunixtime(i[1]),
        }
    return entries

def _set_outbox_db(db, retlist):
    '''
    Updates SQL DB
    '''
    cmd_add  = 'INSERT INTO dasarchive_file (id, fname, size, md5) VALUES (%s, %s, %s, %s)'
    cmd_edit = 'UPDATE dasarchive_file SET fname=%s, size=%s, md5=%s) WHERE id=%s'
    cmd_del  = 'DELETE FROM dasarchive_file WHERE id=%s'
    db = __open_db()
    if (not db):
        print 'Unknown database engine'
        return None, None
    db.autocommit(False)
    cur = db.cursor()
    try:
        for id, act in retlist:
            if (act == DB_ADD):
                data = db[id]
                cur.execute(cmd_add, (id, data['fname'], data['size'], data['md5'],))
            elif (act == DB_EDIT):
                data = db[id]
                cur.execute(cmd_edit, (data['fname'], data['size'], data['md5'], id,))
            else:
                cur.execute(cmd_del, (id,))
        db.commit()
        print 'DB updated ok.'
    except:
        db.rollback()
        print 'DB rolled back'
    cur.close()
    db.close()

def _set_yesterday_db(yesterday):
    '''
    Updates yesterday DB
    '''
    new_index = open(os.path.join(settings.YESTERDAY_ROOT, 'index.txt'), 'wb')
    for id, data in yesterday.iteritems():
        #new_index.write('%s\t%d\t%d\t%s/%s\n' % (data['md5'], __tounixtime(data['mtime']), data['size'], __id2dir(id), data['fname']))
        new_index.write('%s\t%d\t%s/%s\n' % (data['md5'], data['size'], __id2dir(id), data['fname']))

# 2. Check
# Error masks/flags
# 4   - extra files
# 1/5 - lost file/+extra files]
# 2/6 - wrong size/...
# 3/7 - wrong md5/...
# 9   - lost dir
# 12  - extra dir
STATE_OK    = 0
STATE_LOST  = 1
STATE_WSIZE = 2
STATE_WMD5  = 3
MASK_STATE  = 3
MASK_XTRA   = 4
MASK_DIR    = 8 # DIR|XTRA == Extra Dir; DIR|LOST == Lost Dir
def _chk(db, root, full=False, verbose=False):
    '''
    Check DB vs FS.
    @param db: data DB {id: {'fname': str, 'size': long, 'md5': str}}
    @type db: dict
    @param root: folder
    @type root: str
    @return: [(id, errcode),]
    @rtype: list((long, int),)
    '''
    def _log(verbose, id, text):
        if (verbose):
            print '%08X: %s.' % (id, text)
    retvalue = list()
    paths = __get_fs(root)
    for id, src in db.iteritems():
        dst = paths.get(id, None)
        # 1. lost dir
        if (dst == None):
            retvalue.append((id, MASK_DIR | STATE_LOST))
            if (verbose):
                _log(verbose, id, 'folder is absent')
            continue
        # folder exists - check files
        del paths[id]
        fname = src['fname']
        # 2. lost file
        if (not fname in dst):
            extra = MASK_XTRA if len(dst) else 0
            retvalue.append((id, STATE_LOST | extra))
            _log(verbose, id, '"%s" not found%s' % (fname, ' (extra files detected)' if extra else ''))
            continue
        # extra files
        dst.remove(fname)   # remove main file from extra
        extra = MASK_XTRA if len(dst) else 0
        extra_str = ' (extra files detected)' if extra else ''
        # check
        path =  __mkpath(root, id, fname)
        # 4. fast check
        size = os.path.getsize(path.encode('utf-8'))
        if (size != src['size']):
            retvalue.append((id, STATE_WSIZE | extra))
            _log(verbose, id, '"%s" has wrong size (DB=%d, FS=%d)%s' % (fname, src['size'], size, extra_str))
            continue
        # 5. md5 check
        if (full):
            md5 = __file_md5(path)
            if (md5 != src['md5']):
                retvalue.append((id, STATE_WMD5 | extra, md5, dst))
                _log(verbose, id, '"%s" has wrong md5 (DB=%s, FS=%s)%s' % (fname, src['md5'], md5, extra_str))
                continue
        # 6. extra files
        if (extra):
            retvalue.append((id, STATE_OK | extra))
            _log(verbose, id, 'has extra files')
    # X. extra dirs
    for id in paths.keys():
        retvalue.append((id, MASK_DIR | MASK_XTRA))
        _log(verbose, id, 'extra folder')
    return retvalue

# 3. Update
# action flags/masks
ACTION_SKIP     =  0
ACTION_ERROR    =  1
ACTION_DB       =  2
ACTION_FS       =  3
MASK_ACTION     =  3
MASK_VERBOSITY  =  4
MASK_XTRAUSE    =  8
MASK_XTRADEL    = 16
OBJ_EFILE       =  0
OBJ_LFILE       =  1
OBJ_WCHK        =  2
OBJ_EDIR        =  3
OBJ_LDIR        =  4
STATE2OBJ = {
    STATE_OK    | MASK_XTRA :   OBJ_EFILE,
    STATE_LOST              :   OBJ_LFILE,
    STATE_LOST  | MASK_XTRA :   OBJ_LFILE,
    STATE_WSIZE             :   OBJ_WCHK,
    STATE_WSIZE | MASK_XTRA :   OBJ_WCHK,
    STATE_WMD5              :   OBJ_WCHK,
    STATE_WMD5  | MASK_XTRA :   OBJ_WCHK,
    MASK_DIR    | MASK_XTRA :   OBJ_EDIR,
    MASK_DIR    | STATE_LOST:   OBJ_LDIR,
}
DB_ADD          = 0
DB_EDIT         = 1
DB_DEL          = 2
def _upd(db, root, errors, efileflags, lfileflags, chkflags, edirflags, ldirflags):
    '''
    Sync DB and FS due errors.
    - Action (0..3): skip/error/db_update[/fs_update]
    - Verbosity: bool
    - Use_Extra_Files: bool
    - Del_Extra_Files: bool
    TODO:
        * Add extra dir to DB
        * Del lost dir from DB
        * Del lost file from DB
        * Update wrong file in DB
    @return: records to change
    @type: list((id, action),)  # action=Add/Edit/Del;
    '''
    def _log(vrb, id, text):
        '''
        Log action
        '''
        if (vrb):
            print '%08X: %s.' % (id, text)
    # dict to convert state into action
    # 0. setup what to do (object x args) == parse flags
    actions = [efileflags, lfileflags, chkflags, edirflags, ldirflags]  # [object==chk_err_code] x [arg==what_to_do]
    # 1. lets go
    retcode = 0
    retlist = list()
    paths = __get_fs(root)
    for id, state in errors:    # id=long, err=int (1..12), new_value=long/str, xtra_set = set()
        obj = STATE2OBJ[state]  # FIXME: check on exists
        act = actions[obj] | MASK_ACTION
        vrb = actions[obj] | MASK_VERBOSITY
        # 0. skip
        if (act == ACTION_SKIP):
            _log(vrb, id, 'skip')
            continue
        # 1. error
        if (act == ACTION_ERROR):
            _log(vrb, id, 'error')
            retcode += 1
            continue
        # 2,3 - DB/FS
        err  = state & MASK_STATE
        xtra = bool(state & MASK_XTRA)  # extra file/dir
        if (state & MASK_DIR):          # Dir operation
            if (xtra):                  # Extra dir
                __dir = __mkpath(root, id)
                if (act == ACTION_DB):
                    __xtra_set = os.listdir(__dir)
                    if (len(__xtra_set) == 0):
                        _log(vrb, id, 'Cannot add empty extra dir to DB')
                        pass            # TODO: err?
                    if (len(__xtra_set) > 1):
                        _log(vrb, id, 'Cannot add multifile extra dir to DB')
                        pass            # TODO: err?
                    else:
                        _log(vrb, id, 'Add extra dir to DB')
                        __file = __mkpath(root, id, __xtra_set[0])
                        db[id] = {
                            'fname':    __xtra_set[0],
                            'size':     os.path.getsize(__file),
                            'md5':      __file_md5(__file),
                        }
                        retlist.append((id, DB_ADD))
                else:
                    _log(vrb, id, 'Del extra dir from FS')
                    shutil.rmtree(__dir)
            else:                       # Lost dir
                if (act == ACTION_DB):
                    _log(vrb, id, 'Del lost dir from DB')
                    del db[id]
                    retlist.append((id, DB_DEL))
        else:                           # File operation
            if (err):                   # File error: lost/size/md5
                src = db[id]
                xtrause = bool(action[obj] | MASK_XTRAUSE)
                xtradel = bool(action[obj] | MASK_XTRADEL)
                if (xtrause or xtradel):
                    __dir = __mkpath(root, id)
                    __xtra_set = set(os.listdir(__dir))
                __recovered = False
                if (xtrause):
                    if (err != STATE_LOST): # size/md5
                        __xtra_set.remove(src['fname'])
                        errname = 'wrong'
                    else:
                        errname = 'lost'
                    for i in __xtra_set:
                        __file = os.path.join(__dir, i)
                        __size = os.path.getsize(__file)
                        __md5 = __file_md5(__file)
                        if ((src['md5'] == __md5) and (src['size'] == __size)):
                            _log(vrb, id, 'Recover %s file from extra "%s"' % (i, errname))
                            os.rename(__file, __mkpath(root, id, src['fname']))
                            __xtra_set.remove(i)
                            __recovered = True
                            break
                    if (not __recovered):
                        _log(vrb, id, 'Nothing found to recover %s file' % errname)
                if (not __recovered):
                    if (act == ACTION_DB):
                        if (err == STATE_LOST): # lost
                                _log(vrb, id, 'Del lost file from DB')  # TODO: what to do with not-empty lost-file dir?
                                del db[id]
                                retlist.append((id, DB_DEL))
                        else:
                            _log(vrb, id, 'Update wrong file in DB')
                            __file = __mkpath(root, id, src['fname'])
                            db[id]['size']  = os.path.getsize(__file)
                            db[id]['md5']   = __file_md5(__file)
                            retlist.append((id, DB_EDIT))
                    else:
                        _log(vrb, id, 'Skip changes in DB')
            # else:                     # skip simply extra files
            if (xtra and xtradel and __xtra_set):
                _log(vrb, id, 'Del extra files')
                for i in __xtra_set:
                    os.remove(os.path.join(__dir, i))
    return retlist

# 4. Backup
# works with DBs only => need fast check B4

def _backup(current, yesterday, force = False, verbose = False):
    '''
    Backup: current to yesterday and create rollbacks.
    @param current: current db
    @type current: dict
    @param yesterday: yesterday db
    @type yesterday: dict
    @param force: make FS changes
    @type force: bool
    @param verbose: be verbose
    @type verbose: bool
    '''
    def _log(v, s):
        if (v):
            print s
    rollback = settings.ROLLBACK_ROOT
    for id, src in current.iteritems():
        iddir = __id2dir(id)
        srcpath = __mkpath(settings.OUTBOX_ROOT, id, src['fname'])
        dstpath = __mkpath(settings.YESTERDAY_ROOT, id, src['fname'])
        dst = yesterday.get(id, None)
        if (not dst):
            # 1. new
            _log(verbose, 'Created: %d ("%s")' % (id, src['fname']))
            if (force):
                dstdir = os.path.join(settings.YESTERDAY_ROOT, iddir)
                if (not os.path.exists(dstdir)):
                    os.makedirs(dstdir)
                shutil.copy2(srcpath.encode('utf-8'), dstpath.encode('utf-8'))
            yesterday[id] = src
        else:
            # 2. fname changed
            if (src['fname'] != dst['fname']):
                _log(verbose, 'Renamed: %d ("%s" => "%s")' % (id, dst['fname'], src['fname']))
                if (force):
                    shutil.move(__mkpath(settings.YESTERDAY_ROOT, id, dst['fname']).encode('utf-8'), dstpath.encode('utf-8'))
                dst = yesterday[id] # refresh dst
            # 3. compare crc
            if (src['md5'] != dst['md5']):
                _log(verbose, 'Changed: %d ("%s")' % (id, src['fname']))
                _log(verbose, 'MD5: src=%s, dst=%s)' % (src['md5'], dst['md5']))
                #print __file_md5(dstpath)
                # 3.1. mv to rollbacks
                rbname = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                _log(verbose, 'Rollback: %d ("%s" => %s)' % (id, src['fname'], rbname))
                if (force):
                    rbdir = os.path.join(settings.ROLLBACK_ROOT, iddir)
                    if (not os.path.exists(rbdir)):
                        os.makedirs(rbdir)
                    shutil.move(dstpath.encode('utf-8'), os.path.join(rbdir, rbname))
                # 3.2. cp from current
                _log(verbose, 'Renew: %d ("%s")' % (id, src['fname']))
                if (force):
                    shutil.copy2(srcpath.encode('utf-8'), dstpath.encode('utf-8'))
                yesterday[id] = src
    if (force):
        _set_yesterday_db(yesterday)
    return yesterday

# X. parse options
# Y. setup check/update/backup order/args
# Z. Main
def main():
    parser = __init_parser()
    (opts, args) = parser.parse_args()
    time = datetime.datetime.now()
    def _log(s):
        if (opts.v):
            if (opts.t):
                print '%d: %s' % ((datetime.datetime.now() - time).total_seconds(), s)
            else:
                print s
    _log('1. Load data')
    DB_ENTRIES = __get_outbox_db()
    YESTERDAY_ENTRIES = __get_yesterday_db()
    _log('2. Check Current')
    errors_current = _chk(DB_ENTRIES, settings.OUTBOX_ROOT, full=opts.c, verbose=opts.v)
    _log('3. Check Yesterday')
    errors_yesterday = _chk(YESTERDAY_ENTRIES, settings.YESTERDAY_ROOT, full=opts.y, verbose=opts.v)
    if (errors_current or errors_yesterday):
        if errors_current:
            _log('Current need update')
        else:
            _log('Yesterday need update')
    else:
        _log('4. Backup')
        _backup(DB_ENTRIES, YESTERDAY_ENTRIES, force=opts.b, verbose=opts.v)
    _log('The End')

if (__name__ == '__main__'):
    '''
    Modes:
    - check[+update] outbox[full, force]
    - check[+update] yesterday[full, force]
    - clean rollback
    - backup[force]
    '''
    main()
