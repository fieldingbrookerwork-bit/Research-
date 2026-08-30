"""Render brief markdown to standalone HTML pages using site/brief-template.html.

Deliberately tiny markdown subset — the brief writer emits only: h1/h2, bold,
italics (single *), links, bullets, blockquote lines (>), and hr (---). No
external deps, no raw-HTML passthrough (angle brackets are escaped first).
"""

import html
import re
from pathlib import Path

from . import config

_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITAL = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")


def _inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = _LINK.sub(r'<a href="\2">\1</a>', text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITAL.sub(r"<em>\1</em>", text)
    return text


def markdown_to_html(md: str) -> tuple[str, str]:
    """Return (title, body_html)."""
    out: list[str] = []
    title = "Worth the Bid brief"
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for line in md.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            close_list()
            title = stripped[2:].strip()
            out.append(f"<h1>{_inline(title)}</h1>")
        elif stripped.startswith("## "):
            close_list()
            out.append(f"<h2>{_inline(stripped[3:])}</h2>")
        elif stripped.startswith("> "):
            close_list()
            out.append(f"<blockquote>{_inline(stripped[2:])}</blockquote>")
        elif stripped.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(stripped[2:])}</li>")
        elif stripped == "---":
            close_list()
            out.append("<hr>")
        elif stripped == "":
            close_list()
        else:
            close_list()
            out.append(f"<p>{_inline(stripped)}</p>")
    close_list()
    return title, "\n".join(out)


def render_brief(md_path: Path, out_dir: Path) -> Path:
    template = (config.REPO_ROOT / "site" / "brief-template.html").read_text(
        encoding="utf-8")
    title, body = markdown_to_html(md_path.read_text(encoding="utf-8"))
    page = template.replace("{{TITLE}}", html.escape(title)).replace("{{BODY}}", body)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (md_path.stem + ".html")
    out_path.write_text(page, encoding="utf-8")
    return out_path


def render_all() -> list[Path]:
    briefs_dir = config.ensure_state_dir() / "briefs"
    out_dir = config.ensure_state_dir() / "pages"
    return [render_brief(p, out_dir) for p in sorted(briefs_dir.glob("*.md"))]
