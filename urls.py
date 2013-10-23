from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.core.urlresolvers import reverse

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$',		'views.index'),
	url(r'^admin/',		include(admin.site.urls)),
	url(r'^admin/jsi18n',	'django.views.i18n.javascript_catalog'), # hack to use admin form widgets
	#(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
	url(r'^login$',		'django.contrib.auth.views.login'),
	url(r'^logout$',	'django.contrib.auth.views.logout'),
	url(r'^da/',		include('da.urls')),
	url(r'^about$',		'views.about'),
)
