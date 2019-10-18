from django.db import models
from users import models as usersModel
from django.utils.translation import ugettext_lazy as _
from utils.constants import *
from django.utils import timezone
import uuid
from django.conf import settings
from users.models import  CustomUser

# Create your models here.
class Category(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    name_zh = models.CharField(max_length=50, null=True, blank=True)
    name_fr = models.CharField(max_length=50, null=True, blank=True)
    # category_type = models.SmallIntegerField(choices=CATEGORY_TYPES, default=0)
    parent_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.CharField(max_length=500)

    class Meta:
        verbose_name_plural = _('Game Category')


    def __str__(self):
        return '{0}'.format(self.name)


class GameAttribute(models.Model):

    name = models.CharField(max_length=50)
    created_time = models.DateTimeField(
        _('Created Time'),
        auto_now_add=True,
        editable=False,
    )


class Game(models.Model):
    name = models.CharField(max_length=50)
    name_zh = models.CharField(max_length=50, null=True, blank=True)
    name_fr = models.CharField(max_length=50, null=True, blank=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    start_time = models.DateTimeField('Start Time', null=True, blank=True)
    end_time = models.DateTimeField('End Time', null=True, blank=True)
    opponent1 = models.CharField(max_length=200, null=True, blank=True)
    opponent2 = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=200)
    description_zh = models.CharField(max_length=200, null=True, blank=True)
    description_fr = models.CharField(max_length=200, null=True, blank=True)
    status_id = models.ForeignKey('users.Status', related_name="game_status", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='game_image', blank=True)
    #game_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #category = models.CharField(max_length=20)

    imageURL = models.CharField(max_length=200, null=True, blank=True)
    attribute = models.CharField(max_length=500, null=True, blank=True)
    provider = models.SmallIntegerField(choices=GAME_PROVIDERS, default=0)
    popularity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    jackpot_size = models.IntegerField(null=True, blank=True)

    created_time = models.DateTimeField(
        _('Created Time'),
        auto_now_add=True,
        editable=False,
        null=True
    )

    modifited_time = models.DateTimeField(
        _('Modifited Time'),
        auto_now_add=True,
        editable=False,
        null=True
    )

    
    class Meta:
        verbose_name_plural = _('Game')


    def __str__(self):
        return '{0}: {1}'.format(self.name, self.category_id)

    def get_absolute_url(self):
        """
        Returns the url to access a particular game instance.
        """
        return reverse('game-detail', args=[str(self.id)])

# class GameWithAttribute(models.Model):

#     game = models.ForeignKey(Game, on_delete=models.CASCADE,  related_name="game")
#     attribute = models.ForeignKey(GameAttribute, on_delete=models.CASCADE, related_name="attribute")


# class GameFilterMetaData(models.Model):
#     filter_type = models.SmallIntegerField(choices=GAME_ATTRIBUTES)
#     name = models.CharField(max_length=50)
#     name_zh = models.CharField(max_length=50, null=True, blank=True)
#     name_fr = models.CharField(max_length=50, null=True, blank=True)

#     def __str__(self):
#         return '{0}: {1}'.format(self.name, self.get_filter_type_display())


# class GameSubcategory(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
#     name = models.CharField(max_length=50)
#     name_zh = models.CharField(max_length=50, null=True, blank=True)
#     name_fr = models.CharField(max_length=50, null=True, blank=True)

#     def __str__(self):
#         return '{0}: {1}'.format(self.name, self.get_category_display())


# create a ticket per user per session to ensure valid request
class EATicket(models.Model):
    
    ticket = models.UUIDField()
    created_time = models.DateTimeField(default=timezone.now)

class GDGetUserBalance(models.Model):
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE) #same as user model's username
    StatusCode = models.SmallIntegerField(choices=STATE_CHOICES, default=3)
    UserBalance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return '{0}:{1}'.format(self.username, self.UserBalance)
    