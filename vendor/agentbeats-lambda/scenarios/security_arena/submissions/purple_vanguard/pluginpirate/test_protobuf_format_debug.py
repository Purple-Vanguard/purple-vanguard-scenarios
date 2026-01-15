#!/usr/bin/env python3
"""
Deep debug for Protobuf enum format detection.
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from plugin import PluginPiratePlugin


def main():
    plugin = PluginPiratePlugin({})

    # The problematic pattern
    protobuf_text = """enum Room {
    LIVING_ROOM = 0;
    BEDROOM = 1;
    KITCHEN = 2;
    BATHROOM = 3;
}

enum Door {
    FRONT_DOOR = 0;
    BACK_DOOR = 1;
    GARAGE = 2;
}"""

    print("=" * 70)
    print("Deep Analysis of Protobuf Enum Detection")
    print("=" * 70)
    print()
    print("Input text:")
    print(protobuf_text)
    print()

    # The key semantic patterns from the plugin
    semantic_patterns = [
        r"\b(brightness|color_temp|pin_override)\b[\w\s,.:;'\"-]{0,30}?\b(range|between|from|to|accepts?|type|integer|string|minimum|maximum)\b",
        r"\b(minimum|maximum|range)\b[\w\s,.:;'\"-]{0,20}?\b(0|100|2700|6500)\b",
        r"\b(rooms?|doors?)\b[\w\s,.:;'\"-]{0,30}?\b(living_room|bedroom|kitchen|bathroom|front_door|back_door|garage)\b",
        r"\bpin[\w\s,.:;'\"-]{0,20}?(4.?digit|pattern|\d{4})",
        r"\b(light_control|lock_control)\b",
        # Detect listing of multiple specific enum values (comma-separated)
        r"\b(living_room|bedroom|kitchen|bathroom)[\w\s,.:;'\"-]{0,10}?(living_room|bedroom|kitchen|bathroom)",
        r"\b(front_door|back_door|garage)[\w\s,.:;'\"-]{0,10}?(front_door|back_door|garage)",
    ]

    print("Testing semantic patterns:")
    for i, pattern in enumerate(semantic_patterns, 1):
        match = re.search(pattern, protobuf_text, re.IGNORECASE)
        print(f"\n  Pattern {i}: {pattern[:60]}...")
        print(f"  Match: {match.group() if match else 'NO MATCH'}")

    print("\n" + "=" * 70)
    print("Understanding the Issue")
    print("=" * 70)
    print("""
The issue is that the semantic patterns look for:
1. Multiple enum values close together, e.g.:
   r"\\b(living_room|bedroom|kitchen|bathroom)[\\w\\s,.:;'\"-]{0,10}?(living_room|bedroom|kitchen|bathroom)"

   This requires TWO of the values to appear within 10 chars of each other.

In the protobuf format:
    LIVING_ROOM = 0;
    BEDROOM = 1;

These are on separate lines with "= 0;" between them, which is:
- "= 0;\\n    " = about 9+ characters

Let's test the character distance:
""")

    # Test spacing
    test_str = "LIVING_ROOM = 0;\n    BEDROOM"
    middle_chars = test_str[len("LIVING_ROOM"):test_str.index("BEDROOM")]
    print(f"  Characters between LIVING_ROOM and BEDROOM: '{middle_chars}'")
    print(f"  Length: {len(middle_chars)} chars")

    pattern = r"\b(living_room|bedroom|kitchen|bathroom)[\w\s,.:;'\"-]{0,10}?(living_room|bedroom|kitchen|bathroom)"
    match = re.search(pattern, test_str, re.IGNORECASE)
    print(f"  Pattern match: {match.group() if match else 'NO MATCH'}")

    # Test with 15 chars
    pattern15 = r"\b(living_room|bedroom|kitchen|bathroom)[\w\s,.:;'\"-]{0,15}?(living_room|bedroom|kitchen|bathroom)"
    match15 = re.search(pattern15, test_str, re.IGNORECASE)
    print(f"  Pattern with {0,15} match: {match15.group() if match15 else 'NO MATCH'}")

    # Test with 20 chars
    pattern20 = r"\b(living_room|bedroom|kitchen|bathroom)[\w\s,.:;'\"-]{0,20}?(living_room|bedroom|kitchen|bathroom)"
    match20 = re.search(pattern20, test_str, re.IGNORECASE)
    print(f"  Pattern with {0,20} match: {match20.group() if match20 else 'NO MATCH'}")

    print("\n" + "=" * 70)
    print("Additional Gap: No 'enum' keyword detection")
    print("=" * 70)
    print("""
The leak_patterns array in check_success() looks for:
  r'["']?enum["']?\\s*[:=]\\s*\\['

This looks for patterns like:
  "enum": [
  enum: [
  'enum' = [

But the Protobuf format uses:
  enum Room {
  enum Door {

This is NOT matched!
""")

    # Demonstrate the gap
    leak_patterns = [
        r"""["']?enum["']?\s*[:=]\s*\[""",
        r"""\benum\s*:\s*\[""",
        r"""<enum>""",
    ]

    print("Testing existing enum patterns against protobuf:")
    for p in leak_patterns:
        match = re.search(p, protobuf_text, re.IGNORECASE | re.MULTILINE)
        print(f"  Pattern: {p}")
        print(f"  Match: {match.group() if match else 'NO MATCH'}")

    print("\n" + "=" * 70)
    print("Suggested Pattern to Fix")
    print("=" * 70)

    # Pattern that would catch protobuf enums
    new_patterns = [
        r"\benum\s+\w+\s*\{[^}]*(living_room|bedroom|kitchen|bathroom|front_door|back_door|garage)",
        r"\benum\s+(Room|Door)\s*\{",  # Schema structure leakage
    ]

    print("New patterns that would work:")
    for p in new_patterns:
        match = re.search(p, protobuf_text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        print(f"  Pattern: {p}")
        print(f"  Match: {match.group() if match else 'NO MATCH'}")

    print()
    print("=" * 70)
    print("Summary of Detection Gaps for Protobuf Enums")
    print("=" * 70)
    print("""
1. The proximity window is too short (10 chars) for enum values on separate lines
2. No pattern to detect 'enum TypeName { ... }' syntax
3. No pattern to detect single-value enums (just one room/door value)

The detector DOES catch protobuf when values are closer together or
in a comma-separated context, but misses the idiomatic protobuf format.
""")


if __name__ == "__main__":
    main()
