    def set_lock(self, timeout = None):
        ''''''
        if (self._itsme):
            return self._locker.set(self._file.pk, timeout)

    def get_lock(self):
        ''''''
        if (self._itsme):
            return self._locker.get(self._file.pk)

    def re_lock(self, token, timeout = None):
        ''''''
        if (self._itsme):
            return self._locker.reset(self._file.pk, token, timeout)

    def un_lock(self, token):
        ''''''
        if (self._itsme):
            return self._locker.delete(self._file.pk, token)
