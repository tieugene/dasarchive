# -*- coding: utf-8 -*-
'''
TODO:
'''
from django import template
register = template.Library()

@register.filter
def	pathurls(path):
	'''
	* Split path to url list:
	f1/f2/f3 => <a href="f1"> f1 </a> / <a href="f1/f2"> f2 </a> / f3 - not
	f1/f2/f3 => <a href="../.."> f1 </a> / <a href=".."> f2 </a> / f3
	f1/f2/f3 => <a href="{% url views.inbox 'f1' %}"> f1 </a> / <a href="{% url views.inbox 'f1/f2' %}"> f2 </a> / f3
	'''
	pathlist = path.split('/')
	retlist = list()
	for i, p in enumerate(pathlist[:-1]):
		retlist.append('<a href="{% url views.inbox \'%s\' %}"> %s </a>' % ('/'.join(pathlist[:i]), p))
	retvalue = '/'.join(retlist+pathlist[-1:])
	print retvalue
	return retvalue

@register.filter
def	letterbox(s, l = None):
	'''
	Splits s by l chars
	'''
	retvalue = ''
	if (l):
		s = s.ljust(int(l))
	for c in s:
		retvalue += '<div>'+c+'</div>'
	return retvalue

@register.filter
def	sljust(s, lc):
	'''
	rjust string by char
	'''
	#return s
	l, c = lc.split(',')
	if isinstance(s, (int, long)):
		s = unicode(s)
	return s.ljust(int(l), c)

@register.filter
def	towebdav(url):
	return url.replace('http', 'webdav')

@register.filter
def	color(i):
    return '#%06X' % i
