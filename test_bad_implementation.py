#!/usr/bin/env python3
"""
Test script demonstrating the memory leak with singleton exception objects.
"""

import time
import sys
from memory_tracker import MemoryTracker
from bad_implementation import RequestHandler


def run_test(num_requests=1000, user_exists=False):
    """Run test with problematic implementation.
    
    Args:
        num_requests: Number of requests to process
        user_exists: Whether to use a valid user ID
    """
    # Initialize memory tracking
    tracker = MemoryTracker("bad_implementation")
    tracker.start()
    
    # Create handler
    handler = RequestHandler()
    
    # Process multiple requests that will raise and handle exceptions
    for i in range(num_requests):
        # Prepare request data
        request_data = {
            "user_id": "user1" if user_exists else f"nonexistent_user_{i}",
            "token": "valid" if user_exists else "invalid",
            "payload": {
                # Include a large payload to make the memory leak more visible
                "data": "x" * 1000,
                "meta": {f"field_{j}": f"value_{j}" for j in range(100)}
            }
        }
        
        # Process request
        response = handler.handle_request(request_data)
        
        # Record memory usage every 100 requests
        if i % 100 == 0:
            tracker.record()
            print(f"Processed {i} requests. Current response: {response['status']}")
    
    # Record final state
    tracker.record()
    tracker.stop()
    
    # Save and plot results
    data_file = tracker.save_data(f"bad_implementation_memory_{'success' if user_exists else 'error'}.csv")
    plot_file = f"bad_implementation_memory_{'success' if user_exists else 'error'}.png"
    
    tracker.plot(
        title=f"Memory Usage with Singleton Exceptions - {'Successful' if user_exists else 'Error'} Requests",
        save_path=plot_file
    )
    
    print(f"\nTest completed. Processed {num_requests} requests.")
    print(f"Data saved to {data_file}")
    print(f"Plot saved to {plot_file}")
    
    return data_file, plot_file


if __name__ == "__main__":
    # Parse command line arguments
    num_requests = 1000
    if len(sys.argv) > 1:
        try:
            num_requests = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number of requests: {sys.argv[1]}. Using default: 1000")
    
    print("=== Testing BAD Implementation (Singleton Exceptions) ===")
    print(f"Running with {num_requests} requests that will raise exceptions...")
    
    # First test: Error path (will raise exceptions)
    error_data, error_plot = run_test(num_requests, user_exists=False)
    
    print("\n=== Memory Leak Analysis ===")
    import pandas as pd
    data = pd.read_csv(error_data)
    initial_memory = data['memory_mb'].iloc[0]
    final_memory = data['memory_mb'].iloc[-1]
    
    print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Final memory usage: {final_memory:.2f} MB")
    print(f"Memory growth: {final_memory - initial_memory:.2f} MB")
    print(f"Average growth per request: {(final_memory - initial_memory) / num_requests * 1000:.2f} KB/request")
    
    print(f"\nCheck the plot at {error_plot} to visualize the memory leak")