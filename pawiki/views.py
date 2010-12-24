from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from . import models, forms

def view(self, title):
	page = get_object_or_404(models.Page, title=title)
	return direct_to_template(request, 'pawiki/view.html', {'page': page})

def edit(self, title):
	try:
		page = models.Page.objects.get(title=title)
	except Page.DoesNotExist:
		page = Page(title=title)
	revision = models.PageRevision(page=Page, author=request.user)
	form = forms.PageEditForm(data=request.POST or None, instance=revision, page=page)
	if request.method == 'POST':
		if form.is_valid():
			form.save()
	return direct_to_template(request, 'pawiki/edit.html', {'form': form, 'page': page})
