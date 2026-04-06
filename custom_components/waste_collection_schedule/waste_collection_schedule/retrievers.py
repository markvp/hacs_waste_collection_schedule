"""Standard retrieval methods for waste collection sources.

Each retriever is a function that takes a source instance and returns
a raw HTTP response. The source configures URL, params, headers etc
as instance/class attributes.
"""

import requests


def http_get(source) -> requests.Response:
    """Standard HTTP GET request."""
    return requests.get(
        source.API_URL,
        params=getattr(source, "_params", None),
        headers=getattr(source, "_headers", None),
        timeout=getattr(source, "TIMEOUT", 30),
    )


def http_post(source) -> requests.Response:
    """Standard HTTP POST request."""
    return requests.post(
        source.API_URL,
        params=getattr(source, "_params", None),
        data=getattr(source, "_data", None),
        json=getattr(source, "_json", None),
        headers=getattr(source, "_headers", None),
        timeout=getattr(source, "TIMEOUT", 30),
    )
