"""Anonimowy klient HTTP oparty wyłącznie o bibliotekę standardową.

Cele:
  * brak ciasteczek (pusty CookieJar),
  * brak zapisu historii / cache przez aplikację,
  * nagłówek Do Not Track,
  * opcjonalny proxy (np. Tor SOCKS5 127.0.0.1:9050),
  * możliwość ustawienia własnego User-Agent.

Uwaga dla użytkownika (ważne!):
Tryb prywatny w OmniFoto oznacza, że *aplikacja* nie śledzi Cię i nie zapisuje
śladów. Pełną anonimowość w sieci daje dopiero skonfigurowanie proxy/Tor w
ustawieniach. Nie obiecujemy „niewidzialności” bez proxy.
"""

from __future__ import annotations

import gzip
import json
import random
import ssl
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from typing import Any

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
]

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl,en;q=0.8",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
}


class PrivacySession:
    """Lekka sesja HTTP bez ciasteczek i bez stanu między żądaniami."""

    def __init__(self, settings: Any | None = None, timeout: int = 12) -> None:
        self.timeout = timeout
        self.settings = settings
        # Każdy wątek dostaje własny opener - współdzielony CookieJar/opener
        # potrafi zwiesić wyszukiwanie przy równoległych zapytaniach.
        self._local = threading.local()
        self._ssl_context = ssl.create_default_context()
        # nie odrzucaj starszych certyfikatów, ale weryfikuj je (bezpieczeństwo)
        self._ssl_context.check_hostname = True
        self._ssl_context.verify_mode = ssl.CERT_REQUIRED

    # --- konfiguracja -------------------------------------------------------
    @property
    def user_agent(self) -> str:
        custom = ""
        if self.settings is not None:
            custom = str(self.settings.get("user_agent", "") or "")
        return custom or random.choice(USER_AGENTS)

    def _build_opener(self) -> urllib.request.OpenerDirector:
        handlers: list[Any] = [
            urllib.request.HTTPHandler(),
            urllib.request.HTTPSHandler(context=self._ssl_context),
            urllib.request.HTTPCookieProcessor(CookieJar()),  # pusty, nic nie zapisuje
            urllib.request.HTTPRedirectHandler(),
        ]
        proxy = self._proxy_handler()
        if proxy is not None:
            handlers.append(proxy)
        return urllib.request.build_opener(*handlers)

    def _proxy_handler(self) -> Any | None:
        if self.settings is None or not self.settings.get("proxy_enabled", False):
            return None
        host = str(self.settings.get("proxy_host", "127.0.0.1"))
        port = int(self.settings.get("proxy_port", 9050))
        ptype = str(self.settings.get("proxy_type", "socks5")).lower()
        if ptype in ("socks5", "socks5h"):
            try:
                # urllib nie ma natywnego SOCKS - używamy opcjonalnego PySocks
                import socks  # type: ignore
                import sockshandler  # type: ignore
                return sockshandler.SocksiPyHandler(socks.SOCKS5, host, port)
            except ImportError:
                return None
        proxy_url = f"{ptype}://{host}:{port}"
        return urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})

    def _opener_now(self) -> urllib.request.OpenerDirector:
        opener = getattr(self._local, "opener", None)
        if opener is None:
            opener = self._build_opener()
            self._local.opener = opener
        return opener

    # --- żądania ------------------------------------------------------------
    def request(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        method: str = "GET",
        data: bytes | None = None,
    ) -> bytes:
        """Wykonuje żądanie i zwraca surowe bajty. Rzuca wyjątek przy błędzie."""
        if params:
            sep = "&" if "?" in url else "?"
            url = url + sep + urllib.parse.urlencode(params)
        hdrs = dict(DEFAULT_HEADERS)
        hdrs["User-Agent"] = self.user_agent
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        with self._opener_now().open(req, timeout=self.timeout) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding", "").lower() == "gzip":
                raw = gzip.decompress(raw)
            return raw

    def get_json(self, url: str, **kwargs: Any) -> Any:
        raw = self.request(
            url,
            headers={**kwargs.pop("headers", {}), "Accept": "application/json"},
            **kwargs,
        )
        return json.loads(raw.decode("utf-8", "replace"))

    def get_text(self, url: str, **kwargs: Any) -> str:
        return self.request(url, **kwargs).decode("utf-8", "replace")

    def head(self, url: str) -> dict[str, str]:
        """Zwraca nagłówki (np. Content-Length, Content-Type) bez pobierania treści."""
        hdrs = {"User-Agent": self.user_agent, "DNT": "1"}
        req = urllib.request.Request(url, headers=hdrs, method="HEAD")
        try:
            with self._opener_now().open(req, timeout=self.timeout) as resp:
                return {k.lower(): v for k, v in resp.headers.items()}
        except Exception:
            return {}

    @staticmethod
    def is_reachable(url: str, timeout: int = 4) -> bool:
        """Szybkie sprawdzenie, czy źródło odpowiada (używane do pomijania martwych baz)."""
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": random.choice(USER_AGENTS), "DNT": "1"},
                method="HEAD",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status < 500
        except Exception:
            return False
