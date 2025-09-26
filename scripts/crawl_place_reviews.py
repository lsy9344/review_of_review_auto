"""Utility script to fetch Naver SmartPlace reviews by placeId.

This script demonstrates how to reuse ReviewCrawler with the new placeId support.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Callable

from app.services.review_crawler import ReviewCrawler

LogCallback = Callable[[str, str], None]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch SmartPlace reviews for a given placeId using the internal GraphQL API.",
    )
    parser.add_argument(
        "--place-id",
        default="1491365787",
        help="Target placeId to crawl reviews for (default: 1491365787)",
    )
    parser.add_argument(
        "--user-id",
        default=os.getenv("NAVER_USER_ID"),
        help="Naver owner account ID (default: NAVER_USER_ID environment variable)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("NAVER_USER_PASSWORD"),
        help="Naver owner account password (default: NAVER_USER_PASSWORD environment variable)",
    )
    parser.add_argument(
        "--cookies",
        default=str(Path(".auth/cookies.json")),
        help="Path to the stored cookies JSON file (default: .auth/cookies.json)",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=40_000,
        help="GraphQL request timeout in milliseconds (default: 40000)",
    )
    return parser


def stdout_log(level: str, message: str) -> None:
    print(f"[{level}] {message}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.user_id or not args.password:
        parser.error(
            "Naver 자격 증명이 필요합니다. --user-id/--password 인자를 넘기거나 "
            "NAVER_USER_ID/NAVER_USER_PASSWORD 환경 변수를 설정하세요."
        )

    crawler = ReviewCrawler(storage_path=args.cookies, timeout_ms=args.timeout_ms)
    result = crawler.fetch_reviews_by_place_ids(
        place_ids=[args.place_id],
        user_id=args.user_id,
        password=args.password,
        log=stdout_log,
    )

    print("\n=== Crawl Result ===")
    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
