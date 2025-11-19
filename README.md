# 🍳 Emoji Kitchen CLI

A performant Python CLI tool that downloads emoji combinations from Google's Emoji Kitchen service.

**Status:** 🔬 Research Complete → 🚀 Ready for Implementation

---

## 📖 Overview

Emoji Kitchen is a CLI tool that allows you to download emoji combinations (mashups) from Google's Emoji Kitchen service. It supports multiple input modes, intelligent file organization, async downloads, and beautiful terminal output.

### Key Features

- **Multiple Input Modes:**
  - Single pair: `emoji-kitchen 😊 🎉`
  - All combinations: `emoji-kitchen all 😊`
  - Batch processing: `emoji-kitchen batch combos.txt`
  - Interactive mode: `emoji-kitchen` (no args)

- **Smart Organization:**
  - Files organized by base emoji: `downloads/😊/😊_🎉.png`
  - Automatic skip of existing files
  - Cross-platform filename compatibility

- **Production Ready:**
  - Async downloads (50-100 images/second target)
  - Beautiful progress bars with Rich
  - Graceful error handling
  - Configurable rate limiting
  - Comprehensive summary reports

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- UV package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd EmojiKitchen

# Install with UV (when implemented)
uv pip install -e .
```

### Usage

```bash
# Download a single emoji combination
emoji-kitchen 😊 🎉

# Download all combinations for an emoji
emoji-kitchen all 😊

# Process a batch file
emoji-kitchen batch combos.txt

# Interactive mode
emoji-kitchen

# Custom options
emoji-kitchen 😊 🎉 --output ./my-emojis --delay 150 --verbose
```

---

## 📁 Project Structure

```
EmojiKitchen/
├── AGENT.md                    # Project instructions for Claude Code
├── CLAUDE.md                   # Redirect to AGENT.md
├── TODOS.md                    # Project task tracking
├── README.md                   # This file
├── AgentUsage/                 # Comprehensive workflow guides
│   ├── README.md               # Guide index
│   ├── git_guide.md            # Git workflow
│   ├── uv_usage.md             # Python UV package manager
│   ├── testing_strategies.md  # Test patterns
│   └── ... (16 total guides)
├── EmojiKitchen/               # Research documentation
│   ├── PROJECT_SPEC.md         # Original requirements
│   ├── SUMMARY.md              # Research summary
│   ├── TEAM_ACTION_PLAN.md     # Implementation phases
│   ├── EXTRAS.md               # Additional notes
│   └── Research/               # Detailed research
│       ├── 00_QUICK_START_GUIDE.md
│       ├── 01_API_Research.md
│       ├── 02_Python_Emoji_Handling.md
│       ├── 03_Performance_Async_Patterns.md
│       └── 04_Implementation_Recommendations.md
└── src/                        # Implementation (to be created)
    └── emoji_kitchen/
        ├── cli.py              # CLI interface
        ├── orchestrator.py     # Download coordination
        ├── api/                # API client and metadata
        ├── storage/            # File organization
        └── utils/              # Utilities and helpers
```

---

## 🔬 Research Status

All technical research is **complete** ✅

### What's Been Researched

1. **API Access** - Vercel wrapper API identified and documented
2. **Metadata** - 100k+ combinations catalogued and accessible
3. **Python Emoji Handling** - Unicode conversion patterns established
4. **Async Performance** - httpx patterns for 50-100 images/second
5. **Architecture** - Modular design with clear separation of concerns
6. **Cross-platform** - Filename compatibility solutions documented

### Implementation Ready

See `EmojiKitchen/Research/00_QUICK_START_GUIDE.md` for step-by-step implementation instructions.

**Estimated development time:** 10-15 hours across 4 phases

---

## 🎯 Implementation Phases

### Phase 1: Foundation (2-3 hours)
Working CLI that downloads single emoji pairs
- Core utilities (emoji conversion, validation)
- Async HTTP client
- Storage manager
- Basic CLI interface

### Phase 2: All Modes (3-4 hours)
Support for batch, all-combinations, and interactive modes
- Metadata download and caching
- Batch processing
- All combinations finder
- Interactive prompts

### Phase 3: Polish (2-3 hours)
Production-ready UX
- Progress bars
- Summary reports
- Retry logic
- Performance optimization

### Phase 4: Quality (2-3 hours)
Testing and documentation
- Unit and integration tests
- Type checking
- Code quality (ruff, mypy)
- Comprehensive README

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Package Manager:** UV
- **CLI Framework:** Click
- **HTTP Client:** httpx (async with HTTP/2)
- **Terminal UI:** Rich (progress bars and output)
- **Emoji Utils:** emoji library
- **Testing:** pytest, pytest-asyncio
- **Quality:** ruff (linting/formatting), mypy (type checking)

---

## 📚 Documentation

### For Developers

- **AGENT.md** - Main project instructions and architecture
- **TODOS.md** - Current tasks and progress tracking
- **EmojiKitchen/TEAM_ACTION_PLAN.md** - Detailed phase breakdown
- **EmojiKitchen/Research/** - Complete technical research

### For Claude Code Users

This project is optimized for Claude Code CLI:
- AGENT.md contains all project context
- Structured guides in AgentUsage/ directory
- Git workflow with conventional commits
- TODO management integrated into workflow

---

## 🤝 Contributing

This project follows the BaseProject template structure with:
- Conventional commit messages
- Git workflow best practices
- Comprehensive testing requirements
- Code quality standards (ruff, mypy)

See `AgentUsage/git_guide.md` for git workflow details.

---

## 📝 License

This project is provided as-is for personal and educational use.

---

## 🔗 Resources

### External APIs
- **Vercel API:** https://emojik.vercel.app
- **Metadata:** https://raw.githubusercontent.com/xsalazar/emoji-kitchen-backend/main/app/metadata.json

### Library Documentation
- **httpx:** https://www.python-httpx.org/
- **Rich:** https://rich.readthedocs.io/
- **Click:** https://click.palletsprojects.com/
- **emoji:** https://pypi.org/project/emoji/

---

## 📊 Performance Targets

- **Single download:** < 1 second
- **Batch (100 images):** < 30 seconds
- **All combinations (avg):** < 5 minutes per emoji
- **Memory usage:** < 200 MB
- **Test coverage:** 80%+

---

## 🎉 Current Status

**Research:** ✅ Complete
**Implementation:** ⏭ Ready to Start
**Testing:** ⏳ Pending
**Documentation:** ⏳ Pending

See `TODOS.md` for detailed task tracking.

---

**Built with ❤️ using Claude Code and the BaseProject template**

*Last updated: 2025-11-19*
