# TODOs for EmojiKitchen CLI

## Project Overview
Building a performant CLI tool that downloads emoji combinations from Google's Emoji Kitchen service.
Research complete ✅ | Ready for implementation | Estimated time: 10-15 hours

---

## Phase 1: Foundation (2-3 hours) - Single Pair Downloads
- [ ] Initialize project with UV and create directory structure
- [ ] Install dependencies (httpx, rich, emoji, click)
- [ ] Implement emoji utility functions (emoji_utils.py)
  - [ ] emoji_to_codepoint() conversion
  - [ ] codepoint_to_emoji() conversion
  - [ ] validate_emoji() validation
  - [ ] normalize_emoji() normalization
- [ ] Implement async HTTP client (api/client.py)
  - [ ] Basic download_image() method
  - [ ] Rate limiting with configurable delay
  - [ ] 404 error handling for non-existent combos
- [ ] Implement storage manager (storage/manager.py)
  - [ ] Platform detection (emoji vs codepoint filenames)
  - [ ] File path generation
  - [ ] Save to organized directories
  - [ ] Check if file already exists
- [ ] Create basic CLI (cli.py)
  - [ ] Accept two emoji arguments
  - [ ] Emoji validation
  - [ ] Pretty output with Rich
  - [ ] Skip existing files
- [ ] Test single pair download: `emoji-kitchen 😊 🎉`

## Phase 2: All Input Modes (3-4 hours)
- [ ] Implement metadata download and caching (api/metadata.py)
  - [ ] Download from GitHub (100k+ combinations)
  - [ ] Parse and index JSON data
  - [ ] Local caching (~/.emoji-kitchen/metadata.json)
  - [ ] Query interface for finding combinations
- [ ] Add `all` command - download all combinations for one emoji
  - [ ] Query metadata for all pairs
  - [ ] Async batch download
  - [ ] Progress tracking
- [ ] Add `batch` command - process file with emoji pairs
  - [ ] File parsing (one pair per line)
  - [ ] Batch orchestration
  - [ ] Error collection
- [ ] Add interactive mode (no arguments)
  - [ ] User prompts for emojis
  - [ ] Continue/quit flow
  - [ ] Friendly UX

## Phase 3: Polish & Optimization (2-3 hours)
- [ ] Implement Rich progress bars (orchestrator.py)
  - [ ] Download progress visualization
  - [ ] Speed and ETA display
  - [ ] Concurrent download tracking
- [ ] Add retry logic with exponential backoff
- [ ] Implement summary reports (utils/reporting.py)
  - [ ] Success/skipped/failed statistics
  - [ ] Failed downloads with reasons
  - [ ] Performance metrics
- [ ] Optimize async performance
  - [ ] Semaphore-based concurrency control
  - [ ] Connection pooling
  - [ ] Target: 50-100 images/second
- [ ] Add CLI options
  - [ ] --output directory
  - [ ] --delay for rate limiting
  - [ ] --verbose for detailed logging
  - [ ] --filename-format (emoji|codepoint|auto)

## Phase 4: Testing & Quality (2-3 hours)
- [ ] Write unit tests (pytest)
  - [ ] Test emoji conversion functions
  - [ ] Test validators
  - [ ] Test path generation
  - [ ] Mock HTTP responses
- [ ] Add integration tests
  - [ ] Test all CLI commands
  - [ ] Test end-to-end flow
  - [ ] Test cross-platform compatibility
- [ ] Add type hints throughout codebase
- [ ] Run mypy type checking
- [ ] Set up ruff for linting/formatting
- [ ] Add docstrings to all public functions
- [ ] Write comprehensive README.md
  - [ ] Installation instructions
  - [ ] Usage examples for all modes
  - [ ] Troubleshooting guide
- [ ] Target: 80%+ test coverage

## Documentation Available
All research completed in `EmojiKitchen/Research/` directory:
- 00_QUICK_START_GUIDE.md - Step-by-step implementation guide
- 01_API_Research.md - API endpoints and metadata
- 02_Python_Emoji_Handling.md - Unicode conversion patterns
- 03_Performance_Async_Patterns.md - Async download optimization
- 04_Implementation_Recommendations.md - Architecture decisions
- PROJECT_SPEC.md - Original requirements
- TEAM_ACTION_PLAN.md - Detailed phase breakdown
- SUMMARY.md - Research summary

## Success Criteria
- ✅ Download single emoji pairs
- ✅ Download all combinations for an emoji
- ✅ Process batch files
- ✅ Interactive mode
- ✅ Files organized by base emoji
- ✅ Skip existing downloads
- ✅ Graceful error handling
- ✅ Beautiful progress bars
- ✅ 50-100 images/second performance
- ✅ 80%+ test coverage
