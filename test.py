import json

# Load JSON data from a file named data.json
with open('data.json', 'r') as file:
    data = json.load(file)

# Extract all index values as integers
indices = sorted(int(track["index"]) for track in data["tracks"])

# Find the missing numbers in the sequence
missing_indices = [i for i in range(indices[0], indices[-1] + 1) if i not in indices]

print("Missing Songs:", missing_indices)
