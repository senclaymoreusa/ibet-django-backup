from rest_framework import serializers
from games.models import Game, Category, GameProvider


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'notes', 'category_id', 'parent_id')

class CategorySerializer(serializers.ModelSerializer):
    parent_id = SubCategorySerializer(read_only=True)
    class Meta:
        model = Category
        fields = ('parent_id', 'name', 'notes', 'category_id')

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameProvider
        fields = ('provider_name', 'type', 'market')

class GameSerializer(serializers.ModelSerializer):
    category_id = CategorySerializer(read_only=True)
    provider = ProviderSerializer(read_only=True)

    class Meta:
        model = Game
        fields = ('pk','category_id', 'provider', 'name', 'name_zh', 'name_fr', 'description', 'description_zh', 'description_fr', 'start_time', 'end_time', 'opponent1', 'opponent2', 'game_url', 'image_url', 'smallgame_id')