from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse #Used to generate urls by reversing the URL patterns
from django.core.validators import RegexValidator
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
import uuid
from datetime import date
from django.contrib.auth.models import User


USERNAME_REGEX = '^[a-zA-Z0-9.+-]*$'

class MyUserManager(BaseUserManager):
	def create_user(self, username, email, password=None):
		if not email:
			raise ValueError('Users must have an email address')

		user = self.model(
					username = username,
					email = self.normalize_email(email)
				)
		user.set_password(password)
		user.save(using=self._db)
		return user
		# user.password = password # bad - do not do this

	def create_superuser(self, username, email, password=None):
		user = self.create_user(
				username, email, password=password
			)
		user.is_admin = True
		user.is_staff = True
		user.save(using=self._db)
		return user


class CustomUser(AbstractBaseUser):
    # add additional fields in here
    username = models.CharField(
					max_length=300,
					validators = [
						RegexValidator(regex = USERNAME_REGEX,
										message='Username must be alphanumeric or contain numbers',
										code='invalid_username'
							)],
					unique=True
				)
    email = models.EmailField(
			max_length=255,
			unique=True,
			verbose_name='email address'
		)
    
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    block = models.BooleanField(default=False)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    date_of_birth = models.CharField(max_length=100)
    street_address_1 = models.CharField(max_length=100, blank=True)
    street_address_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email

    def get_short_name(self):
	    # The user is identified by their email address
	    return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
		# Simplest possible answer: Yes, always
        return True

    def has_perms(self, perm_list, obj=None):
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


class Status(models.Model):
    status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    notes = models.CharField(max_length=200)
    def __str__(self):
        return '{0}'.format(self.name)


class Category(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    name_zh = models.CharField(max_length=50, null=True, blank=True)
    name_fr = models.CharField(max_length=50, null=True, blank=True)
    parent_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.CharField(max_length=200)
    def __str__(self):
        return '{0}, parent: {1}'.format(self.name, self.parent_id)


class Game(models.Model):
    #game_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    name_zh = models.CharField(max_length=50, null=True, blank=True)
    name_fr = models.CharField(max_length=50, null=True, blank=True)
    #category = models.CharField(max_length=20)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    start_time = models.DateTimeField('Start Time', null=True, blank=True)
    end_time = models.DateTimeField('End Time', null=True, blank=True)
    opponent1 = models.CharField(max_length=200, null=True, blank=True)
    opponent2 = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=200)
    description_zh = models.CharField(max_length=200, null=True, blank=True)
    description_fr = models.CharField(max_length=200, null=True, blank=True)
    status_id = models.ForeignKey(Status, on_delete=models.CASCADE)

    def __str__(self):
        return '{0}: {1}'.format(self.name, self.category_id)

    def get_absolute_url(self):
        """
        Returns the url to access a particular game instance.
        """
        return reverse('game-detail', args=[str(self.id)])


class Language(models.Model):
    """
    Model representing a Language (e.g. English, French, Japanese, etc.)
    """
    name = models.CharField(max_length=200, help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name