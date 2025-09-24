"""
Real-world scenario demonstrating memory growth when reusing exception objects in Python.
This example simulates a web service handling requests with error responses.
"""
import gc
import psutil
import os
import json
import time
from datetime import datetime

# A typical custom exception in a web service
class APIException(Exception):
    def __init__(self, message, status_code=500, error_code=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

# Common pattern: Global exception objects (problematic!)
class ErrorSingleton:
    # These are created once at module load and reused
    NOT_FOUND = APIException("Resource not found", status_code=404, error_code="NOT_FOUND")
    UNAUTHORIZED = APIException("Unauthorized access", status_code=401, error_code="UNAUTHORIZED")
    BAD_REQUEST = APIException("Bad request", status_code=400, error_code="BAD_REQUEST")

# Better pattern: Factory methods
class ErrorFactory:
    @staticmethod
    def not_found():
        return APIException("Resource not found", status_code=404, error_code="NOT_FOUND")
    
    @staticmethod
    def unauthorized():
        return APIException("Unauthorized access", status_code=401, error_code="UNAUTHORIZED")
    
    @staticmethod
    def bad_request():
        return APIException("Bad request", status_code=400, error_code="BAD_REQUEST")

def memory_mb():
    """Get current memory usage in MB"""
    gc.collect()
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)

class WebServiceSimulator:
    def __init__(self):
        """Simulate a web service that processes requests"""
        self.request_count = 0
    
    def process_request(self, user_id, data, singleton=True):
        """Process a request, using either singleton or factory exceptions"""
        self.request_count += 1
        
        # Create a request context (like you'd have in a real web request)
        request_context = {
            'id': f"req-{self.request_count}",
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'data': data,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                # More headers would be here in a real request
            },
            'server': {
                'ip': '192.168.1.1',
                'node': 'web-1',
                'cluster': 'production',
            }
        }
        
        try:
            # Validate user (this will trigger our exception)
            if not user_id or user_id.startswith('invalid'):
                if singleton:
                    # Bad pattern: Reusing the same exception object
                    raise ErrorSingleton.UNAUTHORIZED
                else:
                    # Good pattern: Creating a new exception each time
                    raise ErrorFactory.unauthorized()
            
            # Process the request (would normally do more here)
            return {'status': 'success', 'request_id': request_context['id']}
            
        except APIException as e:
            # Handle the exception (like a real error handler would)
            return {
                'status': 'error',
                'code': e.error_code,
                'message': e.message,
                'status_code': e.status_code,
                'request_id': request_context['id']
            }

# Run the test
def run_test():
    service = WebServiceSimulator()
    
    # Generate some test data (simulating different request payloads)
    def generate_data(size):
        return {f"field_{i}": f"value_{i}" * 20 for i in range(size)}
    
    # Test with singleton exceptions
    print("\n=== Using Singleton Exception Objects (PROBLEMATIC) ===")
    print(f"Initial memory: {memory_mb():.2f} MB")
    
    for i in range(2000):
        # Simulate requests with invalid user IDs (will raise exceptions)
        data = generate_data((i % 10) + 5)  # Varying data sizes
        service.process_request(f"invalid-{i}", data, singleton=True)
        
        if i % 250 == 0:
            print(f"Request {i}: Memory usage = {memory_mb():.2f} MB")
    
    # Test with factory exceptions
    print("\n=== Using Factory Method Exception Objects (GOOD) ===")
    print(f"Initial memory: {memory_mb():.2f} MB")
    
    for i in range(2000):
        # Simulate requests with invalid user IDs (will raise exceptions)
        data = generate_data((i % 10) + 5)  # Same varying data sizes
        service.process_request(f"invalid-{i}", data, singleton=False)
        
        if i % 250 == 0:
            print(f"Request {i}: Memory usage = {memory_mb():.2f} MB")

if __name__ == "__main__":
    run_test()