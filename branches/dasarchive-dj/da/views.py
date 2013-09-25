# -*- coding: utf-8 -*-
'''
Order: beg ASC, end DESC (wider first
Filters:
* top/all (and nothing else)
* IP => 1 record (check reserved IPs: http://en.wikipedia.org/wiki/Reserved_IP_addresses)
* key word => list
* State: not voted/on voting/voted (b/w)
* Findme
TODO:
* top search bar - always
* search IP _or_ word
* word: chk for ascii only
* all == filtered on None
'''

# 1. django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context, loader
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list, object_detail
from django.utils.datastructures import SortedDict

# 2. system
import os, sys, pprint

# 3. 3rd parties

# 4. my
import forms, models

PAGE_SIZE = 20

def	__r_list(request, q):
        return  object_list (
                request,
                queryset = q,
                paginate_by = PAGE_SIZE,
                page = int(request.GET.get('page', '1')),
                template_name = 'ripe_list.html',
		extra_context = {
			'ipform': forms.SearchIPForm(),
			'kwform': forms.SearchWordForm(),
		},
        )

def	index(request):
        return  redirect('da.views.node_path', id=1)

def	node_path(request, id):
        return  object_detail (
                request,
                queryset = models.Node.objects.all(),
                object_id = id,
                template_name = 'node_path.html',
        )
        return  __r_list (request, models.Node.objects.filter(parent__isnull=True))

def	node_tree(request, id):
        return  object_detail (
                request,
                queryset = models.Node.objects.all(),
                object_id = id,
                template_name = 'node_tree.html',
        )

def	node_graph(request, id):
        return  object_detail (
                request,
                queryset = models.Node.objects.all(),
                object_id = id,
                template_name = 'node_graph.html',
        )
