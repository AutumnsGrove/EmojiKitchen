# Python Emoji Handling Guide

## Executive Summary

Handling emojis in Python requires careful attention to Unicode encoding, codepoint conversion, URL encoding, and cross-platform filename compatibility. This guide provides battle-tested patterns for the Emoji Kitchen CLI tool.

---

## Unicode Basics for Emojis

### What Are Emojis in Unicode?

Emojis are Unicode characters with codepoints outside the Basic Multilingual Plane (BMP):
- **BMP Range**: U+0000 to U+FFFF (16-bit)
- **Emoji Range**: Primarily U+1F300 to U+1F9FF (requires 21-bit, stored as UTF-8)

**Key Point:** Most emojis require 4 bytes in UTF-8 encoding.

---

## Codepoint Conversion

### Basic Emoji → Codepoint

```python
def emoji_to_codepoint(emoji: str) -> str:
    """Convert emoji to hexadecimal codepoint without 'U+' prefix."""
    if len(emoji) == 1:
        return hex(ord(emoji))[2:]  # Remove '0x' prefix

    # Handle multi-character sequences
    return '_'.join(hex(ord(c))[2:] for c in emoji)

# Examples
emoji_to_codepoint("😀")  # Returns: "1f600"
emoji_to_codepoint("❤️")   # Returns: "2764_fe0f" (heart + variation selector)
```

### Codepoint → Emoji

```python
def codepoint_to_emoji(codepoint: str) -> str:
    """Convert hexadecimal codepoint to emoji character."""
    # Handle single codepoint
    if '_' not in codepoint:
        return chr(int(codepoint, 16))

    # Handle multi-codepoint sequences
    codepoints = codepoint.split('_')
    return ''.join(chr(int(cp, 16)) for cp in codepoints)

# Examples
codepoint_to_emoji("1f600")       # Returns: "😀"
codepoint_to_emoji("1f468_200d_1f4bb")  # Returns: "👨‍💻" (man technologist)
```

### Google-Style Codepoint Format

For Emoji Kitchen's gstatic URLs, add 'u' prefix:

```python
def emoji_to_gstatic_code(emoji: str) -> str:
    """Convert emoji to Google's u-prefixed format."""
    base_code = emoji_to_codepoint(emoji)
    return f"u{base_code}"

emoji_to_gstatic_code("😀")  # Returns: "u1f600"
```

---

## Complex Emoji Sequences

### Multi-Codepoint Emojis (Graphemes)

Some emojis are composed of multiple codepoints:

**Types:**
1. **Variation Selectors**: `❤️` = U+2764 + U+FE0F (emoji presentation)
2. **ZWJ Sequences**: `👨‍💻` = U+1F468 + U+200D + U+1F4BB (man + ZWJ + laptop)
3. **Skin Tones**: `👋🏽` = U+1F44B + U+1F3FD (waving hand + medium skin tone)
4. **Flags**: `🇺🇸` = U+1F1FA + U+1F1F8 (regional indicators)

### Handling Graphemes

```python
def is_multi_codepoint_emoji(emoji: str) -> bool:
    """Check if emoji is composed of multiple codepoints."""
    return len(emoji) > 1

def split_grapheme_clusters(text: str) -> list[str]:
    """Split text into grapheme clusters (user-perceived characters)."""
    # Python 3.3+ handles this reasonably well
    import unicodedata

    clusters = []
    current_cluster = ""

    for char in text:
        if unicodedata.category(char).startswith('M'):  # Mark category
            current_cluster += char
        elif char == '\u200d':  # Zero-width joiner
            current_cluster += char
        elif unicodedata.category(char) == 'So':  # Other symbol
            if current_cluster:
                clusters.append(current_cluster)
            current_cluster = char
        else:
            current_cluster += char

    if current_cluster:
        clusters.append(current_cluster)

    return clusters
```

### Recommended Library: emoji

```bash
pip install emoji
```

```python
import emoji

# Extract all emojis from text
text = "Hello 😀 World 🌍"
emoji_list = emoji.emoji_list(text)
# Returns: [{'emoji': '😀', 'location': 6}, {'emoji': '🌍', 'location': 14}]

# Check if string is emoji
emoji.is_emoji("😀")  # True
emoji.is_emoji("Hello")  # False

# Get emoji name
emoji.demojize("😀")  # Returns: ":grinning_face:"
emoji.emojize(":grinning_face:")  # Returns: "😀"
```

---

## URL Encoding

### For API Requests

```python
import urllib.parse

def encode_emoji_for_url(emoji: str) -> str:
    """URL-encode emoji for HTTP requests."""
    return urllib.parse.quote(emoji, safe='')

encode_emoji_for_url("😀")  # Returns: "%F0%9F%98%80"

# Using with requests
import requests

emoji1 = "😀"
emoji2 = "🎉"
url = f"https://emojik.vercel.app/s/{emoji1}_{emoji2}?size=128"
# requests handles encoding automatically, but can encode manually if needed
```

### Best Practice

Modern HTTP libraries (requests, httpx, aiohttp) handle URL encoding automatically. Only encode manually if:
1. Building URLs as strings for logging
2. Working with legacy systems
3. Debugging URL construction

---

## Cross-Platform Filename Compatibility

### The Problem

**Windows Limitations:**
- NTFS supports Unicode filenames
- **But**: Windows terminal (cmd.exe, PowerShell) struggles with emoji display
- File Explorer may render emojis as boxes or question marks
- Some tools break on non-BMP characters

**macOS/Linux:**
- Generally good emoji support in filenames
- Filesystem encoding is UTF-8 by default
- Terminal emulators usually render emojis correctly

### Recommended Approach: Codepoint Filenames

**Strategy 1: Use Codepoints Instead of Emojis** (Most Compatible)

```python
def safe_filename(emoji1: str, emoji2: str) -> str:
    """Generate cross-platform compatible filename using codepoints."""
    code1 = emoji_to_codepoint(emoji1)
    code2 = emoji_to_codepoint(emoji2)
    return f"{code1}_{code2}.png"

safe_filename("😀", "🎉")  # Returns: "1f600_1f389.png"
```

**Pros:**
- Works everywhere (Windows, Mac, Linux)
- No encoding issues
- Easily reversible to emoji
- Sortable and searchable

**Cons:**
- Not human-friendly
- Harder to browse in file explorer

---

**Strategy 2: Hybrid Approach** (Recommended for CLI Tool)

```python
import platform
import unicodedata

def should_use_emoji_filenames() -> bool:
    """Detect if platform supports emoji filenames well."""
    system = platform.system()
    return system in ('Darwin', 'Linux')  # macOS and Linux

def create_filename(emoji1: str, emoji2: str) -> str:
    """Create filename based on platform capabilities."""
    if should_use_emoji_filenames():
        # Use emoji characters (user-friendly)
        return f"{emoji1}_{emoji2}.png"
    else:
        # Use codepoints (compatible)
        code1 = emoji_to_codepoint(emoji1)
        code2 = emoji_to_codepoint(emoji2)
        return f"{code1}_{code2}.png"
```

---

**Strategy 3: Emoji with Fallback** (Best User Experience)

```python
import os
from pathlib import Path

def create_safe_path(base_dir: str, emoji1: str, emoji2: str) -> Path:
    """Create safe file path with emoji, falling back to codepoints on error."""
    emoji_filename = f"{emoji1}_{emoji2}.png"
    base_path = Path(base_dir) / emoji1 / emoji_filename

    try:
        # Try creating the directory with emoji name
        base_path.parent.mkdir(parents=True, exist_ok=True)
        # Attempt to write a test file
        test_file = base_path.parent / ".test"
        test_file.touch()
        test_file.unlink()
        return base_path
    except (OSError, UnicodeEncodeError):
        # Fall back to codepoint-based naming
        code1 = emoji_to_codepoint(emoji1)
        code2 = emoji_to_codepoint(emoji2)
        fallback_path = Path(base_dir) / code1 / f"{code1}_{code2}.png"
        fallback_path.parent.mkdir(parents=True, exist_ok=True)
        return fallback_path
```

---

### CLI Option for User Choice

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '--filename-format',
    choices=['emoji', 'codepoint', 'auto'],
    default='auto',
    help='Filename format: emoji (😀_🎉.png), codepoint (1f600_1f389.png), or auto (detect)'
)
```

---

## Unicode Normalization

### Why Normalize?

Same emoji can be represented differently:
- `é` = U+00E9 (precomposed)
- `é` = U+0065 + U+0301 (e + combining acute accent)

**For Emojis:**
- Less common but can happen with variation selectors
- Ensure consistency in lookups and comparisons

```python
import unicodedata

def normalize_emoji(emoji: str) -> str:
    """Normalize emoji to canonical form (NFC)."""
    return unicodedata.normalize('NFC', emoji)

# Before using emoji in filenames or API calls
emoji = normalize_emoji(user_input)
```

**Recommended Form:** NFC (Canonical Decomposition, followed by Canonical Composition)

---

## Error Handling Patterns

### Encoding Errors

```python
def safe_encode_emoji(emoji: str) -> bytes:
    """Safely encode emoji to UTF-8, handling errors."""
    try:
        return emoji.encode('utf-8')
    except UnicodeEncodeError as e:
        print(f"Failed to encode emoji: {e}")
        # Fallback: use codepoint representation
        return emoji_to_codepoint(emoji).encode('ascii')
```

### File Writing Errors

```python
def write_emoji_file(path: Path, content: bytes) -> bool:
    """Write file with emoji filename, handling errors gracefully."""
    try:
        with open(path, 'wb') as f:
            f.write(content)
        return True
    except (OSError, UnicodeEncodeError) as e:
        print(f"Error writing to {path}: {e}")
        # Try fallback with codepoint name
        fallback_path = path.parent / f"{emoji_to_codepoint(path.stem)}.png"
        with open(fallback_path, 'wb') as f:
            f.write(content)
        return True
```

---

## Testing Strategies

### Test Cases to Include

```python
def test_emoji_conversion():
    """Test emoji to codepoint conversion."""
    assert emoji_to_codepoint("😀") == "1f600"
    assert emoji_to_codepoint("❤️") == "2764_fe0f"
    assert emoji_to_codepoint("👨‍💻") == "1f468_200d_1f4bb"

def test_filename_creation():
    """Test cross-platform filename creation."""
    filename = safe_filename("😀", "🎉")
    assert filename == "1f600_1f389.png"

    # Ensure no invalid characters
    assert '/' not in filename
    assert '\\' not in filename
    assert ':' not in filename

def test_unicode_normalization():
    """Test that normalization is consistent."""
    emoji1 = "❤️"  # With variation selector
    emoji2 = "❤"   # Without variation selector
    assert normalize_emoji(emoji1) != normalize_emoji(emoji2)
```

---

## Implementation Checklist

- [ ] Implement emoji_to_codepoint conversion
- [ ] Implement codepoint_to_emoji conversion
- [ ] Add Unicode normalization
- [ ] Create cross-platform filename generator
- [ ] Add URL encoding utilities
- [ ] Handle multi-codepoint emojis (ZWJ sequences)
- [ ] Test on Windows, macOS, Linux
- [ ] Add error handling for encoding failures
- [ ] Provide CLI option for filename format
- [ ] Document edge cases

---

## Recommended Libraries

```toml
[project.dependencies]
emoji = "^2.12.1"  # Emoji utilities and detection
unicodedata2 = "^15.1.0"  # Updated Unicode database (optional)
```

---

## Common Pitfalls to Avoid

1. **Don't assume all emojis are single characters**
   - Use grapheme cluster handling

2. **Don't skip normalization**
   - Variation selectors can cause comparison failures

3. **Don't hardcode emoji ranges**
   - Use the `emoji` library for detection

4. **Don't ignore Windows compatibility**
   - Test on Windows or provide codepoint fallback

5. **Don't forget URL encoding**
   - Though modern libraries handle it, be explicit in tests

---

## Next Steps

1. Install `emoji` library
2. Implement codepoint conversion utilities
3. Create filename generator with platform detection
4. Write comprehensive tests
5. Test on target platforms (Windows/Mac/Linux)
6. Document user-facing filename format options

---

*Research completed: 2025-11-19*
*Python version: 3.10+*
*Key dependencies: emoji, unicodedata*
