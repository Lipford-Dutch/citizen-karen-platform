#!/usr/bin/env python3
"""
scripts/generate_mock_data.py — CLI tool that prints mock complaint records as JSON.

Usage:
    python scripts/generate_mock_data.py [--count N] [--agency AGENCY] [--seed SEED]

Examples:
    python scripts/generate_mock_data.py
    python scripts/generate_mock_data.py --count 5 --agency FCC
    python scripts/generate_mock_data.py --count 100 --seed 42 > mock_complaints.json
"""

import argparse
import json
import random
import sys
import os

# Allow running from repo root without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.utils.mock_data import generate_complaints


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate mock complaint payloads for the Citizen Karen platform."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of complaints to generate (default: 10).",
    )
    parser.add_argument(
        "--agency",
        type=str,
        default=None,
        help="Agency hint to assign to every complaint. "
             "If omitted, each complaint gets a random agency.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible output.",
    )
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    data = generate_complaints(count=args.count, agency=args.agency)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
