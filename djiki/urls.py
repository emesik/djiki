from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
	url(r'^(?P<title>[^/]+)$', views.view, name='djiki-page-view'),
	url(r'^(?P<title>[^/]+)/edit/$', views.edit, name='djiki-page-edit'),
	url(r'^(?P<title>[^/]+)/history/$', views.history, name='djiki-page-history'),
	url(r'^image/$', views.image_new, name='djiki-image-new'),
	url(r'^image/(?P<name>[^/]+)$', views.image_view, name='djiki-image-view'),
	url(r'^image/(?P<name>[^/]+)/serve/$', views.image_serve, name='djiki-image-serve'), # XXX
	url(r'^image/(?P<name>[^/]+)/edit/$', views.image_edit, name='djiki-image-edit'),
	url(r'^image/(?P<name>[^/]+)/history/$', views.image_history, name='djiki-image-history'),
	)
