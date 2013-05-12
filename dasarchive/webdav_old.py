# -*- coding: utf-8 -*-1
'''
lansite.apps.file.webdav
to use:
	KDE: webdav://...
	GNOME: webdav://...
	all:
		wdfs http://localhost:8000/dav/ ~/FUSE/DAV
		fusermount -u ~/FUSE/DAV
'''
# 1. django
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.core.urlresolvers import reverse, resolve
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, render, redirect
from django.utils.log import getLogger
from django.views.generic import RedirectView

# 2. 3rd parties
from lxml import etree
import magic

# 3. system
import sys, os, shutil, datetime, pprint, re, uuid
import logging

# 4. my
import models, views

# constants
log = getLogger('app')
mime = magic.open(magic.MIME_TYPE)
mime.load()
etree.register_namespace('D', 'DAV:')
etree.register_namespace('M', 'urn:schemas-microsoft-com:')
etree.register_namespace('A', 'http://apache.org/dav/props/')

locks = dict()	# id: (token:str, timeout:datetime)
LOCK_MAX_TIMEOUT = 300

def	__url2path(url):
	'''
	? Depth ?
	Converts requested URL into real path
	@return tuple - (ok, File() or None, filename:str or None)
	'''
	err = (False, None, None)
	ishex = re.compile('[0-9A-F]{8}')
	if url == '':						# root
		return (True, None, None)
	path = url.split('/', 1)
	if (ishex.match(path[0])):				# filedir or file
		id = int(path[0], 16)
		try:
			file = models.File.objects.get(pk=id)
		except:
			return err
		if ((len(path) == 1) or (path[1] == '')):	# filedir
			return (True, file, None)
		return (True, file, path[1])			# file
	return err

def	__fill_propfind(props, url, file = None, filename = None):
	'''
	Fills response by real file/dir attributes
	@param props:set - requested properties
	@param usrl:str - href
	@param file:File - filedir - or wanted root if None
	@param filename:str - filename - or wanted filedir if None
	@return lxml.etree.Element
	*:
		creationdate
		getlastmodified
		getcontenttype
		resourcetype
	item:
		+getcontentlength
	'''
	#print 'fill_propfind detected'
	etree.register_namespace('D', 'DAV:')
	etree.register_namespace('M', 'urn:schemas-microsoft-com:')
	etree.register_namespace('A', 'http://apache.org/dav/props/')
	# 0. set defaults
	if (not props):		# defaults (== allprops)
		props = set((	# collection
			'resourcetype',
			'getcontenttype',
			'creationdate',
			'getlastmodified',
			'lockdiscovery',
			'supportedlock',
			#'getetag',
		))
		if (filename):	# file
			props.update((
				'getcontentlength',
				'Win32CreationTime',
				'Win32LastModifiedTime',
				'Win32LastAccessTime',
				'Win32FileAttributes',
				'executable',
			))
	# 1. fill attrs (root, filedir, file)
	if (file == None):	# root
		stat = os.stat(settings.OUTBOX_ROOT)
		rawdata = {
			'mime': 'httpd/unix-directory',
			'ctime': datetime.datetime.fromtimestamp(stat.st_ctime),
			'mtime': datetime.datetime.fromtimestamp(stat.st_mtime),
		}
	elif(filename == None):	# filedir
		rawdata = {
			'mime': 'httpd/unix-directory',
			'ctime': file.ctime,
			'mtime': file.mtime,
		}
	else:			# file
		if (filename == file.fname):
			rawdata = {
				'mime': file.mime,
				'size': file.size,
				'ctime': file.ctime,
				'mtime': file.mtime,
			}
		else:
			path = os.path.join(file.get_full_dir(), filename)
			stat = os.stat(path)
			rawdata = {
				'mime': mime.file(path.encode('utf-8')),
				'size': stat.st_size,
				'ctime': datetime.datetime.fromtimestamp(stat.st_ctime),
				'mtime': datetime.datetime.fromtimestamp(stat.st_mtime),
			}
	# 2. fill response
	response = etree.Element('{DAV:}response')
	etree.SubElement(response, '{DAV:}href').text = url
	# 2.1. usable values
	propstat = etree.SubElement(response, '{DAV:}propstat')
	prop = etree.SubElement(propstat, '{DAV:}prop')
	# 2.1.1. dir/item
	if ('resourcetype' in props):
		if (filename == None):
			etree.SubElement(etree.SubElement(prop, '{DAV:}resourcetype'), '{DAV:}collection')
		else:
			etree.SubElement(prop, '{DAV:}resourcetype')
		props.remove('resourcetype')
	# 2.1.2. mime
	if ('getcontenttype' in props):
		etree.SubElement(prop, '{DAV:}getcontenttype').text = rawdata['mime']
		props.remove('getcontenttype')
	# 2.1.3. size
	if (('getcontentlength' in props) and (('size') in rawdata)):
		etree.SubElement(prop, '{DAV:}getcontentlength').text = str(rawdata['size'])	# FIXME:
		props.remove('getcontentlength')
	# 2.1.4. ctime
	if ('creationdate' in props):
		etree.SubElement(prop, '{DAV:}creationdate').text = rawdata['ctime'].strftime('%Y-%m-%dT%H:%M:%SZ')
		props.remove('creationdate')
	# 2.1.5. mtime
	if ('getlastmodified' in props):
		etree.SubElement(prop, '{DAV:}getlastmodified').text = rawdata['mtime'].strftime('%a, %d %b %Y %X GMT')
		props.remove('getlastmodified')
	# 2.1.6. ctime
	if ('Win32CreationTime' in props):
		etree.SubElement(prop, '{urn:schemas-microsoft-com:}Win32CreationTime').text = rawdata['ctime'].strftime('%a, %d %b %Y %X GMT')
		props.remove('Win32CreationTime')
	# 2.1.7. mtime
	if ('Win32LastModifiedTime' in props):
		etree.SubElement(prop, '{urn:schemas-microsoft-com:}Win32LastModifiedTime').text = rawdata['mtime'].strftime('%a, %d %b %Y %X GMT')
		props.remove('Win32LastModifiedTime')
	# 2.1.8. atime
	if ('Win32LastAccessTime' in props):
		etree.SubElement(prop, '{urn:schemas-microsoft-com:}Win32LastAccessTime').text = rawdata['mtime'].strftime('%a, %d %b %Y %X GMT')
		props.remove('Win32LastAccessTime')
	# 2.1.9. dos-attrs
	if ('Win32FileAttributes' in props):
		etree.SubElement(prop, '{urn:schemas-microsoft-com:}Win32FileAttributes').text = '00002020'
		props.remove('Win32FileAttributes')
	# 2.1.A. exec
	if ('executable' in props):
		etree.SubElement(prop, '{http://apache.org/dav/props/:}executable').text = 'F'
		props.remove('executable')
	# 2.1.x. lock #1
	if ('lockdiscovery' in props):
		etree.SubElement(prop, '{DAV:}lockdiscovery')
		props.remove('lockdiscovery')
	# 2.1.y. lock #2
	if ('supportedlock' in props):
		supportedlock = etree.SubElement(prop,		'{DAV:}supportedlock')
		lockentry = etree.SubElement(supportedlock,	'{DAV:}lockentry')
		etree.SubElement(etree.SubElement(lockentry,	'{DAV:}lockscope'),	'{DAV:}exclusive')
		etree.SubElement(etree.SubElement(lockentry,	'{DAV:}locktype'),	'{DAV:}write')
		lockentry = etree.SubElement(supportedlock,	'{DAV:}lockentry')
		etree.SubElement(etree.SubElement(lockentry,	'{DAV:}lockscope'),	'{DAV:}shared')
		etree.SubElement(etree.SubElement(lockentry,	'{DAV:}locktype'),	'{DAV:}write')
		props.remove('supportedlock')
	# 2.1.z. close
	etree.SubElement(propstat, '{DAV:}status').text = 'HTTP/1.1 200 OK'
	# 2.2. unusable values
	if (props):
		propstat = etree.SubElement(response, '{DAV:}propstat')
		prop = etree.SubElement(propstat, '{DAV:}prop')
		for i in props:
			etree.SubElement(prop, '{DAV:}'+i)	# FIXME: other ns'
		etree.SubElement(propstat, '{DAV:}status').text = 'HTTP/1.1 404 Not Found'
	return response

def	OPTIONS(request, path):
	response = HttpResponse(content_type = 'httpd/unix-directory')
	#response['Allow'] = 'OPTIONS,GET,PUT,HEAD,POST,PROPFIND,PROPPATCH'
	response['Allow'] = 'OPTIONS,GET,HEAD,POST,DELETE,TRACE,PROPFIND,PROPPATCH,COPY,MOVE,LOCK,UNLOCK'
	response['DAV'] = '1,2,<http://apache.org/dav/propset/fs/1>'
	response['Content-Length'] = '0'
	response['MS-Author-Via'] = 'DAV'
	return response

def	PROPFIND(request, path):
	'''
	Schemes:
		* D=DAV:
		* M=urn:schemas-microsoft-com:
		* urn:schemas-microsoft-com:datatypes	not used
		* O=urn:schemas-microsoft-com:office:office
		* A=http://apache.org/dav/props/
	@param path:str - 1. '', 2. 'ID/', 3. 'ID/filename.ext'
	'''
	etree.register_namespace('D', 'DAV:')
	etree.register_namespace('M', 'urn:schemas-microsoft-com:')
	etree.register_namespace('A', 'http://apache.org/dav/props/')
	depth = request.META.get('HTTP_DEPTH', None)
	# 1. parse request
	props = set()
	body = request.read()
	if (len(body)):
		dom = etree.fromstring(body)
		for i in list(list(dom)[0]):	# lxml.etree._Element (base=None, nsmap={'D': 'DAV:'}, prefix='D', tag='{DAV:}tagname'
			props.add(i.tag.split('}', 1)[1] if (i.prefix) else i.tag)
	# 2. generate response
	root = etree.Element('{DAV:}multistatus')
	ok, file, filename = __url2path(path)
	#log.debug('Propfind: path="%s", path_info="%s", full_path="%s"' % (path, request.path_info, request.get_full_path()))
	if ok:
		#if (depth == 0) and (filename == None) and (not path.endswith('/')):
		if (path) and (filename == None) and (not path.endswith('/')):
			return HttpResponsePermanentRedirect(request.path + '/')	# FIXME:
		# 1. root
		# 2. dir
		# 3. file
		root.append(__fill_propfind(props.copy(), request.get_full_path(), file, filename))
		# if root or id only => dir
		if ((filename == None) and (depth == '1')):
			if (file == None):		# root
				for f in models.File.objects.all():
					root.append(__fill_propfind(props.copy(), request.get_full_path() + f.get_fn(), f))
			elif (filename == None):	# file as dir
				for f in (os.listdir(file.get_full_dir())):
					fullurl = request.get_full_path() + f
					root.append(__fill_propfind(props.copy(), fullurl, file, f))
			else:				# file
				fullurl = request.get_full_path()
				root.append(__fill_propfind(props.copy(), fullurl, file, filename))
		content = etree.tostring(root, pretty_print=False, encoding='utf-8', xml_declaration=True)
		response = HttpResponse(content, status = 207, mimetype='text/xml; charset="utf-8"')
		response['Content-Length'] = len(content)
		return response
	raise Http404

def	GET(request, path):
	'''
	FIXME: root, filedir, range
	'''
	#print 'GET:', path
	ok, file, filename = __url2path(path)
	if (ok):
		if (filename):	# get file
			full_path = os.path.join(file.get_full_dir(), filename)
			if (filename == file.fname):
				f_mime = file.mime
			else:
				f_mime = mime.file(full_path.encode('utf-8'))
			response = HttpResponse(
				content = open(full_path).read(),
				content_type = f_mime,
			)
			response['Last-Modified'] = datetime.datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%a, %d %b %Y %H:%M:%S GMT')
			response['Accept-Ranges'] = 'bytes'
			response['Content-Length'] = str(os.path.getsize(full_path))
			return response
		elif(file):
			return HttpResponseRedirect(reverse('file_detail', kwargs={'pk': file.pk}))
		else:
			return HttpResponseRedirect(reverse('file_list'))
	raise Http404

def	PUT(request, path):
	'''
	TODO: lock
	Location
	Statuscode: 201
	Content-Length
	Content-Type
	'''
	ok, file, filename = __url2path(path)
	if ((ok) and (file) and (filename)):	# file own
		full_path = os.path.join(file.get_full_dir(), filename)
		exists = os.path.exists(full_path)
		# 1. write file
		realfile = open(full_path, 'w')
		realfile.write(request.read())
		realfile.flush()
		realfile.close()
		# 2. update DB
		if (filename == file.fname):
			file.fill_with(full_path)
			file.save()
			f_mime = file.mime
			# FIXME: md5
		else:
			f_mime = mime.file(full_path.encode('utf-8'))
		# 3. response
		if (exists):	# update
			response = HttpResponse(status = 204, content_type = f_mime)
		else:		# create
			response = HttpResponse(status = 201, content_type = 'text/xml; charset=UTF-8')
			response['Location'] = reverse('dav', kwargs={'path': file.get_fn()+'/'+filename})
		response['Content-Length'] = '0'
		return response
	raise Http404

def	DELETE(request, path):	# FIXME: inexistant path
	'''
	TODO: lock
	'''
	ok, file, filename = __url2path(path)
	if ((ok) and (file) and (filename) and (file.fname != filename)):
		try:
			os.remove(os.path.join(file.get_full_dir(), filename))
			response = HttpResponse(status = 204, content_type = 'text/xml; charset=UTF-8')	# FIXME?
			response['Content-Length'] = '0'
			return response
		except:
			pass
	raise Http404

def	PROPPATCH(request, path):
	'''
	@param path:str - 1. '', 2. 'ID/', 3. 'ID/filename.ext'
	'''
	ok, file, filename = __url2path(path)
	if ((ok) and (file) and (filename)):
		etree.register_namespace('D', 'DAV:')
		etree.register_namespace('M', 'urn:schemas-microsoft-com:')
		etree.register_namespace('A', 'http://apache.org/dav/props/')
		# 1. prepare response
		root = etree.SubElement(etree.Element('{DAV:}multistatus'), '{DAV:}response')
		etree.SubElement(root, '{DAV:}href').text = request.get_full_path()
		propstat = etree.SubElement(root, '{DAV:}propstat')
		etree.SubElement(propstat, '{DAV:}status').text = 'HTTP/1.1 200 OK'
		prop = etree.SubElement(propstat, '{DAV:}prop')
		# 2. parse request
		body = request.read()
		dom = etree.fromstring(body)
		for i in list(list(list(dom)[0])[0]):
			# 2. fill response - FAKE!!!
			etree.SubElement(prop, i.tag)
		# 4. finish response
		content = etree.tostring(root, pretty_print=False, encoding='utf-8', xml_declaration=True)
		response = HttpResponse(content, status = 207, mimetype='text/xml; charset="utf-8"')
		response['Content-Length'] = len(content)
		return response
	raise Http404

def	LOCK(request, path):
	'''
	exclusive, 1 time, main file-member only
	Store: id:pk, owner:str, due:datetime
	request (new): lockinfo: [locktype: write/, lockscope: exclusive/, owner:root]
	return: 200 w/ opaquetoken and timeout
	Disabled:
		* request body (=> shared, owner)
		* lock of !File (=> depth)
	Refresh:
		if (lock) and (requested_lock == lock):
			if (!timeout):
				reset timeout
				return 200+lock
			else:
				del lock
	Request:
		if (lock):
			if (!timeout):
				return 423 (locked)
			else:
				del lock
		gen uuid
		set lock
		set timeout
		return 200+lock
	return 404
	'''
	ret_200 = False
	ok, file, filename = __url2path(path)
	if ((ok) and (file) and (filename) and (filename == file.fname)):	# 1. item only
		# 0. GET request
		timeout	= request.META.get('HTTP_TIMEOUT', None)
		log.debug('Timeout:'+str(timeout))
		#log.debug(request.META)
		if timeout:
			timeout = int(timeout.lstrip('Second-'))
			if timeout > LOCK_MAX_TIMEOUT:
				timeout = LOCK_MAX_TIMEOUT
		else:
			timeout = LOCK_MAX_TIMEOUT
		refresh	= request.META.get('HTTP_IF', None)
		lock = locks.get(file.pk, None)
		now = datetime.datetime.now()
		if (refresh):
			requested_lock = refresh.split(':', 1)[1][:32]		# FIXME: regex
			log.debug('LOCK refresh token:'+str(requested_lock))
			if ((lock) and (requested_lock == lock[0])):
				if lock[1] <= now:
					lock[1] += datetime.timedelta(0, timeout)
					ret_200 = True
				else:
					del locks[file.pk]
		else:
			if (lock):
				if (lock[1]) <= now:
					return 423
				else:
					del locks[file.pk]
			uid = uuid.uuid4().hex.upper()
			locks[filename] = (uid, now+datetime.timedelta(0, timeout))
			ret_200 = True
	if (ret_200):
		etree.register_namespace('D', 'DAV:')
		root = etree.Element('{DAV:}prop')
		activelock = etree.SubElement(etree.SubElement(root, '{DAV:}lockdiscovery'), '{DAV:}activelock')
		etree.SubElement(etree.SubElement(activelock, '{DAV:}locktype'), '{DAV:}write')
		etree.SubElement(etree.SubElement(activelock, '{DAV:}lockscope'), '{DAV:}exclusive')
		etree.SubElement(activelock, '{DAV:}depth').text = '0'
		etree.SubElement(activelock, '{DAV:}timeout').text = 'Second-%d' % timeout
		etree.SubElement(etree.SubElement(activelock, '{DAV:}locktoken'), '{DAV:}href').text = 'opaquelocktoken:' + uid
		content = etree.tostring(root, pretty_print=False, encoding='utf-8', xml_declaration=True)
		response = HttpResponse(content, status = 200, mimetype='text/xml; charset="utf-8"')
		response['Content-Length'] = len(content)
		if (not refresh):
			response['Lock-Token'] = '<opaquelocktoken:%s>' % uid
			log.debug('LOCK given token:'+str(uid))
		return response
	raise Http404

def	UNLOCK(request, path):
	'''
	exclusive, main file-member only
	Store: id:pk, owner:str, due;datetime
	return: 204
	'''
	#log.debug(request.META)
	ret_200 = False
	ok, file, filename = __url2path(path)
	if ((ok) and (file) and (filename) and (filename == file.fname)):	# 1. item only
		token	= request.META.get('HTTP_LOCK_TOKEN', None)
		log.debug('Token:'+token)
		requested_lock = token.split(':', 1)[1][:32]		# FIXME: regex
		log.debug('UNLOCK requested lock:'+str(requested_lock))
		lock = locks.get(file.pk, None)
		if (lock):
			del locks[file.pk]
		response = HttpResponse(status = 204, mimetype=file.mime)
		response['Content-Length'] = '0'
		return response
	raise Http404

def	hook(request, path):
	log.debug('Hook: "%s", "%s".' % (request.method, path))
	raise Http404

davdict = {
#	type		function	standard, mandatory ('+' == MUST, '-' == OPTIONAL, '' == ...)
	'OPTIONS':	OPTIONS,	# HTTP	+
	'PROPFIND':	PROPFIND,	# DAV	+
	'GET':		GET,		# HTTP	+
	'PUT':		PUT,		# HTTP	+
	'DELETE':	DELETE,		# HTTP	+
	'PROPPATCH':	PROPPATCH,	# DAV	+
	'LOCK':		LOCK,		# DAV	+
	'UNLOCK':	UNLOCK,		# DAV	+

	'HEAD':		hook,		# HTTP	-?
	'POST':		hook,		# HTTP	-?
	'MKCOL':	hook,		# DAV	+
	'COPY':		hook,		# DAV	+
	'MOVE':		hook,		# DAV	+

	'PATCH':	hook,		# HTTP	-
	'TRACE':	hook,		# HTTP	-
	'LINK':		hook,		# HTTP	-
	'UNLINK':	hook,		# HTTP	-
}
