#!/usr/bin/env python3
"""Extract UI-facing string values from translation JSON files for spell checking.

Writes one text file per language to build/translations/ with one string
value per line, suitable for pyspelling to check.

Extracts only high-value UI text (titles, descriptions, field labels, error
messages) and skips data_description fields which contain embedded foreign
place names, street names, and enumerated values.
"""

import json
import os


# Keys whose string values should be spell-checked
_CHECK_KEYS = {"title", "description", "message"}

# Keys whose entire subtree should be spell-checked (field labels)
_CHECK_SUBTREE_KEYS = {"data", "error", "abort"}

# Keys to skip entirely (contain mixed-language examples and enumerations)
_SKIP_KEYS = {"data_description", "docs_url"}


def extract_ui_strings(obj, parent_key=None):
    """Extract UI-facing string values from translation JSON."""
    strings = []

    if isinstance(obj, str):
        strings.append(obj)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if key in _SKIP_KEYS:
                continue
            if key in _CHECK_KEYS and isinstance(value, str):
                strings.append(value)
            elif key in _CHECK_SUBTREE_KEYS and isinstance(value, dict):
                # Field labels: extract all string values
                for v in value.values():
                    if isinstance(v, str):
                        strings.append(v)
            elif isinstance(value, dict):
                strings.extend(extract_ui_strings(value, key))
            elif isinstance(value, list):
                for item in value:
                    strings.extend(extract_ui_strings(item, key))
    elif isinstance(obj, list):
        for item in obj:
            strings.extend(extract_ui_strings(item, parent_key))

    return strings


def filter_strings(strings):
    """Filter out non-prose values."""
    filtered = []
    for s in strings:
        s = s.strip()
        if len(s) < 3:
            continue
        if s.startswith("http://") or s.startswith("https://"):
            continue
        # Skip pure template placeholders
        if s.startswith("{") and s.endswith("}"):
            continue
        filtered.append(s)
    return filtered


def main():
    translations_dir = os.path.join(
        "custom_components",
        "waste_collection_schedule",
        "translations",
    )
    output_dir = os.path.join("build", "translations")
    os.makedirs(output_dir, exist_ok=True)

    for filename in sorted(os.listdir(translations_dir)):
        if not filename.endswith(".json"):
            continue

        lang = filename.removesuffix(".json")
        filepath = os.path.join(translations_dir, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        strings = extract_ui_strings(data)
        filtered = filter_strings(strings)

        output_path = os.path.join(output_dir, f"{lang}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(filtered) + "\n")

        print(f"{lang}: {len(filtered)} strings -> {output_path}")


if __name__ == "__main__":
    main()
