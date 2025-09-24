#!/usr/bin/env python3
"""
This script creates a more detailed Medium article-style demonstration of the Python 
exception memory leak, with visual graphs and step-by-step examples.
"""

import os
import sys
import gc
# import time (removed unused import)
import tracemalloc
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import psutil
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


def create_large_context(size_kb=500):
    """Create a large context object that would be captured in a traceback.
    
    Args:
        size_kb: Approximate size in KB for the object
    
    Returns:
        A large object (list of strings)
    """
    # Create a list of strings to approximate the requested size
    return ["x" * 1000 for _ in range(size_kb)]


def format_memory(bytes_value):
    """Format bytes into a human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024 or unit == 'GB':
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024


class ArticleDemo:
    """Demonstration class for the article."""
    
    def __init__(self):
        """Initialize the demo."""
        self.process = psutil.Process(os.getpid())
        tracemalloc.start()
        self.initial_memory = self.get_memory_usage()
    
    def get_memory_usage(self):
        """Get current memory usage in bytes."""
        return self.process.memory_info().rss
    
    def run_singleton_demo(self, iterations=1000, size_kb=500):
        """Run demo with singleton pattern.
        
        Args:
            iterations: Number of exceptions to raise and catch
            size_kb: Size of the context object in KB
        
        Returns:
            Tuple of (memory_usage_data, trend_coefficient)
        """
        print(f"\n{'=' * 80}")
        print("DEMO 1: Singleton Exception Pattern (BAD)")
        print(f"{'=' * 80}")
        print(f"This demo will raise and catch the SAME exception object {iterations} times")
        print(f"Each exception will capture a context of ~{size_kb}KB in its traceback")
        print(f"{'=' * 80}")
        
        # Setup tracking
        tracker = MemoryTracker("singleton_exception")
        tracker.start()
        
        # Create context that will be captured in traceback
        large_context = create_large_context(size_kb)
        print(f"Created context object of ~{sys.getsizeof(large_context) / 1024:.1f}KB")
        
        # Define nested functions to create a deeper stack trace
        def level3():
            # Reference large_context to ensure it's in the traceback
            print(f"Current memory: {format_memory(self.get_memory_usage())}    ", end="\r")
            # Raise the SAME exception object each time
            raise SINGLETON_EXCEPTION
        
        def level2():
            level3()
        
        def level1():
            level2()
        
        # Force garbage collection before starting
        gc.collect()
        starting_memory = self.get_memory_usage()
        print(f"Starting memory usage: {format_memory(starting_memory)}")
        
        # Run the test
        for i in range(iterations):
            try:
                level1()
            except DemoException:
                # Just catch and continue
                if i % 100 == 0 or i == iterations - 1:
                    tracker.record()
                    current = self.get_memory_usage()
                    print(f"Iteration {i+1}/{iterations}: Memory usage = {format_memory(current)} " +
                          f"(+{format_memory(current - starting_memory)})")
        
        # Cleanup
        tracker.stop()
        
        # Calculate trend
        df = pd.DataFrame({
            'x': tracker.timestamps, 
            'y': tracker.memory_usage
        })
        z = np.polyfit(df['x'], df['y'], 1)
        trend = z[0]  # MB/s
        
        print("\nSingleton Exception Demo Complete:")
        print(f"Memory growth trend: {trend:.3f} MB/s")
        print(f"Total memory increase: {format_memory(self.get_memory_usage() - starting_memory)}")
        
        # Save results
        tracker.plot(
            title="Memory Usage with Singleton Exception Pattern",
            save_path="article_singleton_memory.png"
        )
        
        return tracker, trend
    
    def run_factory_demo(self, iterations=1000, size_kb=500):
        """Run demo with factory pattern.
        
        Args:
            iterations: Number of exceptions to raise and catch
            size_kb: Size of the context object in KB
        
        Returns:
            Tuple of (memory_usage_data, trend_coefficient)
        """
        print(f"\n{'=' * 80}")
        print("DEMO 2: Factory Exception Pattern (GOOD)")
        print(f"{'=' * 80}")
        print(f"This demo will raise and catch {iterations} NEW exception objects")
        print(f"Each exception will capture a context of ~{size_kb}KB in its traceback")
        print(f"{'=' * 80}")
        
        # Setup tracking
        tracker = MemoryTracker("factory_exception")
        tracker.start()
        
        # Create context that will be captured in traceback
        large_context = create_large_context(size_kb)
        print(f"Created context object of ~{sys.getsizeof(large_context) / 1024:.1f}KB")
        
        # Define nested functions to create a deeper stack trace
        def level3():
            # Reference large_context to ensure it's in the traceback
            print(f"Current memory: {format_memory(self.get_memory_usage())}    ", end="\r")
            # Create a NEW exception object each time
            raise create_exception()
        
        def level2():
            level3()
        
        def level1():
            level2()
        
        # Force garbage collection before starting
        gc.collect()
        starting_memory = self.get_memory_usage()
        print(f"Starting memory usage: {format_memory(starting_memory)}")
        
        # Run the test
        for i in range(iterations):
            try:
                level1()
            except DemoException:
                # Just catch and continue
                if i % 100 == 0 or i == iterations - 1:
                    tracker.record()
                    current = self.get_memory_usage()
                    print(f"Iteration {i+1}/{iterations}: Memory usage = {format_memory(current)} " +
                          f"(+{format_memory(current - starting_memory)})")
        
        # Cleanup
        tracker.stop()
        
        # Calculate trend
        df = pd.DataFrame({
            'x': tracker.timestamps, 
            'y': tracker.memory_usage
        })
        z = np.polyfit(df['x'], df['y'], 1)
        trend = z[0]  # MB/s
        
        print("\nFactory Exception Demo Complete:")
        print(f"Memory growth trend: {trend:.3f} MB/s")
        print(f"Total memory increase: {format_memory(self.get_memory_usage() - starting_memory)}")
        
        # Save results
        tracker.plot(
            title="Memory Usage with Factory Exception Pattern",
            save_path="article_factory_memory.png"
        )
        
        return tracker, trend
    
    def create_comparison_chart(self, singleton_tracker, factory_tracker):
        """Create a side-by-side comparison chart.
        
        Args:
            singleton_tracker: Memory tracker for singleton demo
            factory_tracker: Memory tracker for factory demo
        """
        plt.figure(figsize=(12, 8))
        
        # Plot singleton data (normalized to start at 0)
        singleton_data = pd.DataFrame({
            'time': singleton_tracker.timestamps,
            'memory': singleton_tracker.memory_usage
        })
        singleton_data['normalized'] = singleton_data['memory'] - singleton_data['memory'].iloc[0]
        plt.plot(singleton_data['time'], singleton_data['normalized'], 'ro-', 
                 label='Singleton Pattern (Bad)', markersize=4)
        
        # Plot factory data (normalized to start at 0)
        factory_data = pd.DataFrame({
            'time': factory_tracker.timestamps,
            'memory': factory_tracker.memory_usage
        })
        factory_data['normalized'] = factory_data['memory'] - factory_data['memory'].iloc[0]
        plt.plot(factory_data['time'], factory_data['normalized'], 'go-', 
                 label='Factory Pattern (Good)', markersize=4)
        
        # Add trend lines
        if len(singleton_data) > 1:
            z = np.polyfit(singleton_data['time'], singleton_data['normalized'], 1)
            p = np.poly1d(z)
            plt.plot(singleton_data['time'], p(singleton_data['time']), "r--", alpha=0.7,
                     label=f"Singleton Trend: {z[0]:.2f} MB/s")
        
        if len(factory_data) > 1:
            z = np.polyfit(factory_data['time'], factory_data['normalized'], 1)
            p = np.poly1d(z)
            plt.plot(factory_data['time'], p(factory_data['time']), "g--", alpha=0.7,
                     label=f"Factory Trend: {z[0]:.2f} MB/s")
        
        # Add styling
        plt.title("Memory Growth Comparison: Singleton vs Factory Exceptions", fontsize=16)
        plt.xlabel("Time (seconds)", fontsize=14)
        plt.ylabel("Memory Growth (MB)", fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(fontsize=12)
        plt.tight_layout()
        
        # Save the plot
        plt.savefig("article_comparison.png", dpi=300, bbox_inches='tight')
        print("\nComparison chart saved to article_comparison.png")


if __name__ == "__main__":
    # Get number of iterations
    iterations = 1000
    if len(sys.argv) > 1:
        try:
            iterations = int(sys.argv[1])
        except ValueError:
            print(f"Invalid iterations: {sys.argv[1]}. Using default: 1000")
    
    # Run the demos
    demo = ArticleDemo()
    singleton_tracker, singleton_trend = demo.run_singleton_demo(iterations)
    factory_tracker, factory_trend = demo.run_factory_demo(iterations)
    
    # Create comparison visualization
    demo.create_comparison_chart(singleton_tracker, factory_tracker)
    
    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY: Exception Memory Leak Demonstration")
    print(f"{'=' * 80}")
    print(f"Singleton Pattern (Bad) memory growth rate: {singleton_trend:.3f} MB/s")
    print(f"Factory Pattern (Good) memory growth rate: {factory_trend:.3f} MB/s")
    print(f"Difference: {singleton_trend - factory_trend:.3f} MB/s")
    print(f"{'=' * 80}")
    print("Article-ready visualization images:")
    print("1. article_singleton_memory.png - Singleton Exception Memory Usage")
    print("2. article_factory_memory.png - Factory Exception Memory Usage")
    print("3. article_comparison.png - Side-by-side comparison")
    print(f"{'=' * 80}")