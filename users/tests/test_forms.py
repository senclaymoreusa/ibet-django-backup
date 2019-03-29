from django.test import TestCase
from django import forms

from users.models import (
    CustomUser
)
from users.forms import (
    UserCreationForm
)

# Create your tests here.

# Test User Creation Form
class UserCreationFormTest(TestCase):

    def setUp(self):
        self.user_creation = CustomUser.objects.create(username = 'wluuuu', email = 'wluuuu@test.com')

    def test_userCreationForm_valid(self):
        form = UserCreationForm(data={
            'username': 'wluuuu01',
            'email': 'wluuuu01@test.com',
            'password1': 'hellotest1',
            'password2': 'hellotest1'
        },instance = CustomUser.objects.create(username = 'wludksuuu', email = 'wluudsuu@test.com'))
        self.assertTrue(form.is_valid())

    def test_password1_field_label(self):
        form = UserCreationForm()
        self.assertTrue(form.fields['password1'].label == 'Password')

    def test_password2_matches_passwords1(self):
        form = UserCreationForm(data={
            'username': 'wluuuu02',
            'email': 'wluuuu02@test.com',
            'password1': 'hellotest1',
            'password2': 'hellotestdiff'
        },instance = CustomUser.objects.create(username = 'wluddkfksuuu', email = 'wluufsdndsuu@test.com'))
        self.assertFalse(form.is_valid())