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

	def	__paint_branch(self, node, space):
		css = 'me' if (node.pk == self.pk) else ''
		retvalue = space + ' <li> <a href="%s" class="%s"> %s </a>' % (reverse('da.views.node_tree', args=[node.pk]), css, node.name)
		children = node.children.all()
		if (children.count() > 0):
			retvalue += '<ul>\n'
			for i in children:
				retvalue = retvalue + self.__paint_branch(i, space + ' ')
			retvalue = retvalue + space + '</ul>'
		return retvalue + '</li>\n'

	def	paint_tree(self):
		return self.__paint_branch(Node.objects.get(pk=1), ' ')

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
	multiple	= models.BooleanField(null=False, blank=False, default=False, verbose_name=u'Мн')
	mandatory	= models.BooleanField(null=False, blank=False, default=False, verbose_name=u'Обязательно')

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
