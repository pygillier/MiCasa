"""OPML import/export of categories and links.

Layout: one top-level ``<outline>`` per category, one child ``<outline type="link">`` per link.
MiCasa-specific data lives in extra attributes (``isPublic``, ``icon``, ``kumaMonitorId``)
which other OPML readers simply ignore. Top-level outlines that carry a URL
(plain bookmark lists from other tools) are gathered in a fallback category.
"""

from urllib.parse import urlparse
from xml.etree import ElementTree as ET

from defusedxml import ElementTree as SafeET
from defusedxml.common import DefusedXmlException

from ..extensions import db
from ..models import Category, Link, next_position
from ..validation import is_http_url, is_phosphor_icon

FALLBACK_CATEGORY = "Imported"
MAX_BYTES = 2 * 1024 * 1024


class OpmlError(ValueError):
    """The uploaded document cannot be imported (too large, malformed or not OPML)."""


def export_opml() -> bytes:
    """Serialize every category and its links to an OPML 2.0 document (UTF-8 bytes)."""
    root = ET.Element("opml", version="2.0")
    head = ET.SubElement(root, "head")
    ET.SubElement(head, "title").text = "MiCasa"
    body = ET.SubElement(root, "body")
    for cat in Category.query.order_by(Category.position, Category.id):
        node = ET.SubElement(body, "outline", text=cat.name, isPublic=str(cat.is_public).lower())
        if cat.note:
            node.set("note", cat.note)
        for link in cat.links:
            attrs = {"type": "link", "text": link.label, "url": link.url, "icon": link.icon,
                     "isPublic": str(link.is_public).lower()}
            if link.kuma_monitor_id is not None:
                attrs["kumaMonitorId"] = str(link.kuma_monitor_id)
            ET.SubElement(node, "outline", attrs)
    ET.indent(root)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _flag(value: str | None) -> bool:
    """Parse a boolean attribute (``true``/``1``/``yes``, case-insensitive)."""
    return (value or "").strip().lower() in ("true", "1", "yes")


def _icon(value: str | None) -> str:
    """A valid Phosphor class, falling back to ``ph-link``."""
    icon = (value or "").strip()
    return icon if is_phosphor_icon(icon) else "ph-link"


def _monitor_id(value: str | None) -> int | None:
    """Parse a Kuma monitor id; ``None`` when absent or not an integer."""
    try:
        return int(value) if value not in (None, "") else None
    except ValueError:
        return None


def _title(node) -> str:
    """Outline label: ``text``, else ``title``."""
    return (node.get("text") or node.get("title") or "").strip()


def _url(node) -> str:
    """Outline target: ``url``, else ``xmlUrl``, else ``htmlUrl`` (feed lists from other tools)."""
    return (node.get("url") or node.get("xmlUrl") or node.get("htmlUrl") or "").strip()


def import_opml(data: bytes) -> dict:
    """Merge an OPML document into the DB and return created/skipped counts.

    Existing rows are never modified or removed. Links already present in the same category
    (same URL) and entries with a missing label or non-http(s) URL are counted as skipped.
    Raises ``OpmlError`` for oversized, malformed or non-OPML input; nothing is committed then.
    """
    if len(data) > MAX_BYTES:
        raise OpmlError("file too large")
    try:
        root = SafeET.fromstring(data)
    except (ET.ParseError, DefusedXmlException) as exc:
        raise OpmlError(f"invalid OPML: {exc}") from exc
    body = root.find("body")
    if root.tag != "opml" or body is None:
        raise OpmlError("not an OPML document")

    result = {"categories_created": 0, "links_created": 0, "skipped": 0}
    cats: dict[str, Category] = {c.name: c for c in Category.query}

    def category(name: str, node=None) -> Category:
        """Existing category by name, or a new one built from the outline's attributes."""
        name = name[:100]
        if name not in cats:
            attrs = node.attrib if node is not None else {}
            cat = Category(name=name, note=(attrs.get("note") or "")[:100],
                           is_public=_flag(attrs.get("isPublic")), position=len(cats))
            db.session.add(cat)
            db.session.flush()
            cats[name] = cat
            result["categories_created"] += 1
        return cats[name]

    seen = {(link.category_id, link.url) for link in Link.query}
    positions: dict[int, int] = {}

    def add_link(cat: Category, node) -> None:
        label, url = _title(node), _url(node)
        if not label or not is_http_url(url) or (cat.id, url) in seen:
            result["skipped"] += 1
            return
        if cat.id not in positions:
            positions[cat.id] = next_position(Link, category_id=cat.id)
        db.session.add(Link(
            category_id=cat.id, label=label[:100], url=url[:500], icon=_icon(node.get("icon")),
            host=urlparse(url).netloc[:100], position=positions[cat.id],
            is_public=_flag(node.get("isPublic")), kuma_monitor_id=_monitor_id(node.get("kumaMonitorId")),
        ))
        positions[cat.id] += 1
        seen.add((cat.id, url))
        result["links_created"] += 1

    for node in body.findall("outline"):
        if _url(node) and node.find("outline") is None:  # bare bookmark at top level
            add_link(category(FALLBACK_CATEGORY), node)
            continue
        name = _title(node)
        if not name:
            result["skipped"] += 1
            continue
        cat = category(name, node)
        for child in node.iter("outline"):  # flatten deeper nesting into this category
            if child is not node and _url(child):
                add_link(cat, child)
    db.session.commit()
    return result
