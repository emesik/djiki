import re
from django.conf import settings

def urlize_title(title):
	if settings.DJIKI_SPACES_AS_UNDERSCORES:
		return re.sub(r'\s+', '_', title)
	return title

def deurlize_title(title):
	if settings.DJIKI_SPACES_AS_UNDERSCORES:
		return re.sub(r'[_\s]+', ' ', title)
	return title

def anchorize(txt):
	return re.compile(r'[^\w_,\.-]+', re.UNICODE).sub('_', txt).strip('_')
