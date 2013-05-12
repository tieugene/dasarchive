from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
	url(r'^$',	views.index, name='index'),
	url(r'^listdir/(?P<path>.*)$',	views.listdir, name='listdir'),
	url(r'^edit/(?P<path>.*)$',	views.edit, name='edit'),
)
