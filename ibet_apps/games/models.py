from django.db import models
from users import models as usersModel
from django.utils.translation import ugettext_lazy as _
from utils.constants import *
from django.utils import timezone
import uuid

# Create your models here.
class GameProvider(models.Model):
    provider_name = models.CharField(max_length=100)
    type = models.SmallIntegerField(choices=GAME_TYPE_CHOICES)
    market = models.CharField(max_length=50)
    def __str__(self):
        return self.provider_name

class Category(models.Model):
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


class GameProviderWithCategory(models.Model):

    provider = models.ForeignKey(GameProvider, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

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

    # game_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # category = models.CharField(max_length=20, null=True, blank=True, default="Slots")

    gameURL = models.CharField(max_length=200, null=True, blank=True)
    imageURL = models.CharField(max_length=200, null=True, blank=True)
    attribute = models.CharField(max_length=500, null=True, blank=True)
    provider = models.ForeignKey(GameProvider, on_delete=models.CASCADE)
    popularity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    jackpot_size = models.IntegerField(null=True, blank=True)

    created_time = models.DateTimeField(
        _('Created Time'),
        auto_now_add=True,
        editable=False,
        null=True
    )

    modifited_time = models.DateTimeField(
        _('Modified Time'),
        auto_now_add=True,
        editable=False,
        null=True
    )

    class Meta:
        verbose_name_plural = _('Game')

    def __str__(self):
        return 'Game: {0},\nCategory: {1}\nProvider: {2}'.format(self.name, self.category_id, self.provider)

# game bet history model
class GameBet(models.Model):
    SPREAD = 'SPREAD'
    MONEYLINE = 'LINE'
    TOTAL = 'OU'
    BET_TYPES_CHOICES = [
        (SPREAD, 'Spread'),
        (MONEYLINE, 'Moneyline'),
        (TOTAL, 'Total O/U'),
    ]
    provider = models.ForeignKey(GameProvider, on_delete=models.CASCADE) # sportsbook/game provider
    category = models.ForeignKey('Category', on_delete=models.CASCADE) # category within sportsbook/game provider (e.g basketball, soccer, blackjack)
    game_name = models.CharField(max_length=200, blank=True, null=True) # subset of category, (e.g within basketball, there's NBA, FIBA, euroleague, within soccer there's euroleague, premier league, etc.) 
    # expect game_name to be mostly used for sportsbook, as it would be the name of the bet itself (juventus vs. psg, lakers vs. warriors)

    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount_wagered = models.DecimalField(max_digits=12, decimal_places=2) # max digits at 12, assuming no bet is greater than 9,999,999,999.99 = (10 billion - .01)
    amount_won = models.DecimalField(max_digits=12, decimal_places=2) # if amount_won = 0, outcome is also 0 (false)
    outcome = models.BooleanField() # true = win, false = lost
    odds = models.IntegerField() # payout odds (in american odds), e.g. +500, -110, etc.
    bet_type = models.CharField(max_length=6, choices=BET_TYPES_CHOICES, null=True, blank=True)
    line = models.CharField(max_length=50, null=True, blank=True) # examples: if bet_type=spread: <+/-><point difference> | bet_type=moneyline: name of team | bet_type=total: <over/under> 200

    currency = models.SmallIntegerField(choices=CURRENCY_CHOICES, default=0, verbose_name=_('Currency'))
    market = models.SmallIntegerField(choices=MARKET_CHOICES)
    ref_no = models.CharField(max_length=100, null=True, blank=True)
    bet_time = models.DateTimeField(
        _('Time Bet was Placed'),
        auto_now_add=True,
        editable=False,
    )

    resolved_time = models.DateTimeField(null=True, blank=True)



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