from django.db import models
from django.utils.translation import ugettext_lazy as _
from utils.constants import *
from users.models import CustomUser

# Create your models here.
# permission code data will be hardcode in the codebase.

# user group entity model
class UserGroup(models.Model):

    name = models.CharField(_('name'), max_length=50)
    description = models.CharField(_('Description'), max_length=200, blank=True, null=True)
    groupType = models.SmallIntegerField(_('Group Type'), blank=True, null=True, choices=GROUP_TYPE)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    created_time = models.DateTimeField(
        _('Created Time'),
        auto_now_add=True,
        editable=False,
    )
    time_used = models.IntegerField(default=0)
    approvals = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    product = models.IntegerField(blank=True, null=True)
    active_from = models.DateField('Active From', blank=True, null=True)
    active_to = models.DateField('Register From', blank=True, null=True)
    register_from = models.DateField('Register From', blank=True, null=True)
    register_to = models.DateField('Register From', blank=True, null=True)

    
# many to many relation for permission and user group
class PermissionGroup(models.Model):
    
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, verbose_name=_('User Group'))
    permission_code = models.CharField(_('Permission Code'), max_length=50)


# many to many relation for user and user group
class UserToUserGroup(models.Model):

    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, verbose_name=_('User Group'))
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('Custom User'))


# many to many relation for user and standalone permission
class UserPermission(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('Custom User'))
    permission_code = models.CharField(_('Permission Code'), max_length=50)
    