#!/usr/bin/env python3
"""Vivago / HiDream login CLI.

Browser-based login plus local token cache management only.
This script intentionally does not contain ACRC business operations.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import dataclasses
import datetime as dt
import fcntl
import http.server
import json
import os
import pathlib
import signal
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


_ENVS: dict[str, dict[str, str]] = {
    "overseas-dev": {
        "login_url": "http://dev.vivago.ai/login-cli",
        "refresh_url": "https://dev.vivago.ai/prod-api/user/apikey2token",
        "config_file": "vivago_auth_overseas_dev.json",
    },
    "overseas-prod": {
        "login_url": "http://vivago.ai/login-cli",
        "refresh_url": "https://vivago.ai/prod-api/user/apikey2token",
        "config_file": "vivago_auth_overseas_prod.json",
    },
    "domestic-dev": {
        "login_url": "https://dev.hidreamai.com/login-cli",
        "refresh_url": "https://dev.hidreamai.com/prod-api/user/apikey2token",
        "config_file": "vivago_auth_domestic_dev.json",
    },
    "domestic-prod": {
        "login_url": "http://hidreamai.com/login-cli",
        "refresh_url": "https://hidreamai.com/prod-api/user/apikey2token",
        "config_file": "vivago_auth_domestic_prod.json",
    },
}

DEFAULT_ENV = "overseas-prod"
_CONFIG_DIR = pathlib.Path(
    os.environ.get("XDG_CONFIG_HOME", str(pathlib.Path.home() / ".config"))
) / "vivago-auth"
CALLBACK_PORT = 50366
LOGIN_TIMEOUT_SECONDS = 300
HTTP_TIMEOUT = 30
TOKEN_BUFFER_SECONDS = 60
REFRESH_RETRY_COUNT = 1
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


class VivagoAuthError(Exception):
    """Base error for vivago login CLI failures."""


class ConfigError(VivagoAuthError):
    """Config file missing, invalid, or JWT malformed."""


class LoginTimeoutError(VivagoAuthError):
    """Browser login not completed within LOGIN_TIMEOUT_SECONDS."""


class RefreshFailedError(VivagoAuthError):
    """Token refresh API returned an error."""


@dataclasses.dataclass(frozen=True)
class TokenData:
    ticket: str
    refresh_token: str
    ticket_exp: int | None
    refresh_token_exp: int | None
    saved_at: str


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


def _resolve_config_path(env: str) -> pathlib.Path:
    override = os.environ.get("VIVAGO_AUTH_CONFIG_PATH")
    if override:
        return pathlib.Path(override)
    cfg = _ENVS.get(env)
    if cfg is None:
        raise ConfigError(f"unknown environment '{env}'; valid: {', '.join(_ENVS)}")
    return _CONFIG_DIR / cfg["config_file"]


def decode_jwt_payload(token: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ConfigError(f"malformed JWT: expected 3 dot-separated parts, got {len(parts)}")
    payload_b64 = parts[1]
    padding = 4 - (len(payload_b64) % 4)
    if padding != 4:
        payload_b64 += "=" * padding
    try:
        raw_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(raw_bytes)
    except (ValueError, json.JSONDecodeError) as exc:
        raise ConfigError(f"JWT payload decode failed: {exc}") from exc


def jwt_exp_optional(token: str) -> int | None:
    payload = decode_jwt_payload(token)
    exp = payload.get("exp")
    if exp is None:
        return None
    if not isinstance(exp, int):
        raise ConfigError(f"JWT missing or invalid 'exp' field (got {type(exp).__name__})")
    return exp


def is_expired(exp_ts: int, buffer_seconds: int = TOKEN_BUFFER_SECONDS) -> bool:
    return time.time() + buffer_seconds >= exp_ts


def _coerce_optional_exp(raw: dict[str, Any], field: str) -> int | None:
    value = raw.get(field)
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{field} must be int or null, got bool")
    return int(value)


def load_config(path: pathlib.Path) -> TokenData | None:
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError(f"config file {path} must contain a JSON object, got {type(raw).__name__}")
    try:
        return TokenData(
            ticket=str(raw["ticket"]),
            refresh_token=str(raw["refresh_token"]),
            ticket_exp=_coerce_optional_exp(raw, "ticket_exp"),
            refresh_token_exp=_coerce_optional_exp(raw, "refresh_token_exp"),
            saved_at=str(raw.get("saved_at", "")),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigError(f"config file {path} has missing/invalid field: {exc}") from exc


def save_config(data: TokenData, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ticket": data.ticket,
        "refresh_token": data.refresh_token,
        "ticket_exp": data.ticket_exp,
        "refresh_token_exp": data.refresh_token_exp,
        "saved_at": data.saved_at,
    }
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    try:
        os.chmod(tmp, 0o600)
    except OSError as exc:
        eprint(f"Warning: could not set permissions on {tmp}: {exc}")
    tmp.replace(path)


def _build_token_data(ticket: str, refresh_token: str) -> TokenData:
    try:
        ticket_exp = jwt_exp_optional(ticket)
        refresh_token_exp = jwt_exp_optional(refresh_token)
    except ConfigError as exc:
        raise ConfigError(f"server returned invalid JWT in redirect: {exc}") from exc
    return TokenData(
        ticket=ticket,
        refresh_token=refresh_token,
        ticket_exp=ticket_exp,
        refresh_token_exp=refresh_token_exp,
        saved_at=dt.datetime.now(tz=dt.timezone.utc).isoformat(),
    )


def _token_state(exp_ts: int | None) -> str:
    if exp_ts is None:
        return "UNKNOWN"
    return "EXPIRED" if is_expired(exp_ts) else "VALID"


def _token_exp_str(exp_ts: int | None) -> str:
    if exp_ts is None:
        return "unknown"
    return dt.datetime.fromtimestamp(exp_ts, tz=dt.timezone.utc).isoformat()


def _can_use_cached_ticket(data: TokenData) -> bool:
    return data.ticket_exp is not None and not is_expired(data.ticket_exp)


def _can_attempt_refresh(data: TokenData) -> bool:
    return data.refresh_token_exp is None or not is_expired(data.refresh_token_exp)


@contextlib.contextmanager
def _config_lock(path: pathlib.Path):  # type: ignore[return]
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_file = path.with_suffix(".lock")
    with open(lock_file, "w") as lock_handle:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


def _open_browser(url: str) -> None:
    openers = []
    if sys.platform == "darwin":
        openers.append(["open", url])
    openers.append(["xdg-open", url])
    for cmd in openers:
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=5)
            return
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    eprint("Could not open browser automatically.")
    eprint(f"Please open this URL manually: {url}")


def _run_browser_login_flow(
    login_url: str,
    refresh_url: str,
    config_path: pathlib.Path,
    timeout: int = LOGIN_TIMEOUT_SECONDS,
) -> TokenData:
    _ = refresh_url
    result_holder: dict[str, str] = {}
    done_event = threading.Event()

    class _CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            refresh_token = params.get("refresh_token", [None])[0]
            ticket = params.get("ticket", [None])[0]
            if not refresh_token or not ticket:
                body = b"Login failed: missing refresh_token or ticket in redirect."
                self.send_response(400)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            result_holder["refresh_token"] = refresh_token
            result_holder["ticket"] = ticket
            body = b"Login successful. You can close this tab."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            done_event.set()

        def log_message(self, fmt: str, *args: Any) -> None:  # noqa: ARG002
            pass

    try:
        server = http.server.HTTPServer(("127.0.0.1", CALLBACK_PORT), _CallbackHandler)
    except OSError as exc:
        raise VivagoAuthError(
            f"port {CALLBACK_PORT} is already in use — stop any other vivago login process and retry"
        ) from exc

    server.timeout = 1.0

    def _serve() -> None:
        deadline = time.monotonic() + timeout
        while not done_event.is_set() and time.monotonic() < deadline:
            try:
                server.handle_request()
            except Exception:
                pass
        server.server_close()

    eprint(f"Opening browser: {login_url}")
    _open_browser(login_url)
    eprint(f"Waiting for login callback on http://127.0.0.1:{CALLBACK_PORT}/ ...")
    eprint(f"(Timeout in {timeout}s. Press Ctrl+C to cancel.)")

    server_thread = threading.Thread(target=_serve, daemon=True)
    server_thread.start()
    done_event.wait(timeout=timeout + 2)
    server_thread.join(timeout=2)

    if not done_event.is_set():
        raise LoginTimeoutError(
            f"Login not completed within {timeout} seconds. Run 'login' again to retry."
        )

    data = _build_token_data(
        ticket=result_holder["ticket"],
        refresh_token=result_holder["refresh_token"],
    )
    save_config(data, config_path)
    eprint("Login successful. Token saved.")
    return data


def _call_refresh_api(refresh_token: str, refresh_url: str) -> str:
    req = urllib.request.Request(refresh_url)
    req.add_header("Refresh-Token", refresh_token)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", _USER_AGENT)
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RefreshFailedError(f"refresh API HTTP error {exc.code}: {body[:200]}") from exc
    except urllib.error.URLError as exc:
        raise RefreshFailedError(f"refresh API network error: {exc.reason}") from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RefreshFailedError(f"refresh API returned invalid JSON: {body[:200]}") from exc

    if parsed.get("code") != 0:
        raise RefreshFailedError(
            f"refresh API returned error code {parsed.get('code')}: {parsed.get('message', '(no message)')}"
        )
    try:
        return str(parsed["result"]["token"])
    except (KeyError, TypeError) as exc:
        raise RefreshFailedError(f"refresh API response missing result.token: {exc}") from exc


def _do_refresh(data: TokenData, refresh_url: str, config_path: pathlib.Path) -> TokenData:
    last_exc: RefreshFailedError | None = None
    for attempt in range(REFRESH_RETRY_COUNT + 1):
        try:
            new_ticket = _call_refresh_api(data.refresh_token, refresh_url)
            break
        except RefreshFailedError as exc:
            last_exc = exc
            if attempt < REFRESH_RETRY_COUNT:
                eprint(f"Refresh attempt {attempt + 1} failed: {exc}. Retrying...")
                time.sleep(1)
    else:
        raise last_exc  # type: ignore[misc]

    new_data = TokenData(
        ticket=new_ticket,
        refresh_token=data.refresh_token,
        ticket_exp=jwt_exp_optional(new_ticket),
        refresh_token_exp=data.refresh_token_exp,
        saved_at=dt.datetime.now(tz=dt.timezone.utc).isoformat(),
    )
    save_config(new_data, config_path)
    return new_data


def get_token(env: str = DEFAULT_ENV, force_login: bool = False) -> str:
    cfg = _ENVS.get(env)
    if cfg is None:
        raise ConfigError(f"unknown environment '{env}'")
    config_path = _resolve_config_path(env)
    login_url = cfg["login_url"]
    refresh_url = cfg["refresh_url"]

    with _config_lock(config_path):
        if force_login:
            return _run_browser_login_flow(login_url, refresh_url, config_path).ticket

        data: TokenData | None = None
        try:
            data = load_config(config_path)
        except ConfigError as exc:
            eprint(f"Warning: config file corrupt ({exc}), re-authenticating...")

        if data is None:
            return _run_browser_login_flow(login_url, refresh_url, config_path).ticket
        if _can_use_cached_ticket(data):
            return data.ticket
        if _can_attempt_refresh(data):
            try:
                if data.ticket_exp is None:
                    eprint("Ticket expiry unknown, refreshing...")
                else:
                    eprint("Ticket expired, refreshing...")
                refreshed = _do_refresh(data, refresh_url, config_path)
                eprint("Token refreshed successfully.")
                return refreshed.ticket
            except RefreshFailedError as exc:
                eprint(f"Refresh failed: {exc}. Falling back to browser login...")
                return _run_browser_login_flow(login_url, refresh_url, config_path).ticket

        if data.refresh_token_exp is None:
            eprint("Refresh token expiry unknown but refresh is unavailable. Re-authenticating...")
        else:
            eprint("Both ticket and refresh token are expired. Re-authenticating...")
        return _run_browser_login_flow(login_url, refresh_url, config_path).ticket


def handle_login(args: argparse.Namespace) -> int:
    cfg = _ENVS[args.env]
    config_path = _resolve_config_path(args.env)
    with _config_lock(config_path):
        data = _run_browser_login_flow(cfg["login_url"], cfg["refresh_url"], config_path)
    eprint(f"Logged in. Ticket expires: {_token_exp_str(data.ticket_exp)}")
    return 0


def handle_token(args: argparse.Namespace) -> int:
    print(get_token(env=args.env, force_login=getattr(args, "force", False)))
    return 0


def handle_logout(args: argparse.Namespace) -> int:
    config_path = _resolve_config_path(args.env)
    if not config_path.exists():
        eprint("Not logged in (no config file).")
        return 0
    config_path.unlink()
    lock_file = config_path.with_suffix(".lock")
    if lock_file.exists():
        try:
            lock_file.unlink()
        except OSError:
            pass
    eprint("Logged out. Config file removed.")
    return 0


def handle_status(args: argparse.Namespace) -> int:
    config_path = _resolve_config_path(args.env)
    eprint(f"Environment:  {args.env}")
    eprint(f"Config path:  {config_path}")
    eprint(f"Config exists: {config_path.exists()}")
    if not config_path.exists():
        eprint("Status: NOT LOGGED IN")
        return 0
    try:
        data = load_config(config_path)
    except ConfigError as exc:
        eprint(f"Status: CONFIG CORRUPT ({exc})")
        return 1
    if data is None:
        eprint("Status: NOT LOGGED IN")
        return 0

    ticket_state = _token_state(data.ticket_exp)
    refresh_state = _token_state(data.refresh_token_exp)
    eprint(f"Ticket:        {ticket_state} (exp: {_token_exp_str(data.ticket_exp)})")
    eprint(f"Refresh token: {refresh_state} (exp: {_token_exp_str(data.refresh_token_exp)})")
    eprint(f"Saved at:      {data.saved_at}")

    if ticket_state == "VALID":
        eprint("Status: AUTHENTICATED")
    elif ticket_state == "UNKNOWN" and refresh_state in {"VALID", "UNKNOWN"}:
        eprint("Status: TICKET EXPIRY UNKNOWN (refresh available — run 'token' to refresh)")
    elif ticket_state == "UNKNOWN":
        eprint("Status: TICKET EXPIRY UNKNOWN (refresh unavailable — run 'login' to re-authenticate)")
    elif refresh_state in {"VALID", "UNKNOWN"}:
        eprint("Status: TICKET EXPIRED (refresh token valid — run 'token' to auto-refresh)")
    else:
        eprint("Status: FULLY EXPIRED (run 'login' to re-authenticate)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vivago_login.py",
        description="Vivago/HiDream login CLI — browser login and local token cache management only.",
    )
    parser.add_argument("--env", default=DEFAULT_ENV, choices=list(_ENVS))
    subparsers = parser.add_subparsers(dest="command", required=True)

    login_p = subparsers.add_parser("login", help="Open browser login flow and save tokens locally.")
    login_p.set_defaults(handler=handle_login)

    token_p = subparsers.add_parser("token", help="Print a valid ticket to stdout, auto-refreshing if needed.")
    token_p.add_argument("--force", action="store_true", help="Force browser re-login even if token is valid.")
    token_p.set_defaults(handler=handle_token)

    status_p = subparsers.add_parser("status", help="Show cached token status without printing secrets.")
    status_p.set_defaults(handler=handle_status)

    logout_p = subparsers.add_parser("logout", help="Delete the stored auth file for the selected environment.")
    logout_p.set_defaults(handler=handle_logout)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    prev_sigint = signal.getsignal(signal.SIGINT)
    prev_sigterm = signal.getsignal(signal.SIGTERM)
    try:
        return args.handler(args)
    except KeyboardInterrupt:
        eprint("Interrupted.")
        return 130
    except VivagoAuthError as exc:
        eprint(f"Error: {exc}")
        return 1
    finally:
        signal.signal(signal.SIGINT, prev_sigint)
        signal.signal(signal.SIGTERM, prev_sigterm)


if __name__ == "__main__":
    raise SystemExit(main())
