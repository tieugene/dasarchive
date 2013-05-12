# -*- coding: utf-8 -*-
'''
DA - handle DasArchive files via WebDAV.
FIXME: DELETED reset on each request
'''
import os, sys, re, datetime, pprint, logging
from django.conf import settings
import wdp.ds, wdp.dsfs, wdp.util
import models, deleter

reload(sys)
sys.setdefaultencoding('utf-8')

_OPT_MEMBER = wdp.const.OPT_GET|wdp.const.OPT_PUT|wdp.const.OPT_DELETE|wdp.const.OPT_PROPFIND|wdp.const.OPT_COPY|wdp.const.OPT_MOVE
_OPT_COLLECTION = wdp.const.OPT_PROPFIND
_OPT_STORAGE = _OPT_MEMBER|_OPT_COLLECTION

ISHEX = re.compile('[0-9A-F]{8}')

DELETER = deleter.Deleter(settings.DELETER_ROOT, 3)

def _uri2path(uritail):
    '''
    Converts requested URL into real path
    @param uritail: last part of uri (endslashless)
    @type uritail: str
    @rtype: tuple(bool, [File], str)
    @return: (ok, File()|None, filename|None)
    '''
    err = (False, None, None)               # Not found
    if uritail == '':                       # Root
        return (True, None, None)
    path = uritail.split('/', 1)
    if (ISHEX.match(path[0])):              # filedir or file
        id = int(path[0], 16)
        try:
            file = models.File.objects.get(pk=id)
        except:
            return err
        if (len(path) == 1):                # filedir
            return (True, file, None)
        return (True, file, path[1])        # file
    return err

class   DAResource(wdp.dsfs.FSResource):
    ''''''

    def __init__(self, file, itsme, path):
        '''
        @param file: File object
        @type file: File
        @param itsme: handled folder/file
        @type itsme: bool
        '''
        super(DAResource, self).__init__(path)
        self._file = file
        self._itsme = itsme

    def get_ctime(self):
        ''''''
        return super(DAResource, self).get_ctime() if (not self._itsme) else self._file.ctime

    def get_mtime(self):
        ''''''
        return super(DAResource, self).get_mtime() if (not self._itsme) else self._file.mtime

    def _get_deleted(self):
        '''
        5 times
        @param id: pk that tested on deletion
        @type id: int
        @return: id is deleted
        @rtype: bool
        '''
        return DELETER.get(self._file.pk)

class   DAMember(DAResource, wdp.dsfs.FSMember):

    #def __init__(self, file, itsme, path):
    #    DAResource.__init__(self, file, itsme, path)

    def	_update_db(self):
        if (self._itsme):
            self._file.fill_with(self._path)
            self._file.save()

    def	get_options(self):
        return _OPT_MEMBER

    def get_size(self):
        ''''''
        return wdp.dsfs.FSMember.get_size(self) if (not self._itsme) else self._file.size

    def get_mime(self):
        ''''''
        return wdp.dsfs.FSMember.get_mime(self) if (not self._itsme) else self._file.mime

    def read(self, start=0L, size=0L):
        ''''''
        #wdp.util.LOG('DAMember.read: into')
        retvalue = wdp.dsfs.FSMember.read(self, start, size)
        #wdp.util.LOG('DAMember.read: out %d bytes', len(retvalue))
        return retvalue

    def write(self, data):
        ''''''
        #wdp.util.LOG('DAMember.write')
        retvalue = wdp.dsfs.FSMember.write(self, data)
        if (retvalue):
           self._update_db()
        return retvalue

    def delete(self):
        '''
        You can delete any file but main.
        '''
        if (not self._itsme):
            return wdp.dsfs.FSMember.delete(self)
        else:     # MSO hack
            self.__set_deleted()
            return True

    def	_cp_to(self, dstpath):
        '''
        1. cp.
        2. If dst._itsme - update DB.
        '''
        #print 'DAMember._cp_to detected: (%s) %s => %s' % (self._file.pk, self._path, dstpath)
        retvalue = wdp.dsfs.FSMember._cp_to(self, dstpath)
        if (retvalue and self._get_deleted() and self._file.itsme(os.path.basename(dstpath))):  # MSO hack
            self.__del_deleted()
        return retvalue

    def	_mv_to(self, dstpath):
        '''
        1. if self._itsme - break
        2. if dst._itsme - update DB
        '''
        if (not self._itsme):
            retvalue = wdp.dsfs.FSMember._mv_to(self, dstpath)
            if (retvalue and self._get_deleted() and self._file.itsme(os.path.basename(dstpath))):  # MSO hack
                self.__del_deleted()
        else:   # MSO hack
            retvalue = wdp.dsfs.FSMember._cp_to(self, dstpath)
            if (retvalue):
                self.__set_deleted()
        return retvalue

    def __set_deleted(self):
        '''
        2 times (member.delete, member._mv_to) - self
        @param id: pk to add to deleted
        @type id: int
        '''
        DELETER.set(self._file.pk)

    def __del_deleted(self):
        '''
        2 times (member._cp_to, member._mv_to) - self
        @param id: pk to remove from deletion
        @type id: int
        '''
        DELETER.delete(self._file.pk)

class   DACollection(DAResource, wdp.dsfs.FSCollection): # Can't iherit both ds and dsfs
    ''''''

    #def __init__(self, file, itsme, path, deleter):
    #    DAResource.__init__(self, file, itsme, path, deleter)

    def	get_options(self):
        return _OPT_COLLECTION

    def	get_children(self):
        ''''''
        #wdp.util.LOG('dsfs.list: %s', self._path)
        if (not self._get_deleted()):
            return wdp.dsfs.FSCollection.get_children(self)
        else:   # MSO hack
            retvalue = list()
            for i in os.listdir(self._path.encode('utf-8')):
                if (not self._file.itsme(i)):
                    retvalue.append(i)
            return retvalue

    def get_child(self, uritail):
        ''''''
        __path = os.path.join(self._path, uritail)
        if (os.path.exists(__path.encode('utf-8'))):
            __itsme = self._file.itsme(uritail)
            if not ((self._get_deleted()) and __itsme):    # MSO hack
                return DAMember(self._file, __itsme, __path)

    def	mk_mem(self, uritail, data):
        '''
        FIXME: must return DAMember (now not used in dp)
        '''
        return wdp.dsfs.FSCollection.mk_mem(self, uritail, data)

    def	mk_col(self, uritail):
        ''''''

    def delete(self):
        ''''''

    def _cp_to(self, dstpath):
        ''''''

    def _mv_to(self, dstpath):
        ''''''

class   DAStorage(wdp.ds.Collection):
    ''''''

    def	get_options(self):
        return _OPT_STORAGE

    def __init__(self, path):
        super(DAStorage, self).__init__(path)
        # cache *time
        __stat = os.stat(self._path)
        self.__ctime = datetime.datetime.fromtimestamp(__stat.st_ctime)
        self.__mtime = datetime.datetime.fromtimestamp(__stat.st_mtime)

    def get_ctime(self):
        return self.__ctime

    def get_mtime(self):
        return self.__mtime

    def get_children(self):
        '''
        List PKs from db
        '''
        retvalue = list()
        for f in models.File.objects.all():
            retvalue.append(f.get_fn())
        return retvalue

    def get_child(self, uritail):
        ''''''
        #wdp.util.LOG('DAStorage.get_child: %s', uritail)
        if (not uritail):
            return self
        ok, file, filename = _uri2path(uritail)
        if (ok):
            __dir = os.path.join(self._path, file.get_dir())
            if (not filename):
                return DACollection(file, True, __dir)
            else:
                __path = os.path.join(__dir, filename)
                if (os.path.exists(__path.encode('utf-8'))):
                    __itsme = file.itsme(filename)
                    retvalue = DAMember(file, __itsme, __path)
                    if (__itsme and retvalue._get_deleted()):
                        retvalue = None
                    return retvalue
        # default - None

    def __copy_or_move(self, src, dstpath, func):
        '''
        Inside same collection only
        You can cp/mv if:
        * dstpath is X/Y; X is hex; X is in DB
        * X == src.parent
        * Y has no /
        '''
        ok, file, filename = _uri2path(dstpath)
        #print 'CopyMove detected:\n\tsrc._file.pk=%s\n\tsrc._path=%s\n\tself._path=%s\n\tok=%s\n\tfile.pk=%s\n\tfilename=%s' %\
        #(src._file.pk, src._path, self._path, ok, file.pk, filename)
        #print 'Dst path = %s' % os.path.join(self._path, src._file.get_dir(), filename)
        if  (ok) and \
            (src._file.pk == file.pk) and \
            ('/' not in filename) and \
            (func(os.path.join(self._path, src._file.get_dir(), filename))):
            self.get_child(dstpath)._update_db()
            return True

    def	copy(self, src, dstpath):
        ''''''
        #print 'Copy detected: %s => %s' % (src._path, dstpath)
        return self.__copy_or_move(src, dstpath, src._cp_to)

    def	move(self, src, dstpath):
        ''''''
        return self.__copy_or_move(src, dstpath, src._mv_to)
