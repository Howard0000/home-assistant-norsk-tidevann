import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import KartverketTideAPI
from .const import CONF_FORECAST_DAYS, DEFAULT_FORECAST_DAYS, DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Sett opp Norsk Tidevann fra en config entry."""
    latitude = entry.data["latitude"]
    longitude = entry.data["longitude"]
    location_name = entry.data["location_name"]
    forecast_days = entry.options.get(CONF_FORECAST_DAYS, DEFAULT_FORECAST_DAYS)

    api = KartverketTideAPI(latitude, longitude, forecast_days)

    async def async_update_data():
        try:
            return await api.fetch_tide_data()
        except Exception as err:
            raise UpdateFailed(f"Feil ved henting av data: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Kartverket Tide - {location_name}",
        update_method=async_update_data,
        update_interval=timedelta(minutes=15),
        config_entry=entry,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Last ut en config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Last integrasjonen på nytt etter endrede alternativer."""
    await hass.config_entries.async_reload(entry.entry_id)
