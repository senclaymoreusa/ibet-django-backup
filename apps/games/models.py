from django.db import models
import uuid
from users import models as usersModel
from django.utils.translation import ugettext_lazy as _
from utils.constants import *


# Create your models here.
class Category(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    name_zh = models.CharField(max_length=50, null=True, blank=True)
    name_fr = models.CharField(max_length=50, null=True, blank=True)
    parent_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = _('Game Category')


    def __str__(self):
        return '{0}, parent: {1}'.format(self.name, self.parent_id)


class GameAttribute(models.Model):

    name = models.CharField(max_length=50, null=True, blank=True)
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
    status_id = models.ForeignKey(usersModel.Status, related_name="game_status", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='game_image', blank=True)
    #game_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #category = models.CharField(max_length=20)

    imageURL = models.CharField(max_length=200, null=True, blank=True)
    attribute = models.ForeignKey(GameAttribute, on_delete=models.CASCADE)
    provider = models.SmallIntegerField(choices=GAME_PROVIDERS, default=0)
    popularity = models.DecimalField(max_digits=10, decimal_places=2)

    
    class Meta:
        verbose_name_plural = _('Game')


    def __str__(self):
        return '{0}: {1}'.format(self.name, self.category_id)

    def get_absolute_url(self):
        """
        Returns the url to access a particular game instance.
        """
        return reverse('game-detail', args=[str(self.id)])
class GameWithAttribute(models.Model):

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    attribute = models.ForeignKey(GameAttribute, on_delete=models.CASCADE)
