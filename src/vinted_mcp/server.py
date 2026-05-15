"""MCP server exposing Vinted tools."""

from __future__ import annotations

import json
import os
from typing import Any, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .client import VintedAPIError, VintedAuthError, VintedClient
from .templates import TEMPLATES, get_template


load_dotenv()
mcp = FastMCP("vinted")
_client: Optional[VintedClient] = None


def get_client() -> VintedClient:
    global _client
    if _client is None:
        _client = VintedClient()
    return _client


def _fmt(payload: Any) -> str:
    try:
        return json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    except Exception:
        return str(payload)


def _safe_call(fn, *args, **kwargs) -> str:
    try:
        return _fmt(fn(*args, **kwargs))
    except VintedAuthError as e:
        return _fmt({"error": "auth_required", "detail": str(e)})
    except VintedAPIError as e:
        return _fmt({"error": "api_error", "status": e.status_code, "body": e.body})
    except Exception as e:
        return _fmt({"error": "unexpected", "detail": repr(e)})


@mcp.tool()
def whoami() -> str:
    """Return information about the currently logged-in Vinted user."""
    return _safe_call(get_client().me)


@mcp.tool()
def search_items(search_text: str = "", per_page: int = 20, page: int = 1,
                 order: str = "newest_first", price_to: Optional[float] = None,
                 price_from: Optional[float] = None, currency: str = "EUR") -> str:
    """Search Vinted's public catalog."""
    return _safe_call(get_client().search_items, search_text=search_text,
                      per_page=per_page, page=page, order=order, price_to=price_to,
                      price_from=price_from, currency=currency)


@mcp.tool()
def get_item(item_id: int) -> str:
    """Get full details for a single Vinted item by id."""
    return _safe_call(get_client().item_details, item_id)


@mcp.tool()
def list_conversations(page: int = 1, per_page: int = 25) -> str:
    """List your Vinted inbox conversations."""
    return _safe_call(get_client().list_conversations, page=page, per_page=per_page)


@mcp.tool()
def get_conversation(conversation_id: int) -> str:
    """Fetch a specific conversation with its messages."""
    return _safe_call(get_client().get_conversation, conversation_id)


@mcp.tool()
def send_message(conversation_id: int, text: str) -> str:
    """Send a reply in an existing Vinted conversation."""
    if not text.strip():
        return _fmt({"error": "validation", "detail": "text must not be empty"})
    return _safe_call(get_client().send_message, conversation_id, text)


@mcp.tool()
def my_items(page: int = 1, per_page: int = 20, status: Optional[str] = None) -> str:
    """List your items. status: active|sold|reserved|draft|closed."""
    return _safe_call(get_client().my_items, page=page, per_page=per_page, status=status)


@mcp.tool()
def list_my_active_items(page: int = 1, per_page: int = 20) -> str:
    """List your active listings."""
    return _safe_call(get_client().list_my_active_items, page=page, per_page=per_page)


@mcp.tool()
def list_my_sold_items(page: int = 1, per_page: int = 20) -> str:
    """List your sold listings."""
    return _safe_call(get_client().list_my_sold_items, page=page, per_page=per_page)


@mcp.tool()
def update_item_price(item_id: int, new_price: float, currency: str = "EUR") -> str:
    """Change the price of one of your active listings."""
    if new_price <= 0:
        return _fmt({"error": "validation", "detail": "new_price must be > 0"})
    return _safe_call(get_client().update_item_price, item_id, new_price, currency)


@mcp.tool()
def close_item(item_id: int) -> str:
    """Close (deactivate) one of your listings."""
    return _safe_call(get_client().close_item, item_id)


@mcp.tool()
def reactivate_item(item_id: int) -> str:
    """Re-publish a previously closed listing."""
    return _safe_call(get_client().reactivate_item, item_id)


@mcp.tool()
def delete_item(item_id: int) -> str:
    """Permanently delete one of your listings. Irreversible."""
    return _safe_call(get_client().delete_item, item_id)


@mcp.tool()
def get_seller_stats() -> str:
    """Quick summary: active/sold counts, total value, views, favourites."""
    return _safe_call(get_client().get_seller_stats)


@mcp.tool()
def list_reply_templates() -> str:
    """List the available reply templates for common buyer questions."""
    return _fmt(TEMPLATES)


@mcp.tool()
def render_template(template_id: str, variables_json: str = "{}") -> str:
    """Render a reply template with the given variables filled in."""
    tpl = get_template(template_id)
    if not tpl:
        return _fmt({"error": "validation", "detail": f"unknown template_id '{template_id}'"})
    try:
        variables = json.loads(variables_json) if variables_json else {}
    except json.JSONDecodeError as e:
        return _fmt({"error": "validation", "detail": f"variables_json not valid JSON: {e}"})
    try:
        text = tpl["text"].format(**variables)
    except KeyError as e:
        return _fmt({"error": "validation", "detail": f"missing placeholder {e}",
                     "required": list(tpl.get("placeholders", {}).keys())})
    return _fmt({"template_id": template_id, "text": text,
                 "safe_auto": tpl.get("safe_auto", False)})


@mcp.tool()
def debug_get(path: str, params_json: str = "{}") -> str:
    """Hit any /api/v2 endpoint manually."""
    try:
        params = json.loads(params_json) if params_json else {}
    except json.JSONDecodeError as e:
        return _fmt({"error": "validation", "detail": f"params_json is not valid JSON: {e}"})
    return _safe_call(get_client().debug_get, path, params=params)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
