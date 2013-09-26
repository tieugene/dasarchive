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
        return redirect('da.views.node_path', id=1)

def	__node_detail(request, id, tpl):
        return  object_detail (
                request,
                queryset = models.Node.objects.all(),
                object_id = id,
                template_name = tpl,
        )

def	node_path(request, id):
	node = models.Node.objects.get(pk=int(id))
	if (node.pk == 1) or (node.facet):
		form = forms.TagForm(initial={'parent': node})
	else:
		form = forms.FacetForm(initial={'parent': node})
        return render_to_response('node_path.html', context_instance=RequestContext(request, {
		'object': node,
		'form': form,
		'next': reverse('da.views.node_path', args=[id]),
	}))

def	node_tree(request, id):
        return  __node_detail (request, id, 'node_tree.html')

def	node_graph(request, id):
        return  __node_detail (request, id, 'node_graph.html')

def	node_add(request):
	next = request.REQUEST.get('next', request.META['HTTP_REFERER'])
	#return redirect(next)
	if request.method == 'POST':
		parent = models.Node.objects.get(pk=int(request.POST['parent']))
		if (parent.pk == 1) or (parent.facet):
			form = forms.TagForm(request.POST)
		else:
			form = forms.FacetForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(next)
		else:
			return render_to_response(next, context_instance=RequestContext(request, {
				'object': parent,
				'form': form,
				'next': next,
			}))
	else:
		return HttpResponseRedirect(next)
