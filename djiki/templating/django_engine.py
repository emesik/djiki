from django.template import RequestContext, loader
from django.template.response import TemplateResponse

def render_to_response(request, template_name, context):
	return TemplateResponse(request, template_name, context)

def render_to_string(template_name, context, request=None):
	template = loader.get_template(template_name)
	if request:
		context = RequestContext(request, context)
	return template.render(context)
