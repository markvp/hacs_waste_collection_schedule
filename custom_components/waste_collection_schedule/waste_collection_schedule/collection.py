import datetime
import logging
from typing import Optional

from .waste_types import WasteType

_LOGGER = logging.getLogger(__name__)


class Collection:
    """A single waste collection event: (date, WasteType).

    This is the new-style primary interface. Sources that use BaseSource
    return Collection(date, waste_type) and everything else derives from
    the WasteType.
    """

    def __init__(self, date: datetime.date, waste_type: WasteType):
        self._date = date
        self._waste_type = waste_type
        # Overrides applied by source_shell.py Customize
        self._type_override: str | None = None
        self._icon_override: str | None = None
        self._picture: str | None = None

    # --- Properties ---

    @property
    def date(self) -> datetime.date:
        return self._date

    @property
    def daysTo(self) -> int:
        return (self._date - datetime.datetime.now().date()).days

    @property
    def waste_type(self) -> WasteType:
        return self._waste_type

    @property
    def type(self) -> str:
        """Display name: override > WasteType English name."""
        return self._type_override or self._waste_type.names.get("en", self._waste_type.id)

    @property
    def icon(self) -> str:
        """Icon: override > WasteType icon."""
        return self._icon_override or self._waste_type.icon

    @property
    def picture(self) -> str | None:
        return self._picture

    # --- Mutators (used by source_shell.py Customize) ---

    def set_type(self, t: str):
        self._type_override = t

    def set_icon(self, icon: str):
        self._icon_override = icon

    def set_picture(self, picture: str):
        self._picture = picture

    def set_date(self, date: datetime.date):
        self._date = date

    # --- Serialization ---

    def as_dict(self) -> dict:
        return {
            "date": self._date.isoformat(),
            "type": self.type,
            "icon": self.icon,
            "picture": self.picture,
        }

    def __repr__(self):
        return f"Collection{{date={self.date}, waste_type={self._waste_type.id}}}"

    def __eq__(self, other):
        if not isinstance(other, Collection):
            return NotImplemented
        return self.date == other.date and self.type == other.type

    def __hash__(self):
        return hash((self.date, self.type))


class LegacyCollection(Collection):
    """Adapter for old-style sources that pass t= and icon= strings.

    Usage (by legacy sources):
        Collection(date=..., t="Refuse", icon="mdi:trash-can")

    Internally creates an ad-hoc WasteType from the provided strings.
    """

    def __init__(
        self,
        date: datetime.date,
        t: str,
        icon: Optional[str] = None,
        picture: Optional[str] = None,
    ):
        from .waste_types import OTHER

        # Create an ad-hoc WasteType from the legacy string params
        ad_hoc = WasteType(
            id=f"legacy_{t}",
            icon=icon or OTHER.icon,
            color=OTHER.color,
            names={"en": t},
        )
        super().__init__(date=date, waste_type=ad_hoc)
        self._picture = picture


def _collection_factory(
    date: datetime.date,
    t: str | None = None,
    icon: Optional[str] = None,
    picture: Optional[str] = None,
    waste_type: WasteType | None = None,
) -> Collection:
    """Factory that returns the right Collection type.

    This is what old sources get when they `from waste_collection_schedule import Collection`.
    Supports both:
        Collection(date=..., waste_type=GENERAL_WASTE)     → new-style
        Collection(date=..., t="Refuse", icon="mdi:...")   → legacy adapter
    """
    if waste_type is not None:
        c = Collection(date=date, waste_type=waste_type)
        if picture is not None:
            c.set_picture(picture)
        return c
    if t is not None:
        return LegacyCollection(date=date, t=t, icon=icon, picture=picture)
    raise ValueError("Collection requires either waste_type or t parameter")


# Make the factory callable as a class (for `Collection(date=..., t=...)` syntax)
class _CollectionMeta:
    """Wrapper that makes _collection_factory look like a class.

    Supports isinstance() checks and attribute access on the 'class'.
    """

    def __call__(self, *args, **kwargs):
        return _collection_factory(*args, **kwargs)

    def __instancecheck__(self, instance):
        return isinstance(instance, Collection)

    def __subclasscheck__(self, subclass):
        return issubclass(subclass, Collection)


# This is what gets exported — callable like a class, dispatches to the right type
CollectionFactory = _CollectionMeta()


class CollectionGroup:
    """A group of collections on the same date (for calendar display)."""

    def __init__(self, date: datetime.date):
        self._date = date
        self._icon: str | None = None
        self._picture: str | None = None
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
