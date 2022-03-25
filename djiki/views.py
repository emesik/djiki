from diff_match_patch import diff_match_patch
from django.contrib import messages
from django.core.exceptions import PermissionDenied

try:
    from django.urls import reverse  # django >= 2.0
except ImportError:
    from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

try:
    from urllib.parse import urlencode, quote  # py3
except ImportError:
    from urllib import urlencode, quote
from . import models, forms, utils

_templating = utils.get_templating_backend()


def view(request, title, revision_pk=None):
    url_title = utils.urlize_title(title)
    if title != url_title:
        if revision_pk:
            return HttpResponseRedirect(
                reverse(
                    "djiki-page-revision",
                    kwargs={"title": url_title, "revision_pk": revision_pk},
                )
            )
        return HttpResponseRedirect(
            reverse("djiki-page-view", kwargs={"title": url_title})
        )
    page_title = utils.deurlize_title(title)
    auth = utils.get_auth_backend()
    try:
        page = models.Page.objects.get(title=page_title, language=utils.get_lang())
    except models.Page.DoesNotExist:
        html = _templating.render_to_string(
            "djiki/not_found.html", {"title": page_title}, request=request
        )
        return HttpResponseNotFound(html)
    if not auth.can_view(request, page):
        raise PermissionDenied
    if revision_pk:
        if not auth.can_view_history(request, page):
            raise PermissionDenied
        try:
            revision = page.revisions.get(pk=revision_pk)
        except models.PageRevision.DoesNotExist:
            return HttpResponseNotFound()
        messages.info(
            request,
            mark_safe(
                _(
                    "The version you are viewing is not the latest one, "
                    "but represents an older revision of this page, which may have been "
                    "significantly modified. If it is not what you intended to view, "
                    '<a href="%(url)s">proceed to the latest version</a>.'
                )
                % {"url": reverse("djiki-page-view", kwargs={"title": url_title})}
            ),
        )
    else:
        revision = page.last_revision()
    if request.POST.get("raw", request.GET.get("raw", "")):
        response = HttpResponse(mimetype="text/plain")
        response["Content-Disposition"] = "attachment; filename=%s.txt" % quote(
            title.encode("utf-8")
        )
        response.write(revision.content)
        return response
    return _templating.render(
        request, "djiki/view.html", {"page": page, "revision": revision}
    )


def _prepare_preview(request, form):
    messages.info(
        request,
        mark_safe(
            _(
                "The content you see on this page is shown only as "
                "a preview. <strong>No changes have been saved yet.</strong> Please "
                "review the modifications and use the <em>Save</em> button to store "
                "them permanently."
            )
        ),
    )
    return form.cleaned_data.get("content", form.data["content"])


def edit(request, title):
    url_title = utils.urlize_title(title)
    if title != url_title:
        return HttpResponseRedirect(
            reverse("djiki-page-edit", kwargs={"title": url_title})
        )
    page_title = utils.deurlize_title(title)
    # We carry the language information within the form. This is needed to avoid mess in sites
    # which store language info within a session (where user can switch it within a separate
    # browser window).
    # To get out of the chicken and egg problem, we read the lang straight from the request data,
    # if available.
    language = request.POST.get("language", utils.get_lang())
    auth = utils.get_auth_backend()
    try:
        page = models.Page.objects.get(title=page_title, language=language)
        last_content = page.last_revision().content
        if not auth.can_edit(request, page):
            raise PermissionDenied
    except models.Page.DoesNotExist:
        page = models.Page(title=page_title, language=language)
        last_content = ""
        if not auth.can_create(request, page):
            raise PermissionDenied
    revision = models.PageRevision(
        page=page,
        author=request.user
        if utils.call_or_val(request.user.is_authenticated)
        else None,
    )
    form = forms.PageEditForm(
        data=request.POST or None,
        instance=revision,
        page=page,
        initial={"content": last_content},
    )
    preview_content = None
    if form.is_valid():
        if request.POST.get("action") == "preview":
            preview_content = _prepare_preview(request, form)
        else:
            form.save()
            return HttpResponseRedirect(
                reverse("djiki-page-view", kwargs={"title": url_title})
            )
    return _templating.render(
        request,
        "djiki/edit.html",
        {"form": form, "page": page, "preview_content": preview_content},
    )


def history(request, title):
    url_title = utils.urlize_title(title)
    if title != url_title:
        return HttpResponseRedirect(
            reverse("djiki-page-history", kwargs={"title": url_title})
        )
    page_title = utils.deurlize_title(title)
    page = get_object_or_404(models.Page, title=page_title, language=utils.get_lang())
    auth = utils.get_auth_backend()
    if not auth.can_view_history(request, page):
        raise PermissionDenied
    history = page.revisions.order_by("-created")
    return _templating.render(
        request, "djiki/history.html", {"page": page, "history": history}
    )


def diff(request, title):
    url_title = utils.urlize_title(title)
    if title != url_title:
        return HttpResponseNotFound()
    page_title = utils.deurlize_title(title)
    page = get_object_or_404(models.Page, title=page_title, language=utils.get_lang())
    auth = utils.get_auth_backend()
    if not auth.can_view_history(request, page):
        raise PermissionDenied
    try:
        from_rev = page.revisions.get(pk=request.REQUEST["from_revision_pk"])
        to_rev = page.revisions.get(pk=request.REQUEST["to_revision_pk"])
    except (KeyError, models.Page.DoesNotExist):
        return HttpResponseNotFound()
    dmp = diff_match_patch()
    diff = dmp.diff_compute(from_rev.content, to_rev.content, True, 2)
    return _templating.render(
        request,
        "djiki/diff.html",
        {"page": page, "from_revision": from_rev, "to_revision": to_rev, "diff": diff},
    )


def revert(request, title, revision_pk):
    url_title = utils.urlize_title(title)
    if title != url_title:
        return HttpResponseRedirect(
            reverse(
                "djiki-page-revert",
                kwargs={"title": url_title, "revision_pk": revision_pk},
            )
        )
    page_title = utils.deurlize_title(title)
    language = request.POST.get("language", utils.get_lang())  # see comment in edit()
    page = get_object_or_404(models.Page, title=page_title, language=language)
    auth = utils.get_auth_backend()
    if not auth.can_edit(request, page):
        raise PermissionDenied
    src_revision = get_object_or_404(models.PageRevision, page=page, pk=revision_pk)
    new_revision = models.PageRevision(
        page=page,
        author=request.user
        if utils.call_or_val(request.user.is_authenticated)
        else None,
    )
    preview_content = None
    if request.method == "POST":
        form = forms.PageEditForm(
            data=request.POST or None, instance=new_revision, page=page
        )
        if form.is_valid():
            if request.POST.get("action") == "preview":
                preview_content = _prepare_preview(request, form)
            else:
                form.save()
                return HttpResponseRedirect(
                    reverse("djiki-page-view", kwargs={"title": url_title})
                )
    else:
        if src_revision.author:
            description = _("Reverted to revision of %(time)s by %(author)s.") % {
                "time": src_revision.created,
                "author": getattr(
                    src_revision.author, src_revision.author.USERNAME_FIELD
                ),
            }
        else:
            description = _("Reverted to anonymous revision of %(time)s.") % {
                "time": src_revision.created
            }
        form = forms.PageEditForm(
            data=request.POST or None,
            instance=new_revision,
            page=page,
            initial={"content": src_revision.content, "description": description},
        )
    return _templating.render(
        request,
        "djiki/edit.html",
        {
            "page": page,
            "form": form,
            "src_revision": src_revision,
            "preview_content": preview_content,
        },
    )


def undo(request, title, revision_pk):
    url_title = utils.urlize_title(title)
    if title != url_title:
        return HttpResponseRedirect(
            reverse(
                "djiki-page-undo",
                kwargs={"title": url_title, "revision_pk": revision_pk},
            )
        )
    page_title = utils.deurlize_title(title)
    language = request.POST.get("language", utils.get_lang())  # see comment in edit()
    page = get_object_or_404(models.Page, title=page_title, language=language)
    auth = utils.get_auth_backend()
    if not auth.can_edit(request, page):
        raise PermissionDenied
    src_revision = get_object_or_404(models.PageRevision, page=page, pk=revision_pk)
    new_revision = models.PageRevision(
        page=page,
        author=request.user
        if utils.call_or_val(request.user.is_authenticated)
        else None,
    )
    preview_content = None
    if request.method == "POST":
        form = forms.PageEditForm(
            data=request.POST or None, instance=new_revision, page=page
        )
        if form.is_valid():
            if request.POST.get("action") == "preview":
                preview_content = _prepare_preview(request, form)
            else:
                form.save()
                return HttpResponseRedirect(
                    reverse("djiki-page-view", kwargs={"title": url_title})
                )
    else:
        if src_revision.author:
            description = _("Undid revision of %(time)s by %(author)s.") % {
                "time": src_revision.created,
                "author": getattr(
                    src_revision.author, src_revision.author.USERNAME_FIELD
                ),
            }
        else:
            description = _("Undid anonymous revision of %(time)s.") % {
                "time": src_revision.created
            }
        try:
            prev_revision = models.PageRevision.objects.filter(
                page=page, created__lt=src_revision.created
            ).order_by("-created")[0]
            prev_content = prev_revision.content
        except IndexError:
            prev_content = ""
        dmp = diff_match_patch()
        rdiff = dmp.patch_make(src_revision.content, prev_content)
        content, results = dmp.patch_apply(rdiff, page.last_revision().content)
        if False in results:
            messages.warning(
                request,
                _(
                    "It was impossible to automatically undo the change "
                    "you have selected. Perhaps the page has been modified too much in the "
                    "meantime. Review the following content comparison, which represents the "
                    "change you tried to undo, and apply the changes manually to the latest "
                    "revision."
                ),
            )
            urldata = {"to_revision_pk": src_revision.pk}
            if prev_revision:
                urldata["from_revision_pk"] = prev_revision.pk
            return HttpResponseRedirect(
                "%s?%s"
                % (
                    reverse("djiki-page-diff", kwargs={"title": url_title}),
                    urlencode(urldata),
                )
            )
        form = forms.PageEditForm(
            data=request.POST or None,
            page=page,
            initial={"content": content, "description": description},
        )
    return _templating.render(
        request,
        "djiki/edit.html",
        {"page": page, "form": form, "preview_content": preview_content},
    )


def image_new(request):
    auth = utils.get_auth_backend()
    if not auth.can_create(request, models.Image()):
        raise PermissionDenied
    form = forms.NewImageUploadForm(
        data=request.POST or None, files=request.FILES or None
    )
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse("djiki-image-view", kwargs={"name": form.instance.image.name})
            )
    return _templating.render(request, "djiki/image_edit.html", {"form": form})


def image_view(request, name):
    url_name = utils.urlize_title(name)
    if name != url_name:
        return HttpResponseRedirect(
            reverse("djiki-image-view", kwargs={"name": url_name})
        )
    image_name = utils.deurlize_title(name)
    image = get_object_or_404(models.Image, name=image_name)
    auth = utils.get_auth_backend()
    if not auth.can_view(request, image):
        raise PermissionDenied
    return _templating.render(request, "djiki/image_view.html", {"image": image})


def image_edit(request, name):
    url_name = utils.urlize_title(name)
    if name != url_name:
        return HttpResponseRedirect(
            reverse("djiki-image-edit", kwargs={"name": url_name})
        )
    image_name = utils.deurlize_title(name)
    image = get_object_or_404(models.Image, name=image_name)
    auth = utils.get_auth_backend()
    if not auth.can_edit(request, image):
        raise PermissionDenied
    revision = models.ImageRevision(
        image=image,
        author=request.user
        if utils.call_or_val(request.user.is_authenticated)
        else None,
    )
    form = forms.ImageUploadForm(
        data=request.POST or None,
        files=request.FILES or None,
        instance=revision,
        image=image,
    )
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse("djiki-image-view", kwargs={"name": url_name})
            )
    return _templating.render(request, "djiki/image_edit.html", {"form": form})


def image_history(request, name):
    url_name = utils.urlize_title(name)
    if name != url_name:
        return HttpResponseRedirect(
            reverse("djiki-image-view", kwargs={"name": url_name})
        )
    image_name = utils.deurlize_title(name)
    image = get_object_or_404(models.Image, name=image_name)
    auth = utils.get_auth_backend()
    if not auth.can_view_history(request, image):
        raise PermissionDenied
    history = image.revisions.order_by("-created")
    return _templating.render(
        request, "djiki/image_history.html", {"image": image, "history": history}
    )
