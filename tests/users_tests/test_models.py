import datetime

from django.test import TestCase

from users.models import (
    Status
)

from games.models import (
    Category,
    Game,
    GameProvider
)
# Create your tests here.

# Test Game Model
class GameModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        test_game = Game.objects.create(
            name = "TestSport",
            category_id = Category.objects.create(
                name = 'category_id_testcase',
                notes = 'category_id_testcase_notes'
            ),
            provider = GameProvider.objects.create(
                provider_name='Betsoft',
                type=1
            )
        )
        test_game.save()
    
    def test_game_create_success(self):
        game_querySet = Game.objects.all()
        self.assertTrue(Game.objects.filter(name="TestSport").exists())

    def test_data_of_name_label(self):
        game = Game.objects.get(id=1)
        field_label = game._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_data_of_end_time_label(self):
        game = Game.objects.get(id=1)
        field_label = game._meta.get_field('end_time').verbose_name
        self.assertEquals(field_label, 'End Time')

    def test_name_max_length(self):
        game = Game.objects.get(id=1)
        max_length = game._meta.get_field('name').max_length
        self.assertEquals(max_length, 100)

    # def test_get_absolute_url(self):
    #     game = Game.objects.get(id=1)
    #     # This will also fail if the urlconf is not defined.
    #     self.assertEquals(game.get_absolute_url(), '/users/game/1')
    
    # def test_object_name_is_name_colon_category_id(self):
    #     game = Game.objects.get(id=1)
    #     print(game)
    #     expected_object_name = f'{game.name}: {game.category_id}'
    #     self.assertEquals(expected_object_name, str(game))
        
    def test_if_category_null(self):
        game = Game.objects.get(id=1)
        category_id = game._meta.get_field('category_id')
        self.assertNotEqual(category_id, None)

    def test_description_max_length(self):
        game = Game.objects.get(id=1)
        max_length = game._meta.get_field('description').max_length
        self.assertEquals(max_length, 200)