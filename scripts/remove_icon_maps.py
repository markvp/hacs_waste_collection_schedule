#!/usr/bin/env python3
"""Remove or reduce ICON_MAP from all source files.

Strategy:
- Framework now calls guess_icon(t) when icon=None in Collection()
- For each source, compute which ICON_MAP entries guess_icon handles correctly
- Remove those entries from ICON_MAP
- If ICON_MAP becomes empty: remove it entirely + remove icon= from Collection() calls
- If ICON_MAP still has entries: keep it with only the override entries

For sources that iterate ICON_MAP for business logic: flag for manual review.

Usage:
    python scripts/remove_icon_maps.py              # dry run
    python scripts/remove_icon_maps.py --apply      # apply changes
"""

import argparse
import ast
import glob
import os
import re
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


def extract_icon_map(filepath):
    """Extract ICON_MAP dict, start line, end line from a source file."""
    with open(filepath) as f:
        source = f.read()

    if "ICON_MAP" not in source:
        return None, None, None, source

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None, None, None, source

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ICON_MAP":
                    try:
                        val = ast.literal_eval(node.value)
                        if isinstance(val, dict):
                            return val, node.lineno, node.end_lineno, source
                    except (ValueError, TypeError):
                        return None, None, None, source

    return None, None, None, source


def compute_overrides(icon_map):
    """Compute which ICON_MAP entries need to be kept as overrides."""
    overrides = {}
    removed = {}

    for key, expected_icon in icon_map.items():
        if not isinstance(key, str):
            # Non-string keys (e.g., integers) can't be guessed
            overrides[key] = expected_icon
            continue

        guessed = guess_icon(key)
        if guessed == expected_icon:
            removed[key] = expected_icon
        else:
            overrides[key] = expected_icon

    return overrides, removed


def uses_icon_map_for_business_logic(source):
    """Check if source iterates ICON_MAP (used for filtering/validation)."""
    return bool(re.search(r"for\s+.*\bICON_MAP\b", source))


def rebuild_icon_map(overrides):
    """Rebuild a reduced ICON_MAP dict as source code."""
    if not overrides:
        return None

    lines = ["ICON_MAP = {\n"]
    for key in sorted(overrides.keys(), key=lambda x: str(x)):
        value = overrides[key]
        if isinstance(key, str):
            lines.append(f'    "{key}": "{value}",\n')
        else:
            lines.append(f"    {key!r}: \"{value}\",\n")
    lines.append("}\n")
    return "".join(lines)


def remove_icon_map_block(source, start_line, end_line):
    """Remove the ICON_MAP block from source code."""
    lines = source.splitlines(True)
    new_lines = lines[:start_line - 1] + lines[end_line:]

    # Clean up extra blank lines
    result = []
    prev_blank = False
    for line in new_lines:
        is_blank = line.strip() == ""
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank

    return "".join(result)


def replace_icon_map_block(source, start_line, end_line, new_block):
    """Replace the ICON_MAP block with a reduced version."""
    lines = source.splitlines(True)
    if new_block is None:
        new_lines = lines[:start_line - 1] + lines[end_line:]
    else:
        new_lines = lines[:start_line - 1] + [new_block] + lines[end_line:]

    # Clean up extra blank lines
    result = []
    prev_blank = False
    for line in new_lines:
        is_blank = line.strip() == ""
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank

    return "".join(result)


def remove_icon_param_from_collections(source):
    """Remove icon=ICON_MAP.get(...) from Collection() calls."""
    # Pattern: icon=ICON_MAP.get(anything)
    # Also handle: , icon=ICON_MAP.get(anything)) and ,\n            icon=ICON_MAP.get(anything))
    patterns = [
        # icon=ICON_MAP.get(...) at end of argument list
        (r",\s*icon\s*=\s*ICON_MAP\.get\([^)]*\)", ""),
        # icon=ICON_MAP.get(...), at start/middle of argument list
        (r"icon\s*=\s*ICON_MAP\.get\([^)]*\)\s*,\s*", ""),
        # icon=ICON_MAP[...] at end
        (r",\s*icon\s*=\s*ICON_MAP\[[^\]]*\]", ""),
        # icon=ICON_MAP[...], at start/middle
        (r"icon\s*=\s*ICON_MAP\[[^\]]*\]\s*,\s*", ""),
    ]

    for pattern, replacement in patterns:
        source = re.sub(pattern, replacement, source)

    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    args = parser.parse_args()

    source_dir = "custom_components/waste_collection_schedule/waste_collection_schedule/source"
    files = sorted(glob.glob(f"{source_dir}/*.py"))

    fully_removed = 0
    reduced = 0
    manual_review = 0
    skipped = 0

    for filepath in files:
        basename = os.path.basename(filepath)
        icon_map, start_line, end_line, source = extract_icon_map(filepath)

        if icon_map is None:
            continue

        # Check for business logic usage
        if uses_icon_map_for_business_logic(source):
            manual_review += 1
            print(f"MANUAL  {basename} (iterates ICON_MAP for business logic)")
            continue

        overrides, removed_entries = compute_overrides(icon_map)

        if not overrides:
            # All entries handled by guess_icon - remove entirely
            fully_removed += 1
            total = len(icon_map)
            print(f"REMOVE  {basename} ({total} entries all covered by guess_icon)")
            if args.apply:
                new_source = replace_icon_map_block(source, start_line, end_line, None)
                new_source = remove_icon_param_from_collections(new_source)
                with open(filepath, "w") as f:
                    f.write(new_source)
        else:
            reduced += 1
            kept = len(overrides)
            total = len(icon_map)
            print(f"REDUCE  {basename} ({total} → {kept} override entries)")
            if args.apply:
                new_block = rebuild_icon_map(overrides)
                new_source = replace_icon_map_block(
                    source, start_line, end_line, new_block
                )
                with open(filepath, "w") as f:
                    f.write(new_source)

    print(f"\nSummary:")
    print(f"  Fully removed:  {fully_removed}")
    print(f"  Reduced:        {reduced}")
    print(f"  Manual review:  {manual_review}")
    print(f"  Total:          {fully_removed + reduced + manual_review}")

    if not args.apply:
        print("\nDry run. Use --apply to make changes.")


if __name__ == "__main__":
    main()
