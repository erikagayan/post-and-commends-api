import pytest
from django.contrib.auth import get_user_model
from posts.models import Post, Comment

User = get_user_model()


# A fixtura to create a user
@pytest.fixture
def create_user(db):
    return User.objects.create_user(
        email="testuser@example.com", username="testuser", password="testpass123"
    )


# A fix for creating a post
@pytest.fixture
def create_post(db, create_user):
    return Post.objects.create(
        title="Test Post", content="This is a test post.", author=create_user
    )


# A fixture to create a comment
@pytest.fixture
def create_comment(db, create_post, create_user):
    return Comment.objects.create(
        post=create_post, author=create_user, content="This is a test comment."
    )


@pytest.mark.django_db
class TestPostModel:
    def test_create_post(self, create_post):
        """Checking the creation of a post"""
        assert create_post.title == "Test Post"
        assert create_post.content == "This is a test post."
        assert create_post.author.username == "testuser"
        assert Post.objects.count() == 1

    def test_str_post(self, create_post):
        """Checking the __str__ method of the Post model"""
        assert str(create_post) == create_post.title


@pytest.mark.django_db
class TestCommentModel:
    def test_create_comment(self, create_comment):
        """Checking the creation of a comment"""
        assert create_comment.content == "This is a test comment."
        assert create_comment.author.username == "testuser"
        assert create_comment.post.title == "Test Post"
        assert Comment.objects.count() == 1

    def test_str_comment(self, create_comment):
        """Checking __str__ method of Comment model"""
        expected_str = (
            f"Comment by {create_comment.author} on {create_comment.post.title}"
        )
        assert str(create_comment) == expected_str
