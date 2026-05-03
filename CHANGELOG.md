# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-29

### Added

- Initial MVP release
- Core CLI with 4 main commands:
  - `analyze`: Full repository analysis with AI detection metrics
  - `detect-ai`: Detect commits with AI-generated language
  - `timeline`: Visual ASCII timeline with epochs and velocity
  - `suggest-rewrites`: Generate rewrite suggestions for problematic commits
- AI detection algorithm with 0-100 scoring:
  - Keyword detection (enhancing, comprehensive, showcasing, etc.)
  - Phrase pattern matching (improving the, detailing the, etc.)
  - Structural pattern detection (long lists, multiple gerunds)
  - Length-based scoring (>100, >150, >200 chars)
- Risk classification:
  - 🟢 Low (0-30): Clean commits
  - 🟡 Medium (31-60): Review recommended
  - 🔴 High (61-100): Rewrite recommended
- Timeline visualizations:
  - ASCII timeline with commit blocks
  - Velocity chart by epoch
  - Risk heatmap
  - Activity summary
- Epoch grouping (automatic based on 7-day gaps)
- Commit rewriter with Conventional Commits support
- Export formats:
  - Terminal (Rich UI with colors and tables)
  - Markdown (full report)
  - JSON (structured data)
- Templates for Markdown and HTML reports (Jinja2)
- Comprehensive test suite (40 tests, 100% passing)
- Full documentation:
  - README.md with quick start
  - USAGE.md with detailed examples
  - Inline documentation in all modules

### Technical Stack

- Python 3.11+
- Click (CLI framework)
- GitPython (git operations)
- Rich (terminal UI)
- Pydantic (data validation)
- Jinja2 (templates)
- pytest (testing)

### Tested On

- human-code-ai-protocol: 160 commits, 80.6% AI detection
- hkm-knowledge-hub: 10 commits, clean history

## [Unreleased]

### Planned for Future Versions

- Branch comparison (`compare` command)
- Feature tracking (`track-feature` command)
- Interactive rebase assistant (`rebase-plan` command)
- GitHub integration (analyze PRs directly)
- Pre-commit hooks
- HTML dashboard with interactive filters
- AI-powered rewrites using local LLM (ollama)
- Learning mode (fine-tune based on feedback)
- Batch operations
- IDE plugins (VS Code, Cursor)

---

[0.1.0]: https://github.com/druiz912/git-auditor/releases/tag/v0.1.0
