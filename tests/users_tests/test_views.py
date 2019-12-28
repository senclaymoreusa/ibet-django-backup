from django.test import TestCase, Client
from django.urls import reverse
from django.http import HttpResponse
from uuid import UUID

from games.models import (
    Category,
    Game,
    GameProvider
)
import json, uuid


class ViewsTest(TestCase):
    @classmethod
    def setUpTestData(self):
        number_of_game = 12
        category = Category.objects.create(name = 'Games', notes = 'category_id_testcase_notes')
        category_child = Category.objects.create(name = 'child', notes = 'category_id_testcase_notes', parent_id=category)
        for game_id in range(number_of_game):
            test_game = Game.objects.create(
                name = "TestSport",
                category_id = category,
                provider = GameProvider.objects.create(
                    provider_name = 'Betsoft',
                    type = 0
                )
            )
            test_game.save()

    def setUp(self):
        self.client = Client()
    
    # Test GameAPIListView
    def test_game_list_view_url(self):
        response = self.client.get('/games/api/games/?q=')
        self.assertEqual(response.status_code, 200)

    # def test_view_url_accessible_by_name(self):
    #     response = self.client.get(reverse('api_games') + '?term=')
    #     self.assertEquals(response.status_code, 200)
    
    def test_lists_all_games(self):
        # Get all 12 items
        response = self.client.get('/games/api/games/?q=TestSport')
        self.assertEqual(response.status_code, 200)
        # Game list doesn't have the paginate feature now
        # self.assertTrue('is_paginated' in response.context)
        # self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(json.loads(response.content)) == 12)

    def test_view_url_accessible_by_exact_search(self):
        response = self.client.get('/games/api/games/?q=TestSport')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(len(json.loads(response.content)) == 12)

    def test_view_url_accessible_by_search(self):
        response = self.client.get('/games/api/games/?q=Test')
        self.assertEquals(response.status_code, 200)
