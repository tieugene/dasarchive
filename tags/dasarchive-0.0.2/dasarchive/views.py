# -*- coding: utf-8 -*-
'''
'''
# 1. django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context, loader
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list, object_detail
from django.utils.datastructures import SortedDict
from django.utils.log import getLogger
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView, FormView
from django.views.generic.edit import FormMixin

# 2. system
import os, sys, datetime, pprint, logging

# 4. my
from forms import *
import webdav

reload(sys)
sys.setdefaultencoding('utf-8')
log = getLogger('app')
PAGE_SIZE = 20

def	pathurls(path):
	'''
	'''
	pathlist = path.split('/')
	retlist = list()
	for i, p in enumerate(pathlist[:-1]):
		retlist.append(u'<a href="%s"> <button type="button"> %s </button> </a>' % (reverse('dasarchive.views.inbox', args=['/'.join(pathlist[:i+1])]), p))
	return retlist+pathlist[-1:]

@csrf_exempt
def	index(request):
	'''
	'''
	#log.debug('Path: ' + request.path)			# /dasarchive/
	#log.debug('Path_Info: ' + request.path_info)		# /
	#log.debug('Get_Full_Path: ' + request.get_full_path())	# dasarchive/
	if request.method == 'GET':
		return direct_to_template(request, 'index.html')
	elif (request.method == 'PROPFIND'):	# FIXME: content-length == 0
		path = request.path
		if (path.endswith('/')):
			depth = request.META.get('HTTP_DEPTH', None)
			content = render(request, 'dav_root.xml', context_instance=Context({'path': path, 'depth': depth}), content_type='text/xml').content
			response = HttpResponse(content, status = 207, mimetype='text/xml; charset="utf-8"')
			response['Content-Length'] = len(content)
			return response
		else:
			log.debug('I will move you')
			return HttpResponsePermanentRedirect(request.path + '/')
	elif (request.method == 'OPTIONS'):
		return webdav.OPTIONS(request, '')
	raise Http404
	#return direct_to_template(request, 'index.html')

def	inbox(request, path):
	'''
	@parameter path:str - relative path of folder to ls
	TODO: dircache
	'''
	fullpath = os.path.join(settings.INBOX_ROOT, path)
	for (p, d, f) in os.walk(fullpath):
		break
	d.sort()
	f.sort()
	files = SortedDict()
	for isdir, df in ((True, d), (False, f)):
		for i in df:
			stat = os.stat(os.path.join(fullpath, i))
			files[i] = {
				'isdir':	isdir,
				'name':		i,
				'path':		os.path.join(path, i),
				'size':		stat.st_size,
				'mtime':	datetime.datetime.fromtimestamp(stat.st_mtime),
				'ctime':	datetime.datetime.fromtimestamp(stat.st_ctime),
			}
	#files = os.listdir(path)
	return render_to_response(
		'inbox.html',
		context_instance = RequestContext(
			request,
			{
				'pathurls': pathurls(path),
				'data': files,
				'path': path,
			},
		)
	)

@transaction.commit_on_success
def	file_add(request, path):
	'''
	FIXME: path not sent on POST
	'''
	if request.method == 'POST':
		path = request.POST['path']
		f = FileForm(request.POST)
		if f.is_valid():
			src_path = os.path.join(settings.INBOX_ROOT, path)
			file = f.save(commit=False)
			file.fill_with(src_path)
			file.save()
			#file.flush()
			f.save_m2m()
			try:
				# FIXME:
				# exists
				# try...except
				# (try rm dir)
				# ret error
				os.makedirs(file.get_full_dir())
				os.rename(src_path, file.get_full_path())
			except:
				transaction.rollback()
			else:
				# FIXME: return to folder if it's exists
				return HttpResponseRedirect(reverse('dasarchive.views.inbox', args=['']))
	else:
		fname = os.path.split(path)[1]
		f = FileForm(instance=File(fname=fname, comment=path))
	return render_to_response('file_form.html', context_instance=RequestContext(request, {'form': f, 'path': path}))

def	file_list(request):
	filter = {
		'tags': [],
		'concat': 1,
		'deleted': 1,
	}
	if request.method == 'POST':
		form = set_filter()(request.POST)
		if (form.is_valid()):
			# define filters
			q = File.objects.annotate(alltags_count=Count('tags', distinct=True))
			# 1. deleted
			deleted = int(form.cleaned_data['deleted'])
			if (deleted < 3):
				q = q.filter(deleted=(deleted == 2))
			# 2. get tags
			tags = []
			for k, v in form.cleaned_data.iteritems():	# tag1..
				if (k.startswith('tag')):
					for i in v:
						tags.append(int(i))
			if (tags):	# tagged
				# 3. filter logic
				concat = int(form.cleaned_data['concat'])
				# 3.1. OR
				q = q.filter(tags__pk__in=tags).annotate(Count('tags', distinct=True))
				# 3.2. AND+
				if (concat >= 2):
					q = q.extra(select={'tcount': 'SELECT COUNT(*) FROM dasarchive_file_tags WHERE (dasarchive_file_tags.file_id = dasarchive_file.id) AND (dasarchive_file_tags.tagitem_id IN %s)' % str(tuple(tags))}, where=['tcount=%d' % len(tags)])
				# 3.3. AND exact (not works)
					if (concat == 3):
						q = q.filter(alltags_count = len(tags))
			else:		# untagged
				q = q.filter(alltags_count = 0)
			queryset = q
		else:		# form invalid
			queryset = File.objects.none()
	else:			# GET
		form = set_filter()()
		queryset = File.objects.none()
	return  object_list (
		request,
		queryset = queryset,
		paginate_by = PAGE_SIZE,
		page = int(request.GET.get('page', '1')),
		template_name = 'file_list.html',
		extra_context = {
			'form': form,
		}
	)

class	FileListView(FormMixin, ListView):
	'''
	http://django-document-tchinese.readthedocs.org/en/latest/topics/class-based-views/mixins.html
	'''
	model = File
	template_name = 'file_list.html'
	form_class = set_filter()
	success_url = ''
	paginate_by = 10
	filter = {
		'tags': [],
		'concat': 1,
		'deleted': 1,
	}

	def	get_queryset(self):
		# 1. tags
		q = File.objects.annotate(alltags_count=Count('tags', distinct=True))
		if (self.filter['tags']):	# tagged
			# OR
			q = q.filter(tags__pk__in=self.filter['tags']).annotate(Count('tags', distinct=True))
			#q = q.filter(tags__pk__in=(self.filter['tags'])).aggregate(Count('tags'))
			if (self.filter['concat'] == 2):	# AND
				#q2 = TagItem.objects.filter(pk__in=self.filter['tags'])
				#q = q.filter(tags__in=q2)
				q = q.extra(select={'tcount': 'SELECT COUNT(*) FROM dasarchive_file_tags WHERE (dasarchive_file_tags.file_id = dasarchive_file.id) AND (dasarchive_file_tags.tagitem_id IN (2, 5))'}, where=['tcount=2'])
				#print q.query
				#q = q.filter(tcount=2)
			elif (self.filter['concat'] == 3):
				#print self.filter['tags']	# '2', '5'
				#q = q.filter(Q(tags__pk=2) & Q(tags__pk=5))
				q = q.filter(tags__count = len(self.filter['tags']))
		else:				# untagged
			q = q.filter(alltags_count = 0)
		# 2. deleted
		if (self.filter['deleted'] < 3):
			q = q.filter(deleted=(self.filter['deleted'] == 2))
		return q

	def	get_context_data(self, **kwargs):
		context = super(FileListView, self).get_context_data(**kwargs)
		context['form'] = self.get_form(self.get_form_class())
		return context

	def	post(self, request, *args, **kwargs):
		form = self.get_form(self.get_form_class())
		if form.is_valid():
			self.filter['tags'] = []
			for k, v in form.cleaned_data.iteritems():	# tag1..
				if (k.startswith('tag')):
					self.filter['tags'] += v
			self.filter['concat'] = int(form.cleaned_data['concat'])
			self.filter['deleted'] = int(form.cleaned_data['deleted'])
			#return self.form_valid(form)
		else:
			return self.form_invalid(form)
		return self.get(request, **kwargs)
		#return self.render_to_response(self.get_context_data(), **kwargs)

class	FileDetailView(DetailView):
	model = File
	template_name = 'file_detail.html'
	base_url = None

	def	get_context_data(self, **kwargs):
		kwargs.update({'base_url': self.base_url.replace('http://', '')})
		return super(FileDetailView, self).get_context_data(**kwargs)

	def	get(self, *args, **kwargs):
		if (not self.base_url):
			self.base_url = args[0].build_absolute_uri('/')[:-1]
		return super(FileDetailView, self).get(*args, **kwargs)

class	FileUpdateView(UpdateView):
	model = File
	template_name = 'file_form.html'
	form_class = FileForm
	success_url = '..'	# FIXME:

class	FileDeleteView(DeleteView):
	model = File
	template_name = 'file_confirm_delete.html'
	#success_url = reverse('file_list', args=[])
	success_url = '../..'	# FIXME:

def	file_mark_deleted(request, pk):
	file = File.objects.get(pk=int(pk))
	file.deleted = True
	file.save()
	return redirect('file_detail', pk=pk)

def	file_mark_undeleted(request, pk):
	file = File.objects.get(pk=int(pk))
	file.deleted = False
	file.save()
	return redirect('file_detail', pk=pk)

def	file_download(request, pk):
	file = File.objects.get(pk=long(pk))
	response = HttpResponse(content_type = file.mime)	# HttpResponse(mimetype='text/xml; charset=utf-8')
	response['Content-Transfer-Encoding'] = 'binary'
	response['Content-Disposition'] = (u'attachment; filename=\"%s\";' % file.fname).encode('utf-8')
	response.write(open(file.get_full_path()).read())
	return response

@csrf_exempt
def	dav(request, path):
	#print 'Method:', request.method
	func = webdav.davdict.get(request.method, None)
	if func:
		return func(request, path)
	else:
		raise Http404
