#!/usr/bin/env python3
"""Split N1 level into 4 sub-levels (1a, 1b, 1c, 1d) while preserving scores."""

import csv
from pathlib import Path

def split_n1_levels():
    """Distribute N1 entries evenly across 1a, 1b, 1c, 1d sub-levels."""
    
    for csv_file in ["source/data/Kanji.csv", "source/data/Vocab.csv"]:
        csv_path = Path(csv_file)
        
        # Read all rows
        rows = []
        fieldnames = []
        with csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            rows = list(reader)
        
        # Count and assign N1 entries
        n1_entries = [i for i, row in enumerate(rows) if row.get("Level") == "1"]
        n1_count = len(n1_entries)
        
        if n1_count == 0:
            print(f"✓ {csv_file}: No N1 entries to split")
            continue
        
        # Distribute evenly: 1a, 1b, 1c, 1d
        sublevel_map = ["1a", "1b", "1c", "1d"]
        for idx, row_idx in enumerate(n1_entries):
            sublevel = sublevel_map[idx % 4]
            rows[row_idx]["Level"] = sublevel
        
        # Write back
        with csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✓ {csv_file}: Split {n1_count} N1 entries into 1a/1b/1c/1d")

if __name__ == "__main__":
    split_n1_levels()
    print("\n✓ N1 split complete!")
