import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import aiohttp

_LOGGER = logging.getLogger(__name__)

URL_TEMPLATE = (
    "https://vannstand.kartverket.no/tideapi.php?lat={lat}&lon={lon}"
    "&fromtime={fromtime}&totime={totime}&datatype=all&refcode=cd&lang=no"
    "&interval=10&dst=0&tzone=&tide_request=locationdata"
)


class KartverketTideAPI:
    """API-klassen for å hente tidevannsdata fra Kartverket."""

    def __init__(self, lat: float, lon: float, forecast_days: int = 1):
        self.lat = lat
        self.lon = lon
        self.forecast_days = forecast_days

    async def fetch_tide_data(self):
        """Hent tidevannsdata fra API-et."""
        now = datetime.utcnow()
        fromtime = (now - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%S")
        totime = (now + timedelta(days=self.forecast_days)).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        url = URL_TEMPLATE.format(
            lat=self.lat,
            lon=self.lon,
            fromtime=fromtime,
            totime=totime,
        )

        _LOGGER.debug(
            "Henter tidevannsdata for %s dager fra Kartverket", self.forecast_days
        )

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise RuntimeError(
                        f"Feil ved henting av tidevannsdata: HTTP {response.status}"
                    )
                xml_data = await response.text()

        return self.parse_tide_data(xml_data)

    def parse_tide_data(self, xml_data: str):
        """Parse XML-data og returner tidevannsdata."""
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as err:
            raise ValueError(f"Feil ved parsing av XML: {err}") from err

        tide_data = {"observation": [], "prediction": [], "forecast": []}

        for data in root.findall(".//data"):
            data_type = data.attrib.get("type")
            if data_type not in tide_data:
                continue

            for waterlevel in data.findall("waterlevel"):
                try:
                    tide_data[data_type].append(
                        {
                            "time": waterlevel.attrib["time"],
                            "level": float(waterlevel.attrib["value"]),
                        }
                    )
                except (KeyError, ValueError):
                    _LOGGER.warning("Ignorerer ugyldig vannstandspunkt")

        return tide_data
