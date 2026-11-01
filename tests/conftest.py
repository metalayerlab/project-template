"""`--variant`: run one CI job's share of the tests, by the `project` fixture's parameter (#98).

    uv run pytest --variant service     # the tests of the rendered `service` variant
    uv run pytest --variant rest        # the tests that render no variant (their own answers, or none)

Every test lands in exactly one share, so a CI matrix over every variant plus `rest` runs each once.
"""

from __future__ import annotations

import pytest

REST = "rest"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--variant",
        metavar="NAME",
        help=f"only the tests of one rendered variant, or '{REST}' for those that render none",
    )


def variant_of(item: pytest.Item) -> str:
    callspec = getattr(item, "callspec", None)
    return str(callspec.params["project"]) if callspec and "project" in callspec.params else REST


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    wanted = config.getoption("--variant")
    if wanted is None:
        return
    seen = {variant_of(item) for item in items}
    if wanted not in seen:
        # A typo, or a variant renamed without its CI matrix entry: selecting nothing would pass.
        pytest.exit(f"--variant {wanted}: no such variant (have {sorted(seen)})", pytest.ExitCode.USAGE_ERROR)
    keep = [item for item in items if variant_of(item) == wanted]
    config.hook.pytest_deselected(items=[item for item in items if variant_of(item) != wanted])
    items[:] = keep
