from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from . import models, forms, parser

def view(request, title):
	try:
		page = models.Page.objects.get(title=title)
	except models.Page.DoesNotExist:
		return direct_to_template(request, 'djiki/not_found.html', {'title': title})
	if not page.rendered_content:
		page.rendered_content = parser.render(page.last_revision().content)
	return direct_to_template(request, 'djiki/view.html', {'page': page})

def edit(request, title):
	if not settings.DJIKI_ALLOW_ANONYMOUS_EDITS and not request.user.is_authenticated():
		return HttpResponseForbidden()
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

def image_new(request):
	if not settings.DJIKI_ALLOW_ANONYMOUS_EDITS and not request.user.is_authenticated():
		return HttpResponseForbidden()
	form = forms.NewImageUploadForm(data=request.POST or None, files=request.FILES or None)
	if request.method == 'POST':
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(
					reverse('djiki-image-view', kwargs={'name': form.instance.image.name}))
	return direct_to_template(request, 'djiki/image_edit.html', {'form': form})

def image_view(request, name):
	image = get_object_or_404(models.Image, name=name)
	return direct_to_template(request, 'djiki/image_view.html', {'image': image})

def image_edit(request, name):
	if not settings.DJIKI_ALLOW_ANONYMOUS_EDITS and not request.user.is_authenticated():
		return HttpResponseForbidden()
	image = get_object_or_404(models.Image, name=name)
	revision = models.ImageRevision(image=image,
			author=request.user if request.user.is_authenticated() else None)
	form = forms.ImageUploadForm(data=request.POST or None, files=request.FILES or None,
			instance=revision, image=image)
	if request.method == 'POST':
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(
					reverse('djiki-image-view', kwargs={'name': form.instance.image.name}))
	return direct_to_template(request, 'djiki/image_edit.html', {'form': form})

def image_history(request, name):
	image = get_object_or_404(models.Image, name=name)
	history = image.revisions.order_by('-created')
	return direct_to_template(request, 'djiki/image_history.html', {'image': image, 'history': history})
