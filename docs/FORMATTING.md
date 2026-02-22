# Python Code Formatting Guide

This project uses multiple Python formatters and linters to maintain code quality and consistency.

## 🎨 Formatters & Linters

### Black
**The uncompromising Python code formatter**
- Line length: 100 characters
- Config: `[tool.black]` in `pyproject.toml`
- Auto-formats Python code

### isort
**Import statement sorter**
- Compatible with Black profile
- Config: `[tool.isort]` in `pyproject.toml`
- Automatically organizes imports

### Ruff
**Fast Python linter (Rust-based)**
- Replaces flake8, isort, and more
- Config: `[tool.ruff]` in `pyproject.toml`
- Checks for style violations

### Flake8
**Classic Python linter**
- Max line length: 100 characters
- Config: `.flake8`
- Compatible with Black

## 📦 Installation

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Or using Makefile:

```bash
make install
```

## 🚀 Usage

### Using Makefile (Recommended)

```bash
# Format all Python code
make format

# Check formatting without changes
make format-check

# Run linter (ruff)
make lint

# Run flake8 linter
make lint-flake8

# Format + lint
make all

# Clean build artifacts
make clean
```

### Using Python Script

```bash
# Format code
python format.py

# Check formatting only
python format.py --check

# Lint only
python format.py --lint
```

### Using Tools Directly

```bash
# Black
black nays test

# isort
isort nays test

# Ruff
ruff check nays test

# Flake8
flake8 nays test
```

## 📋 Configuration Files

- **`pyproject.toml`** - Black, isort, Ruff configuration
- **`.flake8`** - Flake8 linter configuration
- **`.editorconfig`** - Editor settings (4 spaces for Python)
- **`setup.cfg`** - Legacy tool configuration (mypy, coverage)
- **`format.py`** - Python formatting script
- **`Makefile`** - Convenient formatter commands

## 🔧 Editor Integration

### VS Code

Install extensions:
- **Python** (ms-python.python)
- **Black Formatter** (ms-python.black-formatter)
- **isort** (ms-python.isort)
- **Ruff** (charliermarsh.ruff)

Add to `.vscode/settings.json`:

```json
{
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

### PyCharm / IntelliJ

1. **Settings → Tools → Black**
   - Enable "On save"
   - Set line length: 100

2. **Settings → Editor → Code Style → Python**
   - Set indent: 4 spaces
   - Set max line length: 100

3. **Settings → Editor → Inspections → Python**
   - Enable Flake8 or Ruff

## 📏 Coding Standards

- **Indentation**: 4 spaces (not tabs)
- **Line Length**: 100 characters
- **String Quotes**: Double quotes (`"`) preferred by Black
- **Import Order**: stdlib → third-party → local (enforced by isort)
- **Docstrings**: Use """triple double quotes"""

## 🔍 Pre-commit Hook (Optional)

Install pre-commit to automatically format on each commit:

```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.8

  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
```

Then run:

```bash
pre-commit install
```

## ✅ CI/CD Integration

Add to GitHub Actions (`.github/workflows/lint.yml`):

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Check formatting
        run: make format-check
      - name: Run linter
        run: make lint
```

## 📚 References

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Ruff Documentation](https://beta.ruff.rs/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
