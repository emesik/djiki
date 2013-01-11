import importlib, re
from django.conf import settings

def get_parser():
	# FIXME: Django should have a function to do it better
	ppath = getattr(settings, 'DJIKI_PARSER', 'djiki.parsers.wikicreole')
	try:
		parser = importlib.import_module(ppath)
	except ImportError:
		mpath, cname = ppath.rsplit('.', 1)
		module = importlib.import_module(mpath)
		klass = getattr(module, cname)
		parser = klass()
	return parser

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
