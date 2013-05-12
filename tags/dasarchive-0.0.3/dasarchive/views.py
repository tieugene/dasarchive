# -*- coding: utf-8 -*-
'''
'''
# 1. django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import get_current_site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Count, Aggregate, Q
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context, loader
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list, object_detail
from django.utils.datastructures import SortedDict
from django.utils.log import getLogger
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView, FormView

# 2. system
import os, sys, shutil, datetime, pprint, logging, urllib

# 3. 3rd parties
import wdp.dsfs, wdp.lock, wdp.dp

# 4. my
import models, forms, webdav, utils, uasparser, deleter

# consts
reload(sys)
sys.setdefaultencoding('utf-8')
#log = getLogger('app')
PAGE_SIZE = 20
uas = uasparser.UASparser(settings.UASCACHE_ROOT)
'''
uadict = {
    'Linux/Konqueror':  'webdav://',
    'Linux/Epiphany':   'dav://',
    'Windows/Firefox':  'file://///',
    'Windows/IE':       'file://///',
    'Windows/Chrome':   'file://///',
    'Windows/Safari':   'file://///',
    'Windows/QupZilla': 'file://///',
}
'''
DP = wdp.dp.DavProvider(webdav.DAStorage(settings.OUTBOX_ROOT))

def __get_ua(request):
    # Windows+Firefox
    #ua = 'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18'
    # Mac OS
    #ua = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_5; en-us) AppleWebKit/525.26.2 (KHTML, like Gecko) Version/3.2 Safari/525.26.12'
    #return {'os_family': 'Windows', 'ua_family': 'Firefox'}
    return uas.parse(request.META['HTTP_USER_AGENT'])

def pathurls(path):
    '''
    '''
    pathlist = path.split('/')
    retlist = list()
    for i, p in enumerate(pathlist[:-1]):
        retlist.append(u'<a href="%s"> <button type="button"> %s </button> </a>' % (reverse('dasarchive.views.inbox', args=['/'.join(pathlist[:i+1])]), p))
    return retlist+pathlist[-1:]

@csrf_exempt
def index(request):
    '''
    '''
    #log.debug('Path: ' + request.path)         # /dasarchive/
    #log.debug('Path_Info: ' + request.path_info)       # /
    #log.debug('Get_Full_Path: ' + request.get_full_path()) # dasarchive/
    if request.method == 'GET':
        return redirect('file_list')
    elif (request.method == 'PROPFIND'):    # FIXME: content-length == 0
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
        response = HttpResponse()
        response['Allowed'] = wdp.dp.ALLOWED
        return response
    raise Http404
    #return direct_to_template(request, 'index.html')

@csrf_exempt
def help(request):
    res = __get_ua(request)
    #res = uas.parse('Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18')
    #res = uas.parse('Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_5; en-us) AppleWebKit/525.26.2 (KHTML, like Gecko) Version/3.2 Safari/525.26.12')
    return render_to_response(
        settings.HELP_TEMPLATE,
        context_instance = RequestContext(
            request,
            {
                'os': res['os_family'],
                'browser': res['ua_family'],
                'server': request.get_host(),
                'inbox_url': settings.INBOX_URL,
                'dav_url': reverse('dav', kwargs={'path': ''}),
                'dav_drive': settings.OUTBOX_DRIVE,
            },
        )
    )

def inbox(request, path):
    '''
    @parameter path:str - relative path of folder to ls
    TODO: dircache
    '''
    fullpath = os.path.join(settings.INBOX_ROOT, path).encode('utf-8')
    if (os.path.isdir(fullpath)):
        for (p, d, f) in os.walk(fullpath):
            break
        d.sort()
        f.sort()
        files = SortedDict()
        for isdir, df in ((True, d), (False, f)):
            for i in df:
                stat = os.stat(os.path.join(fullpath, i))
                files[i] = {
                    'isdir':    isdir,
                    'name':     i,
                    'path':     os.path.join(path, i),
                    'size':     stat.st_size,
                    #'mtime':    datetime.datetime.fromtimestamp(stat.st_mtime),
                    #'ctime':    datetime.datetime.fromtimestamp(stat.st_ctime),
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
    else:
        response = HttpResponse(content_type = utils.get_mime(fullpath))
        response['Content-Transfer-Encoding'] = 'binary'
        response['Content-Disposition'] = (u'attachment; filename=\"%s\";' % os.path.basename(fullpath)).encode('utf-8')
        response.write(open(fullpath).read())
        return response

@transaction.commit_on_success
def file_add(request, path):
    '''
    FIXME: path not sent on POST
    '''
    next = request.REQUEST.get('next', request.META.get('HTTP_REFERER', reverse('dasarchive.views.inbox', args=[''])))
    if request.method == 'POST':
        path = request.POST['path']
        f = forms.FileForm(request.POST)
        if f.is_valid():
            src_path = os.path.join(settings.INBOX_ROOT, path)
            file = f.save(commit=False)
            file.fill_with(src_path)
            file.save()
            #file.flush()
            f.save_m2m()
            dst_dir = file.get_full_dir()
            #try:
            if (not os.path.exists(dst_dir)):
                os.makedirs(dst_dir)
            dst_path = file.get_full_path()
            #utils.LOG('src_path: %s', str(isinstance(src_path, str)))   # runserver: False
            os.rename(src_path.encode('utf-8'), dst_path.encode('utf-8'))
            #shutil.copy2(src_path.encode('utf-8'), dst_dir)
            #except:
            #    if os.path.exists(dst_path):
            #        os.rmdir(dst_path)
            #    transaction.rollback()
            ##else:
            ##    # FIXME: return to folder if it's exists
            return HttpResponseRedirect(next)
    else:
        # check file on existance
        md5 = utils.file_md5(os.path.join(settings.INBOX_ROOT, path.encode('utf-8')))
        files = models.File.objects.filter(md5=md5)
        if (files):
            return render_to_response('file_exists.html', context_instance=RequestContext(request, {
            'object_list': files,
            'next': next
        }))
        fname = os.path.split(path)[1]
        f = forms.FileForm(instance=models.File(name=fname, fname=fname))
    return render_to_response('file_form.html', context_instance=RequestContext(request, {
        'form': f,
        'path': path,
        'taggroup_list': models.TagGroup.objects.all(),
        'next': next,
    }))

#from django.db.models.sql import aggregates
class CountIn(Count):
    """
    Hack Count() to get a conditional count working.
    """
    sql_template = '%(function)s(IF((%(field)s IN %(equals)s,TRUE,NULL))'

def file_list(request):
    '''
    TODO: cookie:
    filter_concat: int
    filter_deleted: int
    filter_tags: 1, 2, 3, 4..., X
    '''
    contains = request.COOKIES.get('filter_contains', '')
    deleted = int(request.COOKIES.get('filter_deleted', '1'))  # Live
    concat = int(request.COOKIES.get('filter_concat', '1'))  # OR
    taglist = request.COOKIES.get('filter_tags', None)
    if (taglist):
        tags = map(int, taglist.split(','))
    else:
        tags = []
    q = models.File.objects.all()
    # 2. tags+concat
    if (tags):  # tagged
        # 3. filter logic
        if (concat == 1):   # 3.1. OR
            q = q.filter(tags__pk__in=tags).annotate(alltags_count=Count('tags', distinct=True))
        elif (concat == 2): # 3.2. AND+
            q = q.filter(tags__pk__in=tags).annotate(alltags_count=Count('tags', distinct=True)).filter(alltags_count = len(tags))
        elif (concat == 3): # 3.3. OR exact
            q = q.exclude(tags__pk__in=models.TagItem.objects.exclude(pk__in=tags).values_list('id', flat=True)).annotate(alltags_count=Count('tags', distinct=True))
        else:               # 3.4. AND exact
            q = q.exclude(tags__pk__in=models.TagItem.objects.exclude(pk__in=tags).values_list('id', flat=True)).annotate(alltags_count=Count('tags', distinct=True)).filter(alltags_count = len(tags))
    else:       # untagged
        q = q.annotate(alltags_count=Count('tags', distinct=True)).filter(alltags_count = 0)
    # 2. deleted
    if (deleted < 3):
        q = q.filter(deleted=(deleted == 2))
    # 3. contains
    if (contains):
        q = q.filter(Q(name__icontains=contains) | Q(comment__icontains=contains))
    # 4. lets go
    queryset = q
    form_main = forms.FilterFormMain(prefix='main')
    form_tags = forms.set_filter()(prefix='tags')
    #pprint.pprint(form.fields)
    form_main.fields['contains'].initial = contains
    form_main.fields['deleted'].initial = deleted
    form_main.fields['concat'].initial = concat
    # prepare taglist
    tagdict = {}
    for tag in models.TagItem.objects.filter(pk__in=tags):
        if (tag.group.pk not in tagdict):
            tagdict[tag.group.pk] = list()
        tagdict[tag.group.pk].append(tag.pk)
    # lets go
    for k, v in tagdict.iteritems():
        form_tags.fields['tag%d' % k].initial = v
    #form.css_classes('foo bar')
    # page it
    paginator = Paginator(queryset, PAGE_SIZE)
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:    # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:           # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)
    return render_to_response(
        'file_list.html',
        context_instance = RequestContext(
            request,
            {
                'object_list': queryset,
                'form_main': form_main,
                'form_tags': form_tags,
                'taggroup_list': models.TagGroup.objects.all(),
                'page_start': PAGE_SIZE * (queryset.number - 1),
            },
        )
    )

@csrf_exempt
def file_filter(request):
    concat = None
    deleted = None
    tags = []
    if request.method == 'POST':
        form_main = forms.FilterFormMain(request.POST, prefix='main')
        form_tags = forms.set_filter()(request.POST, prefix='tags')
        if (form_main.is_valid()):
            contains = form_main.cleaned_data['contains']
            deleted = int(form_main.cleaned_data['deleted'])
            concat = int(form_main.cleaned_data['concat'])
        if (form_tags.is_valid()):
            for k, v in form_tags.cleaned_data.iteritems():  # tag1..
                if (k.startswith('tag')):
                    for i in v:
                        tags.append(int(i))
    response = HttpResponseRedirect(reverse('dasarchive.views.file_list'))
    response.set_cookie('filter_contains', contains)
    if (deleted != None):
        response.set_cookie('filter_deleted', str(deleted))
    if (concat != None):
        response.set_cookie('filter_concat', str(concat))
    response.set_cookie('filter_tags', ','.join(map(str, tags)))
    return response

@csrf_exempt
def resettags(request):
    forms.FilterFormTags = None
    return redirect('file_list')

def file_detail(request, pk):
    file = models.File.objects.get(pk=int(pk))
    res = __get_ua(request)
    dav_url = None
    if (res['os_family'] == 'Windows'):
        dav_url = 'file:///%s:/%s/%s' % (settings.OUTBOX_DRIVE, file.get_fn(), file.fname)
    elif (res['os_family'] == 'Linux'):
        url = request.build_absolute_uri(reverse('dav', kwargs={'path': file.get_fn() + '/' + file.fname}))
        if (res['ua_family'] == 'Konqueror'):
            dav_url = url.replace('http://', 'webdav://')
        elif (res['ua_family'] == 'Epiphany'):
            dav_url = url.replace('http://', 'dav://')
    #dav_url = urllib.unquote(request.build_absolute_uri(reverse('dav', kwargs={'path': file.get_fn() + '/' + file.fname})).replace('http://', davproto))    # /dav/...
    return render_to_response(
        'file_detail.html',
        context_instance = RequestContext(
            request,
            {
                'object': file,
                'dav_url': dav_url,
                'os': res['os_family'],
                'browser': res['ua_family'],
            },
        )
    )

def file_edit(request, pk):
    next = request.REQUEST.get('next', reverse('file_detail', args=[pk]))
    #print 'Next:', next
    file = models.File.objects.get(pk=int(pk))
    if request.method == 'POST':
        form = forms.FileForm(request.POST, instance=file)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(next)
    else:
        form = forms.FileForm(instance=file)
    return render_to_response('file_form.html', context_instance=RequestContext(request, {
        'form': form,
        'object': file,
        'taggroup_list': models.TagGroup.objects.all(),
        'next': next,
    }))

class   FileDeleteView(DeleteView):
    model = models.File
    template_name = 'file_confirm_delete.html'
    #success_url = reverse('file_list', args=[])
    success_url = '../..'   # FIXME:

def file_mark_deleted(request, pk):
    file = models.File.objects.get(pk=int(pk))
    file.deleted = True
    file.save()
    return redirect('file_detail', pk=pk)

def file_mark_undeleted(request, pk):
    file = models.File.objects.get(pk=int(pk))
    file.deleted = False
    file.save()
    return redirect('file_detail', pk=pk)

def file_download(request, pk):
    file = models.File.objects.get(pk=long(pk))
    response = HttpResponse(content_type = file.mime)   # HttpResponse(mimetype='text/xml; charset=utf-8')
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = (u'attachment; filename=\"%s\";' % file.fname).encode('utf-8')
    response.write(open(file.get_full_path().encode('utf-8')).read())
    return response

@csrf_exempt
def dav(request, path):
    #print 'dav:', path
    return DP.dispatch(request, path)
