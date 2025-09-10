import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN


class NorskTidevannConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Norsk Tidevann integration."""

    async def async_step_user(self, user_input=None):
        """Håndter konfigurasjonsflyt fra GUI."""
        errors = {}

        if user_input is not None:
            try:
                lat = float(user_input["latitude"])
                lon = float(user_input["longitude"])
            except (KeyError, ValueError, TypeError):
                errors["base"] = "invalid_coords"
            else:
                # Lag en unik ID basert på avrundede koordinater
                uid = f"{round(lat, 4)}_{round(lon, 4)}"
                await self.async_set_unique_id(uid)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input["location_name"],
                    data={
                        "latitude": lat,
                        "longitude": lon,
                        "location_name": user_input["location_name"],
                    },
                )

        # Hent standardposisjon fra Home Assistant
        hass: HomeAssistant = self.hass
        default_latitude = hass.config.latitude
        default_longitude = hass.config.longitude

        # Definer skjemaet for GUI
        schema = vol.Schema({
            vol.Required("location_name", default="Mitt sted"): str,
            vol.Required("latitude", default=default_latitude): float,
            vol.Required("longitude", default=default_longitude): float,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
