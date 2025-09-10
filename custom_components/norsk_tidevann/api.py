import logging
import aiohttp
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)

URL_TEMPLATE = "https://vannstand.kartverket.no/tideapi.php?lat={lat}&lon={lon}&fromtime={fromtime}&totime={totime}&datatype=all&refcode=cd&lang=no&interval=10&dst=0&tzone=&tide_request=locationdata"

class KartverketTideAPI:
    """API-klassen for å hente tidevannsdata fra Kartverket."""

    def __init__(self, lat: float, lon: float):
        """Initialiserer API-klassen med posisjon (breddegrad/lengdegrad)."""
        self.lat = lat
        self.lon = lon

    async def fetch_tide_data(self):
        """Henter tidevannsdata fra API-et."""
        fromtime = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        totime = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        url = URL_TEMPLATE.format(lat=self.lat, lon=self.lon, fromtime=fromtime, totime=totime)
        
        _LOGGER.info(f"Henter tidevannsdata fra: {url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    _LOGGER.error(f"Feil ved henting av tidevannsdata: HTTP {response.status}")
                    return None
                xml_data = await response.text()

        return self.parse_tide_data(xml_data)

    def parse_tide_data(self, xml_data: str):
        """Parser XML-dataen og returnerer tidevannsdata."""
        try:
            root = ET.fromstring(xml_data)
            tide_data = {"observation": [], "prediction": [], "forecast": []}

            for data in root.findall(".//data"):
                data_type = data.attrib.get("type")
                if data_type in tide_data:
                    for waterlevel in data.findall("waterlevel"):
                        tide_data[data_type].append({
                            "time": waterlevel.attrib["time"],
                            "level": float(waterlevel.attrib["value"])
                        })

            return tide_data
        except ET.ParseError as e:
            _LOGGER.error(f"Feil ved parsing av XML: {e}")
            return None














