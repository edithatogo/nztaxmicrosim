import json
import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.historic_tax_search import (
    DatasetInfo,
    fetch_datasets,
    format_dataset,
    save_datasets,
)


@pytest.fixture
def mock_requests_get():
    """Fixture to mock requests.get."""
    with patch("requests.get") as mock_get:
        yield mock_get


def test_fetch_datasets_success(mock_requests_get):
    """Test fetch_datasets with a successful API response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": {
            "results": [
                {
                    "title": "Test Dataset 1",
                    "resources": [{"url": "http://example.com/resource1"}],
                }
            ]
        }
    }
    mock_requests_get.return_value = mock_response

    datasets = fetch_datasets("test query")
    assert len(datasets) == 1
    assert datasets[0].title == "Test Dataset 1"
    assert datasets[0].resources == ["http://example.com/resource1"]


def test_fetch_datasets_http_error(mock_requests_get):
    """Test fetch_datasets with an HTTP error."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_requests_get.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError):
        fetch_datasets("test query")


def test_format_dataset():
    """Test the format_dataset function."""
    dataset = DatasetInfo(
        title="My Test Dataset",
        resources=["http://example.com/a", "http://example.com/b"],
    )
    expected_output = "My Test Dataset\n  - http://example.com/a\n  - http://example.com/b"
    assert format_dataset(dataset) == expected_output


def test_save_datasets(tmp_path):
    """Test the save_datasets function."""
    datasets = [
        DatasetInfo(title="Dataset 1", resources=["r1"]),
        DatasetInfo(title="Dataset 2", resources=["r2"]),
    ]
    output_file = tmp_path / "datasets.json"

    save_datasets(datasets, str(output_file))

    assert os.path.exists(output_file)
    with open(output_file, "r") as f:
        data = json.load(f)
    assert data == [
        {"title": "Dataset 1", "resources": ["r1"]},
        {"title": "Dataset 2", "resources": ["r2"]},
    ]


def test_main_block(mock_requests_get, capsys):
    """Test the main execution block."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": {
            "results": [
                {
                    "title": "Main Test Dataset",
                    "resources": [{"url": "http://main.example.com/resource"}],
                }
            ]
        }
    }
    mock_requests_get.return_value = mock_response

    import runpy

    runpy.run_module("src.historic_tax_search", run_name="__main__")

    captured = capsys.readouterr()
    assert "Main Test Dataset" in captured.out
    assert "http://main.example.com/resource" in captured.out
