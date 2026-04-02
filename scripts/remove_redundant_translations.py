#!/usr/bin/env python3
"""Remove redundant PARAM_TRANSLATIONS from source files.

For each source file that defines PARAM_TRANSLATIONS:
- If ALL entries are covered by default_translations.py → remove entire block
- If SOME entries match → remove matching entries, keep source-specific ones

Usage:
    python scripts/remove_redundant_translations.py          # dry run
    python scripts/remove_redundant_translations.py --apply  # apply changes
"""

import argparse
import ast
import glob
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from default_translations import DEFAULT_PARAM_TRANSLATIONS


def get_param_translations_from_source(filepath):
    """Extract PARAM_TRANSLATIONS dict from a source file using AST."""
    with open(filepath) as f:
        source = f.read()

    if "PARAM_TRANSLATIONS" not in source:
        return None, None, None

    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PARAM_TRANSLATIONS":
                    try:
                        val = ast.literal_eval(node.value)
                        if isinstance(val, dict):
                            return val, node.lineno, node.end_lineno
                    except (ValueError, TypeError):
                        return None, None, None
    return None, None, None


def is_redundant(translations):
    """Check which entries in PARAM_TRANSLATIONS are covered by defaults."""
    redundant = {}
    custom = {}

    for lang, params in translations.items():
        if lang not in DEFAULT_PARAM_TRANSLATIONS:
            custom.setdefault(lang, {}).update(params)
            continue

        for param, value in params.items():
            default_value = DEFAULT_PARAM_TRANSLATIONS.get(lang, {}).get(param)
            if default_value is not None and default_value == value:
                redundant.setdefault(lang, {})[param] = value
            else:
                custom.setdefault(lang, {})[param] = value

    return redundant, custom


def remove_translations_block(filepath, start_line, end_line):
    """Remove the entire PARAM_TRANSLATIONS block from a file."""
    with open(filepath) as f:
        lines = f.readlines()

    # Find the start of the assignment (might include preceding blank line)
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

    with open(filepath, "w") as f:
        f.writelines(result)


def rebuild_translations_block(custom):
    """Rebuild a PARAM_TRANSLATIONS dict with only custom entries."""
    # Remove empty language dicts
    custom = {lang: params for lang, params in custom.items() if params}
    if not custom:
        return None

    lines = ["PARAM_TRANSLATIONS = {\n"]
    for lang in sorted(custom.keys()):
        lines.append(f'    "{lang}": {{\n')
        for param in sorted(custom[lang].keys()):
            value = custom[lang][param]
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'        "{param}": "{escaped}",\n')
        lines.append("    },\n")
    lines.append("}\n")
    return "".join(lines)


def replace_translations_block(filepath, start_line, end_line, new_block):
    """Replace the PARAM_TRANSLATIONS block with a reduced version."""
    with open(filepath) as f:
        lines = f.readlines()

    if new_block is None:
        # Remove entirely
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

    with open(filepath, "w") as f:
        f.writelines(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    args = parser.parse_args()

    source_dir = "custom_components/waste_collection_schedule/waste_collection_schedule/source"
    files = sorted(glob.glob(f"{source_dir}/*.py"))

    fully_removed = 0
    partially_reduced = 0
    kept = 0

    for filepath in files:
        translations, start_line, end_line = get_param_translations_from_source(filepath)
        if translations is None:
            continue

        redundant, custom = is_redundant(translations)

        basename = os.path.basename(filepath)
        has_custom = any(custom.values())

        if not has_custom:
            # All entries are redundant — remove entire block
            fully_removed += 1
            total_entries = sum(len(v) for v in translations.values())
            print(f"REMOVE  {basename} ({total_entries} entries fully covered by defaults)")
            if args.apply:
                replace_translations_block(filepath, start_line, end_line, None)
        elif redundant:
            # Some entries redundant, some custom
            redundant_count = sum(len(v) for v in redundant.values())
            custom_count = sum(len(v) for v in custom.values())
            partially_reduced += 1
            print(f"REDUCE  {basename} (remove {redundant_count}, keep {custom_count} custom entries)")
            if args.apply:
                new_block = rebuild_translations_block(custom)
                replace_translations_block(filepath, start_line, end_line, new_block)
        else:
            kept += 1
            total_entries = sum(len(v) for v in translations.values())
            print(f"KEEP    {basename} ({total_entries} entries all custom)")

    print(f"\nSummary:")
    print(f"  Fully removed:     {fully_removed}")
    print(f"  Partially reduced: {partially_reduced}")
    print(f"  Kept unchanged:    {kept}")
    print(f"  Total with PARAM_TRANSLATIONS: {fully_removed + partially_reduced + kept}")

    if not args.apply:
        print("\nDry run. Use --apply to make changes.")


if __name__ == "__main__":
    main()
