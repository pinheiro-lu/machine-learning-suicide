import pandas as pd
from src.feature_selection import build_code_to_name, find_highly_correlated, drop_correlated_features, write_correlated_pairs
from collections import defaultdict, deque

# Load merged data
df = pd.read_csv('data/processed/merged_data_nohighmissing_rows.csv')

# Load code-to-name mapping
code_to_name = build_code_to_name('data/raw/wdi_metadata.csv')

# Find highly correlated pairs
pairs = find_highly_correlated(df, threshold=0.9)

# Drop features based on completeness (keep the one with more data in each pair)
reduced_df, dropped, tied_pairs = drop_correlated_features(df, pairs, strategy='completeness')

print(f"Dropped features: {dropped}")
print(f"Total features after dropping: {len(reduced_df.columns)-3}")
reduced_df.to_csv('data/processed/merged_data_dedup.csv', index=False)

# --- New logic: Find sets and minimum correlation in each set ---
# Build graph from tied pairs
adj = defaultdict(set)
pair_corr = {}
for col1, col2 in tied_pairs:
    # Find the actual correlation value from pairs
    corr = None
    for a, b, c in pairs:
        if (a == col1 and b == col2) or (a == col2 and b == col1):
            corr = c
            break
    adj[col1].add(col2)
    adj[col2].add(col1)
    pair_corr[frozenset([col1, col2])] = abs(corr) if corr is not None else None

# Find connected components (sets)
visited = set()
sets = []
for node in adj:
    if node not in visited:
        q = deque([node])
        comp = set()
        while q:
            n = q.popleft()
            if n not in visited:
                visited.add(n)
                comp.add(n)
                q.extend(adj[n] - visited)
        sets.append(comp)
print(sets)
# For each set, find the minimum correlation among all pairs in the set (compute all pairwise correlations)
with open('data/interim/remaining_correlated_sets.txt', 'w') as f:
    if sets:
        # Compute correlation matrix for all numeric columns
        numeric_df = df.select_dtypes(include='number')
        corr_matrix = numeric_df.corr().abs()
        for i, s in enumerate(sets, 1):
            features = sorted(s)
            # All unique pairs in the set
            pairs_in_set = [(a, b) for idx, a in enumerate(features) for b in features[idx+1:]]
            # Compute all correlations for these pairs
            corrs = [corr_matrix.loc[a, b] for a, b in pairs_in_set if a in corr_matrix.columns and b in corr_matrix.columns]
            min_corr = min(corrs) if corrs else None
            f.write(f"Set {i} (size {len(s)}):\n")
            for feat in features:
                f.write(f"  {feat} ({code_to_name.get(feat, feat)})\n")
            if min_corr is not None:
                f.write(f"  Least |correlation| in set: {min_corr:.4f}\n\n")
            else:
                f.write("  No correlation value found for this set.\n\n")
    else:
        f.write("No correlated sets found.\n")

# # --- Find a maximum independent set (greedy) ---
# # Build undirected graph from tied pairs
# all_nodes = set()
# for col1, col2 in tied_pairs:
#     all_nodes.add(col1)
#     all_nodes.add(col2)
#     adj[col1].add(col2)
#     adj[col2].add(col1)

# independent_set = set()
# used = set()
# for node in sorted(all_nodes):
#     if node not in used:
#         independent_set.add(node)
#         used.add(node)
#         used.update(adj[node])

# with open('data/interim/independent_set.txt', 'w') as f:
#     f.write("Maximum independent set (no two features are highly correlated):\n")
#     for feat in sorted(independent_set):
#         f.write(f"{feat} ({code_to_name.get(feat, feat)})\n")
#     f.write(f"\nTotal features kept: {len(independent_set)}\n")

# # Drop columns not in the independent set and save the final decorrelated dataframe
# # Ensure all uncorrelated features are also included
# all_tied = set()
# for col1, col2 in tied_pairs:
#     all_tied.add(col1)
#     all_tied.add(col2)
# # Features not involved in any tied pair
# uncorrelated_features = [col for col in reduced_df.columns if col not in all_tied]
# # Final set: independent set + uncorrelated features, only those present in reduced_df
# # Preserve the original column order from reduced_df
# final_features = [col for col in reduced_df.columns if col in independent_set or col not in all_tied]
# final_df = reduced_df[final_features]
# final_df.to_csv('data/processed/merged_data_independent.csv', index=False)
# print(f"Final decorrelated data saved to data/processed/merged_data_independent.csv with {len(final_df.columns)} columns.")

# Explanation:
# - Maximum independent set: largest set of features with no high-correlation pairs between them (no redundancy).
# - Minimum vertex cover: smallest set of features that, if removed, breaks all high-correlation pairs.
# - By keeping the independent set, you ensure all remaining features are mutually uncorrelated above the threshold.
# - The greedy algorithm may not always find the absolute maximum, but is efficient and effective for practical use.
