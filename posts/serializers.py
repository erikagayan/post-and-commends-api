from rest_framework import serializers
from .models import Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(
        source="author.username"
    )

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "content", "created_at"]
        read_only_fields = ["author", "created_at"]


class CommentSerializerForPost(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(
        source="author.username"
    )

    class Meta:
        model = Comment
        fields = ["author", "content", "created_at"]
        read_only_fields = ["author", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    comments = CommentSerializerForPost(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ["id", "title", "content", "author", "created_at", "updated_at", "comments"]
        read_only_fields = ["author", "created_at", "updated_at"]
