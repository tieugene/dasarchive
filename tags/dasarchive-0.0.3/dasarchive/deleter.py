# -*- coding: utf-8 -*-

import sys, datetime
import pytc
import wdp.util

reload(sys)
sys.setdefaultencoding('utf-8')

mask = '%Y%m%d%H%M%S'

class	Deleter():
    '''
    Handle deleted files
    '''

    def	__init__(self, dbname, timeout = 5):
        '''
        '''
        #wdp.util.LOG('Deleter INIT starts')
        self.__timeout = timeout
        self.__db = pytc.HDB(dbname, pytc.HDBOREADER | pytc.HDBOWRITER | pytc.HDBOCREAT | pytc.HDBONOLCK)    # HDBONOLCK/HDBOLCKNB
        #wdp.util.LOG('Deleter INIT ends')

    #def	__del__(self):
    #    wdp.util.LOG('Deleter DEL starts')

    def get(self, id):
        '''
        Test wheter id exists in DB
        @param id: id
        @type id: int
        '''
        #wdp.util.LOG('Deleter.get starts')
        retvalue = False
        id = str(id)
        if (str(id) in self.__db):
            if (self.__db[id] < datetime.datetime.now().strftime(mask)):
                del self.__db[id]
            else:
                retvalue = True
        #wdp.util.LOG('Deleter.get ends')
        return retvalue

    def set(self, id):
        '''
        Add new value into DB
        '''
        self.__db[str(id)] = (datetime.datetime.now() + datetime.timedelta(0, self.__timeout)).strftime(mask)

    def delete(self, id):
        id = str(id)
        if (id in self.__db):
            del self.__db[id]
