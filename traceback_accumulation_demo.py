#!/usr/bin/env python3
"""
Demonstrates how reusing a single exception object causes its traceback to accumulate after multiple raises.
"""

import psutil

class CustomException(Exception):
    pass

# Create a singleton exception
singleton_exc = CustomException("Singleton exception")



process = psutil.Process()

def raise_with_large_context():
    # Large local variable to inflate traceback memory
    big_data = ['x' * 1000] * 1000  # ~1MB
    raise singleton_exc

num_raises = 1000
for i in range(num_raises):
    try:
        raise_with_large_context()
    except CustomException as e:
        tb = e.__traceback__
        # Count the number of frames in the traceback chain
        depth = 0
        current_tb = tb
        while current_tb:
            depth += 1
            current_tb = current_tb.tb_next
        mem_kb = process.memory_info().rss // 1024
        if i % 100 == 0 or i == num_raises - 1:
            print(f"Raise #{i+1}: Traceback frame count = {depth}, Memory usage = {mem_kb} KB")


print("\nNow repeating with a fresh exception each time (factory pattern):\n")

def raise_with_large_context_factory():
    big_data = ['x' * 1000] * 1000  # ~1MB
    raise CustomException("Fresh exception")

for i in range(num_raises):
    try:
        raise_with_large_context_factory()
    except CustomException as e:
        tb = e.__traceback__
        depth = 0
        current_tb = tb
        while current_tb:
            depth += 1
            current_tb = current_tb.tb_next
        mem_kb = process.memory_info().rss // 1024
        if i % 100 == 0 or i == num_raises - 1:
            print(f"Raise #{i+1}: Traceback frame count = {depth}, Memory usage = {mem_kb} KB")

print("\nNotice how the traceback frame count and memory usage do NOT accumulate when using a fresh exception each time.")
