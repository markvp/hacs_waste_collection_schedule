#!/usr/bin/env python3
"""Extract string values from translation JSON files for spell checking.

Writes one text file per language to build/translations/ with one string
value per line, suitable for pyspelling to check.
"""

import json
import os
import sys


def extract_strings(obj):
    """Recursively extract all string values from nested JSON."""
    strings = []
    if isinstance(obj, str):
        strings.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            strings.extend(extract_strings(v))
    elif isinstance(obj, list):
        for item in obj:
            strings.extend(extract_strings(item))
    return strings


def main():
    translations_dir = os.path.join(
        "custom_components",
        "waste_collection_schedule",
        "translations",
    )
    output_dir = os.path.join("build", "translations")
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(translations_dir):
        if not filename.endswith(".json"):
            continue

        lang = filename.removesuffix(".json")
        filepath = os.path.join(translations_dir, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        strings = extract_strings(data)

        # Filter out very short strings, pure placeholders, and URL-like values
        filtered = []
        for s in strings:
            s = s.strip()
            if len(s) < 3:
                continue
            if s.startswith("http://") or s.startswith("https://"):
                continue
            if s.startswith("{") and s.endswith("}"):
                continue
            filtered.append(s)

        output_path = os.path.join(output_dir, f"{lang}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(filtered) + "\n")

        print(f"{lang}: {len(filtered)} strings -> {output_path}")


if __name__ == "__main__":
    main()
