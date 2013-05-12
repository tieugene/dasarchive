# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
# 2. system
import os, sys, hashlib, datetime, pprint
# 3. 3rd parties
import magic

reload(sys)
sys.setdefaultencoding('utf-8')

mime = magic.open(magic.MIME_TYPE)
mime.load()

class	TagGroup(models.Model):
	name	= models.CharField(max_length=32, unique=True, verbose_name=u'Наименование')
	bgcolor	= models.IntegerField(null=True, blank=True, verbose_name=u'Цвет фона')
	fgcolor	= models.IntegerField(null=True, blank=True, verbose_name=u'Цвет текста')

	def     __unicode__(self):
		return self.name

	class   Meta:
		ordering                = ('name', )
		verbose_name            = u'Категория'
		verbose_name_plural     = u'Категории'

class	TagItem(models.Model):
	group	= models.ForeignKey(TagGroup, related_name=u'items', verbose_name=u'Категория')
	name	= models.CharField(max_length=32, unique=True, db_index=True, verbose_name=u'Наименование')

	def	__unicode__(self):
		return self.name

	def	get_full_name(self):
		return u'%s:%s' % (self.group.name, self.name)

	def	get_bgcolor_html(self):
		'''
		@return str - background color (or white)
		'''
		return u'#%06X' % self.group.bgcolor if self.group.bgcolor else 'white'

	def	get_fgcolor_html(self):
		'''
		@return str - foreground color (or black)
		'''
		return u'#%06X' % self.group.fgcolor if self.group.fgcolor else 'black'

	class   Meta:
		#unique_together		= (('group', 'name'),)
		ordering                = ('group', 'name', )
		verbose_name            = u'Тэг'
		verbose_name_plural     = u'Тэги'

def	file_md5(file, block_size=1024*14):
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

class   File(models.Model):
	deleted	= models.BooleanField(default=False, editable=False, verbose_name=u'Удален')
	fname	= models.CharField(max_length=255, db_index=True, verbose_name=u'Наименование')
	mime	= models.CharField(max_length=32, editable=False, db_index=True, verbose_name=u'Тип')
	size	= models.PositiveIntegerField(editable=False, verbose_name=u'Размер')
	ctime	= models.DateTimeField(editable=False, verbose_name=u'Создан')
	mtime	= models.DateTimeField(editable=False, verbose_name=u'Изменен')
	updated	= models.DateTimeField(auto_now=True, editable=False, verbose_name=u'Изменена информация')
	md5	= models.CharField(max_length=32, editable=False, verbose_name=u'MD5')
	comment	= models.TextField(blank=True, verbose_name=u'Комментарии')
	tags	= models.ManyToManyField(TagItem, blank=True, null=True, related_name='files', verbose_name=u'Теги')

	def     __unicode__(self):
		return self.fname

        @models.permalink
	def	get_absolute_url(self):
                return ('dasarchive.views.file_detail', [str(self.pk)])

	def	get_fn(self):
		'''
		@return id as 8xHex
		'''
		return '%08X' % self.pk

	def	get_dir(self):
		'''
		@return id as XX/XX/XX/XX
		'''
		s = self.get_fn()
		return '/'.join((s[:2], s[2:4], s[4:6], s[6:]))

	def	get_full_dir(self):
		return os.path.join(settings.OUTBOX_ROOT, self.get_dir())

	def	get_full_path(self):
		return os.path.join(self.get_full_dir(), self.fname)

	def	rename(self, old_fname, new_fname):
		'''
		FIXME: check new_fname for excluding ../, / etc
		'''
		if (old_fname != new_fname):
			dir = self.get_full_dir()
			os.rename(os.path.join(dir, old_fname), os.path.join(dir, new_fname))

	def	delete(self):
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

	def	save(self, *args, **kwargs):
		if (self.pk):
			self.rename(File.objects.get(pk=self.pk).fname, self.fname)
		super(File, self).save(*args, **kwargs)

	def	fill_with(self, path):
		'''
		Fill fields with path data
		'''
		stat = os.stat(path)
		self.size = stat.st_size
		self.ctime = datetime.datetime.fromtimestamp(stat.st_ctime)
		self.mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
		self.mime = mime.file(path.encode('utf-8'))
		self.md5 = file_md5(path)

	'''
	def	get_full_name(self):
		return u'%s.%s' % (self.name, self.ext)
	'''
	class   Meta:
		ordering                = ('fname',)
		verbose_name            = u'Файл'
		verbose_name_plural     = u'Файлы'
