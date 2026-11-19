import html
import json
import os
import re
from collections.abc import Callable
from pathlib import Path

import httpx

API_URL = "https://commons.wikimedia.org/w/api.php"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FULL_SPHERE_RATIO = 2.0
RATIO_TOLERANCE = 0.05
PANORAMA_WIDTH = 4096
RESULTS_PER_TOPIC = 10
HTML_TAG = re.compile(r"<[^>]+>")


def metadata_text(metadata: dict, key: str) -> str | None:
    raw = metadata.get(key, {}).get("value")
    return html.unescape(HTML_TAG.sub("", raw)).strip() if raw else None


def to_record(page: dict, lesson: dict) -> dict | None:
    info = page["imageinfo"][0]
    metadata = info.get("extmetadata", {})
    license_name, author = metadata_text(metadata, "LicenseShortName"), metadata_text(metadata, "Artist")
    if not (license_name and author):
        return None
    is_full_sphere = abs(info["width"] / info["height"] - FULL_SPHERE_RATIO) <= RATIO_TOLERANCE
    return {
        "external_id": str(page["pageid"]),
        "title": Path(page["title"].removeprefix("File:")).stem,
        "description": metadata_text(metadata, "ImageDescription") or "",
        "content_type": "360_photo" if is_full_sphere else "partial_panorama",
        "page_url": info["descriptionurl"],
        "media_url": info.get("thumburl", info["url"]),
        "license": license_name,
        "license_url": metadata_text(metadata, "LicenseUrl"),
        "author": author,
        "subject": lesson["subject"],
        "grade": lesson["grade"],
        "topic": lesson["topic"],
    }


def search_panoramas(client: httpx.Client, query: str) -> list[dict]:
    response = client.get(
        API_URL,
        params={
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrnamespace": 6,
            "gsrlimit": RESULTS_PER_TOPIC,
            "gsrsearch": f'incategory:"360°_panoramas" {query}',
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata",
            "iiurlwidth": PANORAMA_WIDTH,
            "iiextmetadatafilter": "LicenseShortName|LicenseUrl|Artist|ImageDescription",
        },
    )
    response.raise_for_status()
    return list(response.json().get("query", {}).get("pages", {}).values())


def build_records(lessons: list[dict], search: Callable[[str], list[dict]]) -> list[dict]:
    records = {}
    for lesson in lessons:
        for page in search(lesson["query"]):
            if record := to_record(page, lesson):
                records.setdefault(record["external_id"], record)
    return list(records.values())


def main() -> None:
    lessons = json.loads((DATA_DIR / "topics.json").read_text(encoding="utf-8"))
    user_agent = f"vr-excursions/0.1 ({os.environ['WIKIMEDIA_CONTACT']})"
    with httpx.Client(headers={"User-Agent": user_agent}, timeout=30) as client:
        records = build_records(lessons, lambda query: search_panoramas(client, query))
    output = DATA_DIR / "excursions.json"
    output.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved {len(records)} excursions to {output}")


if __name__ == "__main__":
    main()
