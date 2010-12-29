from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
	url(r'(?P<title>[^/]+)$', views.view, name='djiki-page-view'),
	url(r'(?P<title>[^/]+)/edit/$', views.edit, name='djiki-page-edit'),
	url(r'(?P<title>[^/]+)/history/$', views.history, name='djiki-page-history'),
	)
