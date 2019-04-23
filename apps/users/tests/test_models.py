from django.test import TestCase

from users.models import (
    Category,
    Game,
    Status
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
            status_id = Status.objects.create(
                name = 'status_id_testcase',
                notes = 'status_id_testcase_nodes'
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
        self.assertEquals(max_length, 50)

    def test_get_absolute_url(self):
        game = Game.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEquals(game.get_absolute_url(), '/users/game/1')
    
    def test_object_name_is_name_colon_category_id(self):
        game = Game.objects.get(id=1)
        expected_object_name = f'{game.name}: {game.category_id}'
        self.assertEquals(expected_object_name, str(game))