from django.db.models import Max
from django.template.response import TemplateResponse

from .. import models


def latest_changes(request, limit=50):
    latest = models.Page.objects.annotate(
        latest_change=Max("revisions__created")
    ).order_by("-latest_change")[:limit]
    return TemplateResponse(request, "djiki/latest_changes.html", {"latest": latest})
