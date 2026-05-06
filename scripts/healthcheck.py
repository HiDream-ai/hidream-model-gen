#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fast readiness check for agent integrations."""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.vivago_client import create_client
from scripts.exceptions import MissingCredentialError


REQUIRED_CATEGORIES = [
    "text_to_image",
    "image_to_image",
    "text_to_video",
    "image_to_video",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Vivago auth and generation port config.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--env", default=os.environ.get("VIVAGO_AUTH_ENV", "overseas-prod"))
    args = parser.parse_args()

    os.environ.setdefault("VIVAGO_AUTH_ENV", args.env)

    payload = {
        "ok": False,
        "auth_env": args.env,
        "base_url": None,
        "categories": {},
        "error": None,
    }

    try:
        client = create_client()
        payload["base_url"] = client.base_url
        for category in REQUIRED_CATEGORIES:
            ports = client.list_ports(category)
            payload["categories"][category] = {
                "ok": bool(ports),
                "ports": list(ports.keys()),
            }
        payload["ok"] = all(info["ok"] for info in payload["categories"].values())
    except MissingCredentialError as exc:
        payload["error"] = str(exc)
    except Exception as exc:
        payload["error"] = f"{type(exc).__name__}: {exc}"

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        status = "OK" if payload["ok"] else "FAILED"
        print(f"hidream-model-gen healthcheck: {status}")
        print(f"auth_env: {payload['auth_env']}")
        if payload["base_url"]:
            print(f"base_url: {payload['base_url']}")
        for category, info in payload["categories"].items():
            print(f"{category}: {', '.join(info['ports'])}")
        if payload["error"]:
            print(f"error: {payload['error']}")

    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
