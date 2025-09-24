#!/usr/bin/env python3
"""
Bad implementation: Using singleton exception objects that are reused across requests.
This leads to memory leaks as Python attaches a new traceback to the exception
each time it's raised, without garbage collecting previous ones.
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


# PROBLEMATIC PATTERN: Global singleton exceptions
# These exception objects are created once at module load time
# and reused throughout the application's lifetime
class Errors:
    """Error factory using the singleton pattern (problematic)."""
    
    # These exceptions are created once and reused
    user_not_found = APIServiceException(
        message="User was not found",
        status_code=404,
        error_code="USER_NOT_FOUND"
    )
    
    token_invalid = APIServiceException(
        message="The provided token is invalid",
        status_code=401,
        error_code="TOKEN_INVALID"
    )
    
    authentication_failed = APIServiceException(
        message="Authentication failed",
        status_code=401,
        error_code="AUTH_FAILED"
    )
    
    server_error = APIServiceException(
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
            # PROBLEMATIC: Reusing the same exception object
            # When raised repeatedly, this adds new tracebacks without cleaning old ones
            raise Errors.user_not_found
        
        return user

    def authenticate_user(self, token):
        """Authenticate a user with a token."""
        # Simulate token validation
        if not token or token == "invalid":
            # PROBLEMATIC: Reusing the same exception object
            raise Errors.token_invalid
        
        return {"user_id": "user1", "authenticated": True}


class RequestHandler:
    """Simulates an API request handler."""
    
    def __init__(self):
        self.user_service = UserService()
        
    def handle_request(self, request_data):
        """Process an API request with error handling."""
        try:
            # This large request data is captured in the traceback
            # and contributes to memory leaks when exceptions aren't properly handled
            large_request_payload = request_data.get("payload", {"default": "x" * 10000})
            
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
            # Even though we handle the exception here,
            # the traceback attached to the reused exception object remains
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