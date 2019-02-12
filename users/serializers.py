from rest_framework import serializers
from users.models import Game, Book, Author, Category, BookInstance

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'notes', 'category_id', 'parent_id')

class CategorySerializer(serializers.ModelSerializer):
    parent_id = SubCategorySerializer(read_only=True)
    class Meta:
        model = Category
        fields = ('parent_id', 'name', 'notes', 'category_id')
        
class GameSerializer(serializers.ModelSerializer):
    category_id = CategorySerializer(read_only=True)
    class Meta:
        model = Game
        fields = ('category_id', 'name', 'description', 'start_time', 'end_time', 'opponent1', 'opponent2', 'status_id')

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'date_of_birth', 'date_of_death')

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Book
        fields = ('title', 'author', 'summary')

class BookInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookInstance
        fields = '__all__'