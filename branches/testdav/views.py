# -*- coding: utf-8 -*-
'''
'''
# 1. system
import sys, os, urllib
reload(sys)
sys.setdefaultencoding('utf-8')

# 2. 3rd
import xattr

# 1. django
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, render, redirect
from django.views.generic.simple import direct_to_template, redirect_to
from django import forms
from django.core.urlresolvers import reverse

class	MyForm(forms.Form):
	comment = forms.CharField(max_length = 256, label='Комментарий', required = False)

def	index(request):
	return render_to_response(
		'index.html',
		context_instance = RequestContext(
			request,
			{'dav': settings.MEDIA_URL,},
		)
	)

def	__get_xattr(path):
	try:
		comment = xattr.get(path, 'comment', namespace=xattr.NS_USER)
	except:
		comment = ''
	return comment

def	__set_xattr(path, text):
	try:
		if (text):
			xattr.set(path, 'comment', text, namespace=xattr.NS_USER)
		else:
			xattr.remove(path, 'comment', namespace=xattr.NS_USER)
	except:
		pass

def	listdir(request, path):
	'''
	Dir/file
	Dir: url to go on
	File: size, urls: download, webdav, dav, windows
	'''
	# 1. try to list recursively
	#print path
	p = os.path.join(settings.MEDIA_ROOT, path).encode('utf-8')
	if (not os.path.exists(p)):
		#print 'path "%s" not exists' % p
		redirect(listdir, os.path.split(p)[0])
	if (not os.path.isdir(p)):
		#print 'path "%s" not folder' % p
		#print 'Goto "%s"' % os.path.split(p)[0]
		return HttpResponseRedirect(reverse('listdir', kwargs={'path': os.path.split(path)[0]}))
	#if ((p) and p[:-1] != '/'):
		#return HttpResponseRedirect(reverse('listdir', kwargs={'path': path + '/'}))
	# 2. go
	data = list()
	full_path = os.path.join(settings.MEDIA_ROOT, path).encode('utf-8')
	fnames = os.listdir(full_path)
	fnames.sort()
	for i in fnames:
		p = os.path.join(full_path, i).encode('utf-8')
		stat = os.stat(p)
		relpath = os.path.join(path, i)
		data.append({
			'name': i,
			'isdir': os.path.isdir(p),
			'stat': stat,
			'path': relpath,
			'dav': os.path.join(settings.MEDIA_URL, relpath),
			'comment': __get_xattr(p),
		})
	return render_to_response(
		'listdir.html',
		context_instance = RequestContext(
			request,
			{
				'path': path,
				'data': data,
			},
		)
	)

def	edit(request, path):
	realpath = os.path.join(settings.MEDIA_ROOT, path).encode('utf-8')
	if (not os.path.exists(realpath)) or (os.path.isdir(realpath)):
		return HttpResponseRedirect(reverse('listdir', kwargs={'path': path}))
	if request.method == 'POST':
		path = request.POST['path']
		f = MyForm(request.POST)
		if f.is_valid():
			__set_xattr(realpath, f.cleaned_data['comment'])
			return HttpResponseRedirect(reverse('listdir', kwargs={'path': path}))
	else:
		f = MyForm(initial={'comment': __get_xattr(realpath)})
	return render_to_response('form.html', context_instance=RequestContext(request, {'form': f, 'path': path}))
