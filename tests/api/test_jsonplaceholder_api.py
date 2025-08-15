"""
JSONPlaceholder API tests demonstrating playwright-api-explorer agent capabilities.
This test suite explores and validates the JSONPlaceholder REST API endpoints.
"""

import pytest
import json
from playwright.sync_api import APIRequestContext


class TestJSONPlaceholderAPI:
    """Comprehensive tests for JSONPlaceholder API CRUD operations."""
    
    BASE_URL = "https://jsonplaceholder.typicode.com"
    
    @pytest.fixture
    def api_context(self, playwright_sync):
        """Create API request context."""
        context = playwright_sync.request.new_context(
            base_url=self.BASE_URL,
            extra_http_headers={
                "Content-Type": "application/json"
            }
        )
        yield context
        context.dispose()
    
    @pytest.mark.api
    def test_get_all_posts(self, api_context: APIRequestContext):
        """Test retrieving all posts from the API."""
        response = api_context.get("/posts")
        
        assert response.status == 200
        posts = response.json()
        assert isinstance(posts, list)
        assert len(posts) == 100
        
        # Validate first post structure
        first_post = posts[0]
        assert "id" in first_post
        assert "userId" in first_post
        assert "title" in first_post
        assert "body" in first_post
    
    @pytest.mark.api
    @pytest.mark.smoke
    def test_get_single_post(self, api_context: APIRequestContext):
        """Test retrieving a single post by ID."""
        response = api_context.get("/posts/1")
        
        assert response.status == 200
        post = response.json()
        assert post["id"] == 1
        assert post["userId"] == 1
        assert isinstance(post["title"], str)
        assert isinstance(post["body"], str)
    
    @pytest.mark.api
    def test_create_new_post(self, api_context: APIRequestContext):
        """Test creating a new post."""
        new_post = {
            "title": "Test Post Title",
            "body": "This is a test post body created by Playwright",
            "userId": 1
        }
        
        response = api_context.post("/posts", data=json.dumps(new_post))
        
        assert response.status == 201
        created_post = response.json()
        assert created_post["id"] == 101  # JSONPlaceholder returns 101 for new posts
        assert created_post["title"] == new_post["title"]
        assert created_post["body"] == new_post["body"]
        assert created_post["userId"] == new_post["userId"]
    
    @pytest.mark.api
    def test_update_post_put(self, api_context: APIRequestContext):
        """Test updating a post using PUT method."""
        updated_post = {
            "id": 1,
            "title": "Updated Post Title",
            "body": "This post has been updated using PUT method",
            "userId": 1
        }
        
        response = api_context.put("/posts/1", data=json.dumps(updated_post))
        
        assert response.status == 200
        result = response.json()
        assert result["id"] == 1
        assert result["title"] == updated_post["title"]
        assert result["body"] == updated_post["body"]
    
    @pytest.mark.api
    def test_update_post_patch(self, api_context: APIRequestContext):
        """Test partially updating a post using PATCH method."""
        partial_update = {
            "title": "Partially Updated Title"
        }
        
        response = api_context.patch("/posts/1", data=json.dumps(partial_update))
        
        assert response.status == 200
        result = response.json()
        assert result["id"] == 1
        assert result["title"] == partial_update["title"]
        # Other fields should remain unchanged
        assert "body" in result
        assert "userId" in result
    
    @pytest.mark.api
    def test_delete_post(self, api_context: APIRequestContext):
        """Test deleting a post."""
        response = api_context.delete("/posts/1")
        
        assert response.status == 200
    
    @pytest.mark.api
    def test_get_posts_by_user(self, api_context: APIRequestContext):
        """Test filtering posts by user ID."""
        response = api_context.get("/posts?userId=1")
        
        assert response.status == 200
        posts = response.json()
        assert isinstance(posts, list)
        assert len(posts) == 10
        
        # Verify all posts belong to user 1
        for post in posts:
            assert post["userId"] == 1
    
    @pytest.mark.api
    def test_get_nonexistent_post(self, api_context: APIRequestContext):
        """Test retrieving a non-existent post returns 404."""
        response = api_context.get("/posts/999999")
        
        assert response.status == 404
    
    @pytest.mark.api
    def test_invalid_post_creation(self, api_context: APIRequestContext):
        """Test creating a post with invalid data."""
        invalid_post = {
            "title": "",  # Empty title
            "body": "",   # Empty body
        }
        
        response = api_context.post("/posts", data=json.dumps(invalid_post))
        
        # JSONPlaceholder accepts any data, but in real APIs this might fail
        # This test demonstrates how to test validation
        assert response.status in [201, 400, 422]