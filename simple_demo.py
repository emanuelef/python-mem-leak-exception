"""
Minimal demonstration of Python exception memory leak.
Shows the problem and solution in the simplest way.
"""
import gc
import psutil
import os

def memory_usage():
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)

print("\n--- BAD: Reusing the same exception object ---")
leaky_exc = Exception("leak")
print(f"Initial memory: {memory_usage():.2f} MB")
for i in range(1000):
    try:
        # Simulate large local variable
        data = ["x" * 1000] * 100
        raise leaky_exc
    except Exception:
        pass
    gc.collect()
    if i % 200 == 0:
        print(f"After {i+1} exceptions: {memory_usage():.2f} MB")

print("\n--- GOOD: Creating a new exception each time ---")
print(f"Initial memory: {memory_usage():.2f} MB")
for i in range(1000):
    try:
        data = ["x" * 1000] * 100
        raise Exception("no leak")
    except Exception:
        pass
    gc.collect()
    if i % 200 == 0:
        print(f"After {i+1} exceptions: {memory_usage():.2f} MB")