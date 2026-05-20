"""HTTP client wrapper around Vinted's internal API."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

import httpx


DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class VintedAuthError(Exception):
    pass


class VintedAPIError(Exception):
    def __init__(self, status_code: int, body: Any) -> None:
        super().__init__(f"Vinted API error {status_code}: {body!r}")
        self.status_code = status_code
        self.body = body


@dataclass
class VintedConfig:
    domain: str = "vinted.fr"
    session_cookie: str = ""
    access_token_web: str = ""
    anon_id: str = ""
    user_agent: str = DEFAULT_UA

    @classmethod
    def from_env(cls) -> "VintedConfig":
        return cls(
            domain=os.getenv("VINTED_DOMAIN", "vinted.fr").strip(),
            session_cookie=os.getenv("VINTED_SESSION_COOKIE", "").strip(),
            access_token_web=os.getenv("VINTED_ACCESS_TOKEN_WEB", "").strip(),
            anon_id=os.getenv("VINTED_ANON_ID", "").strip(),
            user_agent=os.getenv("VINTED_USER_AGENT", DEFAULT_UA).strip(),
        )

    @property
    def base_url(self) -> str:
        return f"https://www.{self.domain}"

    @property
    def api_base(self) -> str:
        return f"{self.base_url}/api/v2"

    @property
    def session_cookie_name(self) -> str:
        locale = self.domain.split(".")[-1]
        return f"_vinted_{locale}_session"

    def has_auth(self) -> bool:
        return bool(self.session_cookie or self.access_token_web)


class VintedClient:
    def __init__(self, config: Optional[VintedConfig] = None) -> None:
        self.config = config or VintedConfig.from_env()
        cookies: dict[str, str] = {}
        if self.config.session_cookie:
            cookies[self.config.session_cookie_name] = self.config.session_cookie
        if self.config.access_token_web:
            cookies["access_token_web"] = self.config.access_token_web
        if self.config.anon_id:
            cookies["anon_id"] = self.config.anon_id
        self.http = httpx.Client(
            base_url=self.config.base_url,
            cookies=cookies,
            headers={
                "User-Agent": self.config.user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                "Referer": self.config.base_url + "/",
                "Origin": self.config.base_url,
                "X-Requested-With": "XMLHttpRequest",
            },
            timeout=20.0,
            follow_redirects=True,
        )

    def close(self) -> None:
        self.http.close()

    def _request(self, method: str, path: str, *, params=None, json=None, auth_required: bool = False) -> Any:
        if auth_required and not self.config.has_auth():
            raise VintedAuthError(
                "No Vinted session cookie configured. Set VINTED_SESSION_COOKIE or "
                "VINTED_ACCESS_TOKEN_WEB. See README → 'Get your cookies'."
            )
        url = path if path.startswith("http") else f"{self.config.api_base}{path}"
        resp = self.http.request(method, url, params=params, json=json)
        if resp.status_code in (401, 403):
            raise VintedAuthError(f"Vinted refused the request ({resp.status_code}). Cookies may have expired.")
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        if resp.status_code >= 400:
            raise VintedAPIError(resp.status_code, body)
        return body

    def me(self) -> dict[str, Any]:
        return self._request("GET", "/users/current", auth_required=True)

    def _user_id(self) -> int:
        user = self.me()
        user_id = user.get("user", {}).get("id") or user.get("id")
        if not user_id:
            raise VintedAPIError(0, "Could not find user id in /users/current response")
        return int(user_id)

    def search_items(self, *, search_text: str = "", per_page: int = 20, page: int = 1,
                     order: str = "newest_first", price_to: Optional[float] = None,
                     price_from: Optional[float] = None, currency: str = "EUR",
                     catalog_ids=None, brand_ids=None) -> dict[str, Any]:
        params: dict[str, Any] = {
            "search_text": search_text, "per_page": per_page, "page": page,
            "order": order, "currency": currency,
        }
        if price_to is not None: params["price_to"] = price_to
        if price_from is not None: params["price_from"] = price_from
        if catalog_ids: params["catalog_ids"] = ",".join(str(c) for c in catalog_ids)
        if brand_ids: params["brand_ids"] = ",".join(str(b) for b in brand_ids)
        params = {k: v for k, v in params.items() if v not in ("", None)}
        return self._request("GET", "/catalog/items", params=params)

    def item_details(self, item_id: int) -> dict[str, Any]:
        # Confirmed via real Vinted traffic: /items/{id} returns 404,
        # the actual endpoint is /items/{id}/details (Datadome-protected).
        return self._request("GET", f"/items/{item_id}/details")

    def list_conversations(self, page: int = 1, per_page: int = 25) -> dict[str, Any]:
        return self._request("GET", "/inbox/conversations",
                             params={"page": page, "per_page": per_page}, auth_required=True)

    def get_conversation(self, conversation_id: int) -> dict[str, Any]:
        return self._request("GET", f"/inbox/conversations/{conversation_id}", auth_required=True)

    def send_message(self, conversation_id: int, text: str) -> dict[str, Any]:
        return self._request("POST", f"/inbox/conversations/{conversation_id}/messages",
                             json={"message": {"text": text}}, auth_required=True)

    def my_items(self, page: int = 1, per_page: int = 20, status: Optional[str] = None) -> dict[str, Any]:
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if status: params["status"] = status
        return self._request("GET", f"/users/{self._user_id()}/items",
                             params=params, auth_required=True)

    def list_my_active_items(self, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        return self.my_items(page=page, per_page=per_page, status="active")

    def list_my_sold_items(self, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        return self.my_items(page=page, per_page=per_page, status="sold")

    def update_item_price(self, item_id: int, new_price: float, currency: str = "EUR") -> dict[str, Any]:
        body = {"item": {"id": item_id, "price": f"{new_price:.2f}", "currency": currency}}
        return self._request("PUT", f"/items/{item_id}", json=body, auth_required=True)

    def close_item(self, item_id: int) -> dict[str, Any]:
        return self._request("POST", f"/items/{item_id}/close", auth_required=True)

    def reactivate_item(self, item_id: int) -> dict[str, Any]:
        return self._request("POST", f"/items/{item_id}/reactivate", auth_required=True)

    def delete_item(self, item_id: int) -> dict[str, Any]:
        return self._request("DELETE", f"/items/{item_id}", auth_required=True)

    def get_seller_stats(self) -> dict[str, Any]:
        active = self.list_my_active_items(per_page=96)
        sold = self.list_my_sold_items(per_page=96)
        active_items = active.get("items", [])
        sold_items = sold.get("items", [])

        def _total(items):
            total = 0.0
            for it in items:
                price = it.get("price", {})
                amt = price.get("amount") if isinstance(price, dict) else price
                try: total += float(amt)
                except (TypeError, ValueError): pass
            return round(total, 2)

        return {
            "active_count": len(active_items),
            "sold_count": len(sold_items),
            "active_value_total": _total(active_items),
            "sold_value_total": _total(sold_items),
            "total_views_active": sum(int(it.get("view_count") or 0) for it in active_items),
            "total_favourites_active": sum(int(it.get("favourite_count") or 0) for it in active_items),
            "note": "Counts capped at 96 per status (one page)."
        }

    def debug_get(self, path: str, params=None) -> dict[str, Any]:
        return self._request("GET", path, params=params, auth_required=True)
