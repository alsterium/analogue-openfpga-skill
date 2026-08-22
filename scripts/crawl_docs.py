#!/usr/bin/env python3
"""Crawl Analogue's openFPGA Developer Docs into a small local snapshot.

This helper intentionally writes only to the directory passed with --output.
It uses the site's documentation navigation instead of a hard-coded page list,
so new pages can be discovered on a later refresh.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import time
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = "https://www.analogue.co/developer/docs"
USER_AGENT = "codex-analogue-openfpga-skill/1.0"


def fetch(url: str, timeout: float) -> tuple[str, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace"), final_url


def docs_url(url: str) -> str | None:
    url, _ = urldefrag(url)
    parsed = urlparse(url)
    if parsed.netloc != "www.analogue.co":
        return None
    if not parsed.path.startswith("/developer/docs"):
        return None
    if "/opengraph/" in parsed.path:
        return None
    return f"https://www.analogue.co{parsed.path.rstrip('/') or '/developer/docs'}"


def discover(root_html: str, root_url: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    canonical_root = docs_url(root_url)
    hrefs = re.findall(r"href\s*=\s*[\"']([^\"']+)", root_html, flags=re.I)
    for href in hrefs:
        candidate = docs_url(urljoin(root_url, html.unescape(href).strip()))
        if candidate == "https://www.analogue.co/developer/docs" and canonical_root:
            candidate = canonical_root
        if candidate and candidate not in seen:
            seen.add(candidate)
            found.append(candidate)
    if canonical_root and canonical_root not in seen:
        found.insert(0, canonical_root)
    return list(dict.fromkeys(url.rstrip("/") for url in found))


class HeadingParser(HTMLParser):
    """Fallback extractor used when pandoc is not installed."""

    def __init__(self) -> None:
        super().__init__()
        self.capture = False
        self.depth = 0
        self.heading: str | None = None
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "div" and "docs-content" in (attributes.get("class") or "") and not self.capture:
            self.capture = True
            self.depth = 1
            return
        if self.capture:
            self.depth += 1
            if tag in {"h1", "h2", "h3", "h4"}:
                self.heading = tag

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if self.capture:
            if tag in {"h1", "h2", "h3", "h4"} and self.heading == tag:
                self.parts.append("\n" + "#" * int(tag[1]) + " " + " ".join(self.parts.pop().split()))
                self.heading = None
            self.depth -= 1
            if self.depth <= 0:
                self.capture = False

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if not value:
            return
        if self.in_title:
            self.title_parts.append(value)
        if self.capture:
            if self.heading:
                self.parts.append(value)
            else:
                self.parts.append(value)


def page_title(raw_html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", raw_html, flags=re.I | re.S)
    if not match:
        return "Untitled"
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", match.group(1)))).strip()


class ContentFragmentParser(HTMLParser):
    """Keep the inner HTML of the first docs-content container."""

    VOID_ELEMENTS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if self.depth == 0 and tag == "div" and "docs-content" in (attributes.get("class") or ""):
            self.depth = 1
            return
        if self.depth:
            self.parts.append(self.get_starttag_text() or f"<{tag}>")
            if tag not in self.VOID_ELEMENTS:
                self.depth += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.depth:
            self.parts.append(self.get_starttag_text() or f"<{tag} />")

    def handle_endtag(self, tag: str) -> None:
        if not self.depth:
            return
        if tag == "div" and self.depth == 1:
            self.depth = 0
            return
        self.parts.append(f"</{tag}>")
        if tag not in self.VOID_ELEMENTS:
            self.depth = max(0, self.depth - 1)

    def handle_data(self, data: str) -> None:
        if self.depth:
            self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if self.depth:
            self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self.depth:
            self.parts.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        if self.depth:
            self.parts.append(f"<!--{data}-->")


def content_fragment(raw_html: str) -> str:
    parser = ContentFragmentParser()
    parser.feed(raw_html)
    return "".join(parser.parts) or raw_html


def to_markdown(raw_html: str, title: str) -> str:
    fragment = f"<h1>{html.escape(title)}</h1>{content_fragment(raw_html)}"
    pandoc = shutil.which("pandoc")
    if pandoc:
        result = subprocess.run(
            [pandoc, "-f", "html", "-t", "gfm", "--wrap=none"],
            input=fragment,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip() + "\n"

    parser = HeadingParser()
    parser.feed(fragment)
    body = " ".join(parser.parts)
    body = re.sub(r"\s+", " ", body).strip()
    return f"# {title}\n\n{body}\n"


def filename_for(url: str) -> str:
    path = urlparse(url).path.removeprefix("/developer/docs/").strip("/")
    return (path or "overview").replace("/", "--") + ".md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a Markdown snapshot to this directory")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--delay", type=float, default=0.05)
    parser.add_argument("--max-pages", type=int, default=200)
    args = parser.parse_args()

    try:
        root_html, root_url = fetch(ROOT, args.timeout)
    except Exception as exc:  # pragma: no cover - network failure is environment-specific
        print(f"failed to fetch {ROOT}: {exc}", file=sys.stderr)
        return 2

    urls = discover(root_html, root_url)[: args.max_pages]
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)

    manifest: list[str] = [
        f"# Crawl manifest ({date.today().isoformat()})",
        "",
        f"Source: {ROOT}",
        "",
        "| Status | Title | URL |",
        "| --- | --- | --- |",
    ]

    for index, url in enumerate(urls):
        if index:
            time.sleep(max(0.0, args.delay))
        try:
            raw_html, final_url = fetch(url, args.timeout)
            title = page_title(raw_html)
            print(f"OK\t{title}\t{final_url}")
            manifest.append(f"| OK | {title.replace('|', '\\|')} | [{final_url}]({final_url}) |")
            if args.output:
                (args.output / filename_for(final_url)).write_text(
                    f"Source: [{final_url}]({final_url})\n\n{to_markdown(raw_html, title)}",
                    encoding="utf-8",
                )
        except Exception as exc:  # pragma: no cover - network failure is environment-specific
            print(f"ERROR\t{url}\t{exc}", file=sys.stderr)
            manifest.append(f"| ERROR | {exc} | {url} |")

    if args.output:
        (args.output / "manifest.md").write_text("\n".join(manifest) + "\n", encoding="utf-8")
        print(f"wrote {len(urls)} page entries to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
