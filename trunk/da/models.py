# -*- coding: utf-8 -*-

# 1. django
from django.db import models
from django.core.urlresolvers import reverse

# 2. my

# 3. 3rds

# 4. system
import datetime


class   Node(models.Model):
	'''
	Hidden fields:
	* id
	'''
	parent		= models.ForeignKey('self', related_name='children', null=True, db_index=True, verbose_name=u'Parent')
	name		= models.CharField(null=False, db_index=True, max_length=64, verbose_name=u'Name')
	#comment = models.TextField(blank=True, verbose_name=u'Комментарии')
	#mtime   = models.DateTimeField(editable=False, verbose_name=u'Изменен')

	def     __unicode__(self):
		return self.name

	def     isfacet(self):
		if self.pk == 1:
			return True
		try:
			return bool(self.facet)
		except:
			return False

		return self.name

	def     get_fullpath(self):
		retvalue = list()
		parent = self.parent
		while (parent):
			retvalue.append(parent)
			parent = parent.parent
		retvalue.reverse()
		return retvalue

	#@models.permalink
	#def get_absolute_url(self):
	#	return ('da.views.node_path', [str(self.id)])

	class   Meta:
		db_table = 'node'
		ordering                = ('name',)
		unique_together		= ('parent', 'name')
		verbose_name            = u'Узел'
		verbose_name_plural     = u'Узлы'

class   Facet(Node):
	'''
	Hidden fields:
	* node_ptr_id
	'''
	#multiple	= models.BooleanField(null=False, blank=False, default=False, verbose_name=u'Мн')
	#mandatory	= models.BooleanField(null=False, blank=False, default=False, verbose_name=u'Обязательно')
	pass

	def     __unicode__(self):
		return self.name

	class   Meta:
		db_table = 'facet'
		ordering                = ('name',)
		verbose_name            = u'Фасет'
		verbose_name_plural     = u'Фасеты'

class   Tag(Node):
	pass

	def     __unicode__(self):
		return self.name

	class   Meta:
		db_table = 'tag'
		ordering                = ('name',)
		verbose_name            = u'Ярлык'
		verbose_name_plural     = u'Ярлыки'

class   File(models.Model):
	name    = models.CharField(max_length=255, db_index=True, blank=False, verbose_name=u'Наименование')
	#fname   = models.CharField(max_length=255, db_index=True, blank=False, verbose_name=u'Имя файла')
	##comment = models.TextField(blank=True, verbose_name=u'Комментарии')
	#comment = models.CharField(max_length=255, db_index=True, blank=True, verbose_name=u'Комментарии')
	#mime    = models.CharField(max_length=64, editable=True, db_index=True, verbose_name=u'Тип')
	#size    = models.PositiveIntegerField(editable=False, verbose_name=u'Размер')
	#md5     = models.CharField(max_length=32, editable=False, verbose_name=u'MD5')
	#ctime   = models.DateTimeField(editable=False, verbose_name=u'Создан')
	#mtime   = models.DateTimeField(editable=False, verbose_name=u'Изменен')
	#updated = models.DateTimeField(auto_now=True, editable=False, verbose_name=u'Изменена информация')
	#deleted = models.BooleanField(default=False, editable=False, verbose_name=u'Удален')
	tags    = models.ManyToManyField(Tag, blank=True, null=True, related_name='files', verbose_name=u'Теги')

	def	__init__(self, *args, **kwargs):
		super(File, self).__init__(*args, **kwargs)
		self.__selected_nodes = set()
		self.__enabled_nodes = set()
		self.__cached = False

	def	__cache_nodes(self):
		if (not self.__cached):
			self.__cached = True

	def     get_selected_tags(self):
		self.__cache_nodes()

	class   Meta:
		db_table = 'file'
		#ordering                = ('name',)
		verbose_name            = u'Файл'
		verbose_name_plural     = u'Файлы'
