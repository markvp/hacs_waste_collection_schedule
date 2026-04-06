"""Base class for waste collection sources.

A source is a composition of standard pipeline steps:
  retrieve (how to fetch raw data) → parse (how to interpret the response)
  → classify (how to extract date + waste type from each record)

Sources configure which standard steps to use and only write custom
code for classify() — the source-specific knowledge of what each
record means.
"""

import datetime
import logging

from waste_collection_schedule import Collection
from waste_collection_schedule.waste_types import WasteType
from waste_collection_schedule import retrievers, parsers, date_parsers

_LOGGER = logging.getLogger(__name__)


class BaseSource:
    """Optional base class for waste collection sources."""

    # --- Metadata (replaces module-level vars) ---
    TITLE: str = ""
    DESCRIPTION: str = ""
    URL: str = ""
    COUNTRY: str = ""
    TEST_CASES: dict = {}
    PARAM_TRANSLATIONS: dict = {}
    PARAM_DESCRIPTIONS: dict = {}
    HOW_TO_GET_ARGUMENTS_DESCRIPTION: dict = {}

    # --- Waste types this source produces ---
    WASTE_TYPES: list[WasteType] = []

    # --- Pipeline config ---
    API_URL: str = ""
    TIMEOUT: int = 30

    # Standard pipeline steps — override with alternatives as needed
    retrieve = retrievers.http_get
    parse = parsers.json
    parse_date = date_parsers.auto

    # --- Pipeline orchestration ---

    def fetch(self) -> list[Collection]:
        """Orchestrate: retrieve → parse → classify each → Collection."""
        response = self.retrieve()
        records = self.parse(response)

        if not records:
            return []

        if isinstance(records, dict):
            records = [records]

        entries = []
        for record in records:
            result = self.classify(record)
            if result is None:
                continue

            date_value, waste_type = result

            if isinstance(date_value, str):
                date_value = self.parse_date(date_value)

            entries.append(Collection(date=date_value, waste_type=waste_type))

        return entries

    def classify(self, record) -> tuple[datetime.date | str, WasteType] | None:
        """Classify a single record into (date, WasteType).

        Override this — the source-specific knowledge of what each record means.
        Return None to skip a record.
        """
        raise NotImplementedError("Source must implement classify()")
