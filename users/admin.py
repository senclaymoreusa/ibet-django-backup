from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

from .models import Author, Genre, Book, BookInstance, Language, Country, Category, Status, TransactionType, Game, Line

from django.contrib import admin

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserCreationForm

class UserAdmin(BaseUserAdmin):
	add_form = UserCreationForm

	list_display = ('username','email','is_admin', 'first_name', 'last_name')
	list_filter = ('is_admin',)

	fieldsets = (
			(None, {'fields': ('username','email','password', 'first_name', 'last_name', 'phone', 'country', 'date_of_birth', 'street_address_1', 'street_address_2', 'city', 'state', 'zipcode', 'block')}),
			('Permissions', {'fields': ('is_admin',)})
		)
	search_fields = ('username','email')
	ordering = ('username','email')

	filter_horizontal = ()


admin.site.register(CustomUser, UserAdmin)


admin.site.unregister(Group)

admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(Country)
admin.site.register(Category)
admin.site.register(Status)
admin.site.register(TransactionType)
admin.site.register(Game)
admin.site.register(Line)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username',]

#admin.site.register(CustomUser, CustomUserAdmin)

class BooksInline(admin.TabularInline):
    """
    Defines format of inline book insertion (used in AuthorAdmin)
    """
    model = Book

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """
    Administration object for Author models.
    Defines:
    - fields to be displayed in list view (list_display)
    - orders fields in detail view (fields), grouping the date fields horizontally
    - adds inline addition of books in author view (inlines)
    """
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]

class BooksInstanceInline(admin.TabularInline):
    """
    Defines format of inline book instance insertion (used in BookAdmin)
    """
    model = BookInstance

class BookAdmin(admin.ModelAdmin):
    """
    Administration object for Book models.
    Defines:
    - fields to be displayed in list view (list_display)
    - adds inline addition of book instances in book view (inlines)
    """
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]

admin.site.register(Book, BookAdmin)


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    """
    Administration object for BookInstance models.
    Defines:
    - fields to be displayed in list view (list_display)
    - filters that will be displayed in sidebar (list_filter)
    - grouping of fields into sections (fieldsets)
    """
    list_display = ('book', 'status', 'borrower','due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book','imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back','borrower')                                                 }),
    )








# Register your models here.
