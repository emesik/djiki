from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from . import models, forms

def view(request, title):
	try:
		page = models.Page.objects.get(title=title)
	except models.Page.DoesNotExist:
		return direct_to_template(request, 'djiki/not_found.html', {'title': title})
	return direct_to_template(request, 'djiki/view.html', {'page': page})

def edit(request, title):
	try:
		page = models.Page.objects.get(title=title)
		last_content = page.last_revision().content
	except models.Page.DoesNotExist:
		page = models.Page(title=title)
		last_content = ''
	revision = models.PageRevision(page=page,
			author=request.user if request.user.is_authenticated() else None)
	form = forms.PageEditForm(
			data=request.POST or None, instance=revision, page=page,
			initial={'content': last_content})
	if request.method == 'POST':
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(
					reverse('djiki-page-view', kwargs={'title': title}))
	return direct_to_template(request, 'djiki/edit.html', {'form': form, 'page': page})

def history(request, title):
	page = get_object_or_404(models.Page, title=title)
	history = page.revisions.order_by('-created')
	return direct_to_template(request, 'djiki/history.html', {'page': page, 'history': history})
