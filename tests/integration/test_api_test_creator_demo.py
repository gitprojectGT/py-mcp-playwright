"""
Comprehensive API testing demonstrating playwright-api-test-creator agent capabilities.
This test suite shows advanced API testing patterns and methodologies.
"""

import pytest
import json
import asyncio
from playwright.async_api import APIRequestContext as AsyncAPIRequestContext
from playwright.sync_api import APIRequestContext


class TestAPITestCreatorDemo:
    """Advanced API testing patterns and comprehensive coverage."""
    
    @pytest.mark.api
    def test_posts_crud_operations_sync(self, api_context_sync):
        """Complete CRUD operations test for posts endpoint."""
        # CREATE - Test post creation
        new_post = {
            "title": "Advanced API Testing",
            "body": "Comprehensive testing with Playwright API test creator",
            "userId": 1
        }
        
        create_response = api_context_sync.post(
            "https://jsonplaceholder.typicode.com/posts",
            data=json.dumps(new_post)
        )
        
        assert create_response.status == 201
        created_post = create_response.json()
        post_id = created_post["id"]
        
        # READ - Test retrieving the created post
        read_response = api_context_sync.get(f"https://jsonplaceholder.typicode.com/posts/{post_id}")
        assert read_response.status == 200
        retrieved_post = read_response.json()
        assert retrieved_post["title"] == new_post["title"]
        
        # UPDATE - Test full update with PUT
        updated_post = {
            "id": post_id,
            "title": "Updated API Testing Title",
            "body": "Updated body content",
            "userId": 1
        }
        
        put_response = api_context_sync.put(
            f"https://jsonplaceholder.typicode.com/posts/{post_id}",
            data=json.dumps(updated_post)
        )
        assert put_response.status == 200
        
        # UPDATE - Test partial update with PATCH
        patch_data = {"title": "Partially Updated Title"}
        patch_response = api_context_sync.patch(
            f"https://jsonplaceholder.typicode.com/posts/{post_id}",
            data=json.dumps(patch_data)
        )
        assert patch_response.status == 200
        
        # DELETE - Test post deletion
        delete_response = api_context_sync.delete(
            f"https://jsonplaceholder.typicode.com/posts/{post_id}"
        )
        assert delete_response.status == 200
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_posts_crud_operations_async(self, api_context_async):
        """Async version of CRUD operations test."""
        new_post = {
            "title": "Async API Testing",
            "body": "Testing async operations with Playwright",
            "userId": 2
        }
        
        # CREATE
        create_response = await api_context_async.post(
            "https://jsonplaceholder.typicode.com/posts",
            data=json.dumps(new_post)
        )
        
        assert create_response.status == 201
        created_post = await create_response.json()
        
        # READ
        read_response = await api_context_async.get(
            f"https://jsonplaceholder.typicode.com/posts/{created_post['id']}"
        )
        assert read_response.status == 200
        
        # Verify response structure
        post_data = await read_response.json()
        assert "id" in post_data
        assert "title" in post_data
        assert "body" in post_data
        assert "userId" in post_data
    
    @pytest.mark.api
    def test_error_handling_and_edge_cases(self, api_context_sync):
        """Test error conditions and edge cases."""
        # Test 404 for non-existent resource
        response_404 = api_context_sync.get("https://jsonplaceholder.typicode.com/posts/99999")
        assert response_404.status == 404
        
        # Test invalid JSON in request body
        invalid_response = api_context_sync.post(
            "https://jsonplaceholder.typicode.com/posts",
            data="invalid json content",
            headers={"Content-Type": "application/json"}
        )
        # JSONPlaceholder is lenient, but test the pattern
        assert invalid_response.status in [201, 400, 422]
        
        # Test empty request body
        empty_response = api_context_sync.post(
            "https://jsonplaceholder.typicode.com/posts",
            data=json.dumps({})
        )
        assert empty_response.status == 201  # JSONPlaceholder accepts empty objects
    
    @pytest.mark.api
    def test_authentication_patterns(self, playwright_sync):
        """Demonstrate authentication testing patterns."""
        # Create context with auth headers
        auth_context = playwright_sync.request.new_context(
            base_url="https://httpbin.org",
            extra_http_headers={
                "Authorization": "Bearer test-token-123",
                "X-API-Key": "test-api-key"
            }
        )
        
        try:
            # Test authenticated request
            auth_response = auth_context.get("/bearer")
            assert auth_response.status in [200, 401]  # Depending on actual token validity
            
            # Test request with custom headers
            headers_response = auth_context.get("/headers")
            assert headers_response.status == 200
            
            headers_data = headers_response.json()
            assert "Authorization" in headers_data["headers"]
            assert "X-Api-Key" in headers_data["headers"]
            
        finally:
            auth_context.dispose()
    
    @pytest.mark.api
    def test_data_validation_and_schemas(self, api_context_sync):
        """Test response data validation and schema compliance."""
        response = api_context_sync.get("https://jsonplaceholder.typicode.com/posts/1")
        assert response.status == 200
        
        post_data = response.json()
        
        # Validate required fields
        required_fields = ["id", "userId", "title", "body"]
        for field in required_fields:
            assert field in post_data, f"Required field '{field}' missing from response"
        
        # Validate data types
        assert isinstance(post_data["id"], int), "ID should be integer"
        assert isinstance(post_data["userId"], int), "User ID should be integer"
        assert isinstance(post_data["title"], str), "Title should be string"
        assert isinstance(post_data["body"], str), "Body should be string"
        
        # Validate data constraints
        assert post_data["id"] > 0, "ID should be positive"
        assert post_data["userId"] > 0, "User ID should be positive"
        assert len(post_data["title"]) > 0, "Title should not be empty"
    
    @pytest.mark.api
    def test_performance_and_timing(self, api_context_sync):
        """Test API performance and response timing."""
        import time
        
        start_time = time.time()
        response = api_context_sync.get("https://jsonplaceholder.typicode.com/posts")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status == 200
        assert response_time < 5.0, f"Response time {response_time}s exceeds 5 second threshold"
        
        # Test response size
        posts = response.json()
        assert len(posts) == 100, "Expected 100 posts in response"
    
    @pytest.mark.api
    def test_concurrent_requests(self, playwright_sync):
        """Test handling of concurrent API requests."""
        import threading
        import time
        
        results = []
        
        def make_request(post_id):
            context = playwright_sync.request.new_context()
            try:
                response = context.get(f"https://jsonplaceholder.typicode.com/posts/{post_id}")
                results.append({
                    "post_id": post_id,
                    "status": response.status,
                    "success": response.status == 200
                })
            finally:
                context.dispose()
        
        # Create multiple threads for concurrent requests
        threads = []
        for i in range(1, 6):  # Test with posts 1-5
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        assert len(results) == 5
        for result in results:
            assert result["success"], f"Request for post {result['post_id']} failed"