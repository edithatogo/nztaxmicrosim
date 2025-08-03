from unittest.mock import patch

from src.wff_microsim_main import main


@patch("src.wff_microsim_main.generate_microsim_report")
def test_main_runs_without_error(mock_generate_report):
    """Test that the main function runs without error."""
    main()
    mock_generate_report.assert_called_once()
