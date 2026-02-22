#!/usr/bin/env python3
"""
Python Code Formatter and Linter Script
========================================
Runs black, isort, and ruff on the nays package.

Usage:
    python format.py          # Format all Python files
    python format.py --check  # Check formatting without changes
    python format.py --lint   # Run linter only
"""
import argparse
import subprocess
import sys
from pathlib import Path

# Directories to format
SOURCES = ["nays", "test"]
PROJECT_ROOT = Path(__file__).parent


def run_command(cmd: list, check_only: bool = False) -> int:
    """Run a shell command and return exit code."""
    cmd_str = " ".join(cmd)
    print(f"\n{'='*60}")
    print(f"Running: {cmd_str}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    if result.returncode != 0 and not check_only:
        print(f"❌ Command failed: {cmd_str}")
    else:
        print(f"✅ Command completed: {cmd_str}")
    
    return result.returncode


def format_code(check_only: bool = False) -> int:
    """Format Python code with black and isort."""
    exit_codes = []
    
    # Run black
    black_cmd = ["python", "-m", "black"]
    if check_only:
        black_cmd.append("--check")
    black_cmd.extend(SOURCES)
    exit_codes.append(run_command(black_cmd, check_only))
    
    # Run isort
    isort_cmd = ["python", "-m", "isort"]
    if check_only:
        isort_cmd.append("--check-only")
    isort_cmd.extend(SOURCES)
    exit_codes.append(run_command(isort_cmd, check_only))
    
    return max(exit_codes)


def lint_code() -> int:
    """Lint Python code with ruff."""
    ruff_cmd = ["python", "-m", "ruff", "check"] + SOURCES
    return run_command(ruff_cmd)


def main():
    parser = argparse.ArgumentParser(description="Format and lint Python code")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check formatting without making changes"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run linter only (skip formatting)"
    )
    
    args = parser.parse_args()
    
    if args.lint:
        exit_code = lint_code()
    else:
        exit_code = format_code(check_only=args.check)
        if exit_code == 0 and not args.check:
            # Also run linter after formatting
            print("\n" + "="*60)
            print("Running linter after formatting...")
            print("="*60)
            lint_code()
    
    if exit_code == 0:
        print("\n✅ All checks passed!")
    else:
        print(f"\n❌ Some checks failed (exit code: {exit_code})")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
