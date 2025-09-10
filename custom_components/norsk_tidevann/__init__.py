import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, PLATFORMS
from .api import KartverketTideAPI

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Sett opp Kartverket Tide fra en config entry."""
    latitude = entry.data["latitude"]
    longitude = entry.data["longitude"]
    location_name = entry.data["location_name"]  # 💥 Brukerdefinert navn!

    api = KartverketTideAPI(latitude, longitude)

    async def async_update_data():
        """Hent data fra API-et."""
        try:
            return await api.fetch_tide_data()
        except Exception as err:
            raise UpdateFailed(f"Feil ved henting av data: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Kartverket Tide - {location_name}",  # 💥 Bruk lokasjonsnavnet i logg/system!
        update_method=async_update_data,
        update_interval=timedelta(minutes=15),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True






