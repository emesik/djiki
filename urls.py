from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^$', 'django.views.generic.simple.redirect_to', {'url': u'/Main Page'}),
	(r'', include('djiki.urls')),
)
