"""Test package initialization."""

import importlib
import unittest
from unittest.mock import patch


class TestServiceInit(unittest.TestCase):
    """Tests for service package initialization"""

    @patch("sys.exit")
    def test_init_failure_exits(self, mock_exit):
        """It should log critical and exit when initialization fails"""
        with patch("service.models.init_db", side_effect=Exception("boom")):
            with patch("flask.app.Flask.logger") as mock_logger:
                import service  # pylint: disable=import-outside-toplevel
                importlib.reload(service)

                mock_logger.critical.assert_called()
                mock_exit.assert_called_with(4)
