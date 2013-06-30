import re
import warnings
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

def _setting_to_instance(setting):
	if isinstance(setting, basestring):
		try:
			parser = import_module(setting)
		except ImportError:
			try:
				mpath, cname = setting.rsplit('.', 1)
			except ValueError:
				raise ImproperlyConfigured('"%s" does not describe a module, '
						'object or class' % setting)
			module = import_module(mpath)
			klass = getattr(module, cname)
			parser = klass()
		return parser
	if isinstance(setting, type):
		return setting()
	return setting

def get_parser():
	setting = getattr(settings, 'DJIKI_PARSER', 'djiki.parsers.wikicreole')
	return _setting_to_instance(setting)

def get_auth_backend():
	if hasattr(settings, 'DJIKI_ALLOW_ANONYMOUS_EDITS'):
		warnings.warn('The DJIKI_ALLOW_ANONYMOUS_EDITS is no longer used. '
				'Set DJIKI_AUTHORIZATION_BACKEND instead', DeprecationWarning)
	setting = getattr(settings, 'DJIKI_AUTHORIZATION_BACKEND',
			'djiki.auth.base.UnrestrictedAccess')
	return _setting_to_instance(setting)

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

def get_templating_backend():
	setting = getattr(settings, 'DJIKI_TEMPLATING_BACKEND', 'djiki.templating.django_engine')
	return _setting_to_instance(setting)
