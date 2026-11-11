"""HTML extraction with DNS validation and socket-level destination pinning.

The adapter connects to the exact public IP resolved during validation while
preserving the original hostname for HTTP Host and TLS SNI verification.
Redirects are followed manually and revalidated one hop at a time.
"""
import ipaddress
import socket
from urllib.parse import urljoin, urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager
from urllib3.connection import HTTPConnection, HTTPSConnection
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from urllib3.util import connection as urllib3_connection
from bs4 import BeautifulSoup
from app.core.config import get_settings

_UA = "FactForgeResearchBot/1.0 (+article analysis)"
class UnsafeUrlError(ValueError):
    pass
class ExtractionError(ValueError):
    pass

def _resolve_public(hostname: str, port: int) -> set[str]:
    try:
        infos = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UnsafeUrlError("Hostname could not be resolved") from exc
    addresses = set()
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            raise UnsafeUrlError("Target resolves to a non-public IP address")
        addresses.add(str(ip))
    if not addresses:
        raise UnsafeUrlError("No usable address found")
    return addresses

def _validate_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeUrlError("Only absolute HTTP(S) URLs are accepted")
    if parsed.username or parsed.password:
        raise UnsafeUrlError("Credentials in URLs are not accepted")
    try:
        default_port = 443 if parsed.scheme == "https" else 80
        port = parsed.port or default_port
    except ValueError as exc:
        raise UnsafeUrlError("URL contains an invalid port") from exc
    if port != default_port:
        raise UnsafeUrlError("Only standard HTTP and HTTPS ports are accepted")
    return parsed, sorted(_resolve_public(parsed.hostname, port))[0]

class _PinnedHTTPConnection(HTTPConnection):
    def __init__(self, *args, pinned_ip=None, **kwargs):
        self.pinned_ip = pinned_ip
        super().__init__(*args, **kwargs)
    def _new_conn(self):
        if not self.pinned_ip:
            raise UnsafeUrlError("Outbound connection has no validated destination")
        return urllib3_connection.create_connection(
            (self.pinned_ip, self.port), self.timeout,
            source_address=self.source_address, socket_options=self.socket_options,
        )

class _PinnedHTTPSConnection(HTTPSConnection):
    def __init__(self, *args, pinned_ip=None, **kwargs):
        self.pinned_ip = pinned_ip
        super().__init__(*args, **kwargs)
    def _new_conn(self):
        if not self.pinned_ip:
            raise UnsafeUrlError("Outbound connection has no validated destination")
        return urllib3_connection.create_connection(
            (self.pinned_ip, self.port), self.timeout,
            source_address=self.source_address, socket_options=self.socket_options,
        )

class _PinnedHTTPPool(HTTPConnectionPool):
    ConnectionCls = _PinnedHTTPConnection
class _PinnedHTTPSPool(HTTPSConnectionPool):
    ConnectionCls = _PinnedHTTPSConnection

class _PinnedPoolManager(PoolManager):
    pool_classes_by_scheme = {"http": _PinnedHTTPPool, "https": _PinnedHTTPSPool}

class _PinnedHTTPAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = _PinnedPoolManager(num_pools=connections, maxsize=maxsize, block=block, **pool_kwargs)
    def get_connection_with_tls_context(self, request, verify, proxies=None, cert=None):
        _, pinned_ip = _validate_url(request.url)
        pool = super().get_connection_with_tls_context(request, verify, proxies, cert)
        pool.conn_kw["pinned_ip"] = pinned_ip
        return pool
    def get_connection(self, url, proxies=None):
        # Compatibility path for Requests versions that still call this method.
        _, pinned_ip = _validate_url(url)
        pool = super().get_connection(url, proxies)
        pool.conn_kw["pinned_ip"] = pinned_ip
        return pool

def _fetch_with_redirects(url: str, timeout: float, max_redirects: int = 3) -> str:
    session = requests.Session()
    session.trust_env = False
    session.mount("http://", _PinnedHTTPAdapter())
    session.mount("https://", _PinnedHTTPAdapter())
    current = url
    try:
        for _ in range(max_redirects + 1):
            response = session.get(
                current, headers={"User-Agent": _UA, "Accept": "text/html"},
                timeout=(2.0, timeout), allow_redirects=False, stream=True,
            )
            if response.is_redirect:
                location = response.headers.get("Location")
                response.close()
                if not location:
                    raise ExtractionError("Redirect response did not include a destination")
                current = urljoin(current, location)
                continue
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                response.close()
                raise ExtractionError("URL did not return an HTML document")
            chunks, total, max_bytes = [], 0, 3_000_000
            for chunk in response.iter_content(65536):
                total += len(chunk)
                if total > max_bytes:
                    response.close()
                    raise ExtractionError("Article page exceeds the 3 MB extraction limit")
                chunks.append(chunk)
            encoding = response.encoding or "utf-8"
            response.close()
            return b"".join(chunks).decode(encoding, errors="replace")
        raise ExtractionError("Too many redirects")
    except UnsafeUrlError:
        raise
    except requests.RequestException as exc:
        raise ExtractionError("Unable to retrieve the article page") from exc
    finally:
        session.close()

def extract_text_from_url(url: str) -> str:
    settings = get_settings()
    html = _fetch_with_redirects(url, settings.scrape_timeout_seconds)
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        node.decompose()
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = " ".join(p for p in paragraphs if len(p) > 30)
    if len(text) < 100:
        raise ExtractionError("The page did not contain enough extractable article text")
    return text[:settings.max_scraped_text_length]
