"""Standard configuration parameter types for waste collection sources.

Each param type declares what information the source needs from the user
and how the framework should collect it (GUI widget, validation, labels).

Sources declare PARAMS as a list of param types. The framework reads
these to build the config flow GUI automatically.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConfigParam:
    """Base for all config parameter types."""

    # How this param maps to Source.__init__ kwargs
    fields: dict[str, str]  # {"init_param_name": "display_label", ...}

    # Standard labels per language (framework uses these for GUI)
    labels: dict[str, dict[str, str]] = field(default_factory=dict)

    # Description per language
    descriptions: dict[str, dict[str, str]] = field(default_factory=dict)

    # The widget type the config flow should render
    widget: str = "text"


def coords(lat: str = "lat", lon: str = "lon") -> ConfigParam:
    """Location by map/coordinates. Framework shows a map picker."""
    return ConfigParam(
        fields={lat: "Latitude", lon: "Longitude"},
        widget="map",
        labels={
            "en": {lat: "Latitude", lon: "Longitude"},
            "de": {lat: "Breitengrad", lon: "Längengrad"},
            "fr": {lat: "Latitude", lon: "Longitude"},
            "it": {lat: "Latitudine", lon: "Longitudine"},
        },
        descriptions={
            "en": {
                lat: "Select your location on the map.",
                lon: "Select your location on the map.",
            },
        },
    )


def uprn(field_name: str = "uprn") -> ConfigParam:
    """UK Unique Property Reference Number. Framework shows address lookup."""
    return ConfigParam(
        fields={field_name: "UPRN"},
        widget="uprn_lookup",
        labels={
            "en": {field_name: "UPRN"},
            "de": {field_name: "UPRN"},
            "fr": {field_name: "UPRN"},
            "it": {field_name: "UPRN"},
        },
        descriptions={
            "en": {
                field_name: "Your Unique Property Reference Number. Find it at https://www.findmyaddress.co.uk/",
            },
        },
    )


def postcode(
    postcode_field: str = "postcode",
    house_field: str | None = None,
) -> ConfigParam:
    """Postcode with optional house number."""
    fields = {postcode_field: "Postcode"}
    labels_en = {postcode_field: "Postcode"}
    labels_de = {postcode_field: "Postleitzahl"}
    labels_fr = {postcode_field: "Code postal"}
    labels_it = {postcode_field: "CAP"}

    if house_field:
        fields[house_field] = "House Number"
        labels_en[house_field] = "House Number"
        labels_de[house_field] = "Hausnummer"
        labels_fr[house_field] = "Numéro"
        labels_it[house_field] = "Numero civico"

    return ConfigParam(
        fields=fields,
        widget="postcode",
        labels={"en": labels_en, "de": labels_de, "fr": labels_fr, "it": labels_it},
    )


def address(
    street: str = "street",
    number: str = "house_number",
    postcode_field: str = "postcode",
    city: str | None = None,
) -> ConfigParam:
    """Full address entry with optional city."""
    fields = {
        street: "Street",
        number: "House Number",
        postcode_field: "Postcode",
    }
    labels_en = {street: "Street", number: "House Number", postcode_field: "Postcode"}
    labels_de = {
        street: "Straße",
        number: "Hausnummer",
        postcode_field: "Postleitzahl",
    }
    labels_fr = {street: "Rue", number: "Numéro", postcode_field: "Code postal"}
    labels_it = {street: "Via", number: "Numero civico", postcode_field: "CAP"}

    if city:
        fields[city] = "City"
        labels_en[city] = "City"
        labels_de[city] = "Stadt"
        labels_fr[city] = "Ville"
        labels_it[city] = "Città"

    return ConfigParam(
        fields=fields,
        widget="address",
        labels={"en": labels_en, "de": labels_de, "fr": labels_fr, "it": labels_it},
    )


def municipality(
    field_name: str = "municipality",
    district: str | None = None,
) -> ConfigParam:
    """Municipality/district selection."""
    fields = {field_name: "Municipality"}
    labels_en = {field_name: "Municipality"}
    labels_de = {field_name: "Gemeinde"}
    labels_fr = {field_name: "Commune"}
    labels_it = {field_name: "Comune"}

    if district:
        fields[district] = "District"
        labels_en[district] = "District"
        labels_de[district] = "Ortsteil"
        labels_fr[district] = "Quartier"
        labels_it[district] = "Quartiere"

    return ConfigParam(
        fields=fields,
        widget="text",
        labels={"en": labels_en, "de": labels_de, "fr": labels_fr, "it": labels_it},
    )


def dropdown(
    field_name: str,
    options: list[str],
    label: str | None = None,
) -> ConfigParam:
    """Selection from a fixed list of options."""
    display = label or field_name.replace("_", " ").title()
    return ConfigParam(
        fields={field_name: display},
        widget="select",
        labels={
            "en": {field_name: display},
        },
    )


def text_field(
    field_name: str,
    label: str | None = None,
) -> ConfigParam:
    """Free text entry."""
    display = label or field_name.replace("_", " ").title()
    return ConfigParam(
        fields={field_name: display},
        widget="text",
        labels={
            "en": {field_name: display},
        },
    )
