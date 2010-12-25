from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
	url(r'(?P<title>[^/]+)$', views.view, name='pawiki-page-view'),
	url(r'(?P<title>[^/]+)/edit/$', views.edit, name='pawiki-page-edit'),
	url(r'(?P<title>[^/]+)/history/$', views.history, name='pawiki-page-history'),
	)
