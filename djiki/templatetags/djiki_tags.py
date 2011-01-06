from django import template
from django.utils.safestring import mark_safe
from .. import parser

register = template.Library()

@register.filter
def djiki_markup(txt):
	return mark_safe(parser.render(txt))
