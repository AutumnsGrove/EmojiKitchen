# Emoji Kitchen API Research

## Executive Summary

Google's Emoji Kitchen is accessible through multiple API endpoints and data sources. The primary methods for programmatic access are:

1. **Third-party API wrapper** (emojik.vercel.app)
2. **Direct image downloads from Google CDN** (gstatic.com)
3. **Metadata file** containing all 100,000+ combinations

## API Endpoints

### 1. Vercel Wrapper API (Recommended for Single Downloads)

**Base URL Pattern:**
```
https://emojik.vercel.app/s/:emojis?size=<size>
```

**Alternative Domains (All work identically):**
- `emk.vercel.app` or `emk.now.sh`
- `emjk.vercel.app` or `emjk.now.sh`
- `emojk.vercel.app` or `emojk.now.sh`
- `emoji-kitchen.vercel.app` or `emoji-kitchen.now.sh`

**Parameters:**
- **emojis**: Two emojis separated by underscore `_`
  - Can use actual emoji characters: `🥹_😗`
  - Or Unicode codepoints: `1f979_1f617`
- **size**: Integer from 16 to 512 (pixels for square image)

**Example Requests:**
```bash
# Using emoji characters
https://emojik.vercel.app/s/🥹_😗?size=128

# Using Unicode codepoints
https://emojik.vercel.app/s/1f979_1f617?size=128
```

**Response:** PNG image file

**Rate Limiting:** Unknown, but implement respectful delays (100-200ms recommended)

---

### 2. Google Static CDN (Direct Source)

**URL Pattern:**
```
https://www.gstatic.com/android/keyboard/emojikitchen/{date}/{leftCode}/{leftCode}_{rightCode}.png
```

**Components:**
- **date**: Release date in YYYYMMDD format (e.g., "20201001")
- **leftCode**: Unicode codepoint with 'u' prefix (e.g., "u1f600")
- **rightCode**: Unicode codepoint with 'u' prefix (e.g., "u1f604")

**Example:**
```
https://www.gstatic.com/android/keyboard/emojikitchen/20201001/u1f600/u1f600_u1f604.png
```

**Advantages:**
- Direct access to Google's CDN
- Likely faster and more reliable
- No intermediary API

**Challenges:**
- Requires knowing the date for each combination
- Need to construct correct codepoint format
- Must obtain metadata to know valid combinations

---

### 3. Metadata File (Essential for Bulk Operations)

**URL:**
```
https://raw.githubusercontent.com/xsalazar/emoji-kitchen-backend/main/app/metadata.json
```

**Alternative Data Source:**
```
https://raw.githubusercontent.com/xsalazar/emoji-kitchen/main/scripts/emojiOutput.json
```

**Size:** Very large (exceeded 10MB fetch limit in testing)

**Structure (Based on Research):**

```json
{
  "emoji": {
    "leftEmoji": "😀",
    "leftEmojiCodepoint": "1f600",
    "rightEmoji": "🎉",
    "rightEmojiCodepoint": "1f389",
    "date": "20201001",
    "isLatest": true,
    "gStaticUrl": "https://www.gstatic.com/android/keyboard/emojikitchen/20201001/u1f600/u1f600_u1f389.png"
  }
}
```

**Key Fields:**
- `isLatest`: Boolean - filters for latest version of combinations
- `gStaticUrl`: Direct Google Static URL for the image
- `date`: Release date of the combination
- Emoji codepoints for both left and right emojis

**Extraction Command:**
```bash
# Download metadata
curl -L --compressed https://raw.githubusercontent.com/xsalazar/emoji-kitchen-backend/main/app/metadata.json -o metadata.json

# Extract latest image URLs
jq -r '.. | select(.isLatest?) | .gStaticUrl' metadata.json | sort | uniq > urls.txt
```

---

## Discovery Methods

### Finding All Combinations for a Base Emoji

**Option 1: Query Metadata**
- Download and parse metadata.json
- Filter by leftEmoji or rightEmoji matching target
- Extract gStaticUrl for each match

**Option 2: Brute Force Testing**
- Iterate through common emoji codepoints
- Test API endpoint for each combination
- Handle 404s gracefully for non-existent combinations

**Recommendation:** Use metadata approach for efficiency

---

## Unicode Codepoint Conversion

### Python Conversion Examples

**Emoji → Codepoint:**
```python
emoji = "😀"
codepoint = hex(ord(emoji))[2:]  # Returns "1f600"
codepoint_with_u = f"u{codepoint}"  # Returns "u1f600"
```

**Codepoint → Emoji:**
```python
codepoint = "1f600"
emoji = chr(int(codepoint, 16))  # Returns "😀"
```

**Multi-codepoint Emojis (Sequences):**
```python
# Some emojis are sequences (e.g., skin tones, gender variants)
emoji = "👨‍💻"  # Man technologist
codepoints = [hex(ord(c))[2:] for c in emoji if ord(c) > 127]
# Returns multiple codepoints joined by zero-width joiner
```

**URL Encoding:**
```python
import urllib.parse

emoji = "😀"
encoded = urllib.parse.quote(emoji)  # Returns "%F0%9F%98%80"
```

---

## Implementation Strategy

### Approach A: Vercel API Wrapper (Simpler)

**Pros:**
- No need to manage metadata
- Simple URL construction
- Handles edge cases

**Cons:**
- Dependent on third-party service
- Unknown rate limits
- May be slower for bulk downloads
- Can't discover all combinations for an emoji

**Best For:**
- Single emoji pair downloads
- Interactive mode
- Quick prototyping

---

### Approach B: Metadata + Direct CDN (Recommended)

**Pros:**
- Full control over all 100,000+ combinations
- Direct Google CDN access (faster)
- Can implement "all combinations" feature
- More reliable for bulk operations

**Cons:**
- Must download and parse large metadata file
- More complex implementation
- Need to handle metadata updates

**Best For:**
- Batch downloads
- "All combinations for emoji X" feature
- Production-grade tool

---

## Recommended Implementation Plan

### Phase 1: Quick Win with Vercel API
1. Implement basic CLI using Vercel API
2. Support single pair downloads
3. Test emoji → codepoint conversion
4. Validate URL encoding

### Phase 2: Metadata Integration
1. Download metadata.json on first run (cache locally)
2. Parse metadata into efficient data structure
3. Implement combination discovery
4. Switch to direct CDN downloads

### Phase 3: Optimization
1. Add metadata refresh mechanism
2. Implement connection pooling
3. Add parallel downloads with rate limiting
4. Validate file integrity

---

## Testing Checklist

- [ ] Single emoji pair download works
- [ ] Unicode codepoint conversion accurate
- [ ] URL encoding handles special characters
- [ ] API returns valid PNG files
- [ ] 404 errors handled gracefully
- [ ] Rate limiting prevents abuse
- [ ] Multi-codepoint emojis (ZWJ sequences) work
- [ ] Metadata parsing completes successfully
- [ ] Can discover all combos for a base emoji

---

## Known Challenges

### 1. Not All Combinations Exist
- Google doesn't provide combinations for every emoji pair
- API will return 404 for invalid combinations
- Must handle gracefully and report to user

### 2. Metadata File Size
- Over 10MB compressed
- May take time to download on slow connections
- Consider incremental loading or database

### 3. Emoji Sequences
- Some emojis are multi-codepoint (ZWJ sequences, skin tones)
- Need special handling for these cases
- May appear differently across platforms

### 4. API Availability
- Third-party Vercel API could go offline
- Google CDN is more reliable but requires metadata
- Implement fallback mechanisms

---

## Additional Resources

- **emojikitchen.dev**: Visual browser for combinations
- **GitHub: xsalazar/emoji-kitchen**: Frontend source code
- **GitHub: xsalazar/emoji-kitchen-backend**: Backend Lambda source
- **Gboard**: Original implementation (Android keyboard)

---

## Next Steps for Implementation

1. **Test API endpoints** with sample emoji pairs
2. **Download metadata** and examine structure in detail
3. **Build codepoint converter** and validate with test cases
4. **Implement basic downloader** using Vercel API
5. **Benchmark download speeds** to inform async strategy
6. **Parse metadata** for combination discovery
7. **Switch to CDN** for production downloads

---

*Research completed: 2025-11-19*
*Total combinations available: 100,000+*
*API stability: Good (Google CDN), Unknown (Vercel wrapper)*
