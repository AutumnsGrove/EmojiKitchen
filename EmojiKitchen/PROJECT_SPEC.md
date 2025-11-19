# Emoji Kitchen Downloader - Project Metaprompt

## Project Overview

Create a performant CLI tool that downloads emoji combinations from Google's Emoji Kitchen service. The tool should support multiple input modes, intelligent file organization, and graceful error handling.

## Technical Requirements

### Core Technology
- **Language**: Python 3.10+
- **Package Manager**: UV (for dependency management)
- **Performance**: Fast, async where beneficial, minimal storage footprint
- **Structure**: Clean CLI interface with multiple operation modes

### API Research Needed
- Emoji Kitchen API endpoint discovery (URL pattern analysis)
- Rate limiting investigation (assume none exists, but be respectful)
- Response format understanding
- Error response handling

## Feature Specifications

### Input Modes (All Required)

1. **Two-Emoji Mode**
   ```bash
   emoji-kitchen 😊 🎉
   ```
   Downloads the combination of two specific emojis.

2. **Batch Mode**
   ```bash
   emoji-kitchen --batch file.txt
   ```
   Processes a file containing emoji pairs (one pair per line or specify format).

3. **All-Combinations Mode**
   ```bash
   emoji-kitchen 😊 --all
   ```
   Downloads all available combinations for a single base emoji.

4. **Interactive Mode**
   ```bash
   emoji-kitchen --interactive
   # or just
   emoji-kitchen
   ```
   Prompts user for emoji inputs in a friendly conversational interface.

### File Organization

**Directory Structure:**
```
downloads/
├── 😊/
│   ├── 😊_🎉.png
│   ├── 😊_❤️.png
│   └── 😊_😭.png
├── 🎉/
│   └── 🎉_❤️.png
└── ...
```

**Naming Convention:**
- Format: `{emoji1}_{emoji2}.png`
- Use actual emoji characters in filenames (ensure cross-platform compatibility)
- Organize by base emoji in subdirectories

### Intelligent Behavior

**Deduplication:**
- Automatically skip already-downloaded combinations
- Check file existence before making API calls
- Optional: Verify file integrity (size > 0 bytes)

**Error Handling:**
- Skip failed downloads gracefully (no crashes)
- Log all errors/failures to memory during execution
- Display summary report at end:
  ```
  ✓ Downloaded: 45 combinations
  ⊘ Skipped (existing): 12 combinations
  ✗ Failed: 3 combinations

  Failed combinations:
  - 😊 + 🦄 (combo not available)
  - 🎃 + 🌈 (network error)
  - 💀 + 🎺 (combo not available)
  ```

**Rate Limiting:**
- Implement respectful delays between requests (e.g., 100-200ms)
- Allow configuration via CLI flag: `--delay <ms>`
- Consider adaptive rate limiting if patterns emerge

## Implementation Guidelines

### Code Quality
- Use type hints throughout
- Async/await for API calls where beneficial
- Clear separation of concerns (API layer, file operations, CLI interface)
- Minimal dependencies (leverage stdlib where possible)

### Project Structure
```
emoji-kitchen/
├── pyproject.toml          # UV project configuration
├── src/
│   └── emoji_kitchen/
│       ├── __init__.py
│       ├── __main__.py     # CLI entry point
│       ├── api.py          # Emoji Kitchen API logic
│       ├── downloader.py   # Download orchestration
│       ├── storage.py      # File organization logic
│       └── cli.py          # CLI interface (argparse/click)
├── downloads/              # Default output directory (gitignored)
└── README.md              # Usage instructions
```

### CLI Interface Requirements
- Use `argparse` or `click` for argument parsing
- Provide `--help` with clear usage examples
- Support `--output` to customize download directory
- Support `--verbose` for detailed logging
- Support `--delay` for rate limit control
- Return appropriate exit codes (0 = success, 1 = partial failure, 2 = complete failure)

### Performance Considerations
- Use connection pooling for HTTP requests
- Implement concurrent downloads (with rate limit respect)
- Stream file downloads (don't buffer entire images in memory)
- Avoid redundant API calls

### Storage Optimization
- Only download what's requested
- No caching layers or databases (keep it simple)
- Verify PNG integrity (basic size check)
- Consider compression if storage becomes an issue (future iteration)

## Success Criteria

The tool is complete when it can:

1. ✅ Download a single emoji combination via CLI
2. ✅ Process a batch file of emoji pairs
3. ✅ Fetch all combinations for a given base emoji
4. ✅ Run in interactive mode with user prompts
5. ✅ Organize files by base emoji in subdirectories
6. ✅ Skip existing files automatically
7. ✅ Handle errors gracefully without crashing
8. ✅ Display a summary report after execution
9. ✅ Respect rate limiting (configurable delays)
10. ✅ Install cleanly via UV (`uv pip install -e .`)

## Out of Scope (For Now)

- Obsidian integration
- Predefined categories (Emotions, Tasks, etc.)
- Template generation
- GUI wrapper
- Auto-updates/scheduling
- Advanced analytics/dashboards

## Research Tasks (Day 1)

Before implementation, investigate:

1. **Emoji Kitchen API**
   - Reverse engineer URL pattern from emojikitchen.dev
   - Test endpoint accessibility
   - Understand request/response format
   - Identify available combinations discovery method

2. **Emoji Handling in Python**
   - Unicode normalization requirements
   - Cross-platform filename compatibility
   - URL encoding for emoji parameters

3. **Performance Baseline**
   - Test download speeds
   - Measure average file sizes
   - Estimate total combinations available

## Example Usage (Expected Behavior)

```bash
# Install
uv pip install -e .

# Single combination
emoji-kitchen 😊 🎉
# Output: Downloaded 😊_🎉.png to downloads/😊/

# All combinations for an emoji
emoji-kitchen 😊 --all
# Output: Downloaded 45 combinations to downloads/😊/

# Batch mode
echo "😊 🎉\n❤️ 🔥\n💀 🎺" > combos.txt
emoji-kitchen --batch combos.txt

# Interactive mode
emoji-kitchen --interactive
# > Enter first emoji: 😊
# > Enter second emoji: 🎉
# > Downloaded! Try another? (y/n): n

# Custom output with verbose logging
emoji-kitchen 😊 --all --output ./my-emojis --verbose --delay 150
```

## Notes

- User is using this personally initially, may expand if successful
- Emphasis on clean, maintainable code
- Future expansion may include categories and Obsidian integration
- Keep architecture flexible for feature additions

---

**Target Audience for Metaprompt**: Claude Code agent or developer building the tool from scratch

**Estimated Complexity**: Medium (2-4 hour implementation after API research)

**Priority**: Core downloading functionality > Error handling > Performance optimization

