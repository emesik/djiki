from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^$', 'django.views.generic.simple.redirect_to', {'url': u'/wiki/Main Page'}),
	(r'^wiki/', include('djiki.urls')),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
		)
