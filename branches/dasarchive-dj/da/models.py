# -*- coding: utf-8 -*-

# 1. django
from django.db import models
from django.contrib.auth.models import User

# 2. my

# 3. 3rds

# 4. system
import datetime


class   Node(models.Model):
	#id		= models.BigIntegerField(primary_key=True, verbose_name=u'ID')
	parent		= models.ForeignKey('self', related_name='children', null=True, db_index=True, verbose_name=u'Parent')
	name		= models.CharField(null=False, db_index=True, max_length=64, verbose_name=u'Name')

	def     __unicode__(self):
		return self.name

	#@models.permalink
	#def get_absolute_url(self):
	#	return ('da.views.node_path', [str(self.id)])

	class   Meta:
		db_table = 'node'
		ordering                = ('name',)
		verbose_name            = u'Узел'
		verbose_name_plural     = u'Узлы'

class   Facet(Node):
	multiple	= models.BooleanField(null=False, blank=False, default=False, verbose_name=u'Мн')
	multiple	= models.BooleanField(null=False, blank=False, default=False, verbose_name=u'Мн')

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
