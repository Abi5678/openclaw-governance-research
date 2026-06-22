"""
Generate paper figures for OpenClaw-Govern:
1. Architecture diagram (as ASCII/SVG)
2. Accuracy bar chart from benchmark CSV data
"""

import matplotlib.pyplot as plt
import numpy as np

# Data from composition benchmark
strategies = ["None", "SARC", "AuthZ", "Guardrail", "ROMA", "Async", "Naive", "OpenClaw"]
accuracy = [1/8, 2/8, 3/8, 2/8, 2/8, 3/8, 1/8, 8/8]
latency_ms = [0.0010, 0.0123, 0.0040, 0.0021, 0.0023, 0.0025, 0.0061, 0.0130]

# Create figure with 2 subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Plot 1: Accuracy bar chart
colors = ['#d3d3d3', '#d3d3d3', '#d3d3d3', '#d3d3d3', '#d3d3d3', '#d3d3d3', '#ff7f7f', '#4CAF50']
bars1 = ax1.bar(strategies, [a*100 for a in accuracy], color=colors, edgecolor='black', linewidth=1.2)

ax1.set_ylabel('Accuracy (%)', fontsize=11)
ax1.set_title('Composition Correctness (8 scenarios)', fontsize=12, fontweight='bold')
ax1.set_ylim(0, 110)
ax1.axhline(y=100, color='green', linestyle='--', linewidth=1.5, alpha=0.7, label='Perfect')
ax1.axhline(y=50, color='gray', linestyle=':', linewidth=1, alpha=0.5)

# Add value labels on bars
for bar, acc in zip(bars1, accuracy):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
             f'{acc*100:.0f}%', ha='center', va='bottom', fontsize=9)

ax1.legend(loc='upper right')
ax1.grid(axis='y', alpha=0.3, linestyle='--')
plt.xticks(rotation=30, ha='right')

# Plot 2: Latency comparison
bars2 = ax2.bar(strategies, latency_ms, color='#6baed6', edgecolor='black', linewidth=1.2)
ax2.set_ylabel('Latency (ms per action)', fontsize=11)
ax2.set_title('Runtime Overhead (real adapters)', fontsize=12, fontweight='bold')
ax2.set_ylim(0, 0.018)

# Highlight OpenClaw overhead
for i, bar in enumerate(bars2):
    if strategies[i] == 'OpenClaw':
        bar.set_color('#fd8d3c')

# Add value labels
for bar, lat in zip(bars2, latency_ms):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.0005,
             f'{lat:.3f}ms', ha='center', va='bottom', fontsize=8)

ax2.axhline(y=0.0010, color='gray', linestyle='--', linewidth=1, alpha=0.7, label='Baseline (no gov)')
ax2.legend(loc='upper left')
ax2.grid(axis='y', alpha=0.3, linestyle='--')
plt.xticks(rotation=30, ha='right')

plt.tight_layout()
plt.savefig('/Users/abishek/Projects/research-publications/openclaw-governance/openclaw-governance-research/figures/benchmark_results.png', dpi=300, bbox_inches='tight')
plt.savefig('/Users/abishek/Projects/research-publications/openclaw-governance/openclaw-governance-research/figures/benchmark_results.svg', format='svg', bbox_inches='tight')
plt.close()

print("✓ Bar charts generated:")
print(f"  - figures/benchmark_results.png (300 DPI)")
print(f"  - figures/benchmark_results.svg (vector)")