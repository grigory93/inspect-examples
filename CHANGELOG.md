# Changelog

All notable changes to the inspect-examples project.

## [2024-11-03] - Multi-Example Structure

### Changed

#### Project Structure - Example Organization
- **Organized examples into subfolders** for better scalability
  - `examples/browser.py` → `examples/browser/browser.py`
  - Each example now has its own folder with supporting files
  - Each example includes:
    - `browser.py` - Main task file
    - `__init__.py` - Package initialization with exports
    - `compose.yaml` - Docker configuration
    - `README.md` - Example-specific documentation
  
  This structure makes it easy to add more examples (e.g., `coding/`, `reasoning/`, etc.)

## [2024-11-03] - Project Restructure

### Changed

#### Project Structure
- **Moved all Python files to `examples/` package**
  - `browser.py` → `examples/browser.py` (later moved to subfolder)
  - Added `__init__.py` to make it a proper Python package
  
  This follows Python packaging best practices and keeps code organized.

#### Updated All Commands
All evaluation commands now reference the example subfolder path:
```bash
# Original
inspect eval browser.py --model openai/gpt-4o-mini

# After package move
inspect eval examples/browser.py --model openai/gpt-4o-mini

# Current (example-based)
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini
```

#### Documentation Updates
All documentation files updated to reflect new structure:
- ✅ `README.md` - All eval commands, task references, and uv documentation
- ✅ `QUICKSTART.md` - All step-by-step commands
- ✅ `PLAN.md` - Implementation plan and examples
- ✅ `example_commands.sh` - All command examples
- ✅ `run_comparison.sh` - Default task path
- ✅ `setup_with_uv.sh` - Setup instructions

### Added
- **Example-specific documentation**
  - Each example folder includes its own README.md
  - Browser example has detailed documentation of task, samples, and customization
  - Supporting files (compose.yaml) colocated with examples

- **Enhanced `README.md`** - Consolidated comprehensive project documentation
  - Complete directory tree showing example structure
  - File descriptions
  - Usage patterns
  - Development workflow
  - Best practices for creating new examples

### Benefits of Restructure
1. **Professional Structure**: Follows Python packaging best practices
2. **Cleaner Root**: Documentation and code separated
3. **Easier to Extend**: Add new tasks to the package easily
4. **Better Organization**: Clear separation of concerns
5. **Industry Standard**: Matches how real Python projects are structured
6. **Improved Discoverability**: All evaluation code in one package location

## [2024-11-03] - Migration to uv Package Manager

### Changed

#### Package Management
- **Switched from pip to uv** for faster, more reliable dependency management
- **Created `pyproject.toml`** with proper project configuration
  - Defined all dependencies with version constraints
  - Organized model providers as optional extras
  - Modern Python packaging standards

#### Installation Method
```bash
# Old (pip)
pip install inspect-ai
pip install openai
pip install anthropic

# New (uv)
uv pip install -e ".[openai,anthropic]"
```

#### Performance Improvements
- 10-100x faster package installation
- Better dependency resolution
- Parallel downloads and caching

### Added

#### New Files
- **`pyproject.toml`** - Project configuration and dependencies
- **`setup_with_uv.sh`** - Interactive setup script
  - Installs uv automatically
  - Provider selection menu
  - API key instructions
  - Docker checks
  
- **Enhanced `README.md`** - Consolidated uv documentation
  - Installation guide
  - Migration information and command comparisons
  - Usage examples
  - Troubleshooting
  - FAQs
  - Quick reference
  
- **`.python-version`** - Python 3.11 specification

#### Features
- **Optional dependency groups** in pyproject.toml:
  - `[openai]` - OpenAI models only
  - `[anthropic]` - Anthropic Claude only
  - `[mistral]` - Mistral models only
  - `[ai21]` - AI21 Jamba only
  - `[google]` - Google Gemini only
  - `[all-providers]` - All providers at once

### Updated
- All documentation updated with uv commands
- Installation sections rewritten
- Troubleshooting guides enhanced

## [Initial Release] - Browser Task Example

### Added

#### Core Files
- **`browser.py`** - Browser task
  - Tests web navigation with LLMs
  - Requires Docker for sandboxing
  - Evaluates tool usage and information extraction

#### Documentation
- **`README.md`** - Complete project documentation
- **`QUICKSTART.md`** - 5-minute quick start guide
- **`PLAN.md`** - Implementation plan and architecture

#### Scripts
- **`run_comparison.sh`** - Multi-model comparison automation
- **`example_commands.sh`** - Command reference library

#### Features
- **Browser task evaluation** - Tests LLM agentic capabilities
- **Multi-model support** - OpenAI, Anthropic, Mistral, AI21, Google
- **Docker sandboxing** - Secure code execution
- **Inspect View integration** - Web-based log viewer
- **Comprehensive logging** - Detailed execution traces

### Supported Models
- OpenAI GPT-4, GPT-4o
- Anthropic Claude Sonnet, Opus
- Mistral Large, Medium
- AI21 Jamba
- Google Gemini

---

## Migration Guide

### From Initial Release to Current Version

If you started with the initial release:

1. **Install uv**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install with new method**:
   ```bash
   cd inspect-examples
   uv pip install -e ".[all-providers]"
   ```

3. **Update your commands**:
   ```bash
   # Change all commands from
   inspect eval browser.py --model openai/gpt-4o-mini
   
   # To
   inspect eval examples/browser.py --model openai/gpt-4o-mini
   ```

4. **Everything else stays the same!**

---

## Backward Compatibility

✅ All existing evaluation workflows still work  
✅ Can still use pip if preferred (not recommended)  
✅ Same model APIs and providers  
✅ Same log formats and viewer  
✅ Same Docker requirements  

---

## Future Plans

- [ ] Add more browser task examples
- [ ] Additional model providers
- [ ] Custom scoring examples
- [ ] Multi-agent examples
- [ ] Advanced tool usage examples
- [ ] Performance benchmarking tools

