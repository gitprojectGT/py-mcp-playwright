"""
Example usage of the testing framework for API testing.
This demonstrates how to use the framework components.
"""

import asyncio
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

from src.test_helpers import TestDataGenerator, APITestHelper
from src.config import get_api_config


def example_sync_api_testing():
    """Example of synchronous API testing."""
    print("=== Synchronous API Testing Example ===")
    
    data_generator = TestDataGenerator()
    config = get_api_config()
    
    with sync_playwright() as p:
        # Create API request context
        context = p.request.new_context(**config.get_request_context_options())
        helper = APITestHelper(context)
        
        try:
            # Generate test data
            user_data = data_generator.generate_user_data()
            print(f"Generated user data: {user_data}")
            
            # Test GET request
            print("\n--- Testing GET request ---")
            response, response_time = helper.measure_response_time("GET", "/posts/1")
            print(f"Response status: {response.status}")
            print(f"Response time: {response_time:.3f}s")
            
            if helper.validate_response_status(response, 200):
                data = helper.extract_response_data(response)
                print(f"Response data: {data}")
                
                # Validate response schema
                required_fields = ["id", "userId", "title", "body"]
                if helper.validate_response_schema(response, required_fields):
                    print("✅ Response schema validation passed")
                else:
                    print("❌ Response schema validation failed")
            
            # Test POST request with retry
            print("\n--- Testing POST request with retry ---")
            post_data = data_generator.generate_post_data()
            create_response = helper.make_request_with_retry(
                "POST", 
                "/posts",
                data=post_data
            )
            print(f"Create response status: {create_response.status}")
            
        finally:
            context.dispose()


async def example_async_api_testing():
    """Example of asynchronous API testing."""
    print("\n=== Asynchronous API Testing Example ===")
    
    data_generator = TestDataGenerator()
    config = get_api_config()
    
    async with async_playwright() as p:
        # Create API request context
        context = await p.request.new_context(**config.get_request_context_options())
        
        try:
            # Test concurrent requests
            print("\n--- Testing concurrent requests ---")
            
            async def make_request(post_id: int):
                response = await context.get(f"/posts/{post_id}")
                return {"id": post_id, "status": response.status}
            
            # Make 5 concurrent requests
            tasks = [make_request(i) for i in range(1, 6)]
            results = await asyncio.gather(*tasks)
            
            print("Concurrent request results:")
            for result in results:
                print(f"  Post {result['id']}: Status {result['status']}")
            
            # Test with authentication
            print("\n--- Testing with authentication ---")
            auth_headers = {"Authorization": "Bearer fake-token-123"}
            
            # Note: This would typically use a real API that requires auth
            # For demo purposes, we'll just show the pattern
            auth_response = await context.get("/posts/1", headers=auth_headers)
            print(f"Auth request status: {auth_response.status}")
            
        finally:
            await context.dispose()


def example_data_generation():
    """Example of test data generation."""
    print("\n=== Test Data Generation Example ===")
    
    generator = TestDataGenerator()
    
    # Generate various types of test data
    user = generator.generate_user_data()
    post = generator.generate_post_data()
    product = generator.generate_product_data()
    invalid_data = generator.generate_invalid_data()
    
    print("Generated user data:")
    print(f"  Name: {user['first_name']} {user['last_name']}")
    print(f"  Email: {user['email']}")
    print(f"  Phone: {user['phone']}")
    
    print(f"\nGenerated post: {post['title']}")
    print(f"Generated product: {product['name']} - ${product['price']}")
    
    print(f"\nRandom string: {generator.generate_random_string(15)}")
    print(f"UUID: {generator.generate_uuid()}")
    
    print("\nInvalid data for negative testing:")
    for key, value in invalid_data.items():
        print(f"  {key}: {repr(value)}")


def example_error_handling():
    """Example of error handling in API tests."""
    print("\n=== Error Handling Example ===")
    
    config = get_api_config()
    
    with sync_playwright() as p:
        context = p.request.new_context(**config.get_request_context_options())
        helper = APITestHelper(context)
        
        try:
            # Test 404 error
            print("--- Testing 404 error ---")
            response = helper.make_request_with_retry("GET", "/posts/99999")
            print(f"404 test - Status: {response.status}")
            
            if response.status == 404:
                print("✅ 404 error handled correctly")
            else:
                print("❌ Unexpected response for non-existent resource")
            
            # Test timeout (simulated)
            print("\n--- Testing timeout handling ---")
            try:
                # This would timeout in a real scenario with a slow endpoint
                response = context.get("/posts/1", timeout=1)  # Very short timeout
                print(f"Response received: {response.status}")
            except Exception as e:
                print(f"Timeout handled: {type(e).__name__}")
            
        finally:
            context.dispose()


if __name__ == "__main__":
    # Run synchronous examples
    example_sync_api_testing()
    example_data_generation()
    example_error_handling()
    
    # Run asynchronous example
    asyncio.run(example_async_api_testing())