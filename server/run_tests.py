#!/usr/bin/env python3
"""
Test runner script for Todo API.
Provides easy commands to run different types of tests.
"""

import subprocess
import sys
import argparse


def run_command(cmd):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests for Todo API")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "models", "crud", "services", "controllers", "auth"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Generate coverage report"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Verbose output"
    )
    parser.add_argument(
        "--failfast", "-x", 
        action="store_true", 
        help="Stop on first failure"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add fail fast
    if args.failfast:
        cmd.append("-x")
    
    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html:htmlcov"])
    
    # Select test type
    if args.type == "all":
        cmd.append("tests/")
    elif args.type == "unit":
        cmd.extend(["-m", "unit", "tests/"])
    elif args.type == "integration":
        cmd.extend(["-m", "integration", "tests/"])
    elif args.type == "models":
        cmd.append("tests/test_models.py")
    elif args.type == "crud":
        cmd.append("tests/test_crud.py")
    elif args.type == "services":
        cmd.append("tests/test_services.py")
    elif args.type == "controllers":
        cmd.append("tests/test_controllers.py")
    elif args.type == "auth":
        cmd.append("tests/test_auth.py")
    
    # Run the tests
    return_code = run_command(cmd)
    
    if return_code == 0:
        print("\n✅ All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(return_code)


if __name__ == "__main__":
    main() 