import re
from django.conf import settings

def spaces_as_underscores():
        return getattr(settings, 'DJIKI_SPACES_AS_UNDERSCORES', True)

def urlize_title(title):
	if spaces_as_underscores():
		return re.sub(r'\s+', '_', title)
	return title

def deurlize_title(title):
	if spaces_as_underscores():
		return re.sub(r'[_\s]+', ' ', title)
	return title

def anchorize(txt):
	return re.compile(r'[^\w_,\.-]+', re.UNICODE).sub('_', txt).strip('_')
