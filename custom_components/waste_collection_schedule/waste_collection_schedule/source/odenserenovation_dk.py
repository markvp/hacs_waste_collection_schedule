from datetime import datetime, timedelta

import requests
from waste_collection_schedule import Collection

TITLE = "Odense Renovation"
DESCRIPTION = "Source for Odense Renovation"
URL = "https://odenserenovation.dk"
TEST_CASES = {
    "Jernbanegade 19, Odense C": {"addressNo": 122518},
    "Nyborgvej 3, Odense C": {"addressNo": 133517},
    "Næsbyhave 105, Odense N": {"addressNo": 134008},
}

API_URL = "https://mit.odenserenovation.dk/api/Calendar/GetCalendarByAddress"
ICON_MAP = {
    "00": "mdi:trash-can",
    "10": "mdi:archive",
    "20": "mdi:trash-can",
    "30": "mdi:food-apple",
    "40": "mdi:archive",
    "50": "mdi:bottle-wine",
    "60": "mdi:bottle-soda",
}

class Source:
    def __init__(self, addressNo: int):
        self.addressNo = addressNo

    def fetch(self):
        fromDate = datetime.now()
        toDate = datetime.now() + timedelta(days=+365)

        response = requests.get(
            API_URL,
            params={
                "addressNo": self.addressNo,
                "startDate": fromDate.isoformat(),
                "endDate": toDate.isoformat(),
                "noCache": False,
            },
        )
        response.raise_for_status()

        months = response.json()["Months"]

        entries = []

        for month in months:
            for day in month["Days"]:
                date = datetime.strptime(day["Date"], "%Y-%m-%dT%H:%M:%S").date()
                for bin in day["Bins"]:
                    entries.append(
                        Collection(
                            date=date,
                            t=bin["Label"],
                            icon=ICON_MAP.get(bin["BinCode"], "mdi:trash-can-outline"),
                        )
                    )

        return entries
