"""The most basic authorization backends for Djiki.

Each class must implement the following methods:
	``can_view``, ``can_create``, ``can_edit``,
	``can_view_history``, ``can_undo_revision``,
	``can_revert_to``

These methods must accept the following arguments:
	``request`` - the current HTTP request
	``target`` - the target object (page or image)
	``revision`` - (for revision-scope methods) the revision being undone or reverted to

The methods must return a ``bool`` value.
"""

from djiki.utils import call_or_val


class UnrestrictedAccess(object):
    "Everyone is permitted to do anything."

    def can_view(self, request, target):
        return True

    def can_create(self, request, target):
        return True

    def can_edit(self, request, target):
        return True

    def can_view_history(self, request, target):
        return True


class OnlyAuthenticatedEdits(UnrestrictedAccess):
    "Only authenticated users can modify the contents."

    def can_create(self, request, target):
        return call_or_val(request.user.is_authenticated)

    def can_edit(self, request, target):
        return call_or_val(request.user.is_authenticated)


class OnlyAdminEdits(UnrestrictedAccess):
    "Only admin users can modify the contents."

    def can_create(self, request, target):
        return call_or_val(request.user.is_authenticated) and request.user.is_superuser

    def can_edit(self, request, target):
        return call_or_val(request.user.is_authenticated) and request.user.is_superuser
