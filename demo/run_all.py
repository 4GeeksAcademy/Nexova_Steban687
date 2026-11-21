"""
Nexova Solutions — Demo Runner
Run all demos from a single entry point.

Usage:
    python -m demo.run_all
"""

import subprocess
import sys


def main():
    demos = [
        ("Recruitment Pipeline", "demo.recruitment_pipeline"),
    ]
    
    for name, module in demos:
        print(f"\n{'#' * 70}")
        print(f"# Running: {name}")
        print(f"{'#' * 70}\n")
        result = subprocess.run([sys.executable, "-m", module])
        if result.returncode != 0:
            print(f"❌ {name} failed with code {result.returncode}")
            sys.exit(1)
        print(f"\n✅ {name} completed successfully\n")


if __name__ == "__main__":
    main()