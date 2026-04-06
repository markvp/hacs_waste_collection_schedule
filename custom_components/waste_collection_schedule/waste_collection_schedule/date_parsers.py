"""Date parsing utilities.

Each parser is a function that takes a string and returns a datetime.date.
Sources select a parser by format or use the auto-detect fallback.
"""

import datetime
import logging

from dateutil import parser as dateutil_parser

_LOGGER = logging.getLogger(__name__)


def auto(self, date_str: str) -> datetime.date:
    """Auto-detect date format using dateutil."""
    return dateutil_parser.parse(date_str.strip()).date()


def for_format(fmt: str):
    """Return a date parser method for a specific strptime format."""

    def _parse(self, date_str: str) -> datetime.date:
        return datetime.datetime.strptime(date_str.strip(), fmt).date()

    return _parse
