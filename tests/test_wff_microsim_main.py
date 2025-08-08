from unittest.mock import patch

from src.wff_microsim_main import main


@patch("src.wff_microsim_main.generate_microsim_report")
def test_main_runs_without_error(mock_generate_report):
    """Test that the main function runs without error."""
    main()
    mock_generate_report.assert_called_once()


@patch("src.wff_microsim_main.validate_input_data")
def test_main_validation_error(mock_validate_input_data):
    """Test that the main function handles validation errors."""
    mock_validate_input_data.side_effect = ValueError("Test validation error")
    main()
