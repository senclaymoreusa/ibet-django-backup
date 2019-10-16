import requests
from django.urls import reverse


def get_bonus():
    url = 'http://localhost:8000/bonus/api/bonuses/'
    r = requests.get(url)
    bonus = r.json()
    print("bonus")
    print(bonus)
    print(reverse('bonus_search'))
    return bonus


get_bonus()