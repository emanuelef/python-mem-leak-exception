#!/usr/bin/env python3
"""
Memory tracking utility to monitor and record memory usage during tests.
"""

import os
import time
import psutil
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy as np


class MemoryTracker:
    """Track memory usage over time."""
    
    def __init__(self, label="test"):
        """Initialize the memory tracker.
        
        Args:
            label: String identifier for this tracking session
        """
        self.label = label
        self.process = psutil.Process(os.getpid())
        self.timestamps = []
        self.memory_usage = []
        self.start_time = None
    
    def start(self):
        """Start tracking memory usage."""
        self.start_time = time.time()
        self.timestamps = []
        self.memory_usage = []
        self._record_point()
        
    def _record_point(self):
        """Record the current memory usage."""
        # Force garbage collection to get more accurate measurements
        import gc
        gc.collect()
        
        # Get memory info
        memory_mb = self.process.memory_info().rss / (1024 * 1024)
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        
        # Record data point
        self.timestamps.append(elapsed_time)
        self.memory_usage.append(memory_mb)
    
    def record(self):
        """Record the current memory usage."""
        self._record_point()
        
    def stop(self):
        """Stop tracking and record final data point."""
        self._record_point()
    
    def save_data(self, filename=None):
        """Save memory usage data to a CSV file.
        
        Args:
            filename: Optional filename, defaults to timestamp-based name
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"memory_usage_{self.label}_{timestamp}.csv"
        
        data = {
            "timestamp": self.timestamps,
            "memory_mb": self.memory_usage
        }
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return filename
    
    def plot(self, title=None, save_path=None):
        """Plot memory usage over time.
        
        Args:
            title: Optional title for the plot
            save_path: Optional path to save the plot image
        """
        plt.figure(figsize=(10, 6))
        plt.plot(self.timestamps, self.memory_usage, marker='o', linestyle='-', markersize=3)
        
        plt.xlabel('Time (seconds)')
        plt.ylabel('Memory Usage (MB)')
        
        if title:
            plt.title(title)
        else:
            plt.title(f'Memory Usage Over Time: {self.label}')
        
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add a trend line
        if len(self.timestamps) > 1:
            z = np.polyfit(self.timestamps, self.memory_usage, 1)
            p = np.poly1d(z)
            plt.plot(self.timestamps, p(self.timestamps), "r--", alpha=0.7, 
                    label=f"Trend: {z[0]:.2f} MB/s")
            plt.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        
        return plt.gcf()


if __name__ == "__main__":
    # Demo of the memory tracker
    tracker = MemoryTracker("demo")
    tracker.start()
    
    # Allocate some memory over time
    data = []
    for i in range(10):
        data.append("x" * 1000000)  # Allocate ~1MB
        tracker.record()
        time.sleep(0.5)
    
    tracker.stop()
    tracker.plot(save_path="demo_memory_usage.png")
    tracker.save_data("demo_memory_usage.csv")