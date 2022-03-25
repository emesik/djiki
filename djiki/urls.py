from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^(?P<title>[^/]+)$", views.view, name="djiki-page-view"),
    re_path(r"^(?P<title>[^/]+)/edit/$", views.edit, name="djiki-page-edit"),
    re_path(r"^(?P<title>[^/]+)/history/$", views.history, name="djiki-page-history"),
    re_path(
        r"^(?P<title>[^/]+)/history/(?P<revision_pk>[0-9]+)/$",
        views.view,
        name="djiki-page-revision",
    ),
    re_path(r"^(?P<title>[^/]+)/diff/$", views.diff, name="djiki-page-diff"),
    re_path(
        r"^(?P<title>[^/]+)/undo/(?P<revision_pk>[0-9]+)/$",
        views.undo,
        name="djiki-page-undo",
    ),
    re_path(
        r"^(?P<title>[^/]+)/revert/(?P<revision_pk>[0-9]+)/$",
        views.revert,
        name="djiki-page-revert",
    ),
    re_path(r"^image/$", views.image_new, name="djiki-image-new"),
    re_path(r"^image/(?P<name>[^/]+)$", views.image_view, name="djiki-image-view"),
    re_path(
        r"^image/(?P<name>[^/]+)/edit/$", views.image_edit, name="djiki-image-edit"
    ),
    re_path(
        r"^image/(?P<name>[^/]+)/history/$",
        views.image_history,
        name="djiki-image-history",
    ),
]
