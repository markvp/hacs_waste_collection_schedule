#!/usr/bin/env python3
"""Validate guess_icon() accuracy against all existing ICON_MAP definitions.

Reports per-source and overall coverage statistics.

Usage:
    python scripts/validate_icon_migration.py
"""

import ast
import glob
import os
import sys

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "custom_components",
        "waste_collection_schedule",
    ),
)
from waste_collection_schedule.service.icons import guess_icon


def extract_icon_maps():
    """Extract all ICON_MAP dicts from source files."""
    source_dir = "custom_components/waste_collection_schedule/waste_collection_schedule/source"
    results = {}

    for filepath in sorted(glob.glob(f"{source_dir}/*.py")):
        basename = os.path.basename(filepath)
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
                                results[basename] = val
                        except (ValueError, TypeError):
                            pass

    return results


def main():
    icon_maps = extract_icon_maps()

    total_entries = 0
    total_matches = 0
    total_mismatches = 0
    total_no_guess = 0

    perfect_sources = []
    partial_sources = []
    no_match_sources = []

    mismatch_details = []

    for source, icon_map in sorted(icon_maps.items()):
        matches = 0
        mismatches = 0
        no_guess = 0

        for key, expected_icon in icon_map.items():
            if not isinstance(key, str):
                # Skip non-string keys (e.g., integer IDs)
                no_guess += 1
                continue

            guessed = guess_icon(key)

            if guessed == expected_icon:
                matches += 1
            elif guessed is None:
                no_guess += 1
                mismatch_details.append(
                    (source, key, expected_icon, None)
                )
            else:
                mismatches += 1
                mismatch_details.append(
                    (source, key, expected_icon, guessed)
                )

        total = matches + mismatches + no_guess
        total_entries += total
        total_matches += matches
        total_mismatches += mismatches
        total_no_guess += no_guess

        if total == 0:
            continue

        pct = matches / total * 100
        if matches == total:
            perfect_sources.append(source)
        elif matches > 0:
            partial_sources.append((source, matches, total, pct))
        else:
            no_match_sources.append((source, total))

    print("=" * 70)
    print("ICON MIGRATION VALIDATION REPORT")
    print("=" * 70)
    print(f"\nTotal sources with ICON_MAP: {len(icon_maps)}")
    print(f"Total icon entries: {total_entries}")
    print(f"  Correct matches:  {total_matches} ({total_matches/total_entries*100:.1f}%)")
    print(f"  Wrong icon:       {total_mismatches} ({total_mismatches/total_entries*100:.1f}%)")
    print(f"  No guess (None):  {total_no_guess} ({total_no_guess/total_entries*100:.1f}%)")

    print(f"\nPerfect sources (100% match): {len(perfect_sources)}")
    print(f"Partial match sources: {len(partial_sources)}")
    print(f"No match sources: {len(no_match_sources)}")

    if partial_sources:
        print(f"\n--- Partial match sources ---")
        for source, matches, total, pct in sorted(partial_sources, key=lambda x: -x[3]):
            print(f"  {source}: {matches}/{total} ({pct:.0f}%)")

    if no_match_sources:
        print(f"\n--- No match sources ---")
        for source, total in no_match_sources:
            print(f"  {source}: 0/{total}")

    if mismatch_details:
        print(f"\n--- Mismatch details (first 50) ---")
        for source, key, expected, guessed in mismatch_details[:50]:
            if guessed is None:
                print(f"  {source}: '{key}' expected={expected} got=None")
            else:
                print(f"  {source}: '{key}' expected={expected} got={guessed}")

        if len(mismatch_details) > 50:
            print(f"  ... and {len(mismatch_details) - 50} more mismatches")

    # Summary for migration decision
    print(f"\n{'=' * 70}")
    print("MIGRATION SUMMARY")
    print(f"{'=' * 70}")
    print(f"Sources where ICON_MAP can be removed (100% match): {len(perfect_sources)}")
    print(f"Sources needing explicit icon= overrides: {len(partial_sources) + len(no_match_sources)}")
    print(f"Total icon entries that need explicit override: {total_mismatches + total_no_guess}")


if __name__ == "__main__":
    main()
