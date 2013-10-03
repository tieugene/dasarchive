# -*- coding: utf-8 -*-
'''
'''

# 1. django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context, loader
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list, object_detail
from django.http import HttpResponseRedirect

# 2. system
import os, sys, pprint

# 3. 3rd parties

# 4. my
import forms, models

PAGE_SIZE = 20

def	index(request):
        return redirect('da.views.node_read', id=1)

def	node_add(request):
	next = request.REQUEST.get('next', request.META['HTTP_REFERER'])
	#return redirect(next)
	if request.method == 'POST':
		parent = models.Node.objects.get(pk=int(request.POST['parent']))
		if (parent.isfacet()):
			form = forms.TagForm(request.POST)
		else:
			form = forms.FacetForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(next)
		else:	# FIXME
			return render_to_response(next, context_instance=RequestContext(request, {
				'object': parent,
				'form': form,
				'next': next,
			}))
	else:
		return HttpResponseRedirect(next)

def	node_read(request, id):
	mode = request.COOKIES.get('node_mode', 0)
	#print 'mode:', mode
	tpl = ('node_path.html', 'node_tree.html', 'node_graph.html')[int(mode)]
	node = models.Node.objects.get(pk=int(id))
	if (node.isfacet()):
		form = forms.TagForm(initial={'parent': node})
	else:
		form = forms.FacetForm(initial={'parent': node})
        response = render_to_response(tpl, context_instance=RequestContext(request, {
		'object': node,
		'form': form,
		'mode': mode,
		#'next': reverse('da.views.node_read', args=[id]),
	}))
	# FIXME: don't set existant cookie
	response.set_cookie('node_mode', mode)
	return response

def	__node_detail(request, id, mode):
	response = redirect('da.views.node_read', id=id)
	#print 'mode=', mode
	response.set_cookie('node_mode', mode)
	return response

def	node_read_path(request, id):
	return  __node_detail (request, id, 0)

def	node_read_tree(request, id):
	return  __node_detail (request, id, 1)

def	node_read_graph(request, id):
	return  __node_detail (request, id, 2)

def	node_del(request, id):
	pass

def	node_edit(request, id):
	pass

def	file_create(request):
	if request.method == 'POST':
		form = forms.FileForm(request.POST)
		if form.is_valid():
			form.save()
			return render_to_response('index.html', context_instance=RequestContext(request, {}))
	else:
		form = forms.FileForm()
        return render_to_response('file/form.html', context_instance=RequestContext(request, {
		'form': form,
	}))

def	file_read(request, id):
	return render_to_response('file/read.html', context_instance=RequestContext(request, {
		'object': models.File.objects.get(pk=int(id)),
	}))

def	file_tags(request, id):
	return render_to_response('file/tags.html', context_instance=RequestContext(request, {
		'object': models.File.objects.get(pk=int(id)),
	}))

def	file_update(request, id):
	pass

def	file_tag_switch(request, id, tag_id):
	pass

def	file_delete(request, id):
	pass

def	filter(request):
	return render_to_response('filter_base.html', context_instance=RequestContext(request, {
		'files': models.File.objects.all(),
	}))
