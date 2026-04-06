"""Standard retrieval methods for waste collection sources.

Each retriever is a function that takes a source instance and returns
a raw HTTP response. The source configures URL, params, headers etc
as instance/class attributes.
"""

import requests


def http_get(self) -> requests.Response:
    """Standard HTTP GET request.

    Reads API_URL, _params, _headers, TIMEOUT from the source instance.
    """
    return requests.get(
        self.API_URL,
        params=getattr(self, "_params", None),
        headers=getattr(self, "_headers", None),
        timeout=getattr(self, "TIMEOUT", 30),
    )


def http_post(self) -> requests.Response:
    """Standard HTTP POST request.

    Reads API_URL, _params, _data, _json, _headers, TIMEOUT from the source instance.
    """
    return requests.post(
        self.API_URL,
        params=getattr(self, "_params", None),
        data=getattr(self, "_data", None),
        json=getattr(self, "_json", None),
        headers=getattr(self, "_headers", None),
        timeout=getattr(self, "TIMEOUT", 30),
    )
