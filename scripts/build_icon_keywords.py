#!/usr/bin/env python3
"""Build icon keyword database from all ICON_MAP definitions across source files.

Extracts all ICON_MAP entries, groups by icon value, and generates
keyword patterns for each icon.

Usage:
    python scripts/build_icon_keywords.py
"""

import ast
import glob
import json
import re
from collections import defaultdict


def extract_icon_maps():
    """Extract all ICON_MAP dicts from source files."""
    source_dir = "custom_components/waste_collection_schedule/waste_collection_schedule/source"
    all_entries = defaultdict(set)  # icon -> set of keys

    for filepath in sorted(glob.glob(f"{source_dir}/*.py")):
        try:
            with open(filepath) as f:
                source = f.read()
        except Exception:
            continue

        if "ICON_MAP" not in source:
            continue

        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "ICON_MAP":
                        try:
                            val = ast.literal_eval(node.value)
                            if isinstance(val, dict):
                                for key, icon in val.items():
                                    if isinstance(key, str) and isinstance(icon, str):
                                        all_entries[icon].add(key.lower().strip())
                        except (ValueError, TypeError):
                            pass

    return all_entries


def build_keyword_database(all_entries):
    """Build keyword patterns from icon entries.

    For each icon, extract common substrings/words that can be used
    for substring matching against waste type names.
    """
    # For each icon, we want the set of keywords that appear in the keys
    keyword_db = {}

    for icon, keys in sorted(all_entries.items()):
        # Split all keys into individual words
        words = set()
        for key in keys:
            # Split on common delimiters
            parts = re.split(r'[\s\-_/,;:()]+', key.lower())
            for part in parts:
                if len(part) >= 3:  # Skip very short fragments
                    words.add(part)

        keyword_db[icon] = {
            "keys": sorted(keys),
            "words": sorted(words),
            "count": len(keys),
        }

    return keyword_db


def generate_guess_icon_keywords(keyword_db):
    """Generate the ICON_KEYWORDS dict for guess_icon().

    Strategy: For each icon, find the keywords that are most distinctive
    (appear in keys for this icon but not others).
    """
    # Collect all words across all icons
    icon_words = {}
    for icon, data in keyword_db.items():
        icon_words[icon] = set(data["words"])

    # For each icon, find words that are unique or mostly unique to it
    result = {}
    for icon, words in icon_words.items():
        # Include full keys as exact-match patterns too
        full_keys = set(keyword_db[icon]["keys"])

        # Also include the original full keys for exact substring matching
        result[icon] = {
            "keywords": sorted(full_keys),
            "count": keyword_db[icon]["count"],
        }

    return result


def main():
    all_entries = extract_icon_maps()

    print(f"Total unique icons: {len(all_entries)}")
    print(f"Total key-icon pairs: {sum(len(v) for v in all_entries.values())}")
    print()

    # Sort by frequency
    by_count = sorted(all_entries.items(), key=lambda x: -len(x[1]))

    print("Top 20 icons by frequency:")
    for icon, keys in by_count[:20]:
        print(f"  {icon}: {len(keys)} keys")
        # Show sample keys
        sample = sorted(keys)[:5]
        for k in sample:
            print(f"    - {k}")
        if len(keys) > 5:
            print(f"    ... and {len(keys) - 5} more")
    print()

    # Generate the keyword database
    keyword_db = build_keyword_database(all_entries)

    # Output the raw data for manual review
    output = {
        icon: {
            "keys": sorted(keys),
            "count": len(keys),
        }
        for icon, keys in sorted(all_entries.items(), key=lambda x: -len(x[1]))
    }

    with open("scripts/icon_keywords_raw.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Raw keyword data written to scripts/icon_keywords_raw.json")


if __name__ == "__main__":
    main()
