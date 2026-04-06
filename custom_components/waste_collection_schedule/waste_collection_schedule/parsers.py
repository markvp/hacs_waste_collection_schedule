"""Standard response parsers for waste collection sources.

Each parser is a function that takes a raw HTTP response and returns
parsed data in a format suitable for the source's classify() method.
"""

import requests
from bs4 import BeautifulSoup


def json(self, response: requests.Response):
    """Parse response as JSON."""
    return response.json()


def text(self, response: requests.Response) -> str:
    """Return response as plain text."""
    return response.text


def html(self, response: requests.Response) -> BeautifulSoup:
    """Parse response as HTML."""
    return BeautifulSoup(response.text, "html.parser")
