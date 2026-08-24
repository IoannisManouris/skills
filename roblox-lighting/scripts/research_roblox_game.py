#!/usr/bin/env python3
"""Collect public Roblox experience metadata/media for lighting research.

This helper never uses cookies or bypasses authentication. Roblox endpoint shapes
and availability can change; every request and failure is recorded in the output.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

PLACE_PATTERNS = [
    re.compile(r"/games/(\d+)(?:/|$)"),
    re.compile(r"(?:placeId|placeid)=(\d+)"),
    re.compile(r"^\s*(\d+)\s*$"),
]
USER_AGENT = "roblox-lighting-agent-skill/1.0 (+public metadata research)"


def request_bytes(url: str, timeout: float, retries: int = 2) -> tuple[bytes, dict[str, str], str]:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/json,image/*;q=0.8,*/*;q=0.5",
                },
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                headers = {key.lower(): value for key, value in response.headers.items()}
                return response.read(), headers, response.geturl()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
    assert last_error is not None
    raise last_error


def request_json(url: str, timeout: float) -> tuple[Any, str]:
    raw, _headers, final_url = request_bytes(url, timeout)
    return json.loads(raw.decode("utf-8")), final_url


def resolve_redirect(url: str, timeout: float) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.geturl()


def extract_place_id(value: str) -> int | None:
    for pattern in PLACE_PATTERNS:
        match = pattern.search(value)
        if match:
            return int(match.group(1))
    return None


def safe_slug(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-")
    return text[:80] or "media"


def collect_candidate_ids(media_payload: Any) -> list[int]:
    ids: list[int] = []
    if isinstance(media_payload, dict):
        items = media_payload.get("data", media_payload.get("media", []))
    else:
        items = media_payload
    if not isinstance(items, list):
        return ids
    for item in items:
        if not isinstance(item, dict):
            continue
        for key in ("imageId", "assetId", "thumbnailId", "targetId", "id"):
            value = item.get(key)
            if isinstance(value, int) and value > 0:
                ids.append(value)
                break
            if isinstance(value, str) and value.isdigit():
                ids.append(int(value))
                break
    return list(dict.fromkeys(ids))


def extract_image_urls(payload: Any) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    items = payload.get("data", []) if isinstance(payload, dict) else []
    if not isinstance(items, list):
        return results
    for item in items:
        if not isinstance(item, dict):
            continue
        image_url = item.get("imageUrl") or item.get("url")
        if isinstance(image_url, str):
            results.append(
                {
                    "target_id": item.get("targetId") or item.get("id"),
                    "state": item.get("state"),
                    "image_url": image_url,
                    "version": item.get("version"),
                }
            )
    return results


def download_images(images: list[dict[str, Any]], directory: Path, timeout: float, log: list[dict[str, Any]]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for index, image in enumerate(images, start=1):
        url = image.get("image_url")
        if not isinstance(url, str):
            continue
        try:
            raw, headers, final_url = request_bytes(url, timeout)
            content_type = headers.get("content-type", "").split(";", 1)[0]
            extension = mimetypes.guess_extension(content_type) or Path(urllib.parse.urlparse(final_url).path).suffix or ".png"
            target_id = image.get("target_id") or index
            filename = f"{index:02d}-{safe_slug(str(target_id))}{extension}"
            path = directory / filename
            path.write_bytes(raw)
            image["downloaded_file"] = str(path)
            log.append({"url": url, "ok": True, "final_url": final_url, "file": str(path)})
        except Exception as exc:  # noqa: BLE001
            log.append({"url": url, "ok": False, "error": str(exc)})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roblox_url_or_place_id")
    parser.add_argument("--output", type=Path, default=Path("roblox-research.json"))
    parser.add_argument("--download-dir", type=Path)
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    input_value = args.roblox_url_or_place_id.strip()
    canonical_url = input_value
    place_id = extract_place_id(input_value)
    request_log: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    if place_id is None and input_value.startswith(("http://", "https://")):
        try:
            canonical_url = resolve_redirect(input_value, args.timeout)
            place_id = extract_place_id(canonical_url)
            request_log.append({"purpose": "redirect_resolution", "url": input_value, "ok": True, "final_url": canonical_url})
        except Exception as exc:  # noqa: BLE001
            failures.append({"purpose": "redirect_resolution", "url": input_value, "error": str(exc)})

    if place_id is None:
        print("ERROR: could not extract a Roblox place ID from the input", file=sys.stderr)
        return 2

    result: dict[str, Any] = {
        "schema_version": "1.0",
        "input": input_value,
        "canonical_url": canonical_url,
        "place_id": place_id,
        "universe_id": None,
        "game_metadata": None,
        "official_media": None,
        "thumbnail_delivery": [],
        "source_ledger": [],
        "suggested_search_queries": [],
        "request_log": request_log,
        "failures": failures,
        "limitations": [
            "Public metadata/media do not reveal private Roblox Studio lighting settings.",
            "Official thumbnails can be staged, edited, old, or captured under a different lighting state.",
            "Endpoint availability and response shapes can change; verify against current Roblox documentation."
        ]
    }

    def fetch(purpose: str, url: str) -> Any | None:
        try:
            payload, final_url = request_json(url, args.timeout)
            request_log.append({"purpose": purpose, "url": url, "ok": True, "final_url": final_url})
            return payload
        except Exception as exc:  # noqa: BLE001
            failures.append({"purpose": purpose, "url": url, "error": str(exc)})
            request_log.append({"purpose": purpose, "url": url, "ok": False, "error": str(exc)})
            return None

    universe_url = f"https://apis.roblox.com/universes/v1/places/{place_id}/universe"
    universe_payload = fetch("place_to_universe", universe_url)
    universe_id: int | None = None
    if isinstance(universe_payload, dict):
        raw_universe = universe_payload.get("universeId") or universe_payload.get("universe_id")
        if isinstance(raw_universe, int):
            universe_id = raw_universe
        elif isinstance(raw_universe, str) and raw_universe.isdigit():
            universe_id = int(raw_universe)
    result["universe_id"] = universe_id

    title = None
    creator_name = None
    if universe_id is not None:
        game_url = "https://games.roblox.com/v1/games?" + urllib.parse.urlencode({"universeIds": str(universe_id)})
        game_payload = fetch("game_metadata", game_url)
        result["game_metadata"] = game_payload
        if isinstance(game_payload, dict) and isinstance(game_payload.get("data"), list) and game_payload["data"]:
            game = game_payload["data"][0]
            if isinstance(game, dict):
                title = game.get("name")
                creator = game.get("creator")
                if isinstance(creator, dict):
                    creator_name = creator.get("name")

        media_url = f"https://games.roblox.com/v2/games/{universe_id}/media"
        media_payload = fetch("official_experience_media", media_url)
        result["official_media"] = media_payload
        media_ids = collect_candidate_ids(media_payload)

        delivered: list[dict[str, Any]] = []
        if media_ids:
            thumb_params = {
                "thumbnailIds": ",".join(map(str, media_ids)),
                "size": "768x432",
                "format": "Png",
                "isCircular": "false",
            }
            thumb_url = f"https://thumbnails.roblox.com/v1/games/{universe_id}/thumbnails?" + urllib.parse.urlencode(thumb_params)
            thumb_payload = fetch("official_media_thumbnail_delivery", thumb_url)
            if thumb_payload is not None:
                delivered.extend(extract_image_urls(thumb_payload))

        icon_params = {
            "universeIds": str(universe_id),
            "returnPolicy": "PlaceHolder",
            "size": "512x512",
            "format": "Png",
            "isCircular": "false",
        }
        icon_url = "https://thumbnails.roblox.com/v1/games/icons?" + urllib.parse.urlencode(icon_params)
        icon_payload = fetch("game_icon_delivery", icon_url)
        if icon_payload is not None:
            for item in extract_image_urls(icon_payload):
                item["media_role"] = "game_icon"
                delivered.append(item)

        result["thumbnail_delivery"] = delivered
        for index, item in enumerate(delivered, start=1):
            result["source_ledger"].append(
                {
                    "source_id": f"official-media-{index:02d}",
                    "url": item.get("image_url"),
                    "source_type": "official_experience_media" if item.get("media_role") != "game_icon" else "official_thumbnail",
                    "experience_identity_confidence": 0.99,
                    "raw_gameplay_confidence": 0.55 if item.get("media_role") != "game_icon" else 0.25,
                    "lighting_cluster": None,
                    "similarity_to_user_snapshot": None,
                    "included": False,
                    "notes": ["Requires visual review and lighting-state clustering before use."]
                }
            )

        if args.download_dir and delivered:
            download_images(delivered, args.download_dir, args.timeout, request_log)

    display = title or f"Roblox place {place_id}"
    creator_fragment = f' "{creator_name}"' if creator_name else ""
    result["suggested_search_queries"] = [
        f'"{display}" Roblox gameplay screenshots',
        f'"{display}"{creator_fragment} Roblox gameplay',
        f'"{display}" Roblox walkthrough lighting',
        f'"{display}" Roblox night day update',
        f'"{display}" Roblox map gameplay video',
        f'Roblox place {place_id} gameplay',
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Place ID: {place_id}; Universe ID: {universe_id}")
    print(f"Official delivered images: {len(result['thumbnail_delivery'])}")
    if failures:
        print(f"Completed with {len(failures)} request failure(s); see the output ledger.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
