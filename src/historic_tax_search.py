"""Search for New Zealand tax datasets.

This module queries the data.govt.nz catalogue API for datasets
related to tax rules or parameters. It provides a simple utility to
retrieve titles and resource URLs, which can then be inspected for
historical tax information.
"""

from __future__ import annotations

import json
from typing import Any, Iterable

import requests
from pydantic import BaseModel

DATA_GOVT_API = "https://catalogue.data.govt.nz/api/3/action/package_search"


class DatasetInfo(BaseModel):
    """Basic information about a dataset returned from data.govt.nz."""

    title: str
    resources: list[str] = []


def fetch_datasets(query: str, rows: int = 50) -> list[DatasetInfo]:
    """Fetch datasets from data.govt.nz matching ``query``.

    Parameters
    ----------
    query:
        Search string used to filter datasets.
    rows:
        Maximum number of results to return.
    """

    params: dict[str, Any] = {"q": query, "rows": rows}
    response = requests.get(DATA_GOVT_API, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    results = data.get("result", {}).get("results", [])

    datasets: list[DatasetInfo] = []
    for item in results:
        title = item.get("title", "")
        resources = [res.get("url", "") for res in item.get("resources", [])]
        datasets.append(DatasetInfo(title=title, resources=resources))
    return datasets


def format_dataset(dataset: DatasetInfo) -> str:
    """Return a human-readable string for ``dataset``."""

    lines = [dataset.title]
    lines.extend(f"  - {url}" for url in dataset.resources)
    return "\n".join(lines)


def save_datasets(datasets: Iterable[DatasetInfo], path: str) -> None:
    """Save ``datasets`` as JSON at ``path``."""

    serialised = [dataset.model_dump() for dataset in datasets]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serialised, f, indent=2)


if __name__ == "__main__":
    datasets = fetch_datasets(query="tax")
    for dataset in datasets:
        print(format_dataset(dataset))
