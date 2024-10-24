import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from posts.models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    return User.objects.create_user(
        email="testuser@example.com", username="testuser", password="testpass123"
    )


@pytest.fixture
def create_other_user(db):
    return User.objects.create_user(
        email="otheruser@example.com", username="otheruser", password="testpass123"
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
class TestPostViewSet:
    def test_list_posts(self, api_client, create_post):
        """Test that all users can list posts"""
        url = reverse("posts:post-list")  # Add 'posts:' namespace
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == create_post.title

    def test_create_post_authenticated(self, api_client, create_user):
        """Test that authenticated users can create posts"""
        api_client.force_authenticate(user=create_user)
        url = reverse("posts:post-list")  # Add 'posts:' namespace
        data = {"title": "New Post", "content": "New content"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.count() == 1  # Один пост создается в этом тесте

    def test_create_post_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot create posts"""
        url = reverse("posts:post-list")  # Add 'posts:' namespace
        data = {"title": "New Post", "content": "New content"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_post(self, api_client, create_post, create_user):
        """Test that the author can update their post"""
        api_client.force_authenticate(user=create_user)
        url = reverse(
            "posts:post-detail", args=[create_post.id]
        )  # Add 'posts:' namespace
        updated_data = {"title": "Updated Post", "content": "Updated content"}
        response = api_client.put(url, updated_data)
        assert response.status_code == status.HTTP_200_OK
        create_post.refresh_from_db()
        assert create_post.title == "Updated Post"

    def test_update_post_not_author(self, api_client, create_post, create_other_user):
        """Test that non-authors cannot update the post"""
        api_client.force_authenticate(user=create_other_user)
        url = reverse(
            "posts:post-detail", args=[create_post.id]
        )  # Add 'posts:' namespace
        updated_data = {"title": "Updated Post", "content": "Updated content"}
        response = api_client.put(url, updated_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_post(self, api_client, create_post, create_user):
        """Test that the author can delete their post"""
        api_client.force_authenticate(user=create_user)
        url = reverse(
            "posts:post-detail", args=[create_post.id]
        )  # Add 'posts:' namespace
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Post.objects.count() == 0

    def test_delete_post_not_author(self, api_client, create_post, create_other_user):
        """Test that non-authors cannot delete the post"""
        api_client.force_authenticate(user=create_other_user)
        url = reverse(
            "posts:post-detail", args=[create_post.id]
        )  # Add 'posts:' namespace
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCommentViewSet:
    def test_list_comments(self, api_client, create_comment):
        """Test that all users can list comments"""
        url = reverse("posts:comment-list")  # Add 'posts:' namespace
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["content"] == create_comment.content

    def test_create_comment_authenticated(self, api_client, create_post, create_user):
        """Test that authenticated users can create comments"""
        api_client.force_authenticate(user=create_user)
        url = reverse("posts:comment-list")  # Add 'posts:' namespace
        data = {"post": create_post.id, "content": "New comment"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.count() == 1  # Один комментарий создается в этом тесте

    def test_create_comment_unauthenticated(self, api_client, create_post):
        """Test that unauthenticated users cannot create comments"""
        url = reverse("posts:comment-list")  # Add 'posts:' namespace
        data = {"post": create_post.id, "content": "New comment"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
