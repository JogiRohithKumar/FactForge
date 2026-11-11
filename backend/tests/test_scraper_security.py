import pytest
from urllib.parse import urlparse
from app.services.scraper import _validate_url, _PinnedHTTPSConnection, _PinnedHTTPAdapter, UnsafeUrlError

def test_rejects_non_http_schemes():
    with pytest.raises(UnsafeUrlError):
        _validate_url("file:///etc/passwd")

def test_rejects_embedded_credentials():
    with pytest.raises(UnsafeUrlError):
        _validate_url("https://user:pass@example.com/article")

def test_rejects_non_standard_ports(monkeypatch):
    import app.services.scraper as scraper
    monkeypatch.setattr(scraper, "_resolve_public", lambda host, port: {"93.184.216.34"})
    with pytest.raises(UnsafeUrlError):
        _validate_url("http://example.com:8080/article")

def test_rejects_non_public_resolution(monkeypatch):
    import app.services.scraper as scraper
    monkeypatch.setattr(scraper, "_resolve_public", lambda host, port: (_ for _ in ()).throw(UnsafeUrlError("private")))
    with pytest.raises(UnsafeUrlError):
        _validate_url("http://example.com")

def test_https_socket_connects_to_pinned_ip_but_keeps_hostname(monkeypatch):
    import app.services.scraper as scraper
    calls, sentinel = [], object()
    monkeypatch.setattr(scraper.urllib3_connection, "create_connection", lambda address, *args, **kwargs: (calls.append(address), sentinel)[1])
    connection = _PinnedHTTPSConnection(host="news.example", port=443, pinned_ip="93.184.216.34")
    assert connection._new_conn() is sentinel
    assert calls == [("93.184.216.34", 443)]
    assert connection.host == "news.example"

def test_missing_pinned_ip_fails_closed():
    connection = _PinnedHTTPSConnection(host="news.example", port=443)
    with pytest.raises(UnsafeUrlError):
        connection._new_conn()

def test_adapter_pins_the_validated_dns_result(monkeypatch):
    import app.services.scraper as scraper
    monkeypatch.setattr(scraper, "_validate_url", lambda url: (urlparse(url), "93.184.216.34"))
    adapter = _PinnedHTTPAdapter()
    try:
        import requests
        prepared = requests.Request("GET", "https://news.example/story").prepare()
        pool = adapter.get_connection_with_tls_context(prepared, verify=True)
        assert pool.conn_kw["pinned_ip"] == "93.184.216.34"
        assert pool.host == "news.example"
    finally:
        adapter.close()
