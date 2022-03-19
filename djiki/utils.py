from importlib import import_module
import re
import six
import warnings
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import get_language


def _setting_to_instance(setting):
    if isinstance(setting, six.string_types):
        try:
            parser = import_module(setting)
        except ImportError:
            try:
                mpath, cname = setting.rsplit(".", 1)
            except ValueError:
                raise ImproperlyConfigured(
                    '"%s" does not describe a module, ' "object or class" % setting
                )
            module = import_module(mpath)
            klass = getattr(module, cname)
            parser = klass() if isinstance(klass, type) else klass
        return parser
    if isinstance(setting, type):
        return setting()
    return setting


def get_parser():
    setting = getattr(settings, "DJIKI_PARSER", "djiki.parsers.wikicreole")
    return _setting_to_instance(setting)


def get_auth_backend():
    if hasattr(settings, "DJIKI_ALLOW_ANONYMOUS_EDITS"):
        warnings.warn(
            "The DJIKI_ALLOW_ANONYMOUS_EDITS is no longer used. "
            "Set DJIKI_AUTHORIZATION_BACKEND instead",
            DeprecationWarning,
        )
    setting = getattr(
        settings, "DJIKI_AUTHORIZATION_BACKEND", "djiki.auth.base.UnrestrictedAccess"
    )
    return _setting_to_instance(setting)


def spaces_as_underscores():
    return getattr(settings, "DJIKI_SPACES_AS_UNDERSCORES", True)


def urlize_title(title):
    if spaces_as_underscores():
        return re.sub(r"\s+", "_", title)
    return title


def deurlize_title(title):
    if spaces_as_underscores():
        return re.sub(r"[_\s]+", " ", title)
    return title


def anchorize(txt):
    return re.compile(r"[^\w_,\.-]+", re.UNICODE).sub("_", txt).strip("_")


def get_templating_backend():
    setting = getattr(
        settings, "DJIKI_TEMPLATING_BACKEND", "djiki.templating.django_engine"
    )
    return _setting_to_instance(setting)


def get_lang():
    if getattr(settings, "DJIKI_I18N", getattr(settings, "USE_I18N", False)):
        return get_language()
    return getattr(settings, "LANGUAGE_CODE", "")


def get_images_storage():
    custom_storage = getattr(settings, "DJIKI_IMAGES_STORAGE", None)
    if custom_storage:
        return _setting_to_instance(custom_storage)
    return settings.DEFAULT_FILE_STORAGE


def call_or_val(v):
    return v() if callable(v) else v
