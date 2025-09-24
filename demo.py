#!/usr/bin/env python3
"""
Demonstration of the Python exception object reuse memory leak.
"""

import gc
import sys
import tracemalloc
from memory_tracker import MemoryTracker


# Base exception class
class DemoException(Exception):
    """Demo exception class for memory leak demonstration."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


# Create singleton exception (problematic pattern)
SINGLETON_EXCEPTION = DemoException("This is a singleton exception")


# Define factory function (good pattern)
def create_exception():
    """Create a fresh exception instance."""
    return DemoException("This is a fresh exception")


def show_memory_usage():
    """Print current memory usage."""
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    print(f"[ Top 5 memory users ]")
    for stat in top_stats[:5]:
        print(stat)


def test_singleton_pattern(iterations=1000):
    """Test memory usage with singleton pattern."""
    print("\n=== Testing Singleton Exception Pattern ===")
    
    # Start memory tracking
    tracker = MemoryTracker("demo_singleton")
    tracker.start()
    
    # Generate a large object that will be referenced in the traceback
    large_object = ["x" * 1000 for _ in range(1000)]
    
    def function_that_fails():
        # Reference the large object to ensure it's captured in traceback
        print(f"Large object size: {sys.getsizeof(large_object)} bytes", end="\r")
        # Raise the singleton exception
        raise SINGLETON_EXCEPTION
    
    # Capture initial memory
    initial_snapshot = tracemalloc.take_snapshot()
    
    # Repeatedly raise and catch the same exception object
    for i in range(iterations):
        try:
            function_that_fails()
        except DemoException:
            # Just catch and ignore
            if i % 100 == 0:
                print(f"Iteration {i}: ", end="")
                tracker.record()
                gc.collect()  # Force garbage collection to get cleaner measurements
    
    # Measure memory usage
    tracker.stop()
    final_snapshot = tracemalloc.take_snapshot()
    
    # Display and save results
    tracker.plot(
        title="Memory Usage with Singleton Exception Pattern",
        save_path="demo_singleton_memory.png"
    )
    tracker.save_data("demo_singleton_memory.csv")
    
    # Compare memory usage
    diff = final_snapshot.compare_to(initial_snapshot, 'lineno')
    print("\n[ Top 5 memory differences ]")
    for stat in diff[:5]:
        print(stat)


def test_factory_pattern(iterations=1000):
    """Test memory usage with factory pattern."""
    print("\n=== Testing Factory Exception Pattern ===")
    
    # Start memory tracking
    tracker = MemoryTracker("demo_factory")
    tracker.start()
    
    # Generate a large object that will be referenced in the traceback
    large_object = ["x" * 1000 for _ in range(1000)]
    
    def function_that_fails():
        # Reference the large object to ensure it's captured in traceback
        print(f"Large object size: {sys.getsizeof(large_object)} bytes", end="\r")
        # Create and raise a fresh exception each time
        raise create_exception()
    
    # Capture initial memory
    initial_snapshot = tracemalloc.take_snapshot()
    
    # Repeatedly raise and catch freshly created exceptions
    for i in range(iterations):
        try:
            function_that_fails()
        except DemoException:
            # Just catch and ignore
            if i % 100 == 0:
                print(f"Iteration {i}: ", end="")
                tracker.record()
                gc.collect()  # Force garbage collection to get cleaner measurements
    
    # Measure memory usage
    tracker.stop()
    final_snapshot = tracemalloc.take_snapshot()
    
    # Display and save results
    tracker.plot(
        title="Memory Usage with Factory Exception Pattern",
        save_path="demo_factory_memory.png"
    )
    tracker.save_data("demo_factory_memory.csv")
    
    # Compare memory usage
    diff = final_snapshot.compare_to(initial_snapshot, 'lineno')
    print("\n[ Top 5 memory differences ]")
    for stat in diff[:5]:
        print(stat)


if __name__ == "__main__":
    # Start tracing memory allocations
    tracemalloc.start()
    
    # Get number of iterations
    iterations = 1000
    if len(sys.argv) > 1:
        try:
            iterations = int(sys.argv[1])
        except ValueError:
            print(f"Invalid iterations: {sys.argv[1]}. Using default: 1000")
    
    # Run tests
    test_singleton_pattern(iterations)
    test_factory_pattern(iterations)
    
    print("\nTests complete. Check the generated PNG and CSV files for results.")
    
    # Create comparison visualization
    import visualize_memory
    visualize_memory.compare_implementations()