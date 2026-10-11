"""Input validators shared by the admin API and the OPML importer."""

from urllib.parse import urlparse


def is_http_url(url: str) -> bool:
    """True for an absolute ``http(s)`` URL with a host."""
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def is_phosphor_icon(icon: str) -> bool:
    """True for a Phosphor class name such as ``ph-house`` (``ph-`` prefix, alphanumerics and dashes)."""
    return icon.startswith("ph-") and icon.replace("-", "").isalnum()
