import pytest
from posts.models import Post, Comment
from posts.serializers import PostSerializer, CommentSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def create_user(db):
    return User.objects.create_user(
        email="testuser@example.com", username="testuser", password="testpass123"
    )


@pytest.fixture
def create_post(db, create_user):
    return Post.objects.create(
        title="Test Post", content="This is a test post.", author=create_user
    )


@pytest.fixture
def create_comment(db, create_post, create_user):
    return Comment.objects.create(
        post=create_post, author=create_user, content="This is a test comment."
    )


@pytest.mark.django_db
class TestPostSerializer:
    def test_post_serializer_output(self, create_post, create_comment):
        """Test serialization of post data with comments"""
        serializer = PostSerializer(create_post)
        data = serializer.data

        # Check key fields
        assert data["id"] == create_post.id
        assert data["title"] == create_post.title
        assert data["content"] == create_post.content
        assert data["author"] == create_post.author.username
        assert len(data["comments"]) == 1
        assert data["comments"][0]["author"] == create_comment.author.username
        assert data["comments"][0]["content"] == create_comment.content

    def test_post_serializer_create(self, create_user):
        """Test post creation using PostSerializer"""
        data = {"title": "New Post", "content": "New content", "author": create_user}
        serializer = PostSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestCommentSerializer:
    def test_comment_serializer_output(self, create_comment):
        """Test serialization of comment data"""
        serializer = CommentSerializer(create_comment)
        data = serializer.data

        # Check key fields
        assert data["id"] == create_comment.id
        assert data["post"] == create_comment.post.id
        assert data["author"] == create_comment.author.username
        assert data["content"] == create_comment.content

    def test_comment_serializer_create(self, create_post, create_user):
        """Test comment creation using CommentSerializer"""
        data = {"post": create_post.id, "content": "New comment", "author": create_user}
        serializer = CommentSerializer(data=data)
        assert serializer.is_valid()
