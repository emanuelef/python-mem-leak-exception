#!/usr/bin/env python3
"""
Script to visualize and compare memory usage between different implementations.
"""

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def compare_implementations():
    """Compare memory usage between good and bad implementations."""
    # Find the latest CSV files
    bad_csvs = sorted(glob.glob("bad_implementation_memory_*.csv"))
    good_csvs = sorted(glob.glob("good_implementation_memory_*.csv"))
    
    if not bad_csvs or not good_csvs:
        print("Could not find memory usage CSV files.")
        print("Please run test_bad_implementation.py and test_good_implementation.py first.")
        return
    
    bad_csv = bad_csvs[-1]
    good_csv = good_csvs[-1]
    
    # Load data
    try:
        bad_data = pd.read_csv(bad_csv)
        good_data = pd.read_csv(good_csv)
    except Exception as e:
        print(f"Error loading CSV files: {e}")
        return
    
    # Create comparison plot
    plt.figure(figsize=(12, 8))
    
    # Plot both datasets
    plt.plot(bad_data['timestamp'], bad_data['memory_mb'], 
             'ro-', label='Bad Implementation (Singleton)', markersize=4)
    plt.plot(good_data['timestamp'], good_data['memory_mb'], 
             'go-', label='Good Implementation (Factory Method)', markersize=4)
    
    # Add trend lines
    if len(bad_data) > 1:
        z = np.polyfit(bad_data['timestamp'], bad_data['memory_mb'], 1)
        p = np.poly1d(z)
        plt.plot(bad_data['timestamp'], p(bad_data['timestamp']), "r--", alpha=0.7, 
                label=f"Bad Trend: {z[0]:.2f} MB/s")
    
    if len(good_data) > 1:
        z = np.polyfit(good_data['timestamp'], good_data['memory_mb'], 1)
        p = np.poly1d(z)
        plt.plot(good_data['timestamp'], p(good_data['timestamp']), "g--", alpha=0.7, 
                label=f"Good Trend: {z[0]:.2f} MB/s")
    
    # Styling
    plt.title("Memory Usage Comparison: Singleton vs Factory Method Exceptions", fontsize=16)
    plt.xlabel("Time (seconds)", fontsize=14)
    plt.ylabel("Memory Usage (MB)", fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    
    # Add annotations with statistics
    bad_initial = bad_data['memory_mb'].iloc[0]
    bad_final = bad_data['memory_mb'].iloc[-1]
    bad_growth = bad_final - bad_initial
    
    good_initial = good_data['memory_mb'].iloc[0]
    good_final = good_data['memory_mb'].iloc[-1]
    good_growth = good_final - good_initial
    
    stats_text = (
        f"Bad Implementation:\n"
        f"  Initial: {bad_initial:.2f} MB\n"
        f"  Final: {bad_final:.2f} MB\n"
        f"  Growth: {bad_growth:.2f} MB\n\n"
        f"Good Implementation:\n"
        f"  Initial: {good_initial:.2f} MB\n"
        f"  Final: {good_final:.2f} MB\n"
        f"  Growth: {good_growth:.2f} MB\n\n"
        f"Difference: {bad_growth - good_growth:.2f} MB"
    )
    
    plt.annotate(stats_text, xy=(0.02, 0.97), xycoords='axes fraction',
                 va='top', ha='left', bbox=dict(boxstyle='round', fc='white', alpha=0.7),
                 fontsize=10)
    
    # Save the comparison plot
    plt.tight_layout()
    plt.savefig("memory_usage_comparison.png", dpi=300, bbox_inches='tight')
    print("Saved memory usage comparison to memory_usage_comparison.png")
    
    # Create a second plot with normalized starting points
    plt.figure(figsize=(12, 8))
    
    # Normalize data to start from 0
    bad_data['normalized_mb'] = bad_data['memory_mb'] - bad_data['memory_mb'].iloc[0]
    good_data['normalized_mb'] = good_data['memory_mb'] - good_data['memory_mb'].iloc[0]
    
    # Plot normalized data
    plt.plot(bad_data['timestamp'], bad_data['normalized_mb'], 
             'ro-', label='Bad Implementation (Singleton)', markersize=4)
    plt.plot(good_data['timestamp'], good_data['normalized_mb'], 
             'go-', label='Good Implementation (Factory Method)', markersize=4)
    
    # Add trend lines
    if len(bad_data) > 1:
        z = np.polyfit(bad_data['timestamp'], bad_data['normalized_mb'], 1)
        p = np.poly1d(z)
        plt.plot(bad_data['timestamp'], p(bad_data['timestamp']), "r--", alpha=0.7, 
                label=f"Bad Trend: {z[0]:.2f} MB/s")
    
    if len(good_data) > 1:
        z = np.polyfit(good_data['timestamp'], good_data['normalized_mb'], 1)
        p = np.poly1d(z)
        plt.plot(good_data['timestamp'], p(good_data['timestamp']), "g--", alpha=0.7, 
                label=f"Good Trend: {z[0]:.2f} MB/s")
    
    # Styling
    plt.title("Normalized Memory Growth Comparison", fontsize=16)
    plt.xlabel("Time (seconds)", fontsize=14)
    plt.ylabel("Memory Growth (MB)", fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    
    # Save the normalized plot
    plt.tight_layout()
    plt.savefig("normalized_memory_comparison.png", dpi=300, bbox_inches='tight')
    print("Saved normalized memory comparison to normalized_memory_comparison.png")


if __name__ == "__main__":
    compare_implementations()