#!/usr/bin/env python3
"""Small helpers shared by the agent-facing CLI scripts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path(os.environ.get("HIDREAM_OUTPUT_DIR", "assets"))


def default_output(filename: str) -> str:
    return str(DEFAULT_OUTPUT_DIR / filename)


def ensure_output_parent(path: str) -> None:
    parent = Path(path).expanduser().resolve().parent
    parent.mkdir(parents=True, exist_ok=True)


def image_url(image_id: str) -> str:
    if image_id.startswith("http"):
        return image_id
    if image_id.startswith("p_"):
        return f"https://storage.vivago.ai/image/{image_id}.jpg"
    return image_id


def video_url(video_id: str) -> str:
    if video_id.startswith("http"):
        return video_id
    clean_id = video_id[2:] if video_id.startswith("v_") else video_id
    url = f"https://media.vivago.ai/{clean_id}"
    if not url.endswith(".mp4"):
        url += ".mp4"
    return url


def collect_asset_urls(results: list[dict[str, Any]]) -> list[str]:
    urls = []
    for result in results:
        image_id = result.get("image")
        video_id = result.get("video")
        if isinstance(image_id, str) and image_id:
            urls.append(image_url(image_id))
        if isinstance(video_id, str) and video_id:
            urls.append(video_url(video_id))
    return urls


def save_json(path: str, payload: dict[str, Any]) -> None:
    ensure_output_parent(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
