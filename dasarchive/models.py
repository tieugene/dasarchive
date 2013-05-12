# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
# 2. system
import os, sys, hashlib, datetime, pprint
# 3. 3rd parties
import magic
# 4. my
from utils import file_md5, get_mime

reload(sys)
sys.setdefaultencoding('utf-8')

class   TagGroup(models.Model):
    name    = models.CharField(max_length=32, unique=True, verbose_name=u'Наименование')
    comment = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'Комментарии')
    bgcolor = models.IntegerField(null=True, blank=True, verbose_name=u'Цвет фона')
    fgcolor = models.IntegerField(null=True, blank=True, verbose_name=u'Цвет текста')

    def     __unicode__(self):
        return self.name

    class   Meta:
        ordering                = ('name', )
        verbose_name            = u'Категория'
        verbose_name_plural     = u'Категории'

class   TagItem(models.Model):
    group   = models.ForeignKey(TagGroup, related_name=u'items', verbose_name=u'Категория')
    name    = models.CharField(max_length=32, unique=True, db_index=True, verbose_name=u'Наименование')
    comment = models.CharField(max_length=255, blank=True, null=True, verbose_name=u'Комментарии')

    def __unicode__(self):
        return self.name

    def get_full_name(self):
        return u'%s:%s' % (self.group.name, self.name)

    def get_bgcolor_html(self):
        '''
        @return str - background color (or white)
        '''
        return u'#%06X' % self.group.bgcolor if self.group.bgcolor else 'white'

    def get_fgcolor_html(self):
        '''
        @return str - foreground color (or black)
        '''
        return u'#%06X' % self.group.fgcolor if self.group.fgcolor else 'black'

    class   Meta:
        #unique_together        = (('group', 'name'),)
        ordering                = ('group', 'name', )
        verbose_name            = u'Тэг'
        verbose_name_plural     = u'Тэги'

class   File(models.Model):
    name    = models.CharField(max_length=255, db_index=True, blank=False, verbose_name=u'Наименование')
    fname   = models.CharField(max_length=255, db_index=True, blank=False, verbose_name=u'Имя файла')
    #comment = models.TextField(blank=True, verbose_name=u'Комментарии')
    comment = models.CharField(max_length=255, db_index=True, blank=True, verbose_name=u'Комментарии')
    mime    = models.CharField(max_length=64, editable=True, db_index=True, verbose_name=u'Тип')
    size    = models.PositiveIntegerField(editable=False, verbose_name=u'Размер')
    md5     = models.CharField(max_length=32, editable=False, verbose_name=u'MD5')
    ctime   = models.DateTimeField(editable=False, verbose_name=u'Создан')
    mtime   = models.DateTimeField(editable=False, verbose_name=u'Изменен')
    updated = models.DateTimeField(auto_now=True, editable=False, verbose_name=u'Изменена информация')
    deleted = models.BooleanField(default=False, editable=False, verbose_name=u'Удален')
    tags    = models.ManyToManyField(TagItem, blank=True, null=True, related_name='files', verbose_name=u'Теги')

    def     __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('dasarchive.views.file_detail', [str(self.pk)])

    def get_fn(self):
        '''
        @return id as 8xHex
        '''
        return '%08X' % self.pk

    def get_dir(self):
        '''
        @return id as XX/XX/XX/XX
        '''
        s = self.get_fn()
        return '/'.join((s[:2], s[2:4], s[4:6], s[6:]))

    def get_full_dir(self):
        return os.path.join(settings.OUTBOX_ROOT, self.get_dir())

    def get_full_path(self):
        return os.path.join(self.get_full_dir(), self.fname)

    def itsme(self, s):
        return (s == self.fname)

    def rename(self, old_fname, new_fname):
        '''
        FIXME: check new_fname for excluding ../, / etc
        '''
        if (old_fname != new_fname):
            dir = self.get_full_dir()
            os.rename(os.path.join(dir, old_fname.encode('utf-8')), os.path.join(dir, new_fname.encode('utf-8')))

    def delete(self):
        dir = self.get_full_dir()
        # 1. rm all files and dir own
        for file in os.listdir(dir):
            os.remove(os.path.join(dir, file))
        # 2. recurring rm dirs
        s = self.get_fn()
        dirs = (s[:2], s[2:4], s[4:6], s[6:])
        for i in xrange(4):
            dir = os.path.join(settings.OUTBOX_ROOT, '/'.join(dirs[:4-i]))
            if (not os.listdir(dir)):
                os.rmdir(dir)
            else:
                break
        # 3. del DB record
        super(File, self).delete()

    def save(self, *args, **kwargs):
        if (self.pk):
            self.rename(File.objects.get(pk=self.pk).fname, self.fname)
        super(File, self).save(*args, **kwargs)

    def fill_with(self, path):
        '''
        Fill fields with path data.
        TODO: fill_with(self)
        '''
        path = path.encode('utf-8')
        stat = os.stat(path)
        self.size = stat.st_size
        self.ctime = datetime.datetime.fromtimestamp(stat.st_ctime)
        self.mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
        self.md5 = file_md5(path)
        self.mime = get_mime(path)

    '''
    def get_full_name(self):
        return u'%s.%s' % (self.name, self.ext)
    '''
    class   Meta:
        ordering                = ('name',)
        verbose_name            = u'Файл'
        verbose_name_plural     = u'Файлы'
