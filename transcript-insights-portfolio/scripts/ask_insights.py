#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import execute_transcript_insights  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a mock transcript-insights query.")
    parser.add_argument("query", help="Question to run against the mocked transcript store.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        response = execute_transcript_insights({"query": args.query})
    except Exception as exc:
        print(
            json.dumps(
                {
                    "error": str(exc),
                    "note": (
                        "This portfolio repository preserves the real architecture shape, "
                        "but it does not include private data, credentials, or live provider access."
                    ),
                },
                indent=2,
            )
        )
        return 1
    print(json.dumps(response, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
