"""Icon auto-detection for waste collection types.

Provides `guess_icon()` which maps waste type names to Material Design Icons
based on keyword matching. Supports waste type names in English, German, French,
Italian, Dutch, Swedish, Polish, Czech, Norwegian, Danish, Lithuanian, and more.

Built from keyword analysis of 529 source ICON_MAP definitions covering 1180+
waste type to icon mappings across 141 unique icons.
"""

# Keyword patterns ordered from most specific to least specific.
# Each entry: (keywords_to_match, icon_value)
# Keywords are checked as substrings against the lowercased waste type name.
# First match wins, so more specific patterns must come first.
ICON_KEYWORDS: list[tuple[list[str], str]] = [
    # --- Christmas trees ---
    (
        ["christmas", "christbaum", "weihnachtsbaum", "choinki", "tannenbaum",
         "kerstbo", "juletre", "juletræ", "julgran"],
        "mdi:pine-tree",
    ),
    # --- Hazardous / problematic waste ---
    (
        ["hazardous", "schadstoffe", "schadstoff", "problemmüll", "problemabfall",
         "giftmobil", "farligt", "pericolosi", "sondermüll", "sonderabfall",
         "schadstoffsammlung", "nappy", "sanitary"],
        "mdi:biohazard",
    ),
    # --- Batteries ---
    (
        ["battery", "batterie", "batterien", "batteri"],
        "mdi:battery",
    ),
    # --- Textiles / clothing ---
    (
        ["textile", "textil", "kleidung", "clothing", "kleider", "kläder",
         "tøj", "indumenti", "vêtement", "textiel"],
        "mdi:tshirt-crew",
    ),
    # --- Bulky waste / furniture ---
    (
        ["sperrmüll", "bulky", "sperrgut", "encombrant", "ingombranti",
         "grofvuil", "grofsperr", "skrymmande", "storskrald"],
        "mdi:sofa",
    ),
    # --- Electronics / WEEE ---
    (
        ["electronic", "elektro", "weee", "e-waste", "elektrisk", "raee"],
        "mdi:factory",
    ),
    # --- Food waste (specific, before organic/bio) ---
    (
        ["food waste", "food bin", "food caddy", "food scrap",
         "küchenabf", "déchets alimentaires",
         "food only", "food recycling"],
        "mdi:food",
    ),
    # --- Organic / bio / garden + food ---
    (
        ["kompost", "compost"],
        "mdi:compost",
    ),
    (
        ["bio", "organic", "biotonne", "bioabf", "biomüll", "biowaste",
         "organik", "organisch", "gft", "groente", "végéta",
         "organico", "organiche", "biologico", "grüne tonne",
         "biocontainer", "bioj", "biol", "bioh",
         "matorganic", "nasses", "braune tonne", "food and garden",
         "garden and food", "brown bin", "brown caddy",
         "déchets organiques", "verts", "garden waste", "garden bin",
         "garden vegetation", "gartenabf", "grünschnitt", "grünabfall",
         "grüngut", "grünzeug", "grünabfuhr", "grüne",
         "yard waste", "yard trim", "lawn", "green waste",
         "green lid", "green bin",
         "haveaffald", "trädgård", "matavfall", "madaffald",
         "lebensmittel",
         "braun"],
        "mdi:leaf",
    ),
    # --- Paper / cardboard ---
    (
        ["altpapier", "papier", "paper", "karton", "cardboard", "carta",
         "papir", "pappe", "papper", "tidning", "pappier",
         "blaue tonne", "blue sack", "blue bag", "blue bin",
         "blue lid", "blue box",
         "journal", "newspaper", "drikkekartong"],
        "mdi:package-variant",
    ),
    # --- Glass ---
    (
        ["glas", "glass", "vetro", "verre", "szkło", "altglas",
         "glascontainer", "stikl", "flaschen", "bouteille"],
        "mdi:glass-fragile",
    ),
    # --- Plastic / packaging / recycling (lightweight packaging) ---
    (
        ["gelber sack", "gelbe tonne", "gelbe säcke", "gelben sack",
         "gelbe", "gelber",
         "yellow bag", "yellow bin", "yellow lid", "yellow box",
         "leichtverpackung", "verpackung", "wertstoff",
         "lightweight", "kunststoff", "plastik",
         "plastic", "plastica", "plastique",
         "emballage", "imballaggi", "pmd",
         "tworzywa", "metaal", "metall"],
        "mdi:recycle",
    ),
    # --- Residual / general waste ---
    (
        ["restmüll", "restabfall", "residual", "refuse", "garbage",
         "trash", "rubbish", "general waste", "hausmüll",
         "ordures", "rifiut", "indifferen",
         "zmieszane", "restavfall", "dagsrenovation",
         "black bin", "black bag", "grey bin", "gray bin",
         "red lid", "red bin", "graue tonne", "schwarze tonne",
         "non recycl", "landfill", "mixed waste",
         "mülltonne", "abfalltonne", "kehricht",
         "poubelle", "déchets ménag", "domestic",
         "schwarz", "grau", "restmuell",
         "waste bin", "household waste", "general bin"],
        "mdi:trash-can",
    ),
    # --- Recycling (generic catch-all for recycling terms) ---
    (
        ["recycl", "recyclable", "recyclage", "ricicl",
         "återvinning", "genbrug", "hergebruik",
         "dry mixed", "comingled", "commingled",
         "mixed recycling", "co-mingled"],
        "mdi:recycle",
    ),
]


def guess_icon(waste_type: str) -> str | None:
    """Guess an MDI icon for a waste collection type based on keyword matching.

    Args:
        waste_type: The waste collection type name (e.g., "Restmüll", "Recycling").

    Returns:
        An MDI icon string (e.g., "mdi:trash-can") or None if no match found.
    """
    if not waste_type:
        return None

    lower = waste_type.lower()

    for keywords, icon in ICON_KEYWORDS:
        for keyword in keywords:
            if keyword in lower:
                return icon

    return None
