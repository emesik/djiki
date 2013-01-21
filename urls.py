from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic import RedirectView

urlpatterns = patterns('',
	(r'^$', RedirectView.as_view(url=u'/wiki/Main_Page')),
	(r'^wiki/', include('djiki.urls')),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
		)
