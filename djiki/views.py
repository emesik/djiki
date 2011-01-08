from diff_match_patch import diff_match_patch
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from . import models, forms, utils

def view(request, title, revision_pk=None):
	url_title = utils.urlize_title(title)
	if title != url_title:
		return HttpResponseRedirect(reverse('djiki-page-view', kwargs={'title': url_title}))
	page_title = utils.deurlize_title(title)
	try:
		page = models.Page.objects.get(title=page_title)
	except models.Page.DoesNotExist:
		return direct_to_template(request, 'djiki/not_found.html', {'title': page_title})
	if revision_pk:
		try:
			revision = page.revisions.get(pk=revision_pk)
		except models.PageRevision.DoesNotExist:
			return HttpResponseNotFound()
		is_latest = False
	else:
		revision = page.last_revision()
		is_latest = True
	return direct_to_template(request, 'djiki/view.html',
			{'page': page, 'revision': revision, 'is_latest': is_latest})

def edit(request, title):
	if not settings.DJIKI_ALLOW_ANONYMOUS_EDITS and not request.user.is_authenticated():
		return HttpResponseForbidden()
	url_title = utils.urlize_title(title)
	if title != url_title:
		return HttpResponseRedirect(reverse('djiki-page-edit', kwargs={'title': url_title}))
	page_title = utils.deurlize_title(title)
	try:
		page = models.Page.objects.get(title=page_title)
		last_content = page.last_revision().content
	except models.Page.DoesNotExist:
		page = models.Page(title=page_title)
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

def diff(request, title):
	page = get_object_or_404(models.Page, title=title)
	try:
		from_rev = page.revisions.get(pk=request.REQUEST['from_revision_pk'])
		to_rev = page.revisions.get(pk=request.REQUEST['to_revision_pk'])
	except (KeyError, models.Page.DoesNotExist):
		return HttpResponseNotFound()
	dmp = diff_match_patch()
	diff = dmp.diff_compute(from_rev.content, to_rev.content, True, 2)
	return direct_to_template(request, 'djiki/diff.html',
			{'page': page, 'from_revision': from_rev, 'to_revision': to_rev, 'diff': diff})

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
	url_name = utils.urlize_title(name)
	if name != url_name:
		return HttpResponseRedirect(reverse('djiki-image-view', kwargs={'name': url_name}))
	image_name = utils.deurlize_title(name)
	image = get_object_or_404(models.Image, name=image_name)
	return direct_to_template(request, 'djiki/image_view.html', {'image': image})

def image_edit(request, name):
	if not settings.DJIKI_ALLOW_ANONYMOUS_EDITS and not request.user.is_authenticated():
		return HttpResponseForbidden()
	url_name = utils.urlize_title(name)
	if name != url_name:
		return HttpResponseRedirect(reverse('djiki-image-edit', kwargs={'name': url_name}))
	image_name = utils.deurlize_title(name)
	image = get_object_or_404(models.Image, name=image_name)
	revision = models.ImageRevision(image=image,
			author=request.user if request.user.is_authenticated() else None)
	form = forms.ImageUploadForm(data=request.POST or None, files=request.FILES or None,
			instance=revision, image=image)
	if request.method == 'POST':
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(
					reverse('djiki-image-view', kwargs={'name': url_name}))
	return direct_to_template(request, 'djiki/image_edit.html', {'form': form})

def image_history(request, name):
	url_name = utils.urlize_title(name)
	if name != url_name:
		return HttpResponseRedirect(reverse('djiki-image-view', kwargs={'name': url_name}))
	image_name = utils.deurlize_title(name)
	image = get_object_or_404(models.Image, name=image_name)
	history = image.revisions.order_by('-created')
	return direct_to_template(request, 'djiki/image_history.html', {'image': image, 'history': history})
