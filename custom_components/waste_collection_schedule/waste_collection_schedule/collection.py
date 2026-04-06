import datetime
import logging
from typing import Optional

_LOGGER = logging.getLogger(__name__)


class Collection:
    """A single waste collection event.

    New-style (preferred):
        Collection(date=..., waste_type=GENERAL_WASTE)

    Deprecated (backwards compatible):
        Collection(date=..., t="Refuse", icon="mdi:trash-can")
    """

    def __init__(
        self,
        date: datetime.date,
        t: str | None = None,
        icon: Optional[str] = None,
        picture: Optional[str] = None,
        waste_type=None,
    ):
        self._date = date
        self._waste_type = waste_type
        self._picture = picture

        # Explicit overrides (from user config or legacy source params)
        self._icon_override = icon if waste_type is not None else None
        self._type_override = t if waste_type is not None else None

        if waste_type is None and t is None:
            raise ValueError("Collection requires either waste_type or t parameter")

        # Legacy mode: no waste_type, store raw values
        if waste_type is None:
            self._legacy_type = t
            self._legacy_icon = icon

    # --- Properties ---

    @property
    def date(self) -> datetime.date:
        return self._date

    @property
    def daysTo(self) -> int:
        return (self._date - datetime.datetime.now().date()).days

    @property
    def waste_type(self):
        """The standard WasteType, or None for legacy sources."""
        return self._waste_type

    @property
    def type(self) -> str:
        """Display name. Override > WasteType name > legacy string."""
        if self._waste_type is not None:
            return self._type_override or self._waste_type.names.get("en", self._waste_type.id)
        return self._legacy_type

    @property
    def icon(self) -> str | None:
        """Icon. Override > WasteType icon > legacy icon."""
        if self._waste_type is not None:
            return self._icon_override or self._waste_type.icon
        return self._legacy_icon

    @property
    def picture(self) -> str | None:
        return self._picture

    # --- Mutators (used by source_shell.py Customize) ---

    def set_type(self, t: str):
        if self._waste_type is not None:
            self._type_override = t
        else:
            self._legacy_type = t

    def set_icon(self, icon: str):
        if self._waste_type is not None:
            self._icon_override = icon
        else:
            self._legacy_icon = icon

    def set_picture(self, picture: str):
        self._picture = picture

    def set_date(self, date: datetime.date):
        self._date = date

    # --- Serialization (for framework/HA frontend consumption) ---

    def as_dict(self) -> dict:
        """Serialize for the framework."""
        return {
            "date": self._date.isoformat(),
            "type": self.type,
            "icon": self.icon,
            "picture": self.picture,
        }

    # --- Backwards compat: dict-like access for existing framework code ---

    def __getitem__(self, key):
        return self.as_dict()[key]

    def __setitem__(self, key, value):
        if key == "type":
            self.set_type(value)
        elif key == "icon":
            self.set_icon(value)
        elif key == "picture":
            self.set_picture(value)
        elif key == "date":
            self._date = datetime.date.fromisoformat(value) if isinstance(value, str) else value

    def __contains__(self, key):
        return key in self.as_dict()

    def get(self, key, default=None):
        return self.as_dict().get(key, default)

    def update(self, d: dict):
        for k, v in d.items():
            self[k] = v

    def __repr__(self):
        if self._waste_type:
            return f"Collection{{date={self.date}, waste_type={self._waste_type.id}}}"
        return f"Collection{{date={self.date}, type={self.type}}}"

    def __eq__(self, other):
        if not isinstance(other, Collection):
            return NotImplemented
        return self.date == other.date and self.type == other.type

    def __hash__(self):
        return hash((self.date, self.type))


class CollectionGroup:
    """A group of collections on the same date (for calendar display)."""

    def __init__(self, date: datetime.date):
        self._date = date
        self._icon = None
        self._picture = None
        self._types: list[str] = []

    @staticmethod
    def create(group: list[Collection]):
        x = CollectionGroup(group[0].date)
        if len(group) == 1:
            x._icon = group[0].icon
            x._picture = group[0].picture
        else:
            x._icon = f"mdi:numeric-{len(group)}-box-multiple"
        x._types = [it.type for it in group]
        return x

    @property
    def date(self) -> datetime.date:
        return self._date

    @property
    def daysTo(self) -> int:
        return (self._date - datetime.datetime.now().date()).days

    @property
    def icon(self) -> str | None:
        return self._icon

    @property
    def picture(self) -> str | None:
        return self._picture

    @property
    def types(self) -> list[str]:
        return self._types

    def as_dict(self) -> dict:
        return {
            "date": self._date.isoformat(),
            "icon": self._icon,
            "picture": self._picture,
            "types": self._types,
        }

    def __getitem__(self, key):
        return self.as_dict()[key]

    def __repr__(self):
        return f"CollectionGroup{{date={self.date}, types={self.types}}}"


# Backwards compat — referenced by __init__.py and potentially external code
CollectionBase = Collection
