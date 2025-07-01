import pandas as pd
from src.feature_selection import find_highly_correlated, build_code_to_name
from collections import defaultdict

# Load the cleaned data (after all other removals)
df = pd.read_csv('data/processed/merged_data_after_to_remove_low_variance.csv')
print(f"Number of features before independent set selection: {df.shape[1]}")

# Find highly correlated pairs (after removal)
pairs = find_highly_correlated(df, threshold=0.9)

# Build graph of highly correlated features
adj = defaultdict(set)
for a, b, corr in pairs:
    adj[a].add(b)
    adj[b].add(a)

# Only consider nodes that are in the correlation graph
correlated_nodes = set(adj.keys())
# Build a list of correlated nodes sorted by degree (fewest neighbors first)
nodes_by_degree = sorted(correlated_nodes, key=lambda x: len(adj[x]))

# Compute variance for all correlated nodes (numeric only)
numeric_df = df.select_dtypes(include='number')
variances = numeric_df.var()
# Build a list of correlated nodes sorted by degree (fewest neighbors first), then by variance (highest first)
nodes_by_degree_and_variance = sorted(
    correlated_nodes,
    key=lambda x: (len(adj[x]), -variances.get(x, 0))
)

# Greedy maximum independent set algorithm (hybrid: degree, then variance)
independent_set = set()
used = set()
for node in nodes_by_degree_and_variance:
    node_clean = str(node).strip()
    if node_clean not in used:
        independent_set.add(node_clean)
        used.add(node_clean)
        used.update(str(n).strip() for n in adj[node])
        print(f"Added: {node_clean}, used now: {used}")  # Debug
    else:
        print(f"Skipped: {node_clean}, already in used")  # Debug

# Add all features not in any correlated pair (they are independent by definition)
all_features = set(str(col).strip() for col in df.columns)
independent_set.update(all_features - set(str(n).strip() for n in correlated_nodes))

print(f"Maximum independent set (no two features are highly correlated): {len(independent_set)} features.")

# Save the independent set to a file
with open('data/interim/independent_set.txt', 'w') as f:
    f.write("Maximum independent set (no two features are highly correlated):\n")
    for feat in independent_set:
        f.write(f"{feat}\n")
    f.write(f"\nTotal features kept: {len(independent_set)}\n")

# Save the decorrelated dataframe (preserve original order)
final_df = df[[col for col in df.columns if col in independent_set]]
final_df.to_csv('data/processed/merged_data_independent.csv', index=False)
print(f"Saved decorrelated data to data/processed/merged_data_independent.csv with {len(final_df.columns)} columns.")
