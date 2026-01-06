from rest_framework import serializers
from watchlist_app.models import Watchlist, StreamingPlatform, Review


class ReviewSerializer(serializers.ModelSerializer):
    review_user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        exclude = ("watchlist",)
        # fields = "__all__"


class WatchListSerializer(serializers.ModelSerializer):
    """
    Docstring for MovieSerializer
    this method we no need to define cutom fields one by one like serializer.serializer.

    """

    # reviews = ReviewSerializer(many=True, read_only=True)
    platform = serializers.CharField(source="platform.name")

    class Meta:
        model = Watchlist
        fields = "__all__"


class StreamingPlatformSerializer(serializers.ModelSerializer):
    watchlist = WatchListSerializer(many=True, read_only=True)  # Nested Complete Object
    # watchlist = serializers.StringRelatedField(many=True)     # Show only __str__ in model as nested object
    # watchlist = serializers.PrimaryKeyRelatedField(many=True, read_only=True)   # Show primary keys as nested object
    # watchlist = serializers.HyperlinkedRelatedField(
    #     many=True, read_only=True, view_name="movie-detail"
    # )  # Show HyperLinks  as nested object

    class Meta:
        model = StreamingPlatform
        fields = "__all__"


# # 3 Validators
# def name_length(value):
#     if len(value) < 2:
#         raise serializers.ValidationError("Name is too short!")


# class MovieSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     name = serializers.CharField(validators=[name_length])
#     description = serializers.CharField()
#     active = serializers.BooleanField()

#     def create(self, validated_data):
#         return Movie.objects.create(**validated_data)

#     def update(self, instance, validated_data):
#         instance.name = validated_data.get("name", instance.name)
#         instance.description = validated_data.get("description", instance.description)
#         instance.active = validated_data.get("active", instance.active)
#         instance.save()
#         return instance

#     # 2 Object level validator
#     def validate(self, data):
#         if data["name"] == data["description"]:
#             raise serializers.ValidationError(
#                 "Title and Description should be different!"
#             )
#         return data

# # 1 Field level validator
# def validate_name(self, value):
#     if len(value) < 2:
#         raise serializers.ValidationError("Name is too short!")
#     else:
#         return value
