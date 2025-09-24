#!/usr/bin/env python3
"""
Good implementation: Using factory methods to create fresh exception objects.
This prevents memory leaks by ensuring each exception has its own traceback
that can be properly garbage collected when the exception is handled.
"""

class APIException(Exception):
    """Base exception class for API errors."""
    def __init__(self, message, status_code=500, error_code=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)



# Specialized exception for API errors (previously company-specific)
class APIServiceException(APIException):
    """Specialized exception for API service errors."""
    pass


# IMPROVED PATTERN: Factory methods for exceptions
# Each call creates a fresh exception object with its own traceback
class Errors:
    """Error factory using the factory method pattern (recommended)."""
    
    @staticmethod
    def user_not_found():
        """Return a fresh user not found exception."""
        return APIServiceException(
            message="User was not found",
            status_code=404,
            error_code="USER_NOT_FOUND"
        )
    
    @staticmethod
    def token_invalid():
        """Return a fresh token invalid exception."""
        return APIServiceException(
            message="The provided token is invalid",
            status_code=401,
            error_code="TOKEN_INVALID"
        )
    
    @staticmethod
    def authentication_failed():
        """Return a fresh authentication failed exception."""
        return APIServiceException(
            message="Authentication failed",
            status_code=401,
            error_code="AUTH_FAILED"
        )
    
    @staticmethod
    def server_error():
        """Return a fresh server error exception."""
        return APIServiceException(
            message="Internal server error occurred",
            status_code=500,
            error_code="SERVER_ERROR"
        )


class UserService:
    """Service class that might raise exceptions."""
    
    def __init__(self):
        # Simulating a database of users
        self.users = {
            "user1": {"name": "John", "email": "john@example.com"},
            "user2": {"name": "Alice", "email": "alice@example.com"}
        }
    
    def get_user(self, user_id):
        """Retrieve a user by ID."""
        # Simulate a database lookup
        user = self.users.get(user_id)
        
        if not user:
            # IMPROVED: Creating a new exception instance each time
            # This allows proper garbage collection after handling
            raise Errors.user_not_found()
        
        return user

    def authenticate_user(self, token):
        """Authenticate a user with a token."""
        # Simulate token validation
        if not token or token == "invalid":
            # IMPROVED: Creating a new exception instance each time
            raise Errors.token_invalid()
        
        return {"user_id": "user1", "authenticated": True}


class RequestHandler:
    """Simulates an API request handler."""
    
    def __init__(self):
        self.user_service = UserService()
        
    def handle_request(self, request_data):
        """Process an API request with error handling."""
        try:
            # This large request data is captured in the traceback
            # But with fresh exceptions, it will be properly garbage collected
            _ = request_data.get("payload", {"default": "x" * 10000})
            
            # Validate and process the request
            user_id = request_data.get("user_id")
            token = request_data.get("token")
            
            # Authenticate
            auth_info = self.user_service.authenticate_user(token)
            
            # Get user data
            user = self.user_service.get_user(user_id)
            
            return {
                "status": "success",
                "data": {
                    "user": user,
                    "auth": auth_info
                }
            }
            
        except APIException as e:
            # With the factory pattern, each exception has its own traceback
            # that can be properly garbage collected after handling
            return {
                "status": "error",
                "error": {
                    "message": e.message,
                    "status_code": e.status_code,
                    "error_code": e.error_code
                }
            }
        except Exception as e:
            # Generic error handling
            return {
                "status": "error",
                "error": {
                    "message": str(e),
                    "status_code": 500
                }
            }