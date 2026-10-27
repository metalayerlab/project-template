"""The core/layer boundary, enforced.

- Core files (under template/ and not gated by `language` in their path) contain no
  language-specific tooling: that belongs in layers/<language>/.
- Every `layer.<name>` the core uses is defined by every layer's layer.jinja.
- Every fragment the core includes exists in every layer, unless the include says
  `ignore missing` (an optional hook).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "template"
LAYERS = sorted(p.parent.name for p in (ROOT / "layers").glob("*/layer.jinja"))

# Language-specific tokens that must not appear in core files.
FORBIDDEN = {
    "python": [r"\buv run\b", r"\buv sync\b", r"\bpytest\b", r"\bruff\b", r"\bmypy\b",
               r"pyproject", r"python:\S+-slim", r"/opt/venv", r"\bpip install\b"],  # fmt: skip
}
# Core scripts written in Python on purpose (stdlib only, runnable by any layer's CI).
CORE_PYTHON_SCRIPTS = {"scripts/check-wiki.py", "scripts/[% if personal_data_guard %]check-personal-data.py[% endif %]"}

USE = re.compile(r"(?<![/\w])layer\.(?!jinja\b)([a-z_]+)")
DEFINE = re.compile(r"\[%\s*set\s+([a-z_]+)\s*=")
INCLUDE = re.compile(r"\[%\s*include\s+'layers/'\s*~\s*language\s*~\s*'/([^']+)'(\s+ignore missing)?")


def core_files() -> list[Path]:
    return [
        p
        for p in TEMPLATE.rglob("*")
        if p.is_file()
        and "language ==" not in str(p.relative_to(TEMPLATE))
        and str(p.relative_to(TEMPLATE)) not in CORE_PYTHON_SCRIPTS
    ]


def test_there_is_a_layer() -> None:
    assert LAYERS, "no layers/<language>/layer.jinja found"


@pytest.mark.parametrize("path", core_files(), ids=lambda p: str(p.relative_to(TEMPLATE)))
def test_core_file_is_language_neutral(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    hits = [pat for pats in FORBIDDEN.values() for pat in pats if re.search(pat, text)]
    assert not hits, f"language-specific text in a core file (move it to layers/): {hits}"


@pytest.mark.parametrize("layer", LAYERS)
def test_layer_defines_every_name_the_core_uses(layer: str) -> None:
    defined = set(DEFINE.findall((ROOT / "layers" / layer / "layer.jinja").read_text()))
    used = {m for p in TEMPLATE.rglob("*.jinja") for m in USE.findall(p.read_text())}
    used |= {m for p in (ROOT / "layers" / layer).rglob("*.jinja") for m in USE.findall(p.read_text())}
    assert used <= defined, f"layers/{layer}/layer.jinja lacks: {sorted(used - defined)}"


@pytest.mark.parametrize("layer", LAYERS)
def test_layer_provides_every_required_fragment(layer: str) -> None:
    missing = []
    for p in TEMPLATE.rglob("*.jinja"):
        for frag, optional in INCLUDE.findall(p.read_text()):
            if not optional and not (ROOT / "layers" / layer / frag).is_file():
                missing.append(f"{frag} (included by {p.relative_to(TEMPLATE)})")
    assert not missing, f"layers/{layer}/ lacks: {missing}"
