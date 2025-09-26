# The Hidden Memory Leak in Python Exception Handling
# ⚠️ **Note:** Most of this repository consists of experiments and alternative approaches to demonstrate Python exception memory leaks. If you want a single, clear way to observe the issue, run `traceback_accumulation_demo.py`.

This repository contains a comprehensive demonstration of a subtle but significant memory leak pattern in Python applications that reuse exception objects. The code examples and visualizations help developers understand the issue and how to properly fix it.

## Understanding the Problem

When you raise the same exception object multiple times in Python, each time a new traceback is attached to the exception object. These tracebacks contain references to the entire call stack, including local variables and other objects that might be memory-intensive. If these exceptions are reused over many requests in a server application, the memory usage can grow unbounded.

## Code Example of the Problem

A common pattern seen in many Python applications:

```python
# BAD PATTERN: Global singleton exceptions
class Errors:
    # Created once at module load time and reused throughout the application
    user_not_found = CustomException("User not found", code=404)
    invalid_token = CustomException("Invalid token", code=401)

def process_request(request):
    # ...
    if not user:
        raise Errors.user_not_found  # Reuses the same exception object
    # ...
```

## The Solution

Instead of reusing exception objects, create fresh instances each time:

```python
# GOOD PATTERN: Factory methods for exceptions
class Errors:
    @staticmethod
    def user_not_found():
        return CustomException("User not found", code=404)
    
    @staticmethod
    def invalid_token():
        return CustomException("Invalid token", code=401)

def process_request(request):
    # ...
    if not user:
        raise Errors.user_not_found()  # Creates a new instance each time
    # ...
```

## Repository Contents

This repository includes:

1. `bad_implementation.py` - Demonstrates the problematic singleton pattern
2. `good_implementation.py` - Shows the correct factory method pattern
3. `memory_tracker.py` - Utility for measuring and visualizing memory usage
4. `test_bad_implementation.py` - Test script showing the memory leak
5. `test_good_implementation.py` - Test script showing the fixed behavior
6. `visualize_memory.py` - Script for generating comparison visualizations
7. `demo.py` - Simple demo of the issue with tracemalloc analysis
8. `article_demo.py` - Comprehensive demo with detailed output for article content
9. `traceback_accumulation_demo.py` - Shows how reusing exception objects causes traceback accumulation and memory growth

## Running the Demos

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the memory leak demonstration:
   ```
   python test_bad_implementation.py
   ```

3. Run the fixed implementation demonstration:
   ```
   python test_good_implementation.py
   ```

4. Generate comparative visualizations:
   ```
   python visualize_memory.py
   ```

5. Run the comprehensive article demo:
   ```
   python article_demo.py
   ```

6. Run the traceback accumulation demo:
     ```
     python traceback_accumulation_demo.py
     ```
## Key Findings

1. Reusing exception objects can cause unbounded memory growth
2. Each raised exception keeps its traceback, which references objects in memory
3. The memory leak is proportional to the complexity of the call stack and size of local variables
4. Creating fresh exception instances solves the problem with negligible performance impact
5. This leak can be particularly problematic in long-running server applications

## Traceback Accumulation Demo

`traceback_accumulation_demo.py` demonstrates how reusing a single exception object causes its traceback to accumulate after multiple raises, leading to memory growth. It compares this with the factory pattern, where a fresh exception is created each time, preventing accumulation.

### How it works

### Sample Output
```console
$ python traceback_accumulation_demo.py
Raise #1: Traceback frame count = 2, Memory usage = 14592 KB
Raise #101: Traceback frame count = 202, Memory usage = 15424 KB
Raise #201: Traceback frame count = 402, Memory usage = 16256 KB
Raise #301: Traceback frame count = 602, Memory usage = 17136 KB
Raise #401: Traceback frame count = 802, Memory usage = 18000 KB
Raise #501: Traceback frame count = 1002, Memory usage = 18848 KB
Raise #601: Traceback frame count = 1202, Memory usage = 19664 KB
Raise #701: Traceback frame count = 1402, Memory usage = 20416 KB
Raise #801: Traceback frame count = 1602, Memory usage = 21248 KB
Raise #901: Traceback frame count = 1802, Memory usage = 22080 KB
Raise #1000: Traceback frame count = 2000, Memory usage = 22912 KB

Now repeating with a fresh exception each time (factory pattern):

Raise #1: Traceback frame count = 2, Memory usage = 22928 KB
Raise #101: Traceback frame count = 2, Memory usage = 22928 KB
Raise #201: Traceback frame count = 2, Memory usage = 22928 KB
Raise #301: Traceback frame count = 2, Memory usage = 22928 KB
Raise #401: Traceback frame count = 2, Memory usage = 22928 KB
Raise #501: Traceback frame count = 2, Memory usage = 22928 KB
Raise #601: Traceback frame count = 2, Memory usage = 22928 KB
Raise #701: Traceback frame count = 2, Memory usage = 22928 KB
Raise #801: Traceback frame count = 2, Memory usage = 22928 KB
Raise #901: Traceback frame count = 2, Memory usage = 22928 KB
Raise #1000: Traceback frame count = 2, Memory usage = 22928 KB

Notice how the traceback frame count and memory usage do NOT accumulate when using a fresh exception each time.
```

### Takeaway

## Test Results

Running the comprehensive demo shows a clear difference between the two approaches:

```console
# DEMO 1: Singleton Exception Pattern (BAD)

This demo will raise and catch the SAME exception object 1000 times
Each exception will capture a context of ~500KB in its traceback
Created context object of ~4.1KB
Starting memory usage: 109.59 MB
Iteration 1/1000: Memory usage = 109.59 MB (+0.00 B)
Iteration 101/1000: Memory usage = 109.66 MB (+64.00 KB)
Iteration 201/1000: Memory usage = 109.75 MB (+160.00 KB)
Iteration 301/1000: Memory usage = 109.84 MB (+256.00 KB)
Iteration 401/1000: Memory usage = 109.92 MB (+336.00 KB)
Iteration 501/1000: Memory usage = 110.03 MB (+448.00 KB)
Iteration 601/1000: Memory usage = 110.28 MB (+704.00 KB)
Iteration 701/1000: Memory usage = 110.39 MB (+816.00 KB)
Iteration 801/1000: Memory usage = 110.50 MB (+928.00 KB)
Iteration 901/1000: Memory usage = 110.61 MB (+1.02 MB)
Iteration 1000/1000: Memory usage = 110.72 MB (+1.12 MB)

Singleton Exception Demo Complete:
Memory growth trend: 8.543 MB/s
Total memory increase: 1.44 MB
```

```console
# DEMO 2: Factory Exception Pattern (GOOD)

This demo will raise and catch 1000 NEW exception objects
Each exception will capture a context of ~500KB in its traceback
Iteration 1/1000: Memory usage = 188.48 MB (+0.00 B)
Iteration 101/1000: Memory usage = 188.48 MB (+0.00 B)
Iteration 201/1000: Memory usage = 188.48 MB (+0.00 B)
Iteration 301/1000: Memory usage = 188.48 MB (+0.00 B)
Iteration 401/1000: Memory usage = 188.48 MB (+0.00 B)
Iteration 501/1000: Memory usage = 188.48 MB (+0.00 B)
Iteration 601/1000: Memory usage = 188.48 MB (+0.00 B)
Iteration 701/1000: Memory usage = 188.48 MB (+0.00 B)
Iteration 801/1000: Memory usage = 188.48 MB (+0.00 B)
Iteration 901/1000: Memory usage = 188.48 MB (+0.00 B)
Iteration 1000/1000: Memory usage = 188.48 MB (+0.00 B)

Factory Exception Demo Complete:
Memory growth trend: 0.000 MB/s
Total memory increase: 0.00 B
```

### Summary

The test results clearly demonstrate that the singleton exception pattern causes a significant memory leak, while the factory method pattern maintains stable memory usage.

## Visual Demonstrations

The demos generate several visualization files:

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
