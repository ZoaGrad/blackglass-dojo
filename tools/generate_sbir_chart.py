
import matplotlib.pyplot as plt
import numpy as np
import os

# Ensure the output directory exists
output_dir = r"c:\Users\colem\Code\blackglass-shard-alpha\grants"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'sbir_competitive_matrix.png')

# Data from analysis
systems = {
    'RL Systems\n(18 count)': (0.8, 0.3),      # High autonomy, low safety
    'Task Agents\n(10 count)': (0.5, 0.2),     # Med autonomy, low safety  
    'SpiralOS': (0.9, 0.95),                   # High autonomy, HIGH safety
    'Standard AI': (0.4, 0.1)                  # Low autonomy, low safety
}

fig, ax = plt.subplots(figsize=(10, 8))

for name, (auto, safe) in systems.items():
    color = '#FF6B35' if 'SpiralOS' in name else '#4A4A4A'
    size = 400 if 'SpiralOS' in name else 200
    
    # Plot point
    ax.scatter(auto, safe, s=size, c=color, alpha=0.8, edgecolors='black', linewidth=2, zorder=10)
    
    # Add text annotation
    # Offset SpiralOS slightly to not cover the dot
    xytext = (10, 10) if 'SpiralOS' in name else (10, 5)
    
    ax.annotate(name, (auto, safe), xytext=xytext, textcoords='offset points', 
                fontsize=12, weight='bold' if 'SpiralOS' in name else 'normal',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.7))

# Draw Pareto Frontier curve roughly
t = np.linspace(0, 1, 100)
# This is just a visual aid, a simple curve 
# ax.plot(t, t**2, 'k--', alpha=0.2, label='Pareto Frontier') 

ax.set_xlabel('Operational Autonomy (Task Complexity) →', fontsize=14)
ax.set_ylabel('Constitutional Safety (System 5 Veto) →', fontsize=14)
ax.set_title('SpiralOS: The Safety/Autonomy Pareto Frontier', fontsize=16, weight='bold')

# Quadrant labels (optional but helpful)
ax.text(0.9, 0.1, "High Risk\n(RL Agents)", fontsize=10, color='red', alpha=0.5, ha='center')
ax.text(0.1, 0.9, "Bureaucratic\n(Old Guard)", fontsize=10, color='gray', alpha=0.5, ha='center')
ax.text(0.1, 0.1, "Low Utility\n(Chatbots)", fontsize=10, color='gray', alpha=0.5, ha='center')
ax.text(0.9, 0.8, "The Compliance Metabolism\n(Target Zone)", fontsize=10, color='green', alpha=0.5, ha='center')

ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xlim(0, 1.1)
ax.set_ylim(0, 1.1)

# Highlight the SpiralOS zone
circle = plt.Circle((0.9, 0.95), 0.15, color='#FF6B35', alpha=0.1, zorder=1)
ax.add_patch(circle)

plt.tight_layout()
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Chart saved to: {output_path}")
