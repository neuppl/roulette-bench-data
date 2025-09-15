import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

base_dir = "results"
records = []

def extract_timestamp(folder_name):
    """
    Extract timestamp from folder name like 'run_2025-09-07_18-27-28'
    Returns a datetime object for sorting.
    """
    try:
        # Extract the timestamp part after 'run_'
        timestamp_str = folder_name.split('run_')[1]
        # Parse the timestamp (assuming format: YYYY-MM-DD_HH-MM-SS)
        return datetime.strptime(timestamp_str, '%Y-%m-%d_%H-%M-%S')
    except (IndexError, ValueError):
        # If parsing fails, return the folder name as-is for fallback sorting
        return datetime.min

# Get and sort folders by timestamp
folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
folders.sort(key=extract_timestamp)

# Process folders in sorted order
for folder in folders:
    folder_path = os.path.join(base_dir, folder)
    for fname in os.listdir(folder_path):
        if fname.endswith(".json"):
            with open(os.path.join(folder_path, fname)) as f:
                data = json.load(f)
                data["run"] = folder  # add folder as run label
                data["filename"] = fname
                records.append(data)

df = pd.DataFrame(records)
print(df.head())

# Convert run column to categorical with the sorted order to maintain it in plots
df['run'] = pd.Categorical(df['run'], categories=folders, ordered=True)

# Sort dataframe by run to ensure correct order
df = df.sort_values('run')

for filename, group in df.groupby("filename"):
    plt.figure(figsize=(10, 6))  # Increased figure size for better readability
    
    # Sort group by run to ensure correct plotting order
    group = group.sort_values('run')
    
    # Use index positions for x-axis to ensure proper spacing
    x_positions = range(len(group))
    
    plt.plot(x_positions, group["real_time_ms"], marker="o", label="real_time_ms")
    plt.plot(x_positions, group["cpu_time_ms"], marker="o", label="cpu_time_ms")
    plt.plot(x_positions, group["gc_time_ms"], marker="o", label="gc_time_ms")
    
    plt.title(f"Timing for {filename}")
    plt.xlabel("Run")
    plt.ylabel("Time (ms)")
    plt.legend()
    
    # Set x-tick labels to the run names, but only show every nth label if there are many
    run_labels = group["run"].tolist()
    if len(run_labels) > 10:
        # Show every 2nd or 3rd label if there are many runs
        step = max(1, len(run_labels) // 10)
        tick_positions = list(range(0, len(run_labels), step))
        tick_labels = [run_labels[i] for i in tick_positions]
        plt.xticks(tick_positions, tick_labels, rotation=45, ha='right')
    else:
        plt.xticks(x_positions, run_labels, rotation=45, ha='right')
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{filename[:-5]}.svg", dpi=100, bbox_inches='tight', format='svg')